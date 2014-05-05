(ns subinitd.core
  (:require [subinitd.mq :as mq]
            [langohr.core      :as rmq]
            [taoensso.timbre :as timbre]
            [subinitd.runlevel :as rl])
  (:gen-class))

(timbre/refer-timbre)

(defn -main [& args]
  (let [url   (or (System/getenv "AMQP_URL") "amqp://localhost")
        conn  (rmq/connect {:uri url})
        rl    (Integer/parseInt (or (first args) (System/getenv "SUB_RUNLEVEL") "0"))]
    (rl/-init rl conn)
    (mq/-run conn)
    (rl/-shutdown)
    (rmq/close conn)))
