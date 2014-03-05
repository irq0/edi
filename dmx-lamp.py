#!/usr/bin/env python2

#TODO State regelmaessig auf den Bus schreiben
#TODO Farbprogramme

#key dmx.lamp.subraum.control, body =~ (on|off)
#key dmx.lamp.subraum.0, body =~ \d,\d,\d

#Lampenids: 8, 24, 96

from serial import Serial
import pika
import sys

#ser = Serial('/dev/dmx', 38400, timeout=1) TODO

subsystem='subraum'

def on():
    ser.write('B0')

def off():
    ser.write('B1')

def setrgb(channel, r, g, b):
    print channel, r,g,b
    if r>255: r=255
    if r<0: r=0
    if g>255: g=255
    if g<0: g=0
    if b>255: b=255
    if b<0: b=0
    ser.write("C{0:03d}L000".format(channel-1))
    ser.write("C{0:03d}L{1:03d}".format(channel+0, r))
    ser.write("C{0:03d}L{1:03d}".format(channel+1, g))
    ser.write("C{0:03d}L{1:03d}".format(channel+2, b))
    ser.write("C{0:03d}L000".format(channel+3))

def resolve_color(color):
    import re
    m = re.match('(\d+),(\d+),(\d+)', color)
    if m:
        return [int(m.group(1)), int(m.group(2)), int(m.group(3))]
    m = re.match('#([a-fA-F0-9]{2})([a-fA-F0-9]{2})([a-fA-F0-9]{2})', color)
    if m:
        return [int(m.group(1),16), int(m.group(2),16), int(m.group(3),16)]
    import json
    return json.loads(color)

def cb(ch, methods, props, body):
    routing_key = methods.routing_key
    if routing_key == 'dmx.lamp.'+subsystem+'.control':
        if body == 'on':
            on()
        elif body == 'off':
            off()
        return
    if len(routing_key) <= len('dmx.lamp.'+subsystem+'.'):
        return
    lampid = routing_key[len('dmx.lamp.'+subsystem+'.'):]
    setrgb(lambid, *resolve_color(body))
    print lampid
if __name__ == '__main__':
    
    conn = pika.BlockingConnection(pika.ConnectionParameters(host='mopp'))
    ch = conn.channel()
    ch.exchange_declare(exchange='act_dmx', exchange_type='topic', durable=True)
    ch.queue_declare(queue='act_dmx', durable=True, auto_delete=True)
    ch.queue_bind(exchange='act_dmx', queue='act_dmx', routing_key='dmx.lamp.subraum.*')
    ch.basic_consume(cb, queue='act_dmx')
    ch.start_consuming()
    conn.close()

    A = sys.argv
    if len(A) < 2:
        print "giev args"
        sys.exit()
    if A[1] == 'on':
        on()
    elif A[1] == 'off':
        off()
    elif A[1] == 'setrgb':
        if len(A) < 6:
            print "giev args"
            sys.exit()
        setrgb(int(A[2]), int(A[3]), int(A[4]), int(A[5]))
