#!/bin/env python

import os
import subprocess
import pika
import json
import re
import traceback

import logging
from multiprocessing import Pool

from config import db, UnknownFooException, ParseException

pool = Pool(processes=4)
channel = None

def emit_act(chan, dst, rkey, payload):
    print "---> [%r] rkey=%r payload=%r" % (dst, rkey, payload)
    chan.basic_publish(exchange=dst,
                       routing_key=rkey,
                       body=payload,
                       properties=pika.BasicProperties(
                           content_type="application/octet-stream",
                           delivery_mode=2))

def emit_error(chan, cmd, error):
    key = cmd["src"].replace("recv", "send")
    msg = "%s: %s" % (cmd["user"], error)

    print "---> [%r] %r" % (key, msg)

    chan.basic_publish(exchange="msg",
                       routing_key=key,
                       body=msg,
                       properties=pika.BasicProperties(
                           content_type="text/plain",
                           delivery_mode=2))

def handle_notfound(arg):
    return "I know nothin' about a \"{}\". Try \"help\"".format(" ".join(arg))

def handle_help(arg):
    if len(arg) > 1 and db.has_key(arg[1]):
        return db[arg[1]].help()
    else:
        return "Available actors: {}".format(
            ", ".join((x.name for x in db.itervalues())))

def handle_command(chan, thing_name, args):
    assert db.has_key(thing_name)
    thing = db[thing_name]

    def do():
        dst = db[thing_name].exchange

        payloads = thing.payload(args)
        rkeys = thing.rkey(args)

        print "---> [CONFIG]", "payloads:", payloads, "rkeys:", rkeys

        assert len(payloads) == len(rkeys)

        for p, r in zip(payloads, rkeys):
            success = emit_act(chan, dst, r, p)
            if success:
                print "---> [?] success=%s" % (success)

        return success

    if hasattr(thing, "expansions"):
        print "~~~~ [EXPAND] orig:", thing_name, args

        for thing_name, args in [ ex.split(None, 1) for ex in thing.expansions(args) if ex]:
            print "~~~~ [EXPAND] *", thing_name, args
            handle_command(chan, thing_name, args)
    else:
        do()
#    pool.apply_async(do)


def callback(chan, method, props, body):
    print "<--- [%r] %r" % (method.routing_key, body)

    if props.content_type == "application/json":
        d = json.loads(body)

        args = d["args"].split(None, 1)
        print "~~~~ CALLBACK: args:", args

        try:
            if 0 < len(args) < 1:
                emit_error(chan, d, "More input please")
            elif args[0] == "help":
                emit_error(chan, d, handle_help(args))
            elif 0 < len(args) < 2:
                emit_error(chan, d, "More input please")
            elif args[0] not in db:
                emit_error(chan, d, handle_notfound(args))
            else:
                handle_command(chan, args[0], args[1])
                chan.basic_ack(delivery_tag = method.delivery_tag)

        except UnknownFooException:
            emit_error(chan, d, handle_notfound(args))

        except ParseException:
            # todo print something nicer..
            emit_error(chan, d, handle_notfound(args))

        except Exception, e:
            print "~~~~ EXCEPTION in callback: ", e
            traceback.print_exc()

def main():
    amqp_server = os.getenv("AMQP_SERVER") or "localhost"
    conn = pika.BlockingConnection(pika.ConnectionParameters(amqp_server))
    chan = conn.channel()
    exchange = "cmd"
    queue = "act"

    pika_logger = logging.getLogger('pika')
    pika_logger.setLevel(logging.INFO)

    def setup():
        logging.basicConfig()

        chan.queue_declare(queue=queue,
                           durable=True,
                           auto_delete=True)

        chan.queue_bind(exchange=exchange,
                        queue=queue)

        print "---- Using queue:", queue

    def run():
        print "---- Waiting for messages:"

        chan.basic_consume(callback,
                           queue=queue)

        chan.start_consuming()

    def teardown():
        conn.close()

    try:
        setup()
        run()
    except KeyboardInterrupt:
        pass
    finally:
        teardown()


if __name__ == "__main__":
    main()
