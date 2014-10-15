# hubelmeter

Hubelmeter plugin for the benevolent almighty Subraum AI. Analyzes all messages
on the `msg` exchange with a naive Bayes classifier and yells at sources that
produce messages that are deemed 'hubelig', that is, making excessive use of
unspecific pronouns and conjunctive.

## Usage

Set the environment variable `EDI_HUBEL_FILE` to the path of a json file that stores the hubel score, and set `EDI_HUBEL_CLASSIFIER` to the path of a json file that stores the state of the bayes classifier. Then set `AMQP_SERVER` to the AMQP server to be used and start the service with the service file in `sv/run`.

Unless set, the environment variables have the following values:

    AMQP_SERVER=amqp://mopp
    EDI_HUBEL_CLASSIFIER=/tmp/hubel-classifier.json
    EDI_HUBEL_FILE=/tmp/hubel-score.json

## License

Copyright © 2014 Gregor Best, <gbe@unobtanium.de>

Distributed under the ISC license.
