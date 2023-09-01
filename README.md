## Сайт кафедры cистемного программирования СПбГУ

Основная ветка - **current**

### Установка

Для установки требуется *Python 3.8*

1. Клонировать репозиторий

2. Перейти в корневую папку

3. Переключиться на ветку *ver2_dev*
```bash
git checkout ver2_dev
```

4. Создать виртуальное окружение
```bash
python -m venv venv
```

5. Активировать виртуальное окружение

Windows
```bash
venv\Scripts\activate
```

Linux
```bash
. venv/bin/activate
```

6. Обновить `pip` и установить необходимые пакеты
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

7. Перейти в папку *src*
```bash
cd src
```

8. Инициализировать базу данных
```
python flask_se.py init
```

9. Для локального тестирования запустить сайт (для деплоя надо использовать uWSGI)
```
python flask_se.py
```

10. Сайт запускается по адресу `http://127.0.0.1:5000`
