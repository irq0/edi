#!/usr/bin/env python

import requests
import random
import re

req = requests.get("http://www.liquiddnb.com/mix/featured")
assert req.status_code == 200

def mp3url(urlpart):
    url = "http://www.liquiddnb.com" + urlpart
    req = requests.get(url)
    assert req.status_code == 200
    try:
       return re.findall("\"(http://.+\.mp3)\"", req.text)[0]
    except Exception:
       pass

mixes = frozenset(re.findall("href\=\"(/mix/[a-z0-9\-]+?)\"", req.text))
#print mp3url(random.choice(list(mixes)))
print u"\n".join((mp3url(mix) for mix in mixes if mix))

