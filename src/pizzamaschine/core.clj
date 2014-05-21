;;;; Pizza plugin for the benevolent Subraum-AI
;;;; TODO:
;;;; - i18n? Maybe not.

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

(defn now []
  (java.util.Date.))

(def +help-message+
  (str
    "!pizza-reset      -- Leert die Liste mit Bestellungen\n"
    "!pizza-list       -- Listet Bestellungen\n"
    "!pizza-help       -- Diese Nachricht\n"
    "!pizza $something -- Bestellt $something"))

(def +orders+ (ref '{}))
(def +first-order+ (ref ""))
(def +started-by+ (ref ""))

(defn list-orders []
  (let [f @+first-order+]
    (if (empty? f)
      "Keine Bestellungen :/"
      (str
        "Bestellungen (gestartet: " f " von " @+started-by+ "):\n"
        (apply str
               (interpose "\n"
                           (map #(str (first %) ": " (second %))
                                @+orders+)))))))

(defn handle-request [msg]
  (let [args (:args msg)
        user (:user msg)]
    (cond
      (= args "-reset")
      (dosync
        (let [o (list-orders)]
          (alter +orders+ (fn [x] '{}))
          (str o
               (when-not (empty? @+first-order+)
                 (alter +first-order+ (fn [x] ""))
                 "\nBestelliste wurde geleert."))))
      (or (= args "-list")
          (empty? args))
      (dosync
        (list-orders))
      (or (= args "-help")
        (.startsWith args "-"))
      +help-message+
      :else
      (dosync
        (when (empty? @+first-order+)
          (alter +first-order+ #(str (now)))
          (alter +started-by+ (fn [x] user)))
        (alter +orders+ #(assoc % user args))
        (str "Ack: "
          args)))))

(defn message-handler
  [ch {:keys [content-type delivery-tag] :as meta} ^bytes payload]
  (let [msg (json/read-str (String. payload "UTF-8")
                           :key-fn keyword)
        dst (.replace (:src msg) "recv" "send")
        reply (handle-request msg)]
    (println
      (str "[recv] " msg))
    (lb/publish ch "msg" dst
                (json/write-str {:user (:user msg) :msg reply})
                :content-type "application/json")
    (lb/ack ch delivery-tag)))

(defn setup
  ([] (setup false))
  ([blocking]
    (let [conn  (rmq/connect {:uri (make-url)})
          ch    (lch/open conn)
          qname (:queue (lq/declare ch))
          exchange "cmd"
          keys ["pizza" "pizza-reset" "pizza-list" "pizza-help"]]
      (doseq [k keys]
        (println "Binding to" exchange "/" k)
        (lq/bind ch qname exchange :routing-key k))
      (if blocking
        (lc/blocking-subscribe ch qname #'message-handler)
        (lc/subscribe ch qname #'message-handler))
      {:conn conn :channel ch})))

(comment
  (rmq/close (:conn *conn*))
  (def ^:dynamic *conn* (setup))
)

(defn -main [& args]
  (let [conn (setup true)]
    (rmq/close (:channel conn))
    (rmq/close (:conn conn))
    ))
