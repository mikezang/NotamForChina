#!/bin/bash

if [ "$1" = "login" ]; then
    /usr/local/bin/mysql.server start
    sleep 3
    mysql -u root 
elif [ "$1" = "start" ]; then
    /usr/local/bin/mysql.server $1
elif [ "$1" = "stop" ]; then
    /usr/local/bin/mysql.server $1
elif [ "$1" = "restart" ]; then
    /usr/local/bin/mysql.server $1
else
    echo "Usage: mysql.sh login|start|stop|restart"
fi
