#!/usr/bin/env python
# -*- coding: utf-8 -*-

__title__ = "edi"
__version__ = "0.1"
__author__ = "Marcel Lauhoff"


from .core import init, run, teardown
from .decorators import edi_msg, edi_filter_msg_with_uflag, edi_filter_msg_matches

#foo
