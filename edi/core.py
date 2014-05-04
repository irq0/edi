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
    dispatch_table = {}

    chan.exchange_declare("cmd", "topic", auto_delete=False, durable=True)
    queue, _, _ = chan.queue_declare(durable=True, auto_delete=True)

    log.info("Using queue: %s", queue)

    consumer_tag = chan.basic_consume(queue,
                                      callback=command_dispatcher)

def teardown():
    global conn
    global chan
    global consumer_tag

    chan.basic_cancel(consumer_tag)
    chan.close()
    conn.close()

def command_dispatcher(msg):
    log.info("<--- [%r] %r", msg.routing_key, msg.body)

    if msg.properties["content_type"] == "application/json":
        d = json.loads(msg.body)

        msg.channel.basic_ack(msg.delivery_tag)

        try:
            cmd = d["cmd"]
            assert(cmd == msg.routing_key)

            func = dispatch_table[d["cmd"]]

            log.info("~~~~ Dispatching cmd %r to function: %r", cmd, func)
            ret = func(**d)

            if ret and d.has_key("src"):
                emit.msg_reply(msg.channel, d["src"], ret)

        except Exception:
            log.exception("EXCEPTION in callback")


def register_command(callback, command):
    chan.queue_bind(queue,
                    "cmd",
                    routing_key=command)

    dispatch_table[command] = callback

    log.info("Registered command %r: %r", command, callback)

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
