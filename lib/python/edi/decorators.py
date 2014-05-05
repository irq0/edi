#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
from functools import wraps

def edi_cmd(edi, cmd_name):
    "Register EDI command"
    def decorator(f):
        edi.register_command(f, cmd_name)
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

def edi_filter_msg_with_uflag(uflag):
    def decorator(f):
        @wraps(f)
        def wrapper(**args):
            if uflag in args["uflags"]:
                return f(**args)
        return wrapper
    return decorator

def edi_filter_msg_without_uflag(uflag):
    def decorator(f):
        @wraps(f)
        def wrapper(**args):
            if not uflag in args["uflags"]:
                return f(**args)
        return wrapper
    return decorator
