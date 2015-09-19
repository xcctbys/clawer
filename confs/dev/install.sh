#!/bin/bash

PIP=~/Documents/pyenv/dj14/bin/pip

if [ ! -f ${PIP} ]; then
    PIP=/d/virtualenvs/dj14/Scripts/pip
fi

echo "Python ${PIP}"

LIBS="django==1.4.15 pillow Pygments Markdown MySQL-python django-celery south raven python-memcached django-debug-toolbar six redis requests threadpool python-crontab"

for lib in ${LIBS}
do
   ${PIP} install ${lib}
done
