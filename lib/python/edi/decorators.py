#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ✓

"""
EDI python library
"""

from __future__ import unicode_literals

import re
from functools import wraps


__author__  = "Marcel Lauhoff"
__email__   = "ml@irq0.org"
__license__ = "GPL"


def edi_cmd(edi, cmd_name, **args):
    "Register EDI command"
    def decorator(f):
        edi.register_command(f, cmd_name, **args)
        return f
    return decorator


def edi_msg(edi, key):
    "Listen for EDI msg by routing key"
    def decorator(f):
        edi.register_msg_handler(f, key)
        return f
    return decorator

edi_msg_recv = lambda : edi_msg("#.recv.*")
edi_msg_recv_proto = lambda proto : edi_msg("{}.*.recv.*".format(proto))
edi_msg_recv_ircchan = lambda : edi_msg("irc.*.recv._channel_")

def edi_filter_matches(regex, field="msg"):
    r = re.compile(regex)
    def decorator(f):
        @wraps(f)
        def wrapper(**args):
            match = r.search(args[field])
            if match:
                return f(match.groups(), **args)
        return wrapper
    return decorator

def edi_filter_msg_with_uflag_any(uflags):
    """ Calls the wrapped function if any of the flags are in the users flag
        list.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(**args):
            doit = False
            for f in uflags:
                try:
                    if args["uflags"].index(f) is not None:
                        doit = True
                except:
                    pass
            if doit:
                return fn(**args)
        return wrapper
    return decorator

def edi_filter_msg_with_uflag_none(uflags):
    """ Calls the wrapped function if none of the flags are in the users flag
        list.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(**args):
            doit = True
            for f in uflags:
                try:
                    if args["uflags"].index(f) is not None:
                        doit = False
                except:
                    pass
            if doit:
                return fn(**args)
        return wrapper
    return decorator
