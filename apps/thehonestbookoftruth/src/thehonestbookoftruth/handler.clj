(ns thehonestbookoftruth.handler
  (:use [clj-time.local :only [local-now]]
        [clojurewerkz.serialism.core :as s]
        [thehonestbookoftruth.util :only [parse-eta format-eta format-time-span format-user-list]])
  (:require [thehonestbookoftruth.state :as state]
            [taoensso.timbre :as timbre]))

(timbre/refer-timbre)

(defmulti handler
  (fn [args] (keyword (args :cmd))))

(defmethod handler :inspect [_]
  (s/serialize
    {:app "thehonestbookoftruth"
     :descr "Carbon entity presence"
     :cmds {:ul {:args  "NONE",
                 :descr "Return list of logged in users and ETAs"
                 :attribs {}}
            :login {:args "NONE"
                    :descr "Login user"
                    :attribs {:user "User to log in"}}
            :logout {:args "NONE"
                     :descr "Logout user"
                     :attribs {:user "User to log out"}}
            :logout-all {:args "NONE"
                         :descr "Logout all users"
                         :attribs {}}
            :eta {:args "TIME"
                  :descr "Set ETA. Supports HHMM, HH:MM, HH:MM:SS, HHMMSS"
                  :attribs {:user "User to set ETA for"}}
            :uneta {:args "NONE"
                    :descr "Remove ETA"
                    :attribs {:user "Remove ETA from this user"}}}}
    :json))

(defmethod handler :ul [_]
  (format-user-list (:user @state/*db*)))


(defmethod  handler :login
    [{:keys [user]}]

    (if (state/logged-in? user)
      (str "Already logged in!")
      (and (state/login! user) "Hi!")))

(defmethod handler :logout
  [{:keys [user]}]

  (if (state/logged-in? user)
    (let [span (format-time-span (state/get-login-time user) (local-now))]
      (and (state/logout! user) (str "Cya. You subraumed for " span " mins" )))
    "Hmm, you are not logged in. So, no logout ;)"))

(defmethod handler :logout-all
  [_]
  (and (state/logout-all!)
    "Na, kuchen backen?"))

(defmethod handler :eta
  [{:keys [user args]}]

  (if (state/logged-in? user)
    "Logged in. I'll ignore that ETA :P"
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
