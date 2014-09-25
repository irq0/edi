#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ✓

"""
EDI python library
"""

from __future__ import unicode_literals

import logging
import json
import amqplib.client_0_8 as amqp

__author__  = "Marcel Lauhoff"
__email__   = "ml@irq0.org"
__license__ = "GPL"


log = logging.getLogger("edi.emit")

def cmd(chan, **body):
    assert(all(x in body for x in ["cmd", "args"]))

    log.info("---> CMD[%r]: %r", body["cmd"] , body)

    jbody = json.dumps(body)

    msg = amqp.Message(jbody.encode("utf-8"))
    msg.properties["content_type"] = u"application/json"
    msg.properties["delivery_mode"] = 2
    msg.properties["app_id"] = u"edilib"

    chan.basic_publish(exchange="cmd",
                       routing_key=body["cmd"],
                       msg=msg)

def msg(chan, dst, **body):
    assert(all(x in body for x in ["msg"]))

    log.info("---> MSG[%r]: %r", dst, body)

    jbody = json.dumps(body)
    msg = amqp.Message(jbody.encode("utf-8"))
    msg.properties["content_type"] = u"application/json"
    msg.properties["delivery_mode"] = 2
    msg.properties["app_id"] = u"edilib"

    chan.basic_publish(exchange="msg",
                       routing_key=dst,
                       msg=msg)

def msg_reply(chan, src, **body):
    if "recv" in src:
        dst = src.replace("recv", "send")
        msg(chan, dst, **body)


def emit(chan, ex, rkey, payload, content_type="application/octet-stream"):
    log.info("---> ex=%r rkey=%r c/t=%r: %r", ex, rkey, content_type, payload)

    msg = amqp.Message(payload.encode("utf-8"))
    msg.properties["content_type"] = content_type
    msg.properties["delivery_mode"] = 2
    msg.properties["app_id"] = u"edilib"

    chan.basic_publish(exchange=ex,
                       routing_key=rkey,
                       msg=msg)

def audio_notification(chan, payload, content_type, dst="audio"):
    log.info("---> audio notification with type %r: %d KB", content_type, len(payload)/1024)

    msg = amqp.Message(payload)
    msg.properties["content_type"] = content_type
    msg.properties["delivery_mode"] = 2
    msg.properties["app_id"] = u"edilib"

    chan.basic_publish(exchange="notify",
                       routing_key=dst,
                       msg=msg)
