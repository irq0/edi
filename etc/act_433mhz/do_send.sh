#!/bin/bash

payload="$(cat -)"

echo "Sending \"${payload}\": "

for i in `seq 2`; do
    $(dirname $0)/send $payload
    sleep 1
done

sleep 2

ech
