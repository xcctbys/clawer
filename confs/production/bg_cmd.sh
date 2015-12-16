#!/bin/bash

WORKDIR="/home/webapps/nice-clawer/clawer"
PYTHON="/home/virtualenvs/py27/bin/python"


function safe_run()
{
    file="/tmp/$1.lock"

    (
        flock -xn -w 10 200 || exit 1
        cd ${WORKDIR};${PYTHON} -W "ignore:Unverified HTTPS request" manage_pro.py $*
    ) 200>${file}
}

time safe_run $*

