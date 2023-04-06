# TJPD_RLT

## Использованные технологии

* python 3.10.6;
* aiogram 2.25.1;
* asyncio 3.4.3;
* pymongo 4.3.3;
* pytest 7.2.2;
* pytest-asyncio 0.21.0.


## Как запустить проект:

- Склонируйте репозиторий на компьютер;
```
git clone https://github.com/Timoha23/TJPD_RLT.git
```
- Импортируйте данные из директории dump/sampleDB/ в БД Mongo.
```
mongorestore --db <name> dump/sampleDB/
```
- Установите виртуальное окружение;
```
python -m venv venv
```
- Активируйте виртуальное окружение;
```
source venv/Scripts/activate
```
- Установите зависимости из файла requirements.txt;
```
pip install -r requirements.txt
``` 
- Запустите бота:
```
python bot.py
```
