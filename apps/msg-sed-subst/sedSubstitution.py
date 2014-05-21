#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "space"

"""
find.py - Willie Spelling correction module
Copyright 2011, Michael Yanovich, yanovich.net
Copyright 2013, Edward Powell, embolalia.net
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net

Contributions from: Matt Meinwald and Morgan Goose
This module will fix spelling errors if someone corrects them
using the sed notation (s///) commonly found in vi/vim.

Adapted for the EDI Hackerspace Automation System
by Patrick Meyer
"""

import edi
import sys, os
import time
import json
import operator
import re

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


memory = dict()
SUBSTITUTION_RE = r"""^(?:(\S+)[:,]\s*)?s/((?:\\/|[^/])+)/((?:\\/|[^/])+)(?:/(\S*))?"""


def publish(inc_msg, message):
    edi.emit.msg_reply(e.chan,
           src=inc_msg["rkey"],
           user=inc_msg["user"],
           msg=message)

def substitutionFailed(inc_msg):
    to_send = u"Sorry, %s. I don't know what you are talking about." % (msg["user"])
    publish(inc_msg, to_send)


with edi.Manager(name="Sed", descr="Sed lets you correct yourself, as well as everybody else.") as e:

    @edi.edi_msg(e, "#.recv.*")
    @edi.edi_filter_matches("(?!" + SUBSTITUTION_RE + ")")
    def collect_message(r, **msg):
        user = msg["user"]
        if user in memory:
            memory[user] += [msg["msg"]]
        else:
            memory[user]  = [msg["msg"]]

        # keep only 50 lines
        del memory[user][:-50]

  
    @edi.edi_msg(e, "#.recv.*")
    @edi.edi_filter_matches(SUBSTITUTION_RE)
    def substitute(regroups, **msg):
        rnick   = regroups[0] or msg["user"]    # Correcting other person vs self.
        find    = regroups[1]                   # What shall be replaced
        replace = regroups[2]                   # With what it shall be replaces
        flags   = regroups[3] or ''             # sed flags

        find = find.replace(r'\/', '/')         # Find Escaped slashes
        replace = replace.replace(r'\/', '/')

        if rnick == "EDI":
            publish(msg, "Follow the white Rabbit..MQ")
            return

        # only do something if there is conversation to work with
        if rnick not in memory:
            substitutionFailed(msg)
            return

        # Nick related lines
        nick_memory = reversed(memory[rnick])

        # If 'g' flag is given, replace all. Otherwise, replace once.
        if 'g' in flags:
            max_replace_count = 0
        else:
            max_replace_count = 1

        # re.U turns on unicode replacement.
        re_flags = re.U
        # 'i' flag turns off case sensitivity. 
        if 'i' in flags:
            re_flags = re_flags | re.I

        # repl is a lambda function which performs the substitution. 
        regex = re.compile(find, re_flags)
        repl = lambda s: re.sub(regex, replace, s, max_replace_count)

        # Look back through the user's lines in the channel until you find a line
        # where the replacement works
        for line in nick_memory:
            new_phrase = repl(line)
            if new_phrase != line:  # we are done
                break

        if not new_phrase or new_phrase == line:
            substitutionFailed(msg)
            return  # Didn't find anything

        # output
        if msg["type"] != "action": # no "/me ..." command
            new_phrase = '\x02meant\x02 to say: ' + new_phrase
        elif regroups[0]:  # correcting another user
            new_phrase = '%s thinks %s %s' % (msg["user"], rnick, new_phrase)
        else:
            new_phrase = '%s %s' % (msg["user"], new_phrase)


        publish(msg, new_phrase)

    e.run()
