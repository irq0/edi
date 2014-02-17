#!/bin/bash

amqp-consume -u 'amqp://localhost' -e subinit -r 'rc.#' $(dirname $0)/run-rc.sh
