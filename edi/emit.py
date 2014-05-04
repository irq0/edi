import logging
import json
import amqplib.client_0_8 as amqp

log = logging.getLogger("edi.emit")

def cmd(chan, **body):
    assert(all(x in body for x in ["cmd", "args"]))

    log.info("---> CMD[%r]: %r", body["cmd"] , body)

    jbody = json.dumps(body)

    msg = amqp.Message(jbody.encode("utf-8"))
    msg.properties["content_type"] = u"application/json"
    msg.properties["delivery_mode"] = 2
    msg.properties["app_id"] = u"edilib"

    chan.basic_publish(exchange="cmd",
                       routing_key=body["cmd"],
                       msg=msg)

def msg(chan, dst, **body):
    assert(all(x in body for x in ["msg"]))

    log.info("---> MSG[%r]: %r", key, msg)

    jbody = json.dumps(body)
    msg = amqp.Message(jbody.encode("utf-8"))
    msg.properties["content_type"] = u"application/json"
    msg.properties["delivery_mode"] = 2
    msg.properties["app_id"] = u"edilib"

    chan.basic_publish(exchange="msg",
                       routing_key=dst,
                       msg=msg)

def msg_reply(chan, src, **body):
    assert("recv" in src)
    dst = src.replace("recv", "send")

    msg(chan, dst, **body)
