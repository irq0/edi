(ns edi-test.core
  (:require [langohr.core :as rmq]
            [langohr.channel :as lch]
            [langohr.queue :as lq]
            [langohr.consumers :as lc]
            [langohr.basic :as lb]
            [clojure.data.json :as json]))

(defn make-url []
  (get (System/getenv)
       "CLOUDAMQP_URL" "amqp://guest:guest@mopp"))

(defn make-reply [msg]
  "ich würd mich ja um deine Pizza kümmern, aber ich hab grad Lack getrunken :/")

(defn message-handler
  [ch {:keys [content-type delivery-tag] :as meta} ^bytes payload]
  (let [msg (json/read-str (String. payload "UTF-8")
                           :key-fn keyword)
        dst (.replace (:src msg) "recv" "send")
        reply (make-reply msg)]
    (println
      (str "[recv] " msg))
    (lb/publish ch "msg" dst (json/write-str {:user (:user msg) :msg reply}) :content-type "application/json")
    (lb/ack ch delivery-tag)))

(defn setup
  ([] (setup false))
  ([blocking]
    (let [conn  (rmq/connect {:uri (make-url)})
          ch    (lch/open conn)
          qname (:queue (lq/declare ch))
          exchange "cmd"
          keys ["pizza"]]
      (doseq [k keys]
        (println "Binding to " exchange "/" k)
        (lq/bind ch qname exchange :routing-key k))
      (if blocking
        (lc/blocking-subscribe ch qname #'message-handler)
        (lc/subscribe ch qname #'message-handler))
      [conn ch])))

(comment
  (rmq/close (first *conn*))
  (def ^:dynamic *conn* (setup)))

(defn -main [& args]
  (let [conn (setup)]
    (rmq/close (second conn))
    (rmq/close (first conn))
    ))
