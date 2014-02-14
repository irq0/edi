(ns thehonestbookoftruth.core
  (:use [thehonestbookoftruth.handler :only [handler]])
  (:require [langohr.core      :as rmq]
            [langohr.channel   :as lch]
            [langohr.queue     :as lq]
            [langohr.consumers :as lc]
            [langohr.basic     :as lb]
            [clojure.string    :as str]
            [taoensso.timbre :as timbre]
            [clojurewerkz.serialism.core :as s]
            [thehonestbookoftruth.state :as state]))

(timbre/refer-timbre)

(defn reply [ch msg reply]
  (let [dst (str/replace (:src msg) #"recv" "send")]
    (info (format "---> Handler reply orig_msg=%s key=%s: %s" msg dst reply))
    (lb/publish ch "msg" dst (str reply) :content-type "text/plain")))

(defn message-handler [ch {:keys [content-type delivery-tag] :as meta} ^bytes payload]
  (info (format "<--- Received message: %s, content type: %s"
          (String. payload "UTF-8") content-type))

  (when (= content-type "application/json")
    (try
      (let [msg (s/deserialize payload :json)]
        (reply ch msg (handler msg)))
      (catch com.fasterxml.jackson.core.JsonParseException e
        (error "[HANDLER] json decode failed :("))))
  (lb/ack ch delivery-tag))


(defn -main [& args]
  (let [url   (or (first args) (System/getenv "AMQP_URL") "amqp://localhost")
        conn  (rmq/connect {:uri url})
        ch    (lch/open conn)
        keys  ["login" "logout" "ul" "eta" "uneta" "help" "list"]
        ex    "cmd"
        qname (:queue (lq/declare ch))]


    (state/init-from-file!)
    (state/init-watches)

    (info (format "[MAIN] Connected. Channel id: %d" (.getChannelNumber ch)))

    (doseq [k keys]
      (lq/bind ch qname ex :routing-key k))

    (lc/blocking-subscribe ch qname message-handler)

    (info "[MAIN] Disconnecting...")

    (rmq/close ch)
    (rmq/close conn)))
