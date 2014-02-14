(ns thehonestbookoftruth.handler
  (:use [clj-time.local :only [local-now]]
        [clj-time.coerce :only [to-date from-date]]
        [clj-time.core :as t :only [interval in-minutes]]
        [thehonestbookoftruth.util :only [parse-eta format-eta format-time-span]])
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

(defn- format-ul-user [[user vals]]
  (let [{:keys [eta ts]} vals]
    (cond
      eta (str user " (ETA: " (format-eta (from-date eta))
            " [" (format-time-span (local-now) (from-date eta)) " min])")
      ts (str user " (SINCE: " (format-eta (from-date ts))
           " [" (format-time-span (from-date ts) (local-now)) " min])"))))


(defmethod handler :ul [_]
  (apply str
    (interpose ", "
      (map format-ul-user @state/db))))

(defmethod handler :login
  [{:keys [user]}]
  (if (:ts (@state/db user))
    (str "Already logged in!")
    (do
      (swap! state/db (fn [old]
                        (-> old
                          (assoc-in [user :ts] (to-date (local-now)))
                          (assoc-in [user :eta] nil))))
      (str "Hi, " user))))

(defmethod handler :logout
  [{:keys [user]}]
  (if (:ts (@state/db user))
    (swap! state/db (fn [old] (dissoc old user)))
    "Hmm, you are not logged in. So no logout ;)"))

(defmethod handler :eta
  [{:keys [user args]}]
  (if (:ts (@state/db user))
    "Logged in. I'll ignore the ETA :P"
    (try
      (let [eta (parse-eta args)
            span (format-time-span (local-now) eta)]
        (swap! state/db (fn [old] (assoc old user {:eta (to-date eta)})))
        (str "Cya in " span " minutes"))
      (catch java.lang.IllegalArgumentException e
        (str "Hmpf. \"" args "\" isn't a valid ETA")))))

(defmethod handler :uneta
  [{:keys [user]}]
  (if (:eta (@state/db user))
    (do
      (swap! state/db (fn [old] (assoc-in old [user :eta] nil)))
      "Schade")
    "No ETA"))

(defmethod handler :default [args]
  (error "Command not supported")
  "unsupported")
