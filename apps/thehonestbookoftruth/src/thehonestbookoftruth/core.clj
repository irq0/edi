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
            [thehonestbookoftruth.state :as state])
  (:gen-class))

(timbre/refer-timbre)

(defn reply [ch orig reply]
  (let [dst (str/replace (:src orig) #"recv" "send")
        msg (s/serialize {:user (:user orig) :msg reply} :json)]
    (info (format "---> Handler reply orig_msg=%s key=%s: %s" orig dst msg))
    (lb/publish ch "msg" dst msg :content-type "application/json")))

(defn message-handler [ch {:keys [content-type delivery-tag] :as meta} ^bytes payload]
  (info (format "<--- Received message: %s, content type: %s"
          (String. payload "UTF-8") content-type))

  (when (= content-type "application/json")
    (try
      (let [msg (s/deserialize payload :json)
            result (handler msg)]
        (when-not (empty? result)
          (reply ch msg result)))
      (catch com.fasterxml.jackson.core.JsonParseException e
        (error "[HANDLER] json decode failed :("))
      (catch Exception e
        (error e))))
  (lb/ack ch delivery-tag))


(defn amqp-url [& args]
  (let [server (or (first args) (System/getenv "AMQP_SERVER") "localhost")]
    (str "amqp://" server)))

(defn -main [& args]
  (let [url   (amqp-url args)
        conn  (rmq/connect {:uri url})
        ch    (lch/open conn)
        keys  ["login" "logout" "logout-all" "ul" "eta" "uneta" "inspect"]
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
