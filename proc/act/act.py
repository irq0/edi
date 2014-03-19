#!/bin/env python

import os
import subprocess
import pika
import json

from StringIO import StringIO

from config import db


amqp_server = os.getenv("AMQP_SERVER") or "localhost"
conn = pika.BlockingConnection(pika.ConnectionParameters(amqp_server))
chan = conn.channel()

e = "cmd"
q = "act"

chan.queue_declare(queue=q,
                   durable=True,
                   auto_delete=True)

chan.queue_bind(exchange=e,
                queue=q)

def act(dst, rkey, payload):
    print "---> [%r] %r" % (dst, payload)
    chan.basic_publish(exchange=dst,
                       routing_key=rkey,
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


def make_rkey(thing, args):
    t = db[thing]

    parg = t["pargs"][args[0]]

    if t.has_key("rkey"):
        if hasattr(t["rkey"], '__call__'):
            rkey = t["rkey"](parg, args)
        else:
            rkey = t["rkey"]
    else:
        rkey = ""

    print "---- rkey:", rkey
    return rkey

def make_payload(thing, args):
    t = db[thing]

    payload = t["payload"]
    parg = t["pargs"][args[0]]

    if hasattr(payload, '__call__'):
        payload = payload(parg, args)
    else:
        payload = " ".join((payload, parg))

    print "---- Payload:", payload
    return payload


def callback(ch, method, props, body):

    print "<--- [%r] %r" % (method.routing_key, body)

    if props.content_type == "application/json":
        d = json.loads(body)

        args = d["args"].split()

        if len(args) == 1 and args[0] == "list":
            error(d, "Actors: {}".format(", ".join([ "{} ({})".format(k, v["desc"])
                                                     for k,v in db.iteritems() ])))
        elif len(args) < 2:
            error(d, "USAGE: <thing> <arg> [more args..]")

        elif args[0] not in db:
            error(d, "I know nothin' about a %s" % (args[0]))

        else:
            thing = args[0]

            dst = db[thing]["dst"]
            payload = make_payload(thing, args[1:])
            rkey = make_rkey(thing, args[1:])

            success = act(dst, rkey, payload)
            if success:
                print "---> [?] success=%s" % (success)
                chan.basic_ack(delivery_tag = method.delivery_tag)


print "---- Using queue:", q
print "---- Waiting for messages:"

chan.basic_consume(callback,
                   queue=q)

chan.start_consuming()
conn.close()
