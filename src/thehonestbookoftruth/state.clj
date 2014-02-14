(ns thehonestbookoftruth.state
  (:require [clojure.java.io   :as io]
            [taoensso.timbre :as timbre]
            [clojurewerkz.serialism.core :as s]))

(timbre/refer-timbre)

(def ^:dynamic *db-file* "/tmp/eta.edn")

(def db (atom {}))

(defn persist-db! [_ _ _ db]
  (info "DB saved")
  (spit *db-file* (s/serialize db s/clojure-content-type)))

(defn log-db-changes [_ _ old new]
  (info (str "Old db: " old))
  (info (str "New db: " new)))

(defn- load-db []
  (s/deserialize (slurp *db-file*) s/clojure-content-type))

(defn init-from-file! []
  (reset! db (load-db))
  (info (str "Initialized db from file: " @db)))

(defn init-watches []
  (add-watch db :persist persist-db!)
  (add-watch db :log log-db-changes))
