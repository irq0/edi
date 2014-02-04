#!/bin/bash
amqp-consume --url="amqp://localhost" --exchange="notify" --routing-key="audio" mplayer -
#amqp-consume --url="amqp://localhost" --exchange="notify" --routing-key="audio" oggdec -
