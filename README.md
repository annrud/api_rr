#api_yamdb

*Проект api_yamdb собирает отзывы пользователей на произведения и составляет рейтинг последних.*

##Этапы и команды для сборки и запуска приложения:
1. Установите docker и docker-compose
2. Сборка и запуск контейнеров

```docker-compose up -d --build```

3. Выполнение миграций

```docker-compose exec web python manage.py migrate --noinput``` 

4. Сбор статики

```docker-compose exec web python manage.py collectstatic --no-input```

5. Создание суперпользователя: 

```docker-compose exec web python manage.py createsuperuser```

6. Заполнение базы начальными данными

```docker-compose exec web python manage.py loaddata fixtures.json```