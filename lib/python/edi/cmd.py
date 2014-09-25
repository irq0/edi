#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ✓

"""
EDI python library
"""

from __future__ import unicode_literals

__author__  = "Marcel Lauhoff"
__email__   = "ml@irq0.org"
__license__ = "GPL"

import edi.emit

class Cmd(object):
    def __init__(self, chan, src="NA", user="NA"):
        self.chan = chan
        self.src = src
        self.user = user

    def __getattr__(self, name):
        def cmd( *args):
            return edi.emit.cmd(
                chan=self.chan,
                cmd=name,
                src=self.src,
                user=self.user,
                args=" ".join(map(str, args)))

        return cmd
