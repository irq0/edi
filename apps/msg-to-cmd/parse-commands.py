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

CMD_REGEX = r"^!([\w-]+)\s?(.*?)$"

with edi.Manager() as e:
        @edi.edi_msg(e, "#.recv.*")
        @edi.edi_filter_msg_with_uflag_any(["op", "voice"])
        @edi.edi_filter_matches(CMD_REGEX)
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
        @edi.edi_filter_msg_with_uflag_none(["op", "voice"])
        @edi.edi_filter_matches(CMD_REGEX)
        def reply_unauthorized(regroups, **msg):
            m="No OP/voice, No commands :P (Hint: https://www.c3pb.de/_media/wiki/documents/mitgliedsantrag.pdf)"
            if msg.has_key("user"):
                edi.emit.msg_reply(e.chan,
                        src=msg["rkey"],
                        user=msg["user"],
                        msg=m)

        e.register_inspect_command()
        e.run()
