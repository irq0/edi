#!/bin/sh

# EDI MPD Sink
# Author: Marcel Lauhoff <ml@irq0.org>

INSTANCE="subraum"
exec amqp-consume --url="amqp://${AMQP_SERVER:-localhost}" --exchange="act_mpd" --routing-key="$INSTANCE" $(dirname $0)/mpc_wrapper.sh -
