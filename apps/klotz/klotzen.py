#!/usr/bin/env python

import serial
import re
import os

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


SCRIPTPATH = os.path.realpath(os.path.dirname(__file__))

def process(line):
    matchObj = re.match( r"([0-3]),([0-3])", line)
    if matchObj is not None:
        x = matchObj.group(1)
        y = matchObj.group(2)

    try:
        path = os.path.join(SCRIPTPATH, "actions/%s%s" % (x, y))
        log.info("executing: %S" % (path))
        os.system(path)
    except Exception, e:
        pass
    

def main():
    s = serial.Serial("/dev/ttyACM0", 9600)
    while True:
        line = s.readline().strip() # blocks
        process(line)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Bye!")