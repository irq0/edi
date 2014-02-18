<div id="table-of-contents">
<h2>Table of Contents</h2>
<div id="text-table-of-contents">
<ul>
<li><a href="#sec-1">1. Ideas, Todos</a>
<ul>
<li><a href="#sec-1-1">1.1. Features</a>
<ul>
<li><a href="#sec-1-1-1">1.1.1. <span class="todo OPEN">OPEN</span> User Notifications</a></li>
<li><a href="#sec-1-1-2">1.1.2. <span class="todo ASSIGNED">ASSIGNED</span> pizza / essen / f00d&#xa0;&#xa0;&#xa0;<span class="tag"><span class="_hej">@hej</span>&#xa0;<span class="c3po">c3po</span></span></a></li>
<li><a href="#sec-1-1-3">1.1.3. <span class="done DONE">DONE</span> scheduled messages&#xa0;&#xa0;&#xa0;<span class="tag"><span class="_irq0">@irq0</span></span></a></li>
<li><a href="#sec-1-1-4">1.1.4. <span class="todo TEST">TEST</span> presence: eta login&#xa0;&#xa0;&#xa0;<span class="tag"><span class="_irq0">@irq0</span></span></a></li>
<li><a href="#sec-1-1-5">1.1.5. <span class="todo OPEN">OPEN</span> guess commands&#xa0;&#xa0;&#xa0;<span class="tag"><span class="c3po">c3po</span></span></a></li>
<li><a href="#sec-1-1-6">1.1.6. <span class="todo OPEN">OPEN</span> hubelmeter&#xa0;&#xa0;&#xa0;<span class="tag"><span class="c3po">c3po</span></span></a></li>
<li><a href="#sec-1-1-7">1.1.7. <span class="done DONE">DONE</span> shutdown/startup&#xa0;&#xa0;&#xa0;<span class="tag"><span class="_irq0">@irq0</span></span></a></li>
<li><a href="#sec-1-1-8">1.1.8. <span class="todo OPEN">OPEN</span> subraum init/shutdown auf subinitd migrieren</a></li>
<li><a href="#sec-1-1-9">1.1.9. user authentication</a></li>
<li><a href="#sec-1-1-10">1.1.10. <span class="todo OPEN">OPEN</span> big red button</a></li>
<li><a href="#sec-1-1-11">1.1.11. <span class="done DONE">DONE</span> text to speech command&#xa0;&#xa0;&#xa0;<span class="tag"><span class="_irq0">@irq0</span></span></a></li>
<li><a href="#sec-1-1-12">1.1.12. <span class="done DONE">DONE</span> irc bot&#xa0;&#xa0;&#xa0;<span class="tag"><span class="_irq0">@irq0</span></span></a></li>
<li><a href="#sec-1-1-13">1.1.13. Notify sink</a></li>
<li><a href="#sec-1-1-14">1.1.14. <span class="done DONE">DONE</span> 433MHz actor&#xa0;&#xa0;&#xa0;<span class="tag"><span class="_irq0">@irq0</span></span></a></li>
<li><a href="#sec-1-1-15">1.1.15. <span class="todo OPEN">OPEN</span> jabber bot</a></li>
<li><a href="#sec-1-1-16">1.1.16. <span class="todo OPEN">OPEN</span> mail bot</a></li>
<li><a href="#sec-1-1-17">1.1.17. <span class="todo OPEN">OPEN</span> dmx actor&#xa0;&#xa0;&#xa0;<span class="tag"><span class="c3po">c3po</span></span></a></li>
<li><a href="#sec-1-1-18">1.1.18. <span class="todo ASSIGNED">ASSIGNED</span> actor service / rule engine&#xa0;&#xa0;&#xa0;<span class="tag"><span class="_irq0">@irq0</span></span></a></li>
<li><a href="#sec-1-1-19">1.1.19. <span class="todo ASSIGNED">ASSIGNED</span> openhab integration&#xa0;&#xa0;&#xa0;<span class="tag"><span class="_snowball">@snowball</span></span></a></li>
<li><a href="#sec-1-1-20">1.1.20. <span class="todo OPEN">OPEN</span> irc reader</a></li>
<li><a href="#sec-1-1-21">1.1.21. <span class="todo OPEN">OPEN</span> music player daemon&#xa0;&#xa0;&#xa0;<span class="tag"><span class="c3po">c3po</span></span></a></li>
<li><a href="#sec-1-1-22">1.1.22. <span class="todo OPEN">OPEN</span> calendar integration - ics?</a></li>
</ul>
</li>
<li><a href="#sec-1-2">1.2. Architecture Changes</a>
<ul>
<li><a href="#sec-1-2-1">1.2.1. <span class="todo ASSIGNED">ASSIGNED</span> list, help messages for 'cmd' exchange&#xa0;&#xa0;&#xa0;<span class="tag"><span class="_irq0">@irq0</span></span></a></li>
<li><a href="#sec-1-2-2">1.2.2. <span class="todo IDEA">IDEA</span> state change exchange?</a></li>
</ul>
</li>
<li><a href="#sec-1-3">1.3. Project Name</a>
<ul>
<li><a href="#sec-1-3-1">1.3.1. Subtitle?</a></li>
</ul>
</li>
</ul>
</li>
<li><a href="#sec-2">2. Documentation</a>
<ul>
<li><a href="#sec-2-1">2.1. Glossary</a></li>
<li><a href="#sec-2-2">2.2. Well-defined Exchanges</a>
<ul>
<li><a href="#sec-2-2-1">2.2.1. msg</a></li>
<li><a href="#sec-2-2-2">2.2.2. cmd</a></li>
<li><a href="#sec-2-2-3">2.2.3. notify</a></li>
<li><a href="#sec-2-2-4">2.2.4. <code>act_433mhz</code>&#xa0;&#xa0;&#xa0;<span class="tag"><span class="private">private</span></span></a></li>
<li><a href="#sec-2-2-5">2.2.5. subinit&#xa0;&#xa0;&#xa0;<span class="tag"><span class="private">private</span></span></a></li>
</ul>
</li>
<li><a href="#sec-2-3">2.3. Software, Libs, etc.</a>
<ul>
<li><a href="#sec-2-3-1">2.3.1. Debian packages</a></li>
<li><a href="#sec-2-3-2">2.3.2. docker</a></li>
<li><a href="#sec-2-3-3">2.3.3. Useful libraries</a></li>
</ul>
</li>
<li><a href="#sec-2-4">2.4. Development</a>
<ul>
<li><a href="#sec-2-4-1">2.4.1. Repository Organization</a></li>
<li><a href="#sec-2-4-2">2.4.2. External Documentation</a></li>
<li><a href="#sec-2-4-3">2.4.3. Libraries</a></li>
</ul>
</li>
</ul>
</li>
</ul>
</div>
</div>


