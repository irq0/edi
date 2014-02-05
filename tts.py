#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
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
CACHE_FILENAME = os.path.join(SCRIPTPATH, "cache.dat")

DEFAULT_VOICES = [ s.strip().lower() for s in
                   open(os.path.join(SCRIPTPATH, "default_voices")).read().split(",") ]
DEFAULT_VOICE = "julia"

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

    global CACHE_FILENAME
    filename = None
    hit = True

    cache = anydbm.open(CACHE_FILENAME, "c")

    try:
        filename = json.loads(cache[key])[0]
    except KeyError:
        filename = mkfilename()
        hit = os.path.isfile(sample_path(filename))

    cache.close()
    return (key, filename, hit)

def cache_put(key, filename, meta=None):
    global CACHE_FILENAME
    cache = anydbm.open(CACHE_FILENAME, "c")
    cache[key] = json.dumps([filename, meta])
    cache.close()

def tts(voice, text, pitch=DEFAULT_PITCH, speed=DEFAULT_SPEED, meta=None):
    if voice in DEFAULT_VOICES:
        voice = '%s22k' % voice.lower()
    else:
        voice = "%s22k" % DEFAULT_VOICE.lower()

    print("Voice:", voice, file=sys.stderr)

    if not text.endswith("."):
        text += "."

    key, filename, hit = cache_get(voice, text, pitch, speed)

    print("Text:", text, file=sys.stderr)

    if hit:
        print("Returning cached tts", file=sys.stderr)
        return sample_path(filename)
    else:
        textparam = '\\vct=%d\\ \\spd=%d\\ %s' % (pitch, speed, text)
        url = req_tts(voice, textparam)

        if url:
            success = req_mp3(url, sample_path(filename))

            if success:
                cache_put(key, filename, meta)
                return sample_path(filename)

def list_cache():
    result = []

    global CACHE_FILENAME
    cache = anydbm.open(CACHE_FILENAME, "c")
    if len(cache) > 0:
        result.append("{:<40}\t{:<40}\t{:<10}".format("UUID",
                                                      "Cache Key",
                                                      "Metadata"))
        for k, v in cache.iteritems():
            key = json.loads(k)
            uuid, meta = json.loads(v)

            result.append("{:<40}\t{:<40}\t{:<10}".format(uuid,
                                                         ",".join(map(str,key)),
                                                         meta))

    cache.close()
    return "\n".join(result)

class ArgumentParserError(Exception):
    pass

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)

def parse_args(args=None):
      parser = ThrowingArgumentParser(
          add_help=False)


      parser.add_argument("--voice",
                          choices=DEFAULT_VOICES,
                          default=DEFAULT_VOICE,
                          help="Voice to use. List supported voices and languages with '--list-voices'")
      parser.add_argument("--pitch",
                          type=int,
                          default=DEFAULT_PITCH,
                          help="Pitch (Default: {})".format(DEFAULT_PITCH))
      parser.add_argument("--speed",
                          type=int,
                          default=DEFAULT_SPEED,
                          help="Speed (Default: {})".format(DEFAULT_SPEED))

      group = parser.add_mutually_exclusive_group(required=True)

      group.add_argument("--list-voices",
                          default=False,
                          action="store_true",
                          help="List all available voices. Fetch from server")
      group.add_argument("--list-cache",
                          default=False,
                          action="store_true",
                          help="List cache entries")
      group.add_argument("--text",
                          help="Text",
                          nargs="+")
      group.add_argument("--help",
                         default=False,
                         action="store_true",
                         help="Help message")

      result = parser.parse_args(args)
      result.help_message = parser.format_help()
      return result

def with_args(args=None, meta="cli"):
    args = parse_args(args)
    result = None

    if args.list_voices:
        import voices
        result = ("voices", "\n".join(("{}: {}".format(lang, ", ".join(voices))
                                       for lang, voices in voices.voices().iteritems())))
    elif args.list_cache:
        result = ("cache", list_cache())

    elif args.help:
        result = ("help", args.help_message)

    else:
        d = vars(args)
        d["meta"] = meta
        d["text"] = " ".join(d["text"])
        del d["list_voices"]
        del d["list_cache"]
        del d["help"]
        del d["help_message"]

        result = ("filename", tts(**d))

    return result

if __name__ == "__main__":
    try:
        print(with_args()[1])
    except ArgumentParserError, e:
        print(e)
        sys.exit(1)

    print()
