(ns thehonestbookoftruth.util
  (:require [clj-time.core     :as tc]
            [clj-time.coerce   :as to]
            [clj-time.local    :as tl]
            [clj-time.format   :as tf]))

(defn parse-eta [eta]
  (let [date (tf/unparse (tf/formatter "yyyyMMdd" (tc/default-time-zone)) (tc/now))
        form ["yyyyMMdd HHmm"
              "yyyyMMdd HHmmss"
              "yyyyMMdd HH:mm"
              "yyyyMMdd HH:mm:ss"]]

    (tl/to-local-date-time
      (tf/parse (apply tf/formatter (tc/default-time-zone) form) (str date " " eta)))))

(defn format-eta [^org.joda.time.DateTime d]
  (tf/unparse (tf/formatter "HH:mm" (tc/default-time-zone)) d))

(defn format-time-span [^org.joda.time.DateTime a ^org.joda.time.DateTime b]
  (let [to   (or (and (tc/after? a b) a) b)
        from (or (and (tc/after? a b) b) a)]
    (try
      (tc/in-minutes (tc/interval from to))
    (catch java.lang.IllegalArgumentException _))))

(defmacro swallow-exceptions [& body]
    `(try ~@body (catch Exception e#)))


(defn- format-ul-time [kind user time]
  (format "%s (%s: %s [%s min])"
    user
    kind
    (format-eta (to/from-date time))
    (format-time-span (tl/local-now) (to/from-date time))))

(defn- format-ul-user [[user vals]]
  (let [{:keys [eta ts]} vals]
    (cond
      eta (format-ul-time "ETA" user eta)
      ts (format-ul-time "SINCE" user ts))))

(defn format-user-list [users]
  (apply str
    (interpose ", "
      (map format-ul-user users))))
