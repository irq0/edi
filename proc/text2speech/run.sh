#!/bin/bash

source "$(dirname $0)/SETTINGS"

amqp-consume \
    --url=$URL \
    --exchange="$CONSUME_EXCHANGE" \
    --routing-key="tts" \
    --queue="tts" \
    ./publish.sh
