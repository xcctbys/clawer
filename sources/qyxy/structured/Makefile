USER=root
PASSWORD=poiuytre
SQL_CREATE=profiles/mysql/create.sql
SQL_DROP=profiles/mysql/clear.sql

all:
	python manage.py structured

db:drop_db create_db
	python manage.py migrate

drop_db:
	mysql -u$(USER) -p$(PASSWORD) < $(SQL_DROP)

create_db:
	mysql -u$(USER) -p$(PASSWORD) < $(SQL_CREATE)
