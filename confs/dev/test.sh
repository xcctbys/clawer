#!/bin/bash

PY=~/Documents/pyenv/dj14/bin/python
WORKDIR=/d/gitroom/nice-clawer/clawer

if [ ! -d ${WORKDIR} ];then
    WORKDIR=~/Documents/gitroom/nice-clawer/clawer
fi

if [ ! -f ${PY} ]; then
    PY=~/Documents/pyenv/dj14/Scripts/python
fi


APPS="clawer"

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
