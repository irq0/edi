#!/bin/env python

import requests
import re

class BaseActor(object):
    exchange = ""
    default_rkey = " "

    def __init__(self, name, descr):
        self.name = name
        self.descr = descr

    def payload(self, args):
        return None

    def rkey(self, ignore):
        return [self.default_rkey]

    def help(self):
        return "{}: {}".format(self.name,
                               self.descr)

class FourThreeThreeMhzActor(BaseActor):
    exchange = "act_433mhz"

    states = {
        "on" : "1",
        "off" : "0",
    }

    def __init__(self, name, descr, address):
        super(FourThreeThreeMhzActor, self).__init__(name, descr)
        self.address = address

    def payload(self, args):
        if self.states.has_key(args):
            return ["{} {}".format(self.address, self.states[args])]

    def help(self):
        h = super(FourThreeThreeMhzActor, self).help()
        return "{} - STATES: {}".format(
            h,
            ", ".join(self.states.keys()))

class UnknownFooException(Exception):
    pass

class ParseException(Exception):
    pass

class DMXLampActor(BaseActor):
    exchange = "act_dmx"
    base_rkey = "dmx.lamp"

    def __init__(self, name, location="somewhere", lamps={}, groups={}):
        super(DMXLampActor, self).__init__(name, "{} DMX Actor".format(location))

        self.base_rkey += ".{}".format(location)
        self.lamps = lamps
        self.groups = groups

    def parse_args(self, args):
        try:
            lamp, color = args.split()
        except ValueError:
            raise ParseException

        if lamp in self.lamps:
            return ((lamp,), (color,))
        elif lamp in self.groups:
            group = self.groups[lamp]
            return (group, ((color,) * len(group)))
        else:
            raise UnknownFooException

    def rkey(self, args):
        lamps, ignore = self.parse_args(args)
        return [ self.base_rkey + "." + lamp for lamp in lamps ]

    def payload(self, args):
        ignore, colors = self.parse_args(args)
        return colors

    def help(self):
        h = super(DMXLampActor, self).help()
        return "{} - LAMPS: {} GROUPS: {}".format(
            h,
            ", ".join(self.lamps.keys()),
            ", ".join(self.groups.keys()))


class PassthroughActor(BaseActor):
    def __init__(self, name, descr, exchange, rkey, check_args_fn):
        super(PassthroughActor, self).__init__(name, descr)
        self.exchange = exchange
        self.default_rkey = rkey
        self.check_args = check_args_fn

    def payload(self, args):
        if self.check_args(args):
            return [args]
        else:
            raise ParseException

class RewriteActor(BaseActor):

    def __init__(self, name, descr, rules):
        super(RewriteActor, self).__init__(name, descr)
        self.rules = rules

    def expansions(self, args):
        for rule, expansions in self.rules:
            if re.match(rule, args):
                return expansions
        raise UnknownFooException

    def payload(self, args):
        return None

    def rkey(self, args):
        return None

    def help(self):
        h = super(RewriteActor, self).help()

        return "{} - ALIASES: {}".format(
            h,
            ", ".join(("{}->{}".format(k,v)
                       for k, v in self.rules)))


def fetch_bassdrive_stream_url():
    req = requests.get("http://www.bassdrive.com/v2/streams/BassDrive3.pls")
    if req.ok:
        return re.findall("(http://.*)", req.text)[0]

conf = [
    RewriteActor("music",
                 "Play I some music: dis a $GENRE music!",
                 [("play", ("mpd play 1",)),
                  ("bassdrive", ("mpd clear",
                                 "mpd insert {}".format(fetch_bassdrive_stream_url()),
                                 "mpd play 1")),
                  ("ldnb", ("mpd clear",
                            "mpd insert {}".format(fetch_bassdrive_stream_url()),
                            "mpd play 1")),
              ]),

    FourThreeThreeMhzActor("venti", "Ventilator", "11111 1"),
    FourThreeThreeMhzActor("bulb", "Bunte Lampe", "11111 2"),

    DMXLampActor("dmx",
                 location = "subraum",
                 lamps = {
                     "sofa" : "96",
                     "tuer" : "24",
                     "bastelecke" : "8",
                 },
                 groups = {
                     "all" : ("sofa", "tuer", "bastelecke")
                 }),

    PassthroughActor("mpd",
                     "Music Player Daemon im Subraum - (man mpc)",
                     "act_mpd",
                     "subraum",
                     lambda args : re.match(r"(\w+|\w+ )+", args)),
]



db = { e.name : e for e in conf }

if __name__ == '__main__':

    print "!ACT Configuration:"
    print "\n".join((x.help() for x in conf))
