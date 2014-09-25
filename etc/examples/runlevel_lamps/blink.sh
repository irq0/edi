#!/bin/sh

readonly lamp=$1

cleanup () {
    gpio -g write $lamp 0
}

trap cleanup EXIT

while true; do
    gpio -g write $lamp 1
    sleep 0.6
    gpio -g write $lamp 0
    sleep 0.4
done
