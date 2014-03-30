#!/usr/bin/env python

#
# IRC<->AMQP bot
#

# Note: Twisted irc supports multiple joined channels per irc connection.
# To keep things easier the bot only supports one channel. See config["channel"]


from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl, defer
from twisted.python import log

from threading import Thread

from amqplib import client_0_8 as amqp

import time
import sys
import os
import json
import re


# without ssl
# config = {
#     "host" : "spaceboyz.net",
#     "port" : 6667,
#     "channel" : "#c3pb.sh",
#     "nick" : "EDI",
#     "passwd" : "***REMOVED***"
# }

# ssl "simple", no cacert, no client cert, no real checking. you get encryption tough..
# config = {
#     "ssl" : True,
#     "host" : "spaceboyz.net",
#     "port" : 9999,
#     "channel" : "#c3pb.sh",
#     "nick" : "EDI",
#     "passwd" : "***REMOVED***"
# }

# ssl with ca, client certs
config = {
    "ssl" : "cert",
    "host" : "spaceboyz.net",
    "port" : 9999,
    "channel" : "#c3pb.sh",
    "nick" : "EDI",
    "passwd" : "***REMOVED***",
    "ssl_clicert" : "ssl/hackint-client.pem",
    "ssl_cacert" : "ssl/hackint-cacert.pem",
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

            print "CONSUME: routing_key=%s properties=%s body=%s" % (key, raw_msg.properties, raw_msg.body)

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
        user = user.encode("UTF-8")
        msg = msg.encode("UTF-8")
        dest = dest.encode("UTF-8")

        # long message with user intended for channel -> msg user
        if len(msg) > 120 and dest == config["channel"] and user != config["channel"]:
            self.bot.msg(dest, "{}: Lots of data.. Sending you a msg".format(user))
            dest = user
        # message for channel with known user -> prefix with 'user:'
        elif dest == config["channel"] and user != config["channel"]:
            msg = user + ": " + msg

        # dest is bot (irc recv from /msg) -> map to user
        elif dest == self.bot.nickname and user != self.bot.nickname:
            dest = user

        # fallback to channel
        else:
            dest = config["channel"]


        dest = dest.replace("_channel_", config["channel"])
        print "SEND: dest=%s msg=%s" % (dest, msg)

        self.bot.msg(dest, msg)


    def user_flags(self, user):
        """Return set of user flags"""
        flags = {
            [None, "op"][user in self.bot.ops],
        }

        flags.discard(None)

        return flags

    def irc_recvd(self, user, msg, chan, type):
        """Called whenever something was received from irc"""

        jmsg = json.dumps({
            "user" : user.decode("UTF-8"),
            "msg" : msg.decode("UTF-8"),
            "chan" : chan.decode("UTF-8"),
            "type" : type.decode("UTF-8"),
            "bot" : self.bot.nickname,
            "uflags" : list(self.user_flags(user)),
        })
        print "RECV: user=%s chan=%s msg=%s jmsg=%s" % (user, chan, msg, jmsg)

        amsg = amqp.Message(jmsg)
        amsg.properties["content_type"] = "application/json"
        amsg.properties["delivery_mode"] = 2
        amsg.properties["app_id"] = "edi-irc"

        key = ".".join(("irc",
                        self.bot.nickname,
                        "recv",
                        chan.replace(config["channel"],"_channel_")))


        try:
            print "PUBLISH: routing_key=%s msg=%s" % (key, amsg)

            self.chan.basic_publish(exchange=self.exchange,
                                    routing_key=key,
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

class NamesIRCClient(irc.IRCClient):
    def __init__(self, *args, **kwargs):
        self._namescallback = {}

    def names(self, channel):
        channel = channel.lower()
        d = defer.Deferred()
        if channel not in self._namescallback:
            self._namescallback[channel] = ([], [])

        self._namescallback[channel][0].append(d)
        self.sendLine("NAMES %s" % channel)
        return d

    def irc_RPL_NAMREPLY(self, prefix, params):
        channel = params[2].lower()
        nicklist = params[3].split(' ')

        if channel not in self._namescallback:
            return

        n = self._namescallback[channel][1]
        n += nicklist

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        channel = params[1].lower()
        if channel not in self._namescallback:
            return

        callbacks, namelist = self._namescallback[channel]

        for cb in callbacks:
            cb.callback(namelist)

        del self._namescallback[channel]


class MQBot(NamesIRCClient):
    """http://twistedmatrix.com/documents/8.2.0/api/twisted.words.protocols.irc.IRCClient.html"""

    nickname = config["nick"]
    username = config["nick"]
    password = config["passwd"]
    realname = """Uh, my name's EDI, uh, I'm not an addict."""
    lineRate = 0.5

    ops = set()

    def connectionMade(self):
        print "connection made"
        irc.IRCClient.connectionMade(self)
        self.pub = MQ(self)
        self.pub.start()

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.pub.close()

    def signedOn(self):
        print "IRC: Signed on"

        self.msg("NickServ", "IDENTIFY {}".format(self.password))

        print "IRC: join chan: ", config["channel"]
        self.join(config["channel"])

    def joined(self, chan):
        if chan == config["channel"]:
            self.fetch_chan_ops()

    def modeChanged(self, user, chan, do_set_modes, modes, users):
        if chan == config["channel"] and "o" in modes:
            print "IRC", "OP change for users", users, "to", do_set_modes

            if do_set_modes:
                for u in users:
                    self.ops.add(u)
            else:
                for u in users:
                    self.ops.remove(u)

            print "IRC", config["channel"], "OPS:", self.ops

    def userLeft(self, user, chan):
        if chan == config["channel"]:


            self.fetch_chan_ops()

    def privmsg(self, user, chan, msg):
        print "privmsg:", user, chan
        user = user.split('!', 1)[0]

        print "IRC RECV: <%s> %s" % (user, msg)
        self.pub.irc_recvd(user, msg, chan, "privmsg")

    def action(self, user, chan, msg):
        user = user.split('!', 1)[0]

        print "IRC RECV:* %s %s" % (user, msg)
        self.pub.irc_recvd(user, msg, chan, "action")

    def fetch_chan_ops(self):
        def parseOps(names):
            self.ops = set(( n[1:] for n in names
                             if n.startswith("@")))
            print "IRC", config["channel"], "OPS:", self.ops
        self.names(config["channel"]).addCallback(parseOps)

class BotFactory(protocol.ClientFactory):
    protocol = MQBot

    def clientConnectionLost(self, connector, reason):
        print "IRC: connection lost:", connector, reason
        print "IRC: reconnecting.."
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "IRC: connection failed:", connector, reason
        reactor.stop()

def load_clicert(filename):
    with open(filename, "r") as fd:
        cert = ssl.PrivateCertificate.loadPEM(fd.read())
    return cert

def load_cacert(filename):
    with open(filename, "r") as fd:
        cert = ssl.Certificate.loadPEM(fd.read())
    return cert

def connect(factory):
    if config.has_key("ssl") and config["ssl"]:
        if config["ssl"] == "cert":
            print "CONNECT: SSL with client cert"

            cli = load_clicert(config["ssl_clicert"])
            ca = load_cacert(config["ssl_cacert"])

            print "Using client certificate:"
            print cli.inspect()

            reactor.connectSSL(config["host"],
                               config["port"],
                               factory,
                               ssl.CertificateOptions(
                                   privateKey=cli.privateKey.original,
                                   certificate=cli.original,
                                   verify=True,
                                   caCerts=(ca.original,)))
        else:
            print "CONNECT: SSL default"
            reactor.connectSSL(config["host"],
                               config["port"],
                               factory,
                               ssl.ClientContextFactory())
    else:
        print "CONNECT: No SSL"
        reactor.connectTCP("irc.hackint.org",
                           6666,
                           factory)

if __name__ == '__main__':
    log.startLogging(sys.stdout)

    factory = BotFactory()
    connect(factory)

    # run bot
    reactor.run()
