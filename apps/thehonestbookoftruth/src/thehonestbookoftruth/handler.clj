(ns thehonestbookoftruth.handler
  (:use [clj-time.local :only [local-now]]
        [clj-time.coerce :only [to-date]]
        [clojurewerkz.serialism.core :as s]
        [thehonestbookoftruth.util :only [parse-eta format-eta format-time-span format-user-list]])
  (:require [thehonestbookoftruth.state :as state]
            [thehonestbookoftruth.emit :as emit]
            [taoensso.timbre :as timbre]))

(timbre/refer-timbre)

(defmulti handler
  (fn [_ args] (keyword (args :cmd))))

(defmethod handler :inspect [ch {:keys [src user]}]
  (let [data {:app "thehonestbookoftruth"
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
        json (emit/jsonify data)]

    (emit/msg-reply ch src
      :data data
      :user user
      :msg json)))

(defmethod handler :ul [ch {:keys [src user]}]
  (let [db (:user @state/*db*)
        ul (format-user-list db)
        reply (if (empty? ul)
                "No ETAs or Logins :("
                ul)]
    (emit/msg-reply ch src
      :user user
      :msg reply
      :data db)))

(defmethod  handler :login [ch {:keys [user src]}]
  (if (state/logged-in? user)
    (str "Already logged in!")
    (and
      (state/login! user)
      (do
        (emit/cmd ch
          :cmd "ev.login"
          :args nil
          :user user
          :src src)
        "Hi!"))))

(defmethod handler :logout [ch {:keys [user src]}]
  (if (state/logged-in? user)
    (let [span (format-time-span (state/get-login-time user) (local-now))]
      (and
        (state/logout! user)
        (do
          (emit/cmd ch
            :cmd "ev.logout"
            :args nil
            :user user
            :data {:span span}
            :src src)
          (str "Cya. You subraumed for " span " mins" ))))
    "Hmm, you are not logged in. So, no logout ;)"))

(defmethod handler :clear-all-etas-and-logins [_]
  (state/clear!))

(defmethod handler :eta [ch {:keys [user args src]}]
  (if (state/logged-in? user)
    "Logged in. I'll ignore that ETA :P"
    (try
      (let [eta (parse-eta args)
            span (format-time-span (local-now) eta)]
        (and
          (state/set-eta! user eta)
          (do
            (emit/cmd ch
              :cmd "ev.eta-set"
              :args (str (format-eta eta) " [" span " min]")
              :user user
              :data {:eta (to-date eta)}
              :src src)
            (str "Cya in " span " minutes"))))
      (catch java.lang.IllegalArgumentException e
        (error e "ETA failed:")
        (str "Hmpf. \"" args "\" isn't a valid ETA")))))

(defmethod handler :uneta [ch {:keys [user src]}]
  (if (state/has-eta? user)
    (and
      (state/unset-eta! user)
      (do
        (emit/cmd ch
          :cmd "ev.eta-unset"
          :args nil
          :user user
          :src src)
        "Schade :("))
    "No ETA set :P"))

(defmethod handler :default [ch args]
  (error "Command not supported"))
