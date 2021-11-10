# Учебный проект foodgram, сайт рецептов.

Это сайт рецептов еды, на котором пользователи сами могут их создавать, присваивать им теги,
добавлять в избранное и в список покупок, который сгенерирует файл с необходимым количеством ингредиентов для приготовления.
Пользователи могут подписываться на любимых авторов и отслеживать их обновления.

В учебном проекте уже был готовый фронтенд, к нему реализовал бэкенд по прилагающейся спецификации API.
В нём используются Python 3.9.7, Django 3.2.7, DRF и PostgreSQL.  Cистема аутентификации через токены использует стандартный функционал DRF.
Формат передачи данных API - JSON, примеры запросов вы можете посмотреть в развёрнутом проекте на http://localhost/api/docs/.

Перед развёртывание необходимо настроить .env по примеру в backend/.env.template.
И, если запускаете только бэкенд часть, установить PostgreSQL.

## Развернуть проект в Docker:

Собрать и запустить контейнер:

```
cd infra/

docker-compose up --build -d
```

Выполнить миграции:

```
docker-compose exec backend python manage.py migrate --noinput
```

Заполнить БД началными данными:

```
docker-compose exec backend python manage.py loaddata data/ingredients.json data/tags.json data/users.json
```

Создать суперпользователя:

```
docker-compose exec backend python manage.py createsuperuser
```

Собрать статику:

```
docker-compose exec backend python manage.py collectstatic
```

Проект будет доступен по адресу - http://127.0.0.1/signin

## Как запустить только бэкенд:

Поменять рабочий каталог на папку backend:

```
cd backend
```

Создать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
