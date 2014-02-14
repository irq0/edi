(ns thehonestbookoftruth.handler
  (:use [clj-time.local :only [local-now]]
        [thehonestbookoftruth.util :only [parse-eta format-eta format-time-span format-user-list]])
  (:require [thehonestbookoftruth.state :as state]
            [taoensso.timbre :as timbre]))

(timbre/refer-timbre)

(def help "thehonestbookoftruth: login logout ul eta uneta help")
(def listtxt "thehonestbookoftruth: Presence, ETA")

(defmulti handler
  (fn [args] (keyword (args :cmd))))

(defmethod handler :list [_]
  listtxt)

(defmethod handler :help
  [{:keys [args]}]

  (when (= args "thehonestbookoftruth")
    help))

(defmethod handler :ul [_]
  (format-user-list @state/*db*))

(defmethod handler :login
  [{:keys [user]}]

  (if (state/logged-in? user)
    (str "Already logged in!")
    (and (state/login! user) (str "Hi, " user))))

(defmethod handler :logout
  [{:keys [user]}]

  (if (state/logged-in? user)
    (and (state/logout! user) (str "Cya " user))
    "Hmm, you are not logged in. So no logout ;)"))

(defmethod handler :eta
  [{:keys [user args]}]

  (if (state/logged-in? user)
    "Logged in. I'll ignore the ETA :P"
    (try
      (let [eta (parse-eta args)
            span (format-time-span (local-now) eta)]
        (and (state/set-eta! user eta)
          (str "Cya in " span " minutes")))
      (catch java.lang.IllegalArgumentException e
        (str "Hmpf. \"" args "\" isn't a valid ETA")))))

(defmethod handler :uneta
  [{:keys [user]}]

  (if (state/has-eta? user)
    (and (state/unset-eta! user)
      "Schade :(")
    "No ETA set :P"))

(defmethod handler :default [args]
  (error "Command not supported")
  "unsupported")
