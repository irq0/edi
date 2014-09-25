#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ✓

"""
Message logger

Log everything on msg exchange to sqlite database
"""

from __future__ import unicode_literals

import sys
import os
import time
import json
import time
import logging

import sqlite3

import edi

__author__  = "Marcel Lauhoff"
__email__   = "ml@irq0.org"
__license__ = "GPL"


logging.basicConfig(level=logging.INFO)
log = logging.getLogger("msglogger")

con = sqlite3.connect(os.getenv("EDI_MSGLOGGER_DB") or "/tmp/msglog.sqlite3")
cur = con.cursor()


cur.executescript("""
    create table if not exists raw_msg (
        id integer primary key autoincrement,
        ts_recvd integer not null,
        rkey text not null,
        content_type text not null,
        body text not null);

    create table if not exists msg (
        id integer primary key autoincrement,
        raw_msg integer not null,
        ts_recvd integer not null,
        proto text,
        direction text,
        user text,
        msg text,
        chan text,
        bot text,
        uflags text,
        type text,
        foreign key(raw_msg) references raw_msg(id))
""")


def get_proto(rkey):
        return rkey.split(".", 1)[0]

def get_direction(rkey):
        r = rkey.split(".")

        if "recv" in r:
                return "recv"
        elif "send" in r:
                return "send"
        else:
                return "error"

def something_to_dbstring(x):
        if isinstance(x, basestring):
                return x
        elif isinstance(x, (list, tuple)):
                return "\x1E".join((str(y) for y in x))
        elif isinstance(x, dict):
                return "\x1D".join("{}\x1E{}".format(str(k),str(v)) for k,v in x.iteritems())
        else:
                return repr(x)

def extract_msg(msg):
        x = {}
        x["proto"] = get_proto(msg.routing_key)
        x["direction"] = get_direction(msg.routing_key)

        if msg.properties["content_type"] == "application/json":
                j = json.loads(msg.body)

                for k in ("user", "msg", "chan", "bot", "uflags", "type"):
                        if j.has_key(k):
                                x[k] = something_to_dbstring(j[k])
        elif msg.properties["content_type"] == "text/plain":
                x["msg"] = msg.body

        return x

def msg_sql(x):
        return " ".join(
                ["insert into msg",
                 "(", ",".join(x.iterkeys()), ")",
                 "values",
                 "(", ",".join((":{}".format(k) for k in x.iterkeys())), ")",])

def handle_msg(msg):
        now = int(time.time())
        cur = con.cursor()

        try:
                sql = "insert into raw_msg (ts_recvd, rkey, content_type, body) values (?, ?, ?, ?)"
                log.debug("[SQL] raw_msg: %r", sql)
                cur.execute(sql, (now, msg.routing_key, msg.properties["content_type"], msg.body))
                con.commit()

                try:
                        m = extract_msg(msg)
                        m["raw_msg"] = cur.lastrowid
                        m["ts_recvd"] = now
                        log.debug("EXTRACTED: %r", m)

                        sql = msg_sql(m)
                        log.debug("[SQL] msg: %r", sql)

                        cur.execute(sql, m)
                        con.commit()
                except Exception:
                        log.exception("")

        except Exception:
                log.exception("")

        msg.channel.basic_ack(msg.delivery_tag)
with edi.Manager() as e:
        e.register_callback(handle_msg, "msg", "#")
        e.run()
