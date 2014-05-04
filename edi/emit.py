def cmd(chan, **body):
    assert(all(x in body for x in ["cmd", "args"]))

    log.info("---> CMD[%r]: %r", body["cmd"] , body)

    jbody = json.dumps(body)
    chan.basic_publish(exchange="cmd",
                       routing_key=body["cmd"],
                       body=jbody,
                       properties=pika.BasicProperties(
                           content_type="application/json",
                           delivery_mode=2))

def msg(chan, dst, **body):
    assert(all(x in body for x in ["msg"]))

    log.info("---> MSG[%r]: %r", key, msg)

    jbody = json.dumps(body)
    chan.basic_publish(exchange="msg",
                       routing_key=dst,
                       body=jbody,
                       properties=pika.BasicProperties(
                           content_type="application/json",
                           delivery_mode=2))

def msg_reply(chan, src, **body):
    assert("recv" in src)
    dst = src.replace("recv", "send")

    msg(chan, dst, **body)
