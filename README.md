![Foodgram project](https://github.com/remark-ekz/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# **Foodgram-project**

# Описание

Сервис для размещения своих любымых рецептов в сети. В нем вы можете составить описание рецепта, уточнить какие используются в нем ингредиенты, добавить фото кулинарного шедевра и указать желательное время приема пищи.

# Технологии

- Python 3.9.7
- Django 2.2.16
- Django Rest Framework
- PostgreSQL
- gunicorn
- nginx
- Docker Compose

# URL's

- http://51.250.95.95

# Админ-панель

Данные для доступа в админ-панель:

email: y@mail.ru

password: y

# Документация

Для просмотра документации к API перейдите по адресу:
- http://51.250.95.95/api/redoc

## Начало работы
* Клонировать репозиторий, перейти в директорию с проектом:
```
git clone https://github.com/remark-ekz/foodgram-project-react.git
```
```
cd foodgram-project-react
```

* Установить виртуальное окружение, активировать его:
```
python -m venv venv
```
```
. venv/scripts/activate
```

* Перейти в директорию с приложением ```backend```, установить зависимости:
```
pip install -r requirements.txt
```

* Для подключения GitHub Actions в ```backend```, необходимо создать директорию 
```.github/workflows``` и скопировать в неё файл ```foodgram_workflow.yml``` из
директории проекта.

* Для прохождения тестов, в директории ```infra```, создать файл ```.env``` с
переменными окружения:
```
# settings.py
SECRET_KEY=           # стандартный ключ, который создается при старте проекта

ENGINE=django.db.backends.postgresql
DB_NAME               # имя БД - postgres (по умолчанию)
POSTGRES_USER         # логин для подключения к БД - postgres (по умолчанию)
POSTGRES_PASSWORD     # пароль для подключения к БД (установите свой)
DB_HOST=db            # название сервиса (контейнера)
DB_PORT=5432          # порт для подключения к БД
```

## Workflow

Для использования Continuous Integration (CI) и Continuous Deployment (CD): в
репозитории GitHub Actions ```Settings/Secrets/Actions``` прописать Secrets -
переменные окружения для доступа к сервисам:

```
SECRET_KEY            # стандартный ключ, который создается при старте проекта

ENGINE=django.db.backends.postgresql
DB_NAME               # имя БД - postgres (по умолчанию)
POSTGRES_USER         # логин для подключения к БД - postgres (по умолчанию)
POSTGRES_PASSWORD     # пароль для подключения к БД (установите свой)
DB_HOST=db            # название сервиса (контейнера)
DB_PORT=5432          # порт для подключения к БД

DOCKER_USERNAME       # имя пользователя в DockerHub
DOCKER_PASSWORD       # пароль пользователя в DockerHub
HOST                  # ip_address сервера
USER                  # имя пользователя
SSH_KEY               # приватный ssh-ключ (cat ~/.ssh/id_rsa)
PASSPHRASE            # кодовая фраза (пароль) для ssh-ключа

TELEGRAM_TO           # id телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
TELEGRAM_TOKEN        # токен бота (получить токен можно у @BotFather, /token, имя бота)
```

При push в ветку main автоматически отрабатывают сценарии:
* *tests* - проверка кода на соответствие стандарту PEP8.
Дальнейшие шаги выполняются только если push был в ветку main;
* *build_and_push_to_docker_hub* - сборка и доставка докер-образов на DockerHub
* *deploy* - автоматический деплой проекта на боевой сервер. Выполняется
копирование файлов из DockerHub на сервер;
* *send_message* - отправка уведомления в Telegram.

## Подготовка удалённого сервера
* Войти на удалённый сервер, для этого необходимо знать адрес сервера, имя
пользователя и пароль. Адрес сервера указывается по IP-адресу или по доменному
имени:
```
ssh <username>@<ip_address>
```

* Остановить службу ```nginx```:
```
sudo systemctl stop nginx
```

* Установить Docker и Docker-compose:
```
sudo apt update
sudo apt upgrade -y
sudo apt install docker.io
sudo apt install docker-compose -y
```

* Проверить корректность установки Docker-compose:
```
sudo docker-compose --version
```

* Скопировать файлы ```docker-compose.yaml``` и
```nginx.conf``` из проекта (локально) на сервер в
```home/<username>/docker-compose.yaml``` и
```home/<username>/nginx.conf``` соответственно:

  * перейти в директорию с файлом ```docker-compose.yaml``` и выполните:
  ```
  scp docker-compose.yaml <username>@<ip_address>:/home/<username>/docker-compose.yaml
  ```
  * перейти в директорию с файлом ```nginx.conf``` и выполните:
  ```
  scp nginx.conf <username>@<ip_address>:/home/<username>/nginx.conf
  ```

## После успешного деплоя
* Создать миграции:
```
docker-compose exec backend python manage.py makemigrations
```
* Применить миграции:
```
docker-compose exec backend python manage.py migrate
```
* Создать суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```
* Собрать статические файлы:
```
docker-compose exec backend python manage.py collectstatic --no-input
```
* Заполнить ингредиенты:
```
docker-compose exec backend python manage.py import
```

* Для проверки работоспособности приложения, перейти на страницу:
```
http:/<ip_address>/admin/
```
* Для проверки работоспособности приложения, перейти на страницу