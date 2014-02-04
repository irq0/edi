#!/bin/env python

import subprocess
import pika

from StringIO import StringIO

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
chan = conn.channel()

e = "tts_worker"
q = "tts"

chan.exchange_declare(exchange=e,
                      durable=True,
                      auto_delete=False,
                      type="direct")

chan.queue_declare(queue=q,
                   durable=True,
                   auto_delete=True)


chan.queue_bind(exchange=e,
                queue=q)

def callback(ch, method, props, body):
    p = subprocess.Popen(["./publish.sh"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.communicate(body)
    ret = p.wait()

    print ret
    if ret == 0:
        chan.basic_ack(delivery_tag = method.delivery_tag)

chan.basic_consume(callback,
                   queue=q)

chan.start_consuming()
conn.close()
