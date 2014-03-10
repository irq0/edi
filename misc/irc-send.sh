#!/bin/bash
amqp-publish --url="amqp://localhost" --exchange=msg --routing-key=irc.send.raw --body "$1"
