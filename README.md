# foodgram

## Описание:
«Продуктовый помощник» - сайт для публикации рецептов. На сайте пользователи могут: публиковать рецепты, подписываться на публикации других пользователей, добавлять рецепты в избранное. На сайте есть фукнкция «Список покупок», которая позволяет пользователям скачивать список продуктов с указанием необходимого кол-ва ингредиентов, которые нужно купить для приготовления выбранных пользователем блюд. 

## Технологии
В проекте мной был реализован backend c использованием следующих технологий:
- Python 3.7
- Django 3.2.19
- Django Rest Framework 3.12.4
- PostgreSQL 13.0
- Nginx 1.19.3
- Gunicorn 20.0.4
- Docker 24.0.2
- Docker Compose 1.25.0
- Yandex Cloud

## Запуск проекта:

Инструкция для запуска проекта:

* Клонировать репозиторий

```
git clone git@github.com:MaryMash/foodgram-project-react.git
```

* Перейти в директорию /infra, создать файл .env с переменными среды. Пример заполнения:

```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД 
SECRET_KEY= # секретный ключ из настроек Django
```

* Запустить контейнер

```
docker-compose up -d
```

* Выполнить миграции

```
docker-compose exec backend python manage.py migrate
```

* Собрать статику

```
docker-compose exec backend python manage.py collectstatic --no-input 
```

В директории /infra нахоится файл fixtures.json c данными для загрузки в базу данных. Для их загрузки необходимо:

* Скопировть файл в контейнер
```
docker cp fixtures.json infra_backend_1:app/
```
* Загрузить данные в базу
```
docker-compose exec backend python manage.py loaddata fixtures.json
```
* Создать пользователя с доступом администратора
```
docker-compose exec web python manage.py createsuperuser
```
## Данные для подключения:
- Сайт доступен по адресу http://localhost/
- Админка: http://localhost/admin/
- Документация: http://localhost/api/docs/

## Планы по доработке проекта:
- Добавить тесты
- Реализовать СI/CD c помощью github actions