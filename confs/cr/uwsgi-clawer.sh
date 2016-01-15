#!/bin/bash
#
# Init file for uwsgi clawer server daemon
#
# chkconfig: 2345 55 25
# description: clawer server daemon
#
# processname: uwsgi-clawer
#

NAME=uwsgi-clawer
HOME=/home/webapps/nice-clawer/clawer
PID=/tmp/uwsgi-clawer.pid
CMD=/home/virtualenvs/py27/bin/uwsgi
CONFIG=${HOME}/cr.ini

wait_for_pid () {
    try=0
    while test $try -lt 2 ; do
        case "$1" in
            'created')
            if [ -f "$2" ] ; then
                try=''
                break
            fi
            ;;

            'removed')
            if [ ! -f "$2" ] ; then
                try=''
                break
            fi
            ;;
        esac

        echo -n .
        try=`expr $try + 1`
        sleep 1

    done

}

case "$1" in
    start)
        echo -n "Starting ${NAME} " 

        ulimit -n 10240
        cd ${HOME}; find . -name "*.pyc" -exec rm -rf {} \;
        cd ${HOME}; ${CMD} --ini ${CONFIG}
        if [ "$?" != 0 ] ; then
            echo " failed" 
            exit 1
        fi

        wait_for_pid created $PID

        if [ -n "$try" ] ; then
            echo " failed" 
            exit 1
        else
            echo " done" 
        fi
    ;;
    stop)
        echo -n "Gracefully shutting down ${NAME} " 

        if [ ! -r $PID ] ; then
            echo "warning, no pid file found - ${NAME} is not running ?" 
            exit 1
        fi

        ${CMD} --ini ${CONFIG} --stop $PID
        wait_for_pid removed $PID
        if [ -n "$try" ] ; then
            echo " failed. Use force-exit" 
            killall -9 ${NAME}
            exit 1
        else
            echo " done" 
        fi
    ;;
    restart)
        $0 stop
        sleep 1
        $0 start
    ;;
    reload)
        ${CMD} --ini ${CONFIG} --reload ${PID}
    ;;
    *)
        echo "Usage: $0 {start|stop|restart}" 
        exit 1
    ;;

esac
