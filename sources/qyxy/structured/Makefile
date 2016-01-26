USER=root
PASSWORD=poiuytre
CREATE_DATABASE=profiles/mysql/create.sql
DROP_DATABASE=profiles/mysql/clear.sql

all: data

data:
	python manage.py structured

db: sql
	python manage.py migrate

db_init: drop_database create_database sql
	python manage.py migrate

sql:
	python manage.py makemigrations

drop_database:
	mysql -u$(USER) -p$(PASSWORD) < $(DROP_DATABASE)

create_database:
	mysql -u$(USER) -p$(PASSWORD) < $(CREATE_DATABASE)
