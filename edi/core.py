#!/usr/bin/env python

import amqplib.client_0_8 as amqp

import logging
import uuid
import json
import os
from functools import wraps

import emit

from threading import Thread

log = logging.getLogger("edi.util")

conn = None
chan = None
queue = None
dispatch_table = None
consumer_tag = None

def init(amqp_server=(os.getenv("AMQP_SERVER") or "localhost")):
    """initialize library. mandatory call."""
    global conn
    global chan
    global queue
    global dispatch_table
    global consumer_tag

    conn = amqp.Connection(amqp_server)
    chan = conn.channel()
    dispatch_table = {
        "msg" : {},
        "cmd" : {},
    }

    chan.exchange_declare("cmd", "topic", auto_delete=False, durable=True)
    chan.exchange_declare("msg", "topic", auto_delete=False, durable=True)


def teardown():
    global conn
    global chan
    global consumer_tag

    chan.basic_cancel(consumer_tag)
    chan.close()
    conn.close()

def run():
    global chan
    log.info("Waiting for messages")

    while chan.callbacks:
        chan.wait()

def run_background():
    thread = Thread(target=run)
    thread.daemon = True
    thread.start()

    log.info("Spawning background run thread: %r", thread)
    return thread





def wrap_callback(f):
    @wraps(f)
    def wrapper(msg):
        log.info("<--- [%r] key=%r body=%r", msg.delivery_info["exchange"], msg.routing_key, msg.body)

        try:
            f(msg)
        except Exception:
            log.exception(u"EXCEPTION in callback")
    return wrapper

def wrap_unpack_json(f):
    @wraps(f)
    def wrapper(msg):
            f(**json.loads(msg.body))

    return wrapper

def wrap_fudge_msg_args(f):
    @wraps(f)
    def wrapper(msg):
        if msg.properties["content_type"] == "application/json":
            d = json.loads(msg.body)
            d["rkey"] = msg.routing_key
        elif msg.properties["content_type"] == "text/plain":
            d = {"msg" : msg.body,
                 "rkey" : msg.routing_key,}

        f(**d)
    return wrapper

def register_command(callback, cmd):
    register_callback(wrap_callback(wrap_unpack_json(callback)),
                      "cmd",
                      cmd)

def register_msg_handler(callback, key):
    register_callback(wrap_callback(wrap_fudge_msg_args(callback)),
                      "msg",
                      key)

def register_callback(callback, ex, key):
    queue, _, _ = chan.queue_declare(durable=True, auto_delete=True)

    consumer_tag = chan.basic_consume(queue,
                                      callback=callback)
    chan.queue_bind(queue,
                    ex,
                    routing_key=key)

    log.info("Registered callback ex=%r key=%r q=%r: %r", ex, key, queue, callback)
