#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ✓

import os

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