# Ideas, Todos

## Features

### OPEN User Notifications

-   Im LDAP gibt es eine liste mit wegen einen user zu notifien
    -   IRC nick
    -   jabber id
    -   twitter account (@foo)
    -   email
-   Notifications werden "reliable" zugestellt. Irgendwo kommt die
    notification an
-   Message exchange und consumer sagen nack, wenn nicht zustellbar.
    Z.B. IRC offline
-   Aehlich wie die notify exchange, audio fuer shouts in den subraum
-

### ASSIGNED pizza / essen / f00d     :@hej:c3po:

### DONE scheduled messages     :@irq0:

-   hourly audio messages
-   web gui?
-   clojure + quarz scheduler?

Implementation:
cronjob + amqp-tools + mp3 files

mp3 files found on cube..

### TEST presence: eta login     :@irq0:

Commands: !ul, !eta, !login, !logout
-   cmd exchange consumer/producer
-   store login, eta state somewhere

Implemented:

### OPEN guess commands     :c3po:

-   see `thomas.py`, `pr.py` auf cube

-   aus normalem text informationen gewinnen
-   In etwa "mach mal licht an" -> "cmd bulb on"

### OPEN hubelmeter     :c3po:

### DONE shutdown/startup     :@irq0:

Veralgemeinert implementiert: Init mit runlevels.

Reagiert auf Commands:

-   **telinit:** Runlevel ändern
-   **runlevel:** Aktuelles runlevel zurückgeben

Emitiert Messages auf in der `subinit` Exchange.
Format: `rc.RUNLEVEL.ACTION`

