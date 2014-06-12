#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import edi
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("msg-to-cmd")


# Parse commands from messages (think of irc, jabber,..).
# Two access levels:
# full: All commands allowed
# guest: Only whitelisted commands allowed

CMD_REGEX = r"^!([\w-]+)\s?(.*?)$"

GUEST_CMD_WHITELIST = (
    "ul",
    "pizza-list",
    "pizza",
    "pizza-help",
    "help",
    "describe",
    "apps",
    "commands")

def do_cmd(args, cmd, cmd_args):
    log.info("[CMD] rkey=%r, user=%r uflags=%r: %s %s",
             args["rkey"], args["user"], args["uflags"], cmd, cmd_args)
    edi.emit.cmd(e.chan,
                 cmd=cmd,
                 args=cmd_args,
                 user=args["user"],
                 src=args["rkey"])

def reply_error(args, err):
    log.info("[UNAUTHORIZED] rkey=%r, user=%r uflags=%r",
             args["rkey"], args["user"], args["uflags"])

    edi.emit.msg_reply(e.chan,
                       src=args["rkey"],
                       user=args["user"],
                       msg=err)


with edi.Manager(descr="Parse special strings from messages as EDI commands",
                 name="msg-to-cmd") as e:
    @edi.edi_msg(e, "#.recv.*")
    @edi.edi_filter_matches(CMD_REGEX)
    def parse_cmds(regroups, **args):
        cmd, cmd_args = regroups

        is_full = "op" in args["uflags"]
        is_guest = "voice" in args["uflags"]
        cmd_whitelisted = cmd in GUEST_CMD_WHITELIST

        if is_full or (is_guest and cmd_whitelisted):
            do_cmd(args, cmd, cmd_args)

        elif is_guest and not cmd_whitelisted:
            m = "Guests are only allowed a subset of commands: \n" + \
                ",".join(GUEST_CMD_WHITELIST)
            reply_error(args, m)
        else:
            m = "No OP/voice, No commands :P" \
                "(Hint: https://www.c3pb.de/_media/wiki/documents/mitgliedsantrag.pdf)"
            reply_error(args, m)

    e.register_inspect_command()
    e.run()
