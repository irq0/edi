(ns thehonestbookoftruth.state
  (:use [clj-time.coerce :only [to-date from-date]]
        [clj-time.local :only [local-now]])
  (:require [clojure.java.io :as io]
            [taoensso.timbre :as timbre]
            [clojurewerkz.serialism.core :as s]))

(timbre/refer-timbre)

(def ^:dynamic *db-file* (or (System/getenv "EDI_ETA_FILE") "/tmp/eta.edn"))

(def ^:dynamic *db* (atom {}))

(defn persist-db! [_ _ _ data]
  (info (str "[STATE] DB saved to " *db-file*))
  (spit *db-file* (s/serialize data s/clojure-content-type)))

(defn log-db-changes [_ _ old new]
  (info (str "[STATE] Old db: " old))
  (info (str "[STATE] New db: " new)))

(defn- load-db []
  (s/deserialize (slurp *db-file*) s/clojure-content-type))

(defn init-from-file! []
  (if (.exists (io/as-file *db-file*))
    (reset! *db* (load-db))
    (reset! *db* {:user {}}))
  (info (str "[STATE] Initialized db: " @*db*)))

(defn init-watches []
  (add-watch *db* :persist persist-db!)
  (add-watch *db* :log log-db-changes))

(defn logged-in? [user]
  (boolean (:ts ((:user @*db*) user))))

(defn has-eta? [user]
  (boolean (:eta ((:user @*db*) user))))

(defn logout! [user]
  (info (str "[STATE] Logout: " user))
  (swap! *db* (fn [old] (assoc-in old [:user user] nil))))

(defn clear!
  "Remove entries having :eta or login :ts set"
  []
  (info (str "[STATE] Clear all ETAs and logins"))
  (swap! *db* #(assoc % :user (into {} (filter (complement (fn [[_ data]] (or (:eta data) (:ts data)))) (:user %))))))

(defn logout-all! []
  (info (str "[STATE] Logout: ALL"))
  (swap! *db* #(assoc % :user (into {} (filter (complement (fn [[_ data]] (:ts data))) (:user %))))))

(defn login! [user]
  (info (str "[STATE] Login: " user))
  (swap! *db* (fn [old]
              (-> old
                (assoc-in [:user user :ts] (to-date (local-now)))
                (assoc-in [:user user :eta] nil)))))

(defn set-eta! [user ^org.joda.time.DateTime eta]
  (info (str "[STATE] Set ETA: " user " " eta))
  (swap! *db* (fn [old] (assoc-in old [:user user] {:eta (to-date eta)}))))

(defn unset-eta! [user]
  (info (str "[STATE] Unset ETA: " user))
  (swap! *db* (fn [old] (assoc-in old [:user user :eta] nil))))

(defn get-login-time [user]
  (from-date (:ts ((:user @*db*) user))))
