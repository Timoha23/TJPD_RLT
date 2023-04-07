import json
from datetime import datetime


def data_validator(data: dict) -> dict:
    """
    Проверка данных из data на валидность
    """

    try:
        data = json.loads(data)
        if not isinstance(data, dict):
            return {'error': 'Ожидаю словарь'}
    except json.decoder.JSONDecodeError:
        return {'error': 'Ожидаю словарь'}

    if None in (data.get('dt_from'), data.get('dt_upto'),
                data.get('group_type')):
        return {'error': 'Неверное название полей'}

    group_type = data.get('group_type')

    try:
        start_date = datetime.strptime(data.get('dt_from'),
                                       '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return {'error': 'Ошибка в поле dt_from"). '
                         'Невозможно преобразовать в дату.'}
    try:
        end_date = datetime.strptime(data.get('dt_upto'),
                                     '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return {'error': 'Ошибка в поле dt_upto"). '
                         'Невозможно преобразовать в дату'}

    if start_date >= end_date:
        return {'error': 'Убедитесь что правильно ввели дату.'}

    types = ('hour', 'day', 'month', 'year')
    if group_type not in types:
        return {'error': 'Неизвестный тип.'}

    return {'error': None, 'data': data}
