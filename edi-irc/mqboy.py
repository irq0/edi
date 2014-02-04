from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
from twisted.python import log

from threading import Thread

import time
import sys

import pika
import json

network = {
    "host" : "irc.hackint.eu",
    "port" : 9999,
    "autojoin" : (
        "#c3pb.sh"),
}

class MQ(Thread):
    def __init__(self, bot):
        Thread.__init__(self)


        self.daemon = True
        self.bot = bot

        self.conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        self.chan = self.conn.channel()
        self.exchange = "msg"

        self.chan.exchange_declare(exchange=self.exchange,
                                   type="topic")

        result = self.chan.queue_declare(exclusive=True)
        self.send_queue_name = result.method.queue

        self.chan.queue_bind(exchange=self.exchange,
                             queue=self.send_queue_name,
                             routing_key="irc.send.raw")

        self.chan.basic_consume(self.send,
                                queue=self.send_queue_name)

    def send(self, ch, method, props, body):
        self.bot.msg("#c3pb.sh", body)

    def msg(self, user, msg, chan, type):
        jmsg = json.dumps({
            "user" : user,
            "msg" : msg,
            "chan" : chan,
            "type" : type,
        })

        self.chan.basic_publish(exchange=self.exchange,
                                routing_key="irc.recv.raw",
                                properties=pika.BasicProperties(app_id="edi-irc",
                                                                content_type="application/json"),
                                body=jmsg)

    def run(self):
        self.chan.start_consuming()

    def close(self):
        self.chan.stop_consuming()
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

    reactor.connectTCP("irc.hackint.org",
                       6666,
                       factory)

#    reactor.connectSSL(network["host"],
#                       network["port"],
#                       factory,
#                       ssl.ClientContextFactory())

    # run bot
    reactor.run()
