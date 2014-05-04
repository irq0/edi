#!/usr/bin/env python

import amqplib.client_0_8 as amqp

import logging
import uuid
import json
import os

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

    queue, _, _ = chan.queue_declare(durable=True, auto_delete=True)

    log.info("Using queue: %s", queue)

    consumer_tag = chan.basic_consume(queue,
                                      callback=dispatcher)

def teardown():
    global conn
    global chan
    global consumer_tag

    chan.basic_cancel(consumer_tag)
    chan.close()
    conn.close()

def dispatch_cmd(msg):
    d = json.loads(msg.body)
    cmd = d["cmd"]
    assert(cmd == msg.routing_key)

    func = dispatch_table["cmd"][d["cmd"]]

    log.info("~~~~ Dispatching cmd %r to function: %r", cmd, func)
    ret = func(**d)

    if ret and d.has_key("src"):
        emit.msg_reply(msg.channel, d["src"], ret)

def msg_args(msg):
    if msg.properties["content_type"] == "application/json":
        d = json.loads(msg.body)
        d["rkey"] = msg.routing_key
    elif msg.properties["content_type"] == "text/plain":
        return {"msg" : msg.body,
                "rkey" : msg.routing_key,}

def dispatch_msg(msg):
    fns = dispatch_table["msg"][msg.routing_key]
    for f in fns:
        log.info("~~~~ Dispatching msg rkey=%r to function: %r", msg.routing_key, func)
        ret = func(**msg_args(msg))

def dispatcher(msg):
    log.info("<--- [%r] key=%r body=%r", msg.delivery_info["exchange"], msg.routing_key, msg.body)

    dispatch = msg.delivery_info["exchange"]
    try:
        if msg.properties["content_type"] == "application/json" and dispatch == u"cmd":
            return dispatch_cmd(msg)
        elif msg.properties["content_type"] in ["application/json", "text/plain"] and dispatch == u"msg":
            return dispatch_msg(msg)
        else:
            log.warning(u"Got message from unknown exchange andor content type")

    except Exception:
        log.exception(u"EXCEPTION in callback")

def register_command(callback, command):
    global queue
    chan.queue_bind(queue,
                    "cmd",
                    routing_key=command)

    dispatch_table["cmd"][command] = callback

    log.info("Registered command %r: %r", command, callback)

def register_msg_handler(callback, key):
    global queue
    chan.queue_bind(queue,
                    "msg",
                    routing_key=key)

    try:
        dispatch_table["msg"][key].append(callback)
    except KeyError:
        dispatch_table["msg"][key] = [callback, ]

    log.info("Registered msg handler %r: %r", key, callback)


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
