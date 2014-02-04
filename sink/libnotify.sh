#!/bin/bash
amqp-consume --url="amqp://localhost" --exchange="notify" --routing-key="text" $(dirname $0)/libnotify_send.sh
