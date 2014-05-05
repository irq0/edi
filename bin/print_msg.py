#!/usr/bin/env python

import pika
import sys
import time
import json
import re
import os

amqp_server = os.getenv("AMQP_SERVER") or "localhost"
conn = pika.BlockingConnection(pika.ConnectionParameters(amqp_server))
chan = conn.channel()

result = chan.queue_declare(exclusive=True)
queue_name = result.method.queue

chan.queue_bind(exchange="msg",
                queue=queue_name,
                routing_key="#.recv.*")

def recv_msg(ch, method, props, body):
    if props.content_type == "application/json":
        msg = json.loads(body)

        print "From %s: %s" % (msg["user"],
                               msg["msg"])
	sys.stdout.flush()

        ch.basic_ack(delivery_tag = method.delivery_tag)

chan.basic_consume(recv_msg,
                   queue=queue_name)

chan.start_consuming()
conn.close()
