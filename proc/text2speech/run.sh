#!/bin/bash

source "$(dirname $0)/SETTINGS"

amqp-consume \
    --url=$URL \
    --queue=$CONSUME_QUEUE \
    --declare \
    ./publish.sh