Runleveländerungen (z.B 0 -> 4) generieren Events: 1 start, 2 start, 3
start, 4 start.

Runlevels sind dazu gedacht, um den Subraum auch nur "halb"
anzuschalten zu können. Beispielsweise ohne Mamestation.

1.  Tool: subinit-rc

    Tool um für subinit Messages Scripts zu starten. Aufgebaut wie rc\*.d
    runlevel scripts.

    Skripts werden mit run-parts gestartet und bekommen die ACTION als
    ersten Parameter

### OPEN subraum init/shutdown auf subinitd migrieren

### user authentication

-   irc nick <-> subraum LDAP?
-   ueberhaupt noetig?

1.  ASSIGNED irc bot antwortet nur auf op     :@irq0:

    -   bot: only answer to users having op? (TODO)

### OPEN big red button

-   hardware button loest 'bigredbutton' command aus?

-   Oder: Es können ja durchaus mehrere dinge einen big red button gebrauchen

p

-   Vielleich ein button exchange einrichten auf dem verschiedene dienste
    lauschen können?
-   Mehrere Buttons?
-   Prototyp: Button exchange, Button an raspberry pie?

1.  Story

    Pizza Bestellung endet in 5 minuten. Countdown läuft. Stoppen? Drück
    den button irgendwo im Raum. Zahlenkombination eingeben? Button an der
    Decke?
    -   Bei der Pizza Bestellung angeben? Nur stoppbar durch eingeben von
        31337 auf'm PIN Pad?
        -   Pizza daemon wartet auf button 31337 messages..

### DONE text to speech command     :@irq0:

-   listen for tts, say, fortune commands
-   text to speech messages
-   put mp3 files in notify exchange with key audio

Actually two implementations. One pico2wave in the EDI repo and one
based on the old acapella-group web scripting.

### DONE irc bot     :@irq0:

-   IRC receive -> msg exchange with key irc.recv.raw
-   msg exchange with key irc.send.raw -> IRC send

### Notify sink

1.  text

    `routing_key=text` messages.

    1.  DONE libnotify sink     :@irq0:

    2.  OPEN text notifications on projector

2.  audio

    `routing_key=audio` messages.

    1.  DONE mplayer sink     :@irq0:

        shell one-liner with amqp-tools

3.  OPEN uri

    `routing_key=uri` messages.

    Idea: Play media URIs in messages. Sinilar to the mplayer listener on cube.

### DONE 433MHz actor     :@irq0:

`act_433mhz` exchange
-   consumer on raspberrypi
-   message payload = commandline arguments to rcswitch tool

### OPEN jabber bot

-   user same msg exchange as irc bot

-   Possible routing keys: "jabber.recv.raw" "jabber.send.raw"

### OPEN mail bot

-   wie jabber bot nur ueber email
-   nuetzlich auch fuer den notify: user service
-   unauthenticated mail?!

### OPEN dmx actor     :c3po:

See `cube:/var/git/c3po/dmx`. DMX is connected to the serial port.

Example code:

    [2014-02-06 13:45:04] less dmx-disable.py

     #!/usr/bin/python

     import sys
     import serial

     ser = serial.Serial('/dev/dmx', 38400, timeout=1)

     ser.write("B1")

     ser.close()

There is also a dmx jsonrpc server:
`cube:/var/git/c3po/jsonrpcdmx`

### ASSIGNED actor service / rule engine     :@irq0:

currently a simple python script to map things like 'act bulb on' to
messages on the `act_433_mhz` queue

Idealy something with a rule engine:

-   First user logged in: initiate startup sequence.
-   Last user log out initiate

In the basic incarnation:
Map 'act' messages to actors. *act* messages are something a user
can grasp, e.g *act venti on*. actors are something specific having
their own actor exchanges, e.g *act<sub>433</sub><sub>mhz</sub>* where messages contain
the commands for the sender as payload.

