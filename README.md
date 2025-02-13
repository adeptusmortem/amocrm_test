# Проект: Мониторинг состояния ресурсов серверов
## Описание проекта
Проект представляет собой веб-приложение для мониторинга состояния ресурсов серверов. Приложение периодически опрашивает эндпоинты серверов, собирает данные о загрузке CPU, памяти, диска и времени работы (uptime), сохраняет их в базу данных и проверяет на наличие инцидентов (выход параметров за пределы нормы).  

## Основной функционал:  
1. Периодический опрос эндпоинтов:  
    - Каждые 15 минут приложение опрашивает 30 серверов.
    - Данные сохраняются в базу данных MySQL.
2. Мониторинг ресурсов:  
    - Проверка данных на превышение пороговых значений:
        - CPU: > 85% в течение 30 минут.
        - Память (Mem): > 90% в течение 30 минут.
        - Диск (Disk): > 95% в течение 2 часов.
    - Инциденты записываются в базу данных.
3. Веб-интерфейс:  
    - Просмотр данных о состоянии серверов.
    - Просмотр инцидентов.  

## Технологии:  
- Python: 3.12
- Django: 5.0
- MySQL: 8.0
- Celery: 5.4
- Redis: 5.2
- Docker

## Запуск проекта через Docker  
**Предварительные требования**  
1. Установите Docker и Docker Compose.  
2. Убедитесь, что порты 8000, 3306 и 6379 свободны на вашем компьютере.  

## Инструкция по запуску
1. Скачайте Docker-образ:  
Выполните команду для скачивания готового Docker-образа:  

```bash
docker pull adeptusmortem/monitoring-app:latest
```

2. Создайте файл `docker-compose.yml`:  
Создайте файл `docker-compose.yml` в удобной директории и добавьте в него следующее содержимое:  

```yaml
services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"

  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: monitoring_db
      MYSQL_USER: your_user
      MYSQL_PASSWORD: your_password
      MYSQL_ROOT_PASSWORD: rootpassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  web:
    image: adeptusmortem/monitoring-app:latest
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - db

  celery:
    image: adeptusmortem/monitoring-app:latest
    command: celery -A celery_app worker --loglevel=info --pool=solo
    volumes:
      - .:/app
    depends_on:
      - redis
      - db

  celery-beat:
    image: adeptusmortem/monitoring-app:latest
    command: celery -A celery_app beat --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - redis
      - db

volumes:
  mysql_data:
```

3. Создайте файл `.env`:  
Создайте файл `.env` в той же директории, где находится `docker-compose.yml`, и добавьте в него переменные окружения:  

```env
MYSQL_DATABASE=monitoring_db
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_ROOT_PASSWORD=rootpassword
```

4. Запустите контейнеры:  
Выполните команду для запуска контейнеров:  

```bash
docker-compose up -d
```

5. Примените миграции:  
Откройте новый терминал и выполните:  

```bash
docker-compose exec web python manage.py migrate
```

6. Создайте суперпользователя:  

```bash
docker-compose exec web python manage.py createsuperuser
```

7. Запустите Celery Worker и Beat:  
Если они не запустились автоматически, выполните:  

```bash
docker-compose exec celery celery -A celery_app worker --loglevel=info --pool=solo
docker-compose exec celery-beat celery -A celery_app beat --loglevel=info
```

8. Откройте веб-интерфейс:  
Перейдите по адресу http://localhost:8000.  

## Настройка проекта
Настройка базы данных  
1. Измените настройки базы данных в `settings.py`, если необходимо:  

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_DATABASE', 'monitoring_db'),
        'USER': os.getenv('MYSQL_USER', 'your_user'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD', 'your_password'),
        'HOST': 'db',  # Имя сервиса в docker-compose.yml
        'PORT': '3306',
        'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}
```

2. Убедитесь, что база данных monitoring_db создана в контейнере MySQL.  

## Настройка Celery  
1. Убедитесь, что Redis запущен и доступен:  

```bash
docker-compose exec redis redis-cli ping
```
Ожидаемый ответ: `PONG`.  

2. Проверьте настройки Celery в `settings.py`:  

```python
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
```

## Настройка периодических задач  
1. Периодические задачи настраиваются в `celery.py`:  

```python
app.conf.beat_schedule = {
    'poll-servers': {
        'task': 'monitor.tasks.poll_servers',
        'schedule': 900.0,  # 15 минут
    },
    'check-incidents': {
        'task': 'monitor.tasks.check_incidents',
        'schedule': 300.0,  # 5 минут
    },
}
```

2. Убедитесь, что задачи poll_servers и check_incidents определены в monitor/tasks.py.  

## Развертывание на сервере  
1. Загрузка образа на сервер  
Скачайте Docker-образ на сервер:  

```bash
docker pull adeptusmortem/monitoring-app:latest
```

2. Скопируйте файлы docker-compose.yml и .env на сервер.  

3. Запустите контейнеры:  

```bash
docker-compose up -d
```