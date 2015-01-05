#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "space"

import edi
import json
import feedparser
import os
import re
import time
from threading import Thread

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

jsoned_memory = os.path.abspath(os.getenv("EDI_RSS_FILE") or
                os.path.abspath(os.path.join(os.path.dirname(__file__), 'rss.json')))

if os.path.isfile(jsoned_memory):
    memory = json.load( open( jsoned_memory, "rb" ) )
    log.debug(memory)
else:
    memory = dict()


def write_memory():
    with open( jsoned_memory, "wb" ) as f:
        json.dump( memory, f )

def publish(key, message):
    edi.emit.msg_reply(e.chan,
                       src=key,
                       msg=message)

def add_rss(src, alias, url):
    if not memory.has_key(src):
        memory[src] = dict()

    if not rss_check(url):
        to_send = "That url doesn't seem to be a valid RSS feed."
        publish(src, to_send)
    elif (memory[src].has_key(alias)
       or url in [v['url'] for v in memory[src].values()]):
        to_send = "%s? I already track that for you.." % (alias)
        publish(src, to_send)
    else:
        memory[src][alias] = {  'url'           : url,
                                'last_published': "" }
        write_memory()
        update()

def del_rss(src, alias):
    if memory[src].has_key(alias):
        memory[src].pop(alias)
        write_memory()
        to_send = "I won't track %s anymore." % (alias)
    else:
        to_send = "%s? .. What's that supposed to be?!" % (alias)

    publish(src, to_send)

def list_rss(src):
    if not memory.has_key(src):
        to_send = "I don't track any RSS feeds."
    elif [v['url'] for v in memory[src].values()] == []:
        to_send = "I don't track any RSS feeds."
    else:
        to_send = "I track: %s" % (", ".join(memory[src].keys()))

    publish(src, to_send)

def rss_check(url):
    try:
        feed = feedparser.parse(url)
        assert(feed["bozo"] != 1) # bozo == 1 means, that the feed wasn't parsable.
        assert(feed.entries[0].title)
        assert(feed.entries[0].link)

        res = feed
    except Exception, e:
        res = False

    return res

def update():
    for src in memory.keys():
        for alias in memory[src].keys():
            feed = rss_check(memory[src][alias]['url'])

            if not feed:
                to_send = "Uh.. I couldn't get %s for you." % (alias)
                publish(src, to_send)
                memory[src][alias]['last_published'] = to_send
                continue

            link = feed.entries[0].link
            link = re.findall(r'.{1,400}', link)
            link = "\n".join(link)

            to_send = "%s - %s\n%s" % (alias, feed.entries[0].title, link)
            if to_send == memory[src][alias]['last_published']:
                continue
            else:
                publish(src, to_send)
                memory[src][alias]['last_published'] = to_send

    write_memory()


class FeedUpdater(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

    def run(self):
        while True:
            log.debug("Updating Feeds")
            update()
            time.sleep( 3 * 60 )


with edi.Manager(name="RSS", descr="RSS feed client") as e:

    @edi.edi_cmd(e, "sub",
                 args="TEXT",
                 descr="Track RSS feed")
    def add_rss_recv(**args):
        if len(args["args"].split()) == 2:
            add_rss(args['src'], args["args"].split()[0], args["args"].split()[1])
        else:
            to_send = "Try it like this: !sub <alias> <url>"
            publish(args["src"], to_send)

    @edi.edi_cmd(e, "unsub",
                 args="TEXT",
                 descr="Un-Track RSS feed")
    def del_rss_recv(**args):
        if len(args["args"].split()) == 1:
            del_rss(args['src'], args["args"].split()[0])
        else:
            to_send = "Try it like this: !unsub <alias>"
            publish(args["src"], to_send)

    @edi.edi_cmd(e, "list",
                 args="TEXT",
                 descr="List tracked RSS feeds")
    def list_rss_recv(**args):
        list_rss(args['src'])

    e.register_inspect_command()
    FeedUpdater().start()    
    e.run()
