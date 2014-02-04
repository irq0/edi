#!/bin/env python

import subprocess
import pika
import json

from StringIO import StringIO

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
chan = conn.channel()

e = "cmd"
q = "tts"

chan.queue_declare(queue=q,
                   durable=True,
                   auto_delete=True)

chan.queue_bind(exchange=e,
                queue=q)

def call_tts(text):
    p = subprocess.Popen(["./publish.sh"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.communicate(text)
    ret = p.wait()

    return ret == 0

def callback(ch, method, props, body):
    print "<--- [%r] %r" % (method.routing_key, body)

    if props.content_type == "application/json":

        d = json.loads(body)
        msg = "Message from %s: %s" % (d["user"], " ".join(d["args"]))

        success = call_tts(msg)
        if success:
            print "---> [?] return=%s" % (success)
            chan.basic_ack(delivery_tag = method.delivery_tag)

print "---- Using queue:", q
print "---- Waiting for messages:"

chan.basic_consume(callback,
                   queue=q)

chan.start_consuming()
conn.close()
