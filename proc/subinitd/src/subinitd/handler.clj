(ns subinitd.handler
  (:use [subinitd.runlevel :only [runlevel telinit!]])
  (:require [taoensso.timbre :as timbre]))

(timbre/refer-timbre)

(def help "subinitd: telinit runlevel")
(def listtxt "subinit: Subraum initd - sysvinit like")

(defmulti handler
  (fn [args] (keyword (args :cmd))))

(defmethod handler :list [_]
  listtxt)

(defmethod handler :help
  [{:keys [args]}]

  (when (= args "subinitd")
    help))


(defmethod handler :telinit
  [{:keys [user args]}]

  (try
    (let [to (Integer/parseInt args)
          from (telinit! to)]
      (info (format "Runlevel change to %s initated by %s" to user))
      (if (= to from)
        (format "SUBINIT: unchanged")
        (format "SUBINIT: %s->%s" from to)))

    (catch Exception e
      (format "SUBINIT: \"%s\" not a number :(" args))))


(defmethod handler :runlevel
  [_]
  (format "SUBINIT: %s" @runlevel))


(defmethod handler :default [args]
  (error "Command not supported")
  "unsupported")
