#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import amqplib.client_0_8 as amqp

import logging
import uuid
import json
import os
from functools import wraps

import emit

from threading import Thread

log = logging.getLogger("edi.util")


######## Wrapper for callback functions

def wrap_check_cmd(f):
    """Basic sanity checks for cmds"""
    @wraps(f)
    def wrapper(**args):
        if not all(k in args for k in ["cmd", "args", "user", "src"]):
            raise InvalidCMDException
        else:
            f(**args)
    return wrapper

def wrap_check_msg(f):
    """Basic sanity checks for msgs"""
    @wraps(f)
    def wrapper(**args):
        if not all(k in args for k in ["msg", "rkey"]):
            raise InvalidMSGException
        else:
            f(**args)
    return wrapper

def wrap_callback(f):
    """Catch exceptions, log payload"""
    @wraps(f)
    def wrapper(msg):
        log.info("<--- [%r] key=%r body=%r", msg.delivery_info["exchange"], msg.routing_key, msg.body)

        try:
            f(msg)
        except Exception:
            log.exception(u"EXCEPTION in callback")

        ## XXX this may be unwanted, but is generally what you would expect.
        ## Messages deliverd are consumed regardless of success or failure of the processing code
        ## Other possibility would be: ACK successful processing, NACK on exception
        msg.channel.basic_ack(msg.delivery_tag)
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

######## Context Manager

class InvalidCMDException(Exception):
    pass

class InvalidMSGException(Exception):
    pass

class Manager(object):
    """Context manager class. Establishes connection to AMQP Server."""
    consumer_tags = []

    metadata = {
        "app" : "unknown",
        "descr" : "unnamed pyedi app",
        "cmds" : {}
    }

    def __init__(self, name=None, descr=None, amqp_server=(os.getenv("AMQP_SERVER") or "localhost")):
        self.amqp_server = amqp_server
        if name:
            self.set_app_name(name)
        if descr:
            self.set_app_descr(descr)

    def __enter__(self):
        log.info("Connecting to AMQP Server: %r", self.amqp_server)

        self.conn = amqp.Connection(self.amqp_server)
        self.chan = self.conn.channel()

        self.chan.exchange_declare("cmd", "topic", auto_delete=False, durable=True)
        self.chan.exchange_declare("msg", "topic", auto_delete=False, durable=True)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for tag in self.consumer_tags:
            self.chan.basic_cancel(tag)

        self.chan.close()
        self.conn.close()

    def run(self):
        log.info("Waiting for messages")

        while self.chan.callbacks:
            try:
                self.chan.wait()
            except KeyboardInterrupt:
                log.info("Shutting down")
                self.__exit__(None, None, None)
            except:
                log.exception("Exception in edi run loop")

    def set_app_name(self, name):
        self.metadata["app"] = name

    def set_app_descr(self, descr):
        self.metadata["descr"] = descr

    def set_cmd_metadata(self, cmd, args="none", descr=None, attribs={}):
        if not descr:
            descr = self.metadata["descr"]

        self.metadata["cmds"][cmd] = {
            "args" : args,
            "descr" : descr,
            "attribs" : attribs,
        }

        log.debug("Command %r metadata: args=%r descr=%r attribs=%r",
                  cmd, args, descr, attribs)

    def register_inspect_command(self):
        def inspect(src, **args):
            emit.msg_reply(self.chan,
                           src=src,
                           msg=json.dumps(self.metadata))

        self.register_command(inspect, "inspect", descr="pyedi default inspect")

    def register_command(self, callback, cmd, args="none", descr=None, attribs={}):
        self.register_callback(wrap_callback(wrap_unpack_json(wrap_check_cmd(callback))),
                               "cmd",
                               cmd)
        self.set_cmd_metadata(cmd, args, descr, attribs)

    def register_msg_handler(self, callback, key):
        self.register_callback(wrap_callback(wrap_fudge_msg_args(wrap_check_msg(callback))),
                               "msg",
                               key)

    def register_callback(self, callback, ex, key):
        queue, _, _ = self.chan.queue_declare(durable=True, auto_delete=True)

        self.consumer_tags.append(self.chan.basic_consume(queue,
                                                          callback=callback))
        self.chan.queue_bind(queue,
                             ex,
                             routing_key=key)

        log.info(u"Registered callback ex=%r key=%r q=%r: %r", ex, key, queue, callback)
