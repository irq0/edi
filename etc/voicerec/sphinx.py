#!/usr/bin/env python

import time

import pygtk
pygtk.require('2.0')
import gtk

import gobject
import pygst
pygst.require('0.10')
gobject.threads_init()
import gst


def application_message(bus, msg):
    msgtype = msg.structure.get_name()
    if msgtype == 'partial_result':
        print msg.structure['hyp'], msg.structure['uttid']
    elif msgtype == 'result':
        print msg.structure['hyp'], msg.structure['uttid']
#        self.pipeline.set_state(gst.STATE_PAUSED)

def asr_partial_result(asr, text, uttid):
    """Forward partial result signals on the bus to the main thread."""
    struct = gst.Structure('partial_result')
    struct.set_value('hyp', text)
    struct.set_value('uttid', uttid)
    asr.post_message(gst.message_new_application(asr, struct))


def asr_result(asr, text, uttid):
    """Forward result signals on the bus to the main thread."""
    struct = gst.Structure('result')
    struct.set_value('hyp', text)
    struct.set_value('uttid', uttid)
    asr.post_message(gst.message_new_application(asr, struct))

pipeline = gst.parse_launch('alsasrc device=hw:0 ! audioconvert ! audioresample '
                            + '! vader name=vad auto_threshold=true '
                            + '! pocketsphinx name=asr ! filesink append=true location=/tmp/sphinx.wav')


asr = pipeline.get_by_name('asr')
asr.connect('partial_result', asr_partial_result)
asr.connect('result', asr_result)
asr.set_property('configured', True)
asr.set_property('lm', '/home/seri/WORKSPACE/edi/src/voicerec/knowledgebase/3475.lm')
asr.set_property('dict', '/home/seri/WORKSPACE/edi/src/voicerec/knowledgebase/3475.dic')

bus = pipeline.get_bus()
bus.add_signal_watch()
bus.connect('message::application', application_message)

pipeline.set_state(gst.STATE_PLAYING)


gtk.main()
