#!/bin/sh

exec amqp-consume -s "${AMQP_SERVER:-localhost}" -e subinit -q "subinit-rc-$(hostname)" -r 'rc.#' $(dirname $0)/set-runlevel-lamps.sh
