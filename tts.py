#!/usr/bin/env python

from __future__ import print_function

import sys
import anydbm
import random
import re
import os
import uuid
import os.path
import json

import requests

SCRIPTPATH = os.path.realpath(os.path.dirname(__file__))
SAMPLE_PATH = os.path.join(SCRIPTPATH, "samples")
CACHE = anydbm.open(os.path.join(SCRIPTPATH, "cache.dat"), "c")

DEFAULT_VOICES = [ s.lower() for s in
                   open(os.path.join(SCRIPTPATH, "default_voices")).read().split(",") ]

DEFAULT_PITCH = 100
DEFAULT_SPEED = 180

PASSWORD= '0g7znor2aa'

def req_tts(voice, req_text):
    """Make tts requests. Returns url to mp3 file"""

    params = {
        'cl_env': 'FLASH_AS_3.0',
        'req_asw_type': 'INFO',
        'req_voice': voice,
        'req_timeout': '120',
        'cl_vers': '1-30',
        'req_snd_type': '',
        'req_text': req_text,
        'cl_app': 'PROD',
        'cl_login': 'ACAPELA_BOX',
        'prot_vers': '2',
        'req_snd_id': '0_0_84%s88' % random.randint(0, 32767),
        'cl_pwd': PASSWORD
    }

    headers = {
        "Accept": "text/plain",
        "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0",
    }

    req = requests.post("http://vaassl3.acapela-group.com/Services/AcapelaBOX/0/Synthesizer",
                        data=params,
                        headers=headers)

    if req.status_code == 200:
        if "res=NO" in req.text:
            print("ERROR:", req.text, file=sys.stderr)
        else:
            url = re.search('http://.*\.mp3', req.text).group()
            print("Found mp3 URL:", url, file=sys.stderr)
            return url

def req_mp3(url, filename):
    req = requests.get(url)

    if req.status_code == 200:

        with open(filename, 'wb') as fd:
            for chunk in req.iter_content(1024):
                fd.write(chunk)
        return filename

def mkfilename():
    return "{}".format(uuid.uuid4())

def sample_path(filename):
    return os.path.join(SAMPLE_PATH, filename)

def cache_get(*args):
    key = json.dumps(args)

    try:
        filename = json.loads(CACHE[key])[0]
    except KeyError:
        filename = mkfilename()

    hit = os.path.isfile(sample_path(filename))

    return (key, filename, hit)

def cache_put(key, filename, meta=None):
    CACHE[key] = json.dumps([filename, meta])

def tts(voice, text, pitch=DEFAULT_PITCH, speed=DEFAULT_SPEED, meta=None):
    if voice in DEFAULT_VOICES:
        voice = '%s22k' % voice.lower()
    else:
        voice = "%s22k" % DEFAULT_VOICES[0].lower()

    print("Voice", voice, file=sys.stderr)

    if not text.endswith("."):
        text += "."

    key, filename, hit = cache_get(voice, text, pitch, speed)

    if hit:
        print("TTS is cached", file=sys.stderr)
        return sample_path(filename)
    else:
        textparam = '\\vct=%d\\ \\spd=%d\\ %s' % (pitch, speed, text)
        url = req_tts(voice, textparam)

        if url:
            success = req_mp3(url, sample_path(filename))

            if success:
                cache_put(key, filename, meta)
                return filename

def print_cache():
    if len(CACHE) > 0:
        print("{:<40}\t{:<40}\t{:<10}".format("UUID",
                                              "Cache Key",
                                              "Metadata"))
        for k, v in CACHE.iteritems():
            key = json.loads(k)
            uuid, meta = json.loads(v)

            print("{:<40}\t{:<40}\t{:<10}".format(uuid,
                                                         ",".join(map(str,key)),
                                                         meta),
                  file=sys.stderr)
        print()

if __name__ == "__main__":
    print_cache()
    print(tts("lucy", " ".join(sys.argv[1:]), meta="cli"))
    CACHE.close()
