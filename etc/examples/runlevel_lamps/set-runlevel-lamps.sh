#!/bin/bash

IFS="." read -r rc level action

echo -e "level:\t${level}"
echo -e "action:\t${action}"

case "$level $action" in
    "1 start")
	nohup ./blink.sh 22 &
	;;
    "1 stop")
	pkill -f "blink.sh 22"
	./lamp.sh 22 0
	;;

    "4 start")
	pkill -f "blink.sh 22"
	./lamp.sh 22 1
	;;
    "4 stop")
	nohup ./blink.sh 22 &
	;;
esac
