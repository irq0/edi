#!/bin/bash
amqp-consume --url="amqp://localhost" --queue=say --declare  mplayer -
