#!/usr/bin/env python

import time
import os
import json
import logging

import edi
import RPi.GPIO as GPIO

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("actor-service")

def setup_gpio():
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(25, GPIO.IN, pull_up_down = GPIO.PUD_UP)

    print "input 23 - schluessel", GPIO.input(23)
    print "input 24 - rot       ", GPIO.input(24)
    print "input 25 - gruen     ", GPIO.input(25)

with edi.Manager() as e:
    cmd = edi.Cmd(e.chan)

    def process_input():
        if GPIO.input(23) == GPIO.LOW and GPIO.input(24) == GPIO.LOW:
            cmd.telinit("0")
            time.sleep(5)
        elif GPIO.input(23) == GPIO.LOW and GPIO.input(25) == GPIO.HIGH:
            cmd.telinit("4")
            time.sleep(5)
        elif GPIO.input(25) == GPIO.HIGH:
            cmd.sob("chewy")
            time.sleep(5)
        elif GPIO.input(24) == GPIO.LOW:
            cmd.sob("chewy")
            time.sleep(5)

        time.sleep(0.01)

    try:
        setup_gpio()
        while True:
            process_input()

    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
