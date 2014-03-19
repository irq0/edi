#!/bin/env python

import dmx

db = {
    "venti" : {
        "dst" : "act_433mhz",
        "payload" : "11111 1",
        "desc" : "Ventilator",
        "pargs" : {
            "on" : "1",
            "off" : "0"
        },
    },
    "bulb" : {
        "dst" : "act_433mhz",
        "payload" : "11111 2",
        "desc" : "Bunte Lampe :)",
        "pargs" : {
            "on" : "1",
            "off" : "0"
        },
    },
    "dmx" : {
        "dst" : "act_dmx",
        "payload" : dmx.payload,
        "rkey" : dmx.rkey,
        "desc" : "DMX",
        "pargs" : {
            "sofa" : "96",
            "tuer" : "24",
            "bastelecke" : "8",
        },
    },
}
