(ns thehonestbookoftruth.util
  (:use [clj-time.coerce :only [from-date]]
        [clj-time.local :only [local-now to-local-date-time]])
  (:require [clj-time.core     :as time]
            [clojure.string    :as str]
            [clj-time.format   :as tf]))

(declare format-eta)

(defn- expand-special-etas [x]
  (if (some #{(str/upper-case x)} ["SOON" "GLEICH" "BALD"])
    (format-eta (time/plus (local-now) (time/minutes 43)))
    x))

(defn parse-eta [x]
  (let [eta (expand-special-etas x)
        date (tf/unparse (tf/formatter "yyyyMMdd" (time/default-time-zone)) (time/now))
        form ["yyyyMMdd HHmm"
              "yyyyMMdd HHmmss"
              "yyyyMMdd HH:mm"
              "yyyyMMdd HH:mm:ss"]]

    (to-local-date-time
      (tf/parse (apply tf/formatter (time/default-time-zone) form) (str date " " eta)))))

(defn format-eta [^org.joda.time.DateTime d]
  (tf/unparse (tf/formatter "HH:mm" (time/default-time-zone)) d))

(defn format-time-span [^org.joda.time.DateTime a ^org.joda.time.DateTime b]
  (let [to   (or (and (time/after? a b) a) b)
        from (or (and (time/after? a b) b) a)]
    (try
      (let [span (time/in-minutes (time/interval from to))]
        (if (time/after? b a)
          (+ span)
          (- span)))
    (catch java.lang.IllegalArgumentException _))))

(defmacro swallow-exceptions [& body]
    `(try ~@body (catch Exception e#)))

(defn- format-ul-time [kind user time]
  (let [date (format-eta (from-date time))
        span (format-time-span (local-now) (from-date time))]
  (format "%s (%s: %s [%s])"
    user
    kind
    date
    (if (pos? span)
      (str "in " span " min")
      (str (- span) " min ago")))))

(defn- format-ul-user [[user vals]]
  (let [{:keys [eta ts]} vals]
    (cond
      eta (format-ul-time "ETA" user eta)
      ts (format-ul-time "SINCE" user ts))))

(defn format-user-list [users]
  (apply str
    (interpose ", "
      (filter (complement str/blank?)
        (map format-ul-user users)))))
