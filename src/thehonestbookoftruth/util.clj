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

(defn format-eta [d]
  (tf/unparse (tf/formatter "HH:mm" (tc/default-time-zone)) d))

(defn format-time-span [a b]
  (try
    (tc/in-minutes (tc/interval a b))
    (catch java.lang.IllegalArgumentException _)))
