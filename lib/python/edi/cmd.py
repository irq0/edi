#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import edi.emit

class Cmd(object):
    def __init__(self, chan):
        self.chan = chan

    def __getattr__(self, name):
        def cmd(*args):
            return edi.emit.cmd(
                self.chan,
                {"cmd" : name,
                 "args" : " ".join(args)})

        return cmd
