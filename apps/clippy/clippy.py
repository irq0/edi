#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ✓

"""
Clippy

Basic help and inspection commands. Uses the inspect command to gather data.
"""

from __future__ import unicode_literals

import os
import binascii
import sys
import time
import json
import logging

import edi

__author__  = "Marcel Lauhoff"
__email__   = "ml@irq0.org"
__license__ = "GPL"

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("clippy")

MSG_SRC = "clippy.recv.{}".format(binascii.b2a_hex(os.urandom(15)))
MSG_DST = MSG_SRC.replace("recv", "send")
MSG_USER = "clippy"

cmds = {}
apps = {}

def update(x):
        """update local datastructures"""
        log.info("Updating app inspect cache: %r", x["app"])

        apps[x["app"]] = x

        for cmd, vals in x["cmds"].iteritems():
                vals["app"] = x["app"]
                cmds[cmd] = vals

def trunc(s, wd):
        if len(s) > wd:
                s = s[:wd-3] + '...'
        return s

def command_list():
        try:
                global cmds
                return ["{:<20s}\t{:<60s}".format(trunc(cmd,20),
                                                  trunc(props["descr"], 60))
                        for cmd, props in cmds.iteritems()
                        if cmd not in ["inspect"] ]
        except:
                log.exception("Should not happen")

def app_list():
        try:
                global apps
                return ["{:<20s}\t{:<60s}".format(trunc(app["app"],20),
                                                  trunc(app["descr"], 60))
                        for app in apps.itervalues()]
        except:
                log.exception("Should not happen")

def describe_cmd(cmd):
        try:
                global cmds
                return ['Command "{}"'.format(cmd),
                        cmds[cmd]["descr"],
                        'Part of app "{}"'.format(cmds[cmd]["app"]),
                        "Arguments: {}".format(cmds[cmd]["args"])]
        except:
                log.exception("Should not happen")
                return ["Unknown command"]

with edi.Manager(name="Clippy", descr="It looks like you're using EDI. Would you like help?") as e:
        cmd = edi.Cmd(e.chan, src=MSG_SRC, user=MSG_USER)
        data = {}

        @edi.edi_cmd(e, "commands",
                     descr="List available commands")
        def cmd_commands(**args):
                cmd.inspect()
                time.sleep(1)

                edi.emit.msg_reply(e.chan,
                                   src=args["src"],
                                   user=args["user"],
                                   msg="\n".join(command_list()))

        @edi.edi_cmd(e, "apps",
                     descr="List running apps")
        def cmd_apps(**args):
                cmd.inspect()
                time.sleep(1)

                edi.emit.msg_reply(e.chan,
                                   src=args["src"],
                                   user=args["user"],
                                   msg="\n".join(app_list()))
        @edi.edi_cmd(e, "describe",
                     descr="Describe command")
        def cmd_describe(**args):
                cmd.inspect()
                time.sleep(1)

                edi.emit.msg_reply(e.chan,
                                   src=args["src"],
                                   user=args["user"],
                                   msg="\n".join(describe_cmd(args["args"])))

        @edi.edi_cmd(e, "help",
                     descr="Help")
        def cmd_describe(**args):
                cmd.inspect()
                time.sleep(1)

                edi.emit.msg_reply(e.chan,
                                   src=args["src"],
                                   user=args["user"],
                                   msg="It looks like you're using EDI. Would you like help? Try commands 'commands' 'apps' and 'describe <CMD>'")


        @edi.edi_msg(e, MSG_DST)
        def recv_replies(**msg):
                try:
                        j = json.loads(msg["msg"])
                        update(j)

                except:
                        log.exception("Recv reply error")

        e.register_inspect_command()
        e.run()

        cmd.inspect()
