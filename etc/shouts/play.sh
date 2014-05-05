#!/bin/bash

(
	cd $(dirname $0)
	amqp-publish -u 'amqp://mopp' --exchange=notify --routing-key=audio --content-type=audio/mpeg < "$1"
)
