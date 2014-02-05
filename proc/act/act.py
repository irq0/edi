#!/bin/env python

import subprocess
import pika
import json

from StringIO import StringIO

conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
chan = conn.channel()

e = "cmd"
q = "act"

db = {
    "venti" : {
        "dst" : "act_433mhz",
        "payload" : "11111 1",
        "args" : {
            "on" : "1",
            "off" : "0"
        },
    },
    "bulb" : {
        "dst" : "act_433mhz",
        "payload" : "11111 2",
        "args" : {
            "on" : "1",
            "off" : "0"
        },
    },
}

chan.queue_declare(queue=q,
                   durable=True,
                   auto_delete=True)

chan.queue_bind(exchange=e,
                queue=q)

def act(dst, payload):
    print "---> [%r] %r" % (dst, payload)
    chan.basic_publish(exchange=dst,
                       routing_key="",
                       body=payload,
                       properties=pika.BasicProperties(
                           content_type="application/octet-stream",
                           delivery_mode=2))

def error(cmd, error):
    key = cmd["src"].replace("recv", "send")
    msg = "%s: %s" % (cmd["user"], error)

    print "---> [%r] %r" % (key, msg)

    chan.basic_publish(exchange="msg",
                       routing_key=key,
                       body=msg,
                       properties=pika.BasicProperties(
                           content_type="text/plain",
                           delivery_mode=2))

def callback(ch, method, props, body):

    print "<--- [%r] %r" % (method.routing_key, body)

    if props.content_type == "application/json":
        d = json.loads(body)

        args = d["args"].split()

        if len(args) < 2:
            error(d, "USAGE: <thing> <on|off>")
        elif args[0] not in db:
            error(d, "I know nothin' about a %s" % (args[0]))
        elif args[1] not in ("on", "off"):
            error(d, "'on' or 'off' what else could there be?")
        else:
            thing = args[0]
            dst = db[thing]["dst"]
            payload = db[thing]["payload"]
            state = db[thing]["args"][args[1]]

            success = act(dst, " ".join((payload, state)))
            if success:
                print "---> [?] success=%s" % (success)
                chan.basic_ack(delivery_tag = method.delivery_tag)


print "---- Using queue:", q
print "---- Waiting for messages:"

chan.basic_consume(callback,
                   queue=q)

chan.start_consuming()
conn.close()
