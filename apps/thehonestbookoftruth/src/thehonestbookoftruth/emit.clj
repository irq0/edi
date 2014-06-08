(ns thehonestbookoftruth.emit
  (:require [clojure.string    :as str]
            [langohr.basic     :as lb]
            [taoensso.timbre :as timbre]
            [clojurewerkz.serialism.core :as s]))

(timbre/refer-timbre)

(defn jsonify [x]
  (s/serialize x :json))

(defn cmd [ch &{:as body}]
  {:pre [(contains? body :cmd) (contains? body :args)]}

  (let [json (jsonify body)]
    (debug (format "---> CMD[%s]: orig=%s json=%s" (:cmd body) body json))
    (lb/publish ch "cmd" (:cmd body) json :content-type "application/json")))


(defn msg [ch dst &{:as body}]
  {:pre [(contains? body :msg)]}

  (let [json (jsonify body)]
    (debug (format "---> MSG[%s]: orig=%s json=%s" dst body json))
    (lb/publish ch "msg" dst json :content-type "application/json")))


(defn msg-reply [ch src &{:as body}]
  {:pre [(contains? body :msg) (re-matches #".*\.recv\..*" src)]}

  (let [dst (str/replace src #"recv" "send")
        json (jsonify body)]
    (debug (format "---> MSG REPLY[%s]: orig=%s json=%s" dst body json))
    (lb/publish ch "msg" dst (jsonify body) :content-type "application/json")))
