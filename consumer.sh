#!/bin/bash

amqp-consume -u 'amqp://localhost' -e subinit -q "subinit-rc-$(hostname)" -r 'rc.#' $(dirname $0)/run-rc.sh
