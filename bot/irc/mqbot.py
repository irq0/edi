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

config = {
    "host" : "spaceboyz.net",
    "port" : 9999,
    "channel" : "#/dev/subraum",
}

AMQP_SERVER = os.getenv("AMQP_SERVER") or "localhost"

class MQ(Thread):
    def __init__(self, bot):
        Thread.__init__(self)
        self.daemon = True
        self.bot = bot
        self.init_connection()


    def init_connection(self):
        self.conn = amqp.Connection(host=AMQP_SERVER)
        self.chan = self.conn.channel()
        self.exchange = "msg"

        self.consumer_tags = []

        self.chan.exchange_declare(exchange=self.exchange,
                                   durable=True,
                                   auto_delete=False,
                                   type="topic")

        result = self.chan.queue_declare(exclusive=True)
        self.send_queue_name = result[0]

        self.chan.queue_bind(exchange=self.exchange,
                             queue=self.send_queue_name,
                             routing_key=".".join(("irc", self.bot.nickname, "send", "*")))

        self.chan.queue_bind(exchange=self.exchange,
                             queue=self.send_queue_name,
                             routing_key=".".join(("irc", self.bot.nickname, "presence")))

        self.add_consumer()

    def add_consumer(self):
        self.consumer_tags.append(self.chan.basic_consume(callback=self.handle_consume,
                                                          queue=self.send_queue_name))

    def handle_consume(self, raw_msg):
        try:
            key = raw_msg.delivery_info["routing_key"].split(".")

            if raw_msg.properties["content_type"] == "application/json":
                self.handle_json_message(key, json.loads(raw_msg.body))
            elif raw_msg.properties["content_type"] == "text/plain":
                self.handle_plain_message(key, raw_msg.body)
            else:
                print "Message with unknown content type:", raw_msg

        except Exception, e:
            print "Exception in consume handler:", e

    def handle_json_message(self, key, msg):
        if key[2] == "presence":
            self.irc_presence(msg["status"], msg["msg"])
        elif key[2] == "send":
            self.irc_send(key[3], msg["user"], msg["msg"])
        else:
            print "Unknown message type:", key[2], msg

    def handle_plain_message(self, key, msg):
        if key[2] == "presence":
            self.irc_presence(msg, u"")
        elif key[2] == "send":
            self.irc_send(key[3], key[3], msg)
        else:
            print "Unknown message type:", key[2], msg

    def remove_consumer(self):
        for tag in self.consumer_tags:
            self.chan.basic_cancel(tag)

    def irc_presence(self, status, msg):
        print "PRESENCE:", status, msg

        if status == "away":
            self.bot.away(msg.encode("UTF-8"))
        elif status == "online":
            self.bot.back()
        else:
            print "Received unknown status:", status

    def irc_send(self, dest, user, msg):
        print "SEND:", dest, user, msg

        user = user.encode("UTF-8")
        msg = msg.encode("UTF-8")
        dest = dest.encode("UTF-8")

        # long message with user intended for channel -> msg user
        if len(msg) > 120 and dest == config["channel"] and user != config["channel"]:
            dest = user
        # message for channel with known user -> prefix with 'user:'
        elif dest == config["channel"] and user != config["channel"]:
            msg = user + ": " + msg

        self.bot.msg(dest, msg)


    def irc_recvd(self, user, msg, chan, type):
        """Called whenever something was received from irc"""

        jmsg = json.dumps({
            "user" : user.decode("UTF-8"),
            "msg" : msg.decode("UTF-8"),
            "chan" : chan.decode("UTF-8"),
            "type" : type.decode("UTF-8"),
            "bot" : self.bot.nickname,
        })

        amsg = amqp.Message(jmsg)
        amsg.properties["content_type"] = "application/json"
        amsg.properties["delivery_mode"] = 2
        amsg.properties["app_id"] = "edi-irc"

        try:
            self.chan.basic_publish(exchange=self.exchange,
                                    routing_key=".".join(("irc", self.bot.nickname, "recv", chan)),
                                    msg=amsg)
        except Exception, e:
            print "Exception while publishing message:", e

    def run(self):
        while self.chan.callbacks:
            try:
                self.chan.wait()
            except Exception:
                time.sleep(5)

    def close(self):
        try:
            self.conn.close()
        except IOError, e:
            print "Error while closing amqp connection:", e

class MQBot(irc.IRCClient):
    """http://twistedmatrix.com/documents/8.2.0/api/twisted.words.protocols.irc.IRCClient.html"""

    nickname = "ESI"
    realname = "Enhanced Subraum Intelligence"
    username = "ESI"
    password = "***REMOVED***"
    lineRate = 0.1


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

        print "join chan: ", config["channel"]
        self.join(config["channel"])

    def privmsg(self, user, chan, msg):
        print "privmsg:", user, chan
        user = user.split('!', 1)[0]

        print "<%s> %s" % (user, msg)
        self.pub.irc_recvd(user, msg, chan, "privmsg")

    def action(self, user, chan, msg):
        user = user.split('!', 1)[0]

        print "* %s %s" % (user, msg)
        self.pub.irc_recvd(user, msg, chan, "action")

class BotFactory(protocol.ClientFactory):
    protocol = MQBot

    def clientConnectionLost(self, connector, reason):
        print "connection lost:", connector, reason
        print "reconnecting.."
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", connector, reason
        reactor.stop()


if __name__ == '__main__':
    log.startLogging(sys.stdout)

    factory = BotFactory()

#    reactor.connectTCP("irc.hackint.org",
#                       6666,
#                       factory)

    reactor.connectSSL(config["host"],
                       config["port"],
                       factory,
                       ssl.ClientContextFactory())

    # run bot
    reactor.run()
