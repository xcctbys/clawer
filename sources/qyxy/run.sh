#!/bin/bash

WORKDIR="/home/webapps/nice-clawer/sources/qyxy"
PYTHON="/home/virtualenvs/dj18/bin/python"


function safe_run()
{
    file="/tmp/enterprise.lock"

    (
        flock -xn -w 10 200 || exit 1
        cd ${WORKDIR}; ${PYTHON} run.py $1
    ) 200>${file}
}

ENT_CRAWLER_SETTINGS=settings_pro time safe_run $*

