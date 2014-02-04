#!/bin/bash

amqp-consume --url="amqp://localhost" --exchange="act_433mhz" --routing-key="act_433mhz" cat -
