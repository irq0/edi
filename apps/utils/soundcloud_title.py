#!/usr/bin/env python

import requests
import sys

r = requests.get("""http://api.soundcloud.com/resolve.json?url={}&client_id={}""".format(
    sys.argv[1],
    "8f7c6373041b5ef757e5bd2880a14b64"))

print r.json()["title"]
#print r.json()["description"]
