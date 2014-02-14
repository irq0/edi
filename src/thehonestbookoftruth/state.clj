(ns thehonestbookoftruth.state
  (:use [clj-time.coerce :only [to-date from-date]]
        [clj-time.local :only [local-now]])
  (:require [clojure.java.io :as io]
            [taoensso.timbre :as timbre]
            [clojurewerkz.serialism.core :as s]))

(timbre/refer-timbre)

(def ^:dynamic *db-file* "/tmp/eta.edn")

(def ^:dynamic *db* (atom {}))

(defn persist-db! [_ _ _ data]
  (info "DB saved")
  (spit *db-file* (s/serialize data s/clojure-content-type)))

(defn log-db-changes [_ _ old new]
  (info (str "Old db: " old))
  (info (str "New db: " new)))

(defn- load-db []
  (s/deserialize (slurp *db-file*) s/clojure-content-type))

(defn init-from-file! []
  (reset! *db* (load-db))
  (info (str "Initialized db from file: " @*db*)))

(defn init-watches []
  (add-watch *db* :persist persist-db!)
  (add-watch *db* :log log-db-changes))

(defn logged-in? [user]
  (boolean (:ts (@*db* user))))

(defn has-eta? [user]
  (boolean (:eta (@*db* user))))

(defn logout! [user]
  (swap! *db* (fn [old] (dissoc old user))))

(defn login! [user]
  (swap! *db* (fn [old]
              (-> old
                (assoc-in [user :ts] (to-date (local-now)))
                (assoc-in [user :eta] nil)))))

(defn set-eta! [user ^org.joda.time.DateTime eta]
  (swap! *db* (fn [old] (assoc old user {:eta (to-date eta)}))))

(defn unset-eta! [user]
  (swap! *db* (fn [old] (assoc-in old [user :eta] nil))))
