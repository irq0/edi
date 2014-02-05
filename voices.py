#!/usr/bin/env python

import operator
import requests

from itertools import groupby
from bs4 import BeautifulSoup


def voices():
    r = requests.get("http://www.acapela-group.com/demo-tts/DemoHTML5Form_V2.php")

    if r.status_code == 200:
        s = BeautifulSoup(r.text)

        sonid2lang = {
            o["value"] : o.contents[0].strip()
            for o in s.find(id="typetalkdemo").find("select", id="MyLanguages").find_all("option")
        }

        sonid2voices = [
            (o["class"][1], o["value"])
            for o in reduce(operator.add,
                            map(lambda x : x.find_all("option"),
                                s.find(id="typetalkdemo").find_all("select",
                                                                   {"class" : "allselects"})))
        ]

        lang2voices = {
            sonid2lang[sonid] : [ g[1] for g in group ]
            for sonid, group in
            groupby(sonid2voices, operator.itemgetter(0))
        }

        return lang2voices
    else:
        return {}


if __name__ == "__main__":
    print "\n".join(("{}: {}".format(lang, ", ".join(voices))
                     for lang, voices in voices().iteritems()))
