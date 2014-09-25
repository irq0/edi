#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "space"

import edi
import sys, os
import time
import json
import operator
import re

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

jsoned_memory = os.path.abspath(os.getenv("EDI_KARMA_FILE") or
                         os.path.abspath(os.path.join(os.path.dirname(__file__), 'karma.json')))

if os.path.isfile(jsoned_memory):
    memory = json.load( open( jsoned_memory, "rb" ) )
    log.debug(memory)
else:
    memory = dict()

def handle_get_karma(args, thing):
    if thing in memory:
        to_send = "%s: %s" % (thing, memory[thing])
    else:
        to_send = "%s? .. What's that supposed to be?!" % (thing)

    edi.emit.msg_reply(e.chan,
                       src=args["src"],
                       user=args["user"],
                       msg=to_send)

def mod_karma(thing, operator):
    if thing in memory:
        memory[thing] = operator(memory[thing], 1)
    else:
        memory[thing] = operator(0, 1)

    log.info("%s's new karma: %s" % (thing, memory[thing]))
    with open( jsoned_memory, "wb" ) as f:
        json.dump( memory, f )

with edi.Manager(name="Karma", descr="Rate what you love and hate.") as e:

    @edi.edi_cmd(e, "karma",
                 args="TEXT",
                 descr="Get karma of $arg")
    def get_karma_recv(**args):
        handle_get_karma(args, args["args"])

    @edi.edi_cmd(e, "kinc",
                 args="TEXT",
                 descr="Increment Karma of $arg")
    def inc_karma(args, **rest):
        mod_karma(args, operator.add)

    @edi.edi_cmd(e, "kdec",
                 args="TEXT",
                 descr="Decrement Karma of $arg")
    def inc_karma(args, **rest):
        mod_karma(args, operator.sub)

    @edi.edi_msg(e, "#.recv.*")
    @edi.edi_filter_matches(r"\b(\S+?)\s?(\+\++|--+)")
    def mod_karma_recv(regroups, **msg):
        assert len(regroups) == 2
        thing, action = regroups

        if action[0] == "+":
            mod_karma(thing, operator.add)
        elif action[0] == "-":
            mod_karma(thing, operator.sub)

    e.register_inspect_command()
    e.run()