1.  Idee

    -   Jedes event transformiert den aktuellen system state in einen neuen
        (clojure swap! semantik)
    -   Ändern des systemstates stösst die rule engine an
    -   Regeln verändern den state nicht (direkt). Können aber events
        emiten.
    -   State änderungen sind atomar. Ein event verändert. Andere events
        warten die änderungen ab. Änderungen sind ganz oder garnicht.
    -   Rule engine ausführungen immer auf neuen state. Rule engine
        ausführungen sind unabhängig voneinander
    -   Was ist mit aktoren?
        -   State änderung muss irgendwie auch aktoren triggern können..
        -   Hm.
        -   State change funktionen für bestimmte events?
            -   führen auch aktionen aus?

        -   should-be relation:
            -   event sagt "an", state sagt "aus" -> an aktion generieren
            -   event sagt "an", state sagt "an" -> nop

                    EVENT -> OLD STATE -> STATE CHANGE -> NEW STATE
                                           -> ACTIONS

                    EVENT -> OLD STATE -> STATE CHANGE -> NEW STATE
                                                       -> DIFFERENCE OLD NEW
                                                       -> ACTIONS
    -   Fakten, konfiguration
        -   aktor name zu triggernes foo
        -   'act bulb on' -> msg `11111 1 on` an `act_433mhz` exchange.

    -   `(state-change old)`

### ASSIGNED openhab integration     :@snowball:

### OPEN irc reader

1.  assign voices to each participant

    1.  parameters

        -   speed
        -   pitch
        -   voice: lea, julia, kenny&#x2026;

2.  participants can change voices

### OPEN music player daemon     :c3po:

-   mpd commands als messages
-   Story: Ein EDI MQ command kann verschiedene music player daemons steuern
-   Probleme
    -   Mehrere mpds unterstützen; gleichzeitig steuern?

### OPEN calendar integration - ics?

-   Repeadedly parse calendar files. Idealy ics. Load from caldav?
    google calendar?

1.  Variants

    1.  Calendar Commands

        -   Im Kallender stehen edi commands. Diese zu den eingestellten Zeiten
            injecten.

        Quasi alternative zu CRON.

        irq0: Damit koennte ich mir meinen Wecker bauen..

    2.  Events

        -   **Event:** Something is going to happen at a point in time. Wie das
            digitale Zeitalter..

        Per TTS, Text notification, IRC, Jabber whatever hinweisen

## Architecture Changes

### ASSIGNED list, help messages for 'cmd' exchange     :@irq0:

Everyone on the cmd exchange should consume list and help messages.

1.  Replies

    -   **help:** If "args" = "$0" : Reply with brief usage and supported commands
    -   **list:** Reply with something like "I exist and my name is"

2.  Destination

        (str/replace (:src msg) #"recv" "send")

3.  Status

    -   The newer commands have this build in. Works fine.

### IDEA state change exchange?

Ohne globalen state müssen state veränderungen irgendwie kommuniziert
werden. Beispiel: user loggt sich ein.

Beispiel:

-   user loggt sich ein
-   tts begrüssung triggern
-   rule engine wertet systemzustand aus

Mögliche umsetzung
*st* exchange. User presence manager sendet message mit "userloggedin"
oder so an den exchange.

Ein event->tts consumer generiert tts commands wenn nötig

Die rule engine verändert ihren systemzustand und wertet rules neu aus.

## Project Name

-   **EDI:** ++
-   **ESI:** Enhanced Subraum Intelligence?

### Subtitle?

-   The hacker (friendly) space automation?

# Documentation

The core of the architecture is the rabbitmq amqp message server.
Every pice of code connects in some way to it.

Most services share a couple of well defined exchanges. See the
2.2 for a description.

## Glossary

-   **source:** Apps that only/mainly produce messages
-   **sink:** Apps that only/mainly consume messages
-   **processor:** Apps that transform messages. Consume -> Produce.
-   **bot:** Consumer/Producer that add external/foreign interfaces to the
    system. Like IRC.

## Well-defined Exchanges

![img](//git.c3pb.de/c3pb/subraum-automatisierung/blob/master/doc/exchanges.jpeg)

### msg

Raw messages received from somewhere. This should be something that
can be parsed to a command.

Type: topic

1.  Routing Keys

    In general: protocol.bot-name.{send,recv,presence}.channel
    -   irc.EDI.recv.#c3pb.sh
    -   irc.EDI.send.#c3pb.sh
    -   irc.EDI.presence

2.  Messages

    1.  #.send.\*

        Content-Type: application/json
        -   **msg:** Message body
        -   **user:** Destination user

        Content-Type: text/plain
        body: Message

    2.  #.recv.\*

        Content-Type: application/json
        -   **msg:** Message body
        -   **user:** Message sender

3.  Processors

    1.  parse-commands.py

        Transform `!<command>` to **cmd** Messages. (See **cmd** Exchange)

4.  Bots

    1.  IRC Bot - mqbot.py

        IRC -> MQ, MQ -> IRC

5.  Sinks

6.  Sources

### cmd

Messages that do something :)

Type: topic

1.  Known routing Keys

    1.  TTS

        -   tts
        -   say
        -   forune

    2.  Actor Service

        -   act

    3.  subinit

        -   telinit
        -   runlevel

    4.  thehonestbookoftruth

        -   login
        -   logout
        -   logout-all
        -   ul
        -   eta
        -   uneta

    5.  What every command should implement:

        -   list
        -   help

2.  Messages

    Content-Type: application/json
    -   **cmd:** Usually the same as the routing key when parsed from **msg**
        Messages. Could be different. Not sure why I include it. The
        clojure tools use the to dispatch handlers..
    -   **args:** Argument string.
    -   **user:** User that send the command. The command may use this to log.
    -   **src:** Command origin. Replies will be send here with the word
        *recv* replaced by *send*. If the src is invalid replies will
        just vanish :)

