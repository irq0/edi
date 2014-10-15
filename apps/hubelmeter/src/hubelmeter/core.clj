(ns hubelmeter.core
  (:require [langohr.core      :as rmq]
            [langohr.channel   :as lch]
            [langohr.queue     :as lq]
            [langohr.consumers :as lc]
            [langohr.basic     :as lb]
            [langohr.exchange  :as le]

            [clojure.string    :as str]
            [clojure.data.json :as json]

            [hubelmeter.constants  :as hc]
            [hubelmeter.classifier :as hcl]
            [hubelmeter.score      :as hs])
  (:gen-class))

(defn make-url []
  (str "amqp://" "mopp"))

(defn make-url []
  (let [server (or (System/getenv "AMQP_SERVER") "127.0.0.1")]
    (println (str "Using amqp server " server))
    (str "amqp://" server)))

(defn make-classifier-path []
  (let [path (or (System/getenv "EDI_HUBEL_CLASSIFIER") "/tmp/hubel-classifier.json")]
    (println "Using classifier path" path)
    path))

(defn emit-msg-reply [ch src &{:as body}]
  {:pre [(contains? body :msg) (re-matches #".*\.recv\..*" src)]}
  (println (str "[send] src=" src " body=" body))
  (let [dst  (str/replace src #"recv" "send")
        json (json/write-str body)]
    (lb/publish ch "msg" dst json :content-type "application/json")
 ))

(defn is-hubelig? [c msg]
  (= (hcl/classify c msg)
     :negative))

(defn- mark-hubelig! [c items]
  (if (hcl/learn! c items :negative)
    "ACK"
    "What?"))

(defn- mark-unhubelig! [c items]
  (if (hcl/learn! c items :positive)
    "ACK"
    "What?"))

(defn- inspect [ch msg]
  (let [data {:app "hubelmeter"
              :descr "yeah"
              :cmds {:hubel {:args "TEXT"
                             :descr "Learns TEXT as hubelig"
                             :attribs {}}
                     :unhubel {:args "TEXT"
                               :descr "Learns TEXT as unhubelig"
                               :attribs {}}
                     :hubel-check {:args "TEXT"
                                   :descr "Checks whether TEXT is hubelig"
                                   :attribs {}}}}
        json (json/write-str data)]
    (emit-msg-reply ch (:src msg)
                    :data data
                    :user (:user msg)
                    :msg json)))

(defn- dispatch-command [cl ch msg]
  (let [{:keys [args user cmd src]} msg]
    (cond
      (= cmd "hubel")
      (mark-hubelig! cl args)
      (= cmd "unhubel")
      (mark-unhubelig! cl args)
      (= cmd "hubel-check")
      (let [p (hcl/probabilities cl args)]
        (format "Goodness %.3f -- Badness %.3f -- Verdict: %s"
                (float (:positive p))
                (float (:negative p))
                (if (is-hubelig? cl args)
                  "hubelig" "unhubelig")
                ))
      (= cmd "inspect")
      (inspect ch msg))))

(defn- cmd-handler
  [classifier ch {:keys [content-type delivery-tag] :as meta} ^bytes payload]
  (let [msg (json/read-str (String. payload "UTF-8")
                           :key-fn keyword)
        reply (dispatch-command classifier ch msg)]
    (println "[cmd ]" msg)
    (emit-msg-reply ch (:src msg)
                    :msg reply
                    :user (:user msg))
    (lb/ack ch delivery-tag)))

(defn- message-handler
  [classifier ch {:keys [content-type delivery-tag routing-key] :as meta} ^bytes payload]
  (let [msg (json/read-str (String. payload "UTF-8") :key-fn keyword)]
    (println (format "[msg ] %s" (str msg)))
    (when (not (.startsWith (:msg msg) "!"))
      (hs/inc-linecount! (:user msg))
      (when (is-hubelig? classifier (:msg msg))
        (hs/inc-hubel! (:user msg))
        (emit-msg-reply ch routing-key
                        :msg (format "%s Neuer Score: %.3f"
                                     (hc/get-warning)
                                     (hs/get-score (:user msg)))
                        :user (:user msg)
                        )))))

(defn setup
  ([] (setup false))
  ([blocking]
   (let [classifier (hcl/make-classifier (make-classifier-path))

         conn     (rmq/connect {:uri (#'make-url)})

         ch-msg   (lch/open conn)
         q-msg    (:queue (lq/declare ch-msg))
         xchg-msg "msg"

         ch-cmd   (lch/open conn)
         q-cmd    (:queue (lq/declare ch-cmd))
         xchg-cmd "cmd"
         keys-cmd ["hubel" "unhubel" "hubel-check" "inspect"]]
     (le/declare ch-msg xchg-msg "topic" :auto-delete false :durable true)
     (lq/bind ch-msg q-msg xchg-msg :routing-key "#.recv.#")
     (lc/subscribe ch-msg q-msg
                   #(message-handler classifier %1 %2 %3))
     (println "bound to msg queue")

     (doseq [k keys-cmd]
       (println "Binding to" xchg-cmd "/" k)
       (lq/bind ch-cmd q-cmd xchg-cmd :routing-key k))
     ((if blocking
        lc/blocking-subscribe
        lc/subscribe)
      ch-cmd q-cmd #(cmd-handler classifier %1 %2 %3))

     conn)))

(defn stop [con]
  (rmq/close con))

(defn -main [& args]
  (let [conn (setup true)]
    (stop conn)))
