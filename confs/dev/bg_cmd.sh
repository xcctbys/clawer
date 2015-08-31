#!/bin/bash

WORKDIR=/d/gitroom/todo/todo
PY=~/Documents/pyenv/dj14/bin/python

if [ ! -d ${WORKDIR} ]; then
    WORKDIR=~/Documents/gitroom/todo/todo
fi

if [ ! -f ${PY} ]; then
    PY=/d/virtualenvs/dj14/Scripts/python
fi

cd ${WORKDIR};${PY} manage.py $*
