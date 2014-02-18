#!/bin/env python

from __future__ import print_function

import subprocess
import pika
import json

import tts

from StringIO import StringIO

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
chan = conn.channel()

e = "cmd"

chan.queue_declare(queue="say",
                   durable=True,
                   auto_delete=True)
chan.queue_declare(queue="tts",
                   durable=True,
                   auto_delete=True)
chan.queue_declare(queue="fortune",
                   durable=True,
                   auto_delete=True)

chan.queue_bind(exchange=e,
                queue="say")
chan.queue_bind(exchange=e,
                queue="tts")
chan.queue_bind(exchange=e,
                queue="fortune")

def error(cmd, error):
    key = cmd["src"].replace("recv", "send")
    msg = json.dumps({
        "user" : cmd["user"],
        "msg" : error
    })

    print("---> [%r] %r" % (key, msg))

    chan.basic_publish(exchange="msg",
                       routing_key=key,
                       body=msg,
                       properties=pika.BasicProperties(
                           content_type="application/json",
                           delivery_mode=2))

def notify_audio(payload, content_type):
    print("---> %d bytes of %s" % (len(payload), content_type))
    chan.basic_publish(exchange="notify",
                       routing_key="audio",
                       body=payload,
                       properties=pika.BasicProperties(
                           content_type=content_type,
                           delivery_mode=2))

def say_callback(ch, method, props, body):
    print("<---SAY [%r] %r" % (method.routing_key, body))

    if props.content_type == "application/json":
        d = json.loads(body)
        msg = d["args"]

        # TODO: detect language
        try:
            filename = tts.tts("julia", msg, meta="user=%s" % d["user"])
            print(filename)

            if filename:
                with open(filename, "r") as fd:
                    notify_audio(fd.read(), "audio/mpeg")

                chan.basic_ack(delivery_tag = method.delivery_tag)
        except Exception,e:
            print(e)

def fortune():
    p = subprocess.Popen(["fortune", "-s", "-o"], stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout.encode("UTF-8")

def fortune_callback(ch, method, props, body):
    print("<---SAY [%r] %r" % (method.routing_key, body))

    if props.content_type == "application/json":
        d = json.loads(body)
        try:
            filename = tts.tts("queenelizabeth", fortune(), meta="user=%s;source=fortune" % d["user"])
            print(filename)

            if filename:
                with open(filename, "r") as fd:
                    notify_audio(fd.read(), "audio/mpeg")

                chan.basic_ack(delivery_tag = method.delivery_tag)
        except Exception,e:
            print(e)


def tts_callback(ch, method, props, body):
    print("<---TTS [%r] %r" % (method.routing_key, body))

    if props.content_type == "application/json":
        d = json.loads(body)

        try:
            result, data = tts.with_args(args=d["args"].split(), meta="user={}".format(d["user"]))

            if result == "filename":
                with open(data, "r") as fd:
                    notify_audio(fd.read(), "audio/mpeg")
            else:
                error(d, data)

            chan.basic_ack(delivery_tag = method.delivery_tag)

        except tts.ArgumentParserError, e:
            print(e)
            error(d, e)
        except Exception, e:
            print(e)

print("---- Waiting for messages:")

chan.basic_consume(say_callback,
                   queue="say")

chan.basic_consume(tts_callback,
                   queue="tts")

chan.basic_consume(fortune_callback,
                   queue="fortune")

chan.start_consuming()
conn.close()
