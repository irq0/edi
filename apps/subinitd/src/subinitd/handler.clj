(ns subinitd.handler
  (:use [subinitd.runlevel :only [runlevel telinit!]]
        [clojurewerkz.serialism.core :as s])
  (:require [taoensso.timbre :as timbre]))

(timbre/refer-timbre)

(def help "subinit: telinit runlevel")
(def listtxt "subinit: Subraum initd - sysvinit like")

(defmulti handler
  (fn [args] (keyword (args :cmd))))

(defmethod handler :inspect [_]
  (s/serialize
    {:app "subinitd"
     :descr "Subraum distributed init system"
     :cmds {:runlevel {:args  "NONE",
                 :descr "Return current runlevel"
                 :attribs {}}
            :telinit {:args [0 1 2 3 4 5]
                      :descr "Switch runlevel"
                      :attribs {}}}}
    :json))

(defmethod handler :telinit
  [{:keys [user args]}]

  (try
    (let [to (Integer/parseInt args)
          from (telinit! to)]
      (info (format "Runlevel change to %s initated by %s" to user))
      (if (= to from)
        (format "SUBINIT: unchanged")
        (format "SUBINIT: %s->%s" from to)))

    (catch NumberFormatException e
      (format "SUBINIT: \"%s\" not a number :(" args))))


(defmethod handler :runlevel
  [_]
  (format "SUBINIT: %s" @runlevel))


(defmethod handler :default [args]
  (error "Command not supported")
  "unsupported")
