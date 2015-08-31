#!/bin/bash

WORKDIR=/home/webapps/nice-clawer/clawer
PY=/home/virtualenvs/py27/bin/python


cd ${WORKDIR};${PY} manage_pro.py $*
