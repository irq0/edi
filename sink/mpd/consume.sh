#!/bin/bash -x

INSTANCE="subraum"
exec amqp-consume --url="amqp://${AMQP_SERVER:-localhost}" --exchange="act_mpd" --routing-key="$INSTANCE" $(dirname $0)/mpc_wrapper.sh -
