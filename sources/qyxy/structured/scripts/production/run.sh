WORKDIR=/home/webapps/nice-clawer/sources/qyxy/structured
PYTHON=/home/virtualenvs/dj18/bin/python


function safe_run()
{
    file="/tmp/structure.lock"

    (
        flock -xn -w 10 200 || exit 1
        cd ${WORKDIR}; ${PYTHON} manage_pro.py structured
    ) 200>${file}
}

time safe_run

