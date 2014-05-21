;;;; Pizza plugin for the benevolent Subraum-AI
;;;; TODO:
;;;; - i18n? Maybe not.

(ns pizzamaschine.core
  (:require [langohr.core :as rmq]
            [langohr.channel :as lch]
            [langohr.queue :as lq]
            [langohr.consumers :as lc]
            [langohr.basic :as lb]
            [clojure.data.json :as json])
  (:gen-class))

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
  (dosync
  (let [f @+first-order+]
    (if (empty? f)
      "Keine Bestellungen :/"
      (str
        (apply str
               (interpose "\n"
                           (map #(str (first %) ": " (second %))
                                @+orders+)))
        "\n(gestartet: " f " von " @+started-by+ ")\n"
        )))))

(defn add-order [user order]
  (dosync
    (when (empty? @+first-order+)
      (alter +first-order+ (fn [x] (str (now))))
      (alter +started-by+ (fn [x] user)))
    (alter +orders+ #(assoc % user order))
    (str "Ack: "
         order)))

(defn dispatch-command [msg]
  (let [args (:args msg)
        user (:user msg)
        cmd  (:cmd msg)]
    (cond
      (= cmd "pizza-reset")
      (dosync
        (let [o (list-orders)]
          (alter +orders+ (fn [x] '{}))
          (str o
               (when-not (empty? @+first-order+)
                 (alter +first-order+ (fn [x] ""))
                 "\nBestelliste wurde geleert."))))
      (= cmd "pizza-list")
      (list-orders)
      (or (= cmd "pizza-help")
          (empty? args))
      +help-message+
      :else
      (add-order user args))))

(defn message-handler
  [ch {:keys [content-type delivery-tag] :as meta} ^bytes payload]
  (let [msg (json/read-str (String. payload "UTF-8")
                           :key-fn keyword)
        dst (.replace (:src msg) "recv" "send")
        reply (dispatch-command msg)]
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
