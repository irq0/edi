#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

#
# Parse commands from messages (think of irc, jabber,..).
#

import edi
import sys
import time

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("parse-commands")

with edi.Manager() as e:
        @edi.edi_msg(e, "#.recv.*")
        @edi.edi_filter_msg_with_uflag("op")
        @edi.edi_filter_msg_matches(r"^!(\w+)\s?(.*?)$")
        def parse_cmds(regroups, **msg):
                cmd, args = regroups

                try:
                        user = msg["user"]
                except KeyError:
                        user = "NA"

                edi.emit.cmd(e.chan,
                             cmd=cmd,
                             args=args,
                             user=user,
                             src=msg["rkey"])

        @edi.edi_msg(e, "#.recv.*")
        @edi.edi_filter_msg_without_uflag("op")
        @edi.edi_filter_msg_matches(r"^!(\w+)\s?(.*?)$")
        def reply_unauthorized(regroups, **msg):
                if msg.has_key("user"):
                        edi.emit.msg_reply(e.chan,
                                           src=msg["rkey"],
                                           user=msg["user"],
                                           msg="No OP. No commands :P")
        e.run()
