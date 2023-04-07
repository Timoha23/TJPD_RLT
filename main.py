import calendar
import os
from datetime import datetime, timedelta

import pymongo
from dotenv import load_dotenv


load_dotenv()

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

HOURS_IN_DAY = 24

TYPES = {
    'hour': lambda x: 1,
    'day': lambda x: HOURS_IN_DAY,
    'month': lambda x: calendar.monthrange(x.year, x.month)[1] * HOURS_IN_DAY,
    'year': lambda x: (366 * HOURS_IN_DAY if x.year % 4 == 0
                       else 365 * HOURS_IN_DAY),
}


def get_full_date(date: dict) -> str:
    """
    Преобразование даты в нужный формат
    """

    year = date.get('year')
    month = date.get('month') or 1
    day = date.get('day') or 1
    hour = date.get('hour') or 0
    full_date = datetime(year=year, month=month, day=day, hour=hour)

    return full_date.strftime('%Y-%m-%dT%H:%M:%S')


def get_group_by_date(type: str) -> dict:
    """
    Получение выражения группировки в зависимости от типа
    """

    default_group = {'year': {'$year': '$dt'}}

    if type == 'month':
        default_group.update({'month': {'$month': '$dt'}})

    elif type == 'day':
        default_group.update({'month': {'$month': '$dt'},
                              'day': {'$dayOfMonth': '$dt'}})
    elif type == 'hour':
        default_group.update({'month': {'$month': '$dt'},
                              'day': {'$dayOfMonth': '$dt'},
                              'hour': {'$hour': '$dt'}},)

    return default_group


def get_db_collection():
    """
    Соединение с бд и получение коллекции
    """

    db_client = pymongo.MongoClient(HOST, int(PORT))
    current_db = db_client['workers']
    collection = current_db['sample_collection']

    return collection


def get_correct_date(start: str, end: str, group_type: str) -> tuple:
    """
    Коррекция данных start_date и end_date
    """

    if group_type == 'hour':
        start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
    elif group_type == 'day':
        start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S').replace(hour=0)
    elif group_type == 'month':
        start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S').replace(day=1,
                                                                      hour=0)
    elif group_type == 'year':
        start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S').replace(month=1,
                                                                      day=1,
                                                                      hour=0)
    end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')
    return (start, end)


async def get_salary_aggregation(data: dict) -> dict:
    """
    Получение агрегации по зп
    """

    result = {
        "dataset": [],
        "labels": [],
        }

    group_type = data.get('group_type')

    start_date, end_date = get_correct_date(data.get('dt_from'),
                                            data.get('dt_upto'),
                                            group_type)

    group_by_date = get_group_by_date(group_type)
    collection = get_db_collection()

    collection = collection.aggregate([
        {'$match': {'$and': [{'dt': {'$gte': start_date}},
                             {'dt': {'$lte': end_date}}]}},
        {'$group':
            {'_id': group_by_date, 'total': {'$sum': '$value'}}},
        {'$sort': {'_id': 1}}
    ])

    for item in collection:
        full_date_label = get_full_date(item['_id'])
        full_date = datetime.strptime(full_date_label, '%Y-%m-%dT%H:%M:%S')

        while start_date != full_date and start_date <= end_date:
            result['labels'].append(start_date.strftime('%Y-%m-%dT%H:%M:%S'))
            result['dataset'].append(0)
            start_date += timedelta(hours=TYPES.get(
                data.get('group_type'))(start_date))

        result['dataset'].append(item['total'])
        result['labels'].append(full_date_label)
        start_date += timedelta(hours=TYPES.get(
            data.get('group_type'))(start_date))

    while start_date <= end_date:
        result['labels'].append(start_date.strftime('%Y-%m-%dT%H:%M:%S'))
        result['dataset'].append(0)
        start_date += timedelta(hours=TYPES.get(
            data.get('group_type'))(start_date))

    return result
