(ns subinitd.runlevel
  (:require [langohr.core      :as rmq]
            [langohr.channel   :as lch]
            [langohr.queue     :as lq]
            [langohr.consumers :as lc]
            [langohr.basic     :as lb]
            [taoensso.timbre :as timbre]))

(timbre/refer-timbre)


(def subinit-exchange "subinit")

(def runlevel (atom nil))

(def chan (atom nil))


(defn change-seq [from to]
  (if (> to from)
    (for [l (range (inc from) (inc to))] [l "start"])
    (for [l (reverse (range (inc to) (inc from)))] [l "stop"])))

(defn- publish [key body]
  (lb/publish @chan subinit-exchange key body))

(defn- change-runlevel! [level state]
  (let [key (format "rc.%s.%s" level state)]
    (info (format "Publishing runlevel change: Key=%s" key))
    (publish key (str key "\n"))))


(defn telinit! [to]
  "Change runlevel. Side effects: Publishes runlevel change messages"
  (let [from @runlevel]
    (doseq [ch (change-seq from to)]
      (apply change-runlevel! ch))
    (reset! runlevel to)
    from))


(defn -init [rl conn]
  (reset! chan (lch/open conn))
  (reset! runlevel rl))

(defn -shutdown []
  (rmq/close @chan))
