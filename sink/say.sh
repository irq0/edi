#!/bin/bash

#amqp-consume --url="amqp://mopp" --exchange="notify" --queue="audio-$HOSTNAME" --routing-key="audio" mplayer -

amqp-consume --url="amqp://mopp" --exchange="notify" --queue="audio-$HOSTNAME" --routing-key="audio" $(dirname $0)/say_mplayer.sh -
