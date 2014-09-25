#!/usr/bin/env python

import pika
import sys
import time
import json
import re
import uuid
import os
import binascii

DST_KEY = "{}_{}".format("msg_to_tts",
                         binascii.b2a_hex(os.urandom(15)))

# consume msg -> publish tts command
def recv_msg(ch, method, props, body):
    if props.content_type == "application/json":
        msg = json.loads(body)

        ch.basic_publish(exchange="cmd",
                         routing_key="tts",
                         body=json.dumps({
                                 "cmd" : "tts",
                                 "args" : "--voice lea --text Von %s: %s" % (msg["user"], msg["msg"]),
                                 "dst" : DST_KEY,
                                 "user" : msg["user"],
                                 "src" : method.routing_key,}),
                         properties=pika.BasicProperties(
                               content_type="application/json",
                               delivery_mode=2))

        ch.basic_ack(delivery_tag = method.delivery_tag)

# consume tts reply
def recv_tts(ch, method, props, body):
        fd = output_file()
        fd.write(body)

        ch.basic_ack(delivery_tag = method.delivery_tag)

        if fd == sys.stdout:
                sys.exit(0)

def setup(chan):

        result = chan.queue_declare(exclusive=True)
        qn_msg = result.method.queue

        result = chan.queue_declare(exclusive=True)
        qn_tts = result.method.queue


        chan.exchange_declare(exchange="msg",
                              durable=True,
                              type="topic")

        chan.queue_bind(exchange="msg",
                        queue=qn_msg,
                        routing_key="#.recv.*")

        chan.queue_bind(exchange="notify",
                        queue=qn_tts,
                        routing_key=DST_KEY)

        print >>sys.stderr, "---- Using queue (msg):", qn_msg
        print >>sys.stderr, "---- Using queue (tts):", qn_tts
        print >>sys.stderr, "---- Waiting for messages:"

        chan.basic_consume(recv_msg,
                           queue=qn_msg)

        chan.basic_consume(recv_tts,
                           queue=qn_tts)

def output_file():
        return sys.stdout

def output_file_to_dir(directory):
        print >>sys.stderr, "Writing to dir", directory
        def output_file():
                filename = os.path.join(directory, "{}.mp3".format(uuid.uuid4()))
                print filename
                sys.stdout.flush()
                return open(filename, "w+")
        return output_file

def main():
        if len(sys.argv) > 1 and  os.path.isdir(sys.argv[1]):
                global output_file
                output_file = output_file_to_dir(sys.argv[1])

        amqp_server = os.getenv("AMQP_SERVER") or "localhost"
        conn = pika.BlockingConnection(pika.ConnectionParameters(amqp_server))
        chan = conn.channel()

        setup(chan)

        chan.start_consuming()
        conn.close()

if __name__ == '__main__':
        main()
