#!/bin/bash

PY=~/Documents/pyenv/dj14/bin/python
WORKDIR=/d/gitroom/todo/todo

if [ ! -d ${WORKDIR} ];then
    WORKDIR=~/Documents/gitroom/todo/todo
fi

if [ ! -f ${PY} ]; then
    PY=/d/virtualenvs/dj14/Scripts/python
fi


APPS="simplefan like social comment note help notification sla sitelog account sitehelper psychological todo"

if [ ! -z $* ]; then
    APPS="$*"
fi


for app in ${APPS}
do
    echo "=========== ${app} ==============="
    cd ${WORKDIR};$PY manage.py test ${app} --failfast --noinput
    if [ ! $? -eq 0 ]; then
       exit 1
    fi 
    echo "------------------------------------"
done
