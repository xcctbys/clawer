USER=root
PASSWORD=poiuytre
CREATE_DATABASE=profiles/mysql/create.sql
DROP_DATABASE=profiles/mysql/clear.sql

all:
	python manage.py structured

db:drop_database create_database
	python manage.py migrate

drop_database:
	mysql -u$(USER) -p$(PASSWORD) < $(DROP_DATABASE)

create_database:
	mysql -u$(USER) -p$(PASSWORD) < $(CREATE_DATABASE)
