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

def queue_name():
    """return unique name for amqp queue"""
    return "pyedi__{}".format(uuid.uuid4())

def init(amqp_server=(os.getenv("AMQP_SERVER") or "localhost")):
    """initialize library. mandatory call."""
    global conn
    global chan
    global queue
    global dispatch_table

    conn = pika.BlockingConnection(pika.ConnectionParameters(amqp_server))
    chan = conn.channel()
    dispatch_table = {}
    queue = queue_name()

    log.info("Using queue: %s", queue)

    chan.queue_declare(queue=queue,
                       durable=True,
                       auto_delete=True)

    chan.basic_consume(command_dispatcher,
                       queue=queue)

def teardown():
    global conn
    chan.stop_consuming()
    conn.close()

def command_dispatcher(chan, method, props, body):
    log.into("<--- [%r] %r", method.routing_key, body)

    if props.content_type == "application/json":
        d = json.loads(body)

        try:
            cmd = d["cmd"]
            args = d["args"].split(None, 1)

            func = cmds[d["cmd"]]

            log.info("~~~~ Dispatching cmd %r to function: %r", cmd, func)
            ret = func(d)

            if ret and d.has_key("src"):
                emit.msg_reply(chan, d["src"], ret)

        except Exception, e:
            print "~~~~ EXCEPTION in callback: ", e
            traceback.print_exc()

        pass

def register_command(callback, command):
    chan.queue_bind(exchange="cmd",
                    queue=queue,
                    routing_key=command)

    dispatch_table[command] = callback

    log.info("Registered command %r: %r", command, callback)

def run():
    global chan
    log.info("Waiting for messages")
    chan.start_consuming()


def run_background():
    thread = Thread(target=run)
    thread.start()

    log.info("Spawning background run thread: %r", thread)
    return thread
