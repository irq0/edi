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
                      type="topic")

chan.queue_bind(exchange="msg",
                queue=queue_name,
                routing_key="#.recv.raw")

print "Using queue:", queue_name
print "Waiting for messages.."


def callback(ch, method, props, body):
    print " [x] recvd %r %r" % (method.routing_key, body)

    if props.content_type == "application/json":
        msg = json.loads(body)

        if re.match(r"^!tts", msg["msg"]):
            chan.basic_publish(exchange="tts_worker",
                               routing_key="tts",
                               body=msg["msg"][len("!tts "):])

    ch.basic_ack(delivery_tag = method.delivery_tag)

chan.basic_consume(callback,
                   queue=queue_name)

chan.start_consuming()
conn.close()
