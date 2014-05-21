#!/bin/bash

PID="/tmp/uwsgi.pid"

Start()
{
    if  test -f "$PID" ; then
        echo 'there is pid file already'
    else
        uwsgi uwsgi.ini
        echo 'started'
    fi
    return
}
Stop()
{
    if test -f "$PID"; then
        kill -9 `cat $PID`
        rm $PID
        echo 'stoped'
    else
        echo "no pid found $PID"
    fi
}

case $1 in
    start)
        Start
        ;;
    stop)
        Stop
        ;;
    restart)
        Stop
        Start
        ;;
esac
