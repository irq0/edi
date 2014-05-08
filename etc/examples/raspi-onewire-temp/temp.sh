#!/bin/bash
temp="$(awk '/YES/ { ok=1 }  /t=/ { FS="="; $0=$10; if (ok) { print ($2/1000.0) } }' /sys/bus/w1/devices/28-0000054da533/w1_slave)"
now="$(date +'%Y-%m-%d %H:%M:%S')"

echo "$now $temp" >> $(dirname $0)/temp.log
echo $temp

