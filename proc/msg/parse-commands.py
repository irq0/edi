#!/usr/bin/env python

#
# Parse commands from messages (think of irc, jabber,..).
# The idea is to loosly parse things that look like commands and add them to
# the cmd exchange with a routing key resembling that command
#


# TODO verify users somehow
# TODO add user authorizations?

import pika
import sys
import time
import json
import re

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
chan = conn.channel()

result = chan.queue_declare(exclusive=True)
queue_name = result.method.queue

chan.exchange_declare(exchange="msg",
                      durable=True,
                      type="topic")

chan.queue_bind(exchange="msg",
                queue=queue_name,
                routing_key="#.recv.*")

print "---- Using queue:", queue_name
print "---- Waiting for messages:"

def publish(key, data):
        print "---> [%r] %r" % (key, data)
        chan.basic_publish(exchange="cmd",
                           routing_key=key,
                           body=data,
                           properties=pika.BasicProperties(
                               content_type="application/json",
                               delivery_mode=2))

def recv(ch, method, props, body):
    print "<--- [%r] %r" % (method.routing_key, body)

    if props.content_type == "application/json":
        msg = json.loads(body)

        m = re.search(r"^!(\w+)\s?(.*?)$", msg["msg"])

        if m and "op" in msg["uflags"]:
            assert len(m.groups()) == 2

            cmd, args = m.groups()
            publish(cmd,
                    json.dumps({
                        "cmd" : cmd,
                        "args" : args,
                        "user" : msg["user"],
                        "src" : method.routing_key,}))

        ch.basic_ack(delivery_tag = method.delivery_tag)


chan.basic_consume(recv,
                   queue=queue_name)

chan.start_consuming()
conn.close()
