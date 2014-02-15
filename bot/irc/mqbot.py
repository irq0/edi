#!/usr/bin/env python

#
# Simple IRC<->AMQP bot
#

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
from twisted.python import log

from threading import Thread

from amqplib import client_0_8 as amqp

import time
import sys
import os
import json

network = {
    "host" : "irc.hackint.eu",
    "port" : 9999,
    "autojoin" : (
        "#c3pb.sh"),
}

AMQP_SERVER = os.getenv("AMQP_SERVER") or "localhost"

class MQ(Thread):
    def __init__(self, bot):
        Thread.__init__(self)
        self.daemon = True
        self.bot = bot

        self.conn = amqp.Connection(host=AMQP_SERVER)
        self.chan = self.conn.channel()
        self.exchange = "msg"

        self.chan.exchange_declare(exchange=self.exchange,
                                   durable=True,
                                   auto_delete=False,
                                   type="topic")

        result = self.chan.queue_declare(exclusive=True)
        self.send_queue_name = result[0]

        self.chan.queue_bind(exchange=self.exchange,
                             queue=self.send_queue_name,
                             routing_key="irc.send.raw")

        self.chan.basic_consume(callback=self.send,
                                queue=self.send_queue_name)


    def send(self, msg):
        print msg.body

	lines = msg.body.split("\n")
	for line in lines:
	        self.bot.msg("#c3pb.sh", line)
		time.sleep(0.5)

    def msg(self, user, msg, chan, type):
        jmsg = json.dumps({
            "user" : user,
            "msg" : msg,
            "chan" : chan,
            "type" : type,
        })

        amsg = amqp.Message(jmsg)
        amsg.properties["content_type"] = "application/json"
        amsg.properties["delivery_mode"] = 2
        amsg.properties["app_id"] = "edi-irc"

        self.chan.basic_publish(exchange=self.exchange,
                                routing_key="irc.recv.raw",
                                msg=amsg)

    def run(self):
        self.running = True
        while self.running:
            try:
                self.chan.wait()
            except Exception:
                time.sleep(5)

    def close(self):
        self.running = False
        self.conn.close()


class MQBot(irc.IRCClient):
    nickname = "EDI"
    realname = "Enhanced Subraum Intelligence"
    username = "ESI"
    password = "***REMOVED***"

    def connectionMade(self):
        print "connection made"
        irc.IRCClient.connectionMade(self)
        self.pub = MQ(self)
        self.pub.start()

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.pub.close()

    def signedOn(self):
        print "Signed on"

        self.msg("NickServ", "IDENTIFY {}".format(self.password))

        for chan in ("#c3pb.sh", ):
            print "join chan: ", chan
            self.join(chan)

    def privmsg(self, user, chan, msg):
        user = user.split('!', 1)[0]

        print "<%s> %s" % (user, msg)
        self.pub.msg(user, msg, chan, "privmsg")

    def action(self, user, channel, msg):
        user = user.split('!', 1)[0]

        print "* %s %s" % (user, msg)
        self.pub.msg(user, msg, "action")

class BotFactory(protocol.ClientFactory):
    protocol = MQBot

    def clientConnectionLost(self, connector, reason):
        print "connection lost.. reconnecting"
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    log.startLogging(sys.stdout)

    factory = BotFactory()

#    reactor.connectTCP("irc.hackint.org",
#                       6666,
#                       factory)

    reactor.connectSSL(network["host"],
                       network["port"],
                       factory,
                       ssl.ClientContextFactory())

    # run bot
    reactor.run()
