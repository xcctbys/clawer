#!/bin/bash

PIP=/home/virtualenvs/py27/bin/pip

echo "Python ${PIP}"

LIBS="django==1.4.15 pillow Pygments Markdown MySQL-python django-celery south raven python-memcached django-debug-toolbar six redis"

for lib in ${LIBS}
do
   ${PIP} install ${lib}
done
