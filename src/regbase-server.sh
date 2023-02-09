#!/usr/bin/env sh

OS=$(uname)

echo OS

BASEDIR=$(dirname "$0")
PID_FILE=$BASEDIR/regbase.pid
LOG_FILE=$BASEDIR/regbase.log
ERROR_LOG=$BASEDIR/regbase-error.log
STDERR_LOG=$BASEDIR/regbase-stderr.log
ACCESS_LOG=$BASEDIR/regbase-access.log

PORT=8000
LISTEN_IP='0.0.0.0'

COMMAND="gunicorn --bind $LISTEN_IP:$PORT --access-logfile $ACCESS_LOG --error-logfile $ERROR_LOG --log-file $LOG_FILE --pid $PID_FILE ddhf.wsgi >/dev/null >2&1 "

status() {
    echo
    echo "> Status"
    if [ -f $PID_FILE ]
    then
        echo "  Pid file: $( cat $PID_FILE ) [$PID_FILE]"
        echo
        ps -ef | grep -v grep | grep $( cat $PID_FILE )
    else
        echo "No Pid file found"
        echo
    fi
}

start() {
    if [ -f $PID_FILE ]
    then
        echo
        echo "Already started. PID: [$( cat $PID_FILE )]"
    else
        echo "> Starting ... "
#        if [ -f nohub.out ]
#        then
#          rm nohub.out
#        fi
        touch $PID_FILE
        echo executing $COMMAND
        if nohup $COMMAND > $STDERR_LOG 2>&1 &
        then echo $! >$PID_FILE
             echo "Done."
             echo "$(date '+%Y-%m-%d %X'): START" >>$LOG_FILE
        else echo "Error... "
             /bin/rm $PID_FILE
        fi
    fi
    echo
}

stop() {
    echo -n "> Stopping ... "

    if [ -f $PID_FILE ]
    then
        if kill -9 $( cat $PID_FILE )
        then echo "Done."
             echo "$(date '+%Y-%m-%d %X'): STOP" >>$LOG_FILE
        fi
        /bin/rm $PID_FILE
    else
        echo "No pid file. Sure it is running?"
    fi
    echo
}

case "$1" in
    'start')
            start
            ;;
    'stop')
            stop
            ;;
    'restart')
            stop ;
            sleep 1 ;
            start
            ;;
    'status')
            status
            ;;
    *)
            echo
            echo "Usage: $0 { start | stop | restart | status }"
            echo
            exit 1
            ;;
esac

exit 0
