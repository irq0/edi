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
__title__   = "pyedi"
__version__ = "0.1"

from .core import Manager
from .decorators import edi_msg, edi_cmd, edi_msg_recv, edi_msg_recv_proto, edi_msg_recv_ircchan, edi_filter_msg_with_uflag_any, edi_filter_msg_with_uflag_none, edi_filter_matches
from .cmd import Cmd