3.  Sources

4.  Sinks

5.  Processors

    1.  tts

        Transform *tts* **cmd** Messages to notification audio messages.

        Text -> Audio file.

    2.  Simple Actor Service - act.py

        Map *act* commands to actors.

        Example:
        venti on => 433Mhz sender, payload 11111 1 1

        See `act_433mhz` exchange for the 433Mhz actor implementation.

### notify

**Sink** exchage for notifications.

1.  Routing Keys

    -   audio
    -   text

2.  Sinks

    1.  mplayer one-liner

            amqp-consume --url="amqp://mopp" --exchange="notify" --routing-key="audio" mplayer -

3.  Messages

    Content-Type depending on exchange keys. Should be directly usable by
    the sink (e.g mp3 file to hand over to mplayer).

### `act_433mhz`     :private:

**Sink** exchange to signal 433mhz transmitter.

Type: fanout

1.  Messages

    Commandline arguments for \`rcswitch-pi\`.

2.  Sinks

### subinit     :private:

**Sink** exchange for subinit messages

Type: topic

1.  Messages

    Content-type: text/plain

    Must always contain the same as the routing key.

2.  Sinks

    1.  subinit-rc

        Launch scripts on subinit messages consumed. Feel similar to sysvinit
        scripts and runlevels

## Software, Libs, etc.

### Debian packages

-   rabbitmq-server (debian testing ist aktuell genug)
-   python-pika
-   python-amqplib
-   amqp-tools

### docker

For development docker seemes a good choice:

    sudo docker run -p :5672 -p :15672 -v /scratch/docker-data/rabbitmq:/var/lib/rabbitmq/mnesia f04150b0661e
    sudo docker build github.com/mikaelhg/docker-rabbitmq.git

Note that the exchanges are configured by hand..

Use `mopp`, running on the dell netbook.

### Useful libraries

## Development

Install requirements. Setup exchanges in rabbitmq. The web interfaces
comes in handy here ;)

### Repository Organization

-   **src:** Tools that only **publish** messages
-   **sink:** Tools that only **consume** messages
-   **proc:** Tools that **consume** and **publish** with some kind of
    processing going on
-   **bot:** Adapter to other protocols like IRC. **publisher** and **consumer**
-   **demo:** Useful stuff for testing, reference, whatever

Most larger tools are subtree merged from elsewhere. This repo is kind
of the collected deployment branch.

Have something to add? Let me pull your repo!

### External Documentation

-   [Must read rabbitmq tutorial - covers all the basic use cases](http://www.rabbitmq.com/getstarted.html)

### Libraries

1.  Python

    -   **pika:** <http://pika.readthedocs.org/en/latest/> Documented, Async lib
    -   **amqplib:** simpler non-threaded library; documentation shipped in
        the .py files. Which are quite readable ;)

2.  Commandline

    -   **amqp-tools:** Make sure you get the recent ones. Debian testing
        works quite well. Debian stable not so.

3.  Clojure

    -   **langohr:** <http://clojurerabbitmq.info/> Excellent library.
