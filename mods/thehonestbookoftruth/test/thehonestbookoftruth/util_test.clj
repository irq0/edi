(ns thehonestbookoftruth.util-test
  (:require [clojure.test :refer :all]
            [thehonestbookoftruth.util :refer :all]
            [clj-time.core     :as tc]
            [clj-time.coerce   :as to]
            [clj-time.local    :as tl]
            [clj-time.format   :as tf]))


(deftest parse-eta-tests
  (testing "Parse ETAs"
    (let [date (tl/to-local-date-time (tc/today-at 23 42 00))
          tests ["2342" "23:42" "234200" "23:42:00"]]
      (doseq [t tests]
        (is (= (parse-eta t) date))))))


(deftest eta-format-tests
  (testing "Format ETA"
    (let [eta (tl/to-local-date-time (tc/today-at 23 42 00))]
      (is (= (format-eta eta) "23:42"))))
  (testing "Format time span"
    (let [a (tl/to-local-date-time (tc/today-at 10 42 00))
          b (tl/to-local-date-time (tc/today-at 20 42 00))]
      (testing "Valid time spans"
        (is (= (format-time-span a b) (* 10 60)))
        (is (= (format-time-span b a) (* 10 60)))))))


(deftest ul-format-tests
  (let [with-eta {"Malaclypse_the_Younger"
                  {:eta (to/to-date (tc/date-time 2000 5 20 20 00))}}
        with-ts  {"Malaclypse_the_Older"
                  {:ts (to/to-date (tc/date-time 1941 5 21 20 00 00))}}
        now      (tl/local-now)]

  (testing "User with ETA"
    (is (= (format-user-list with-eta)
          (format "%s (%s: %s [%s min])" "Malaclypse_the_Younger" "ETA"
            (format-eta (tc/date-time 2000 5 20 20 00))
            (str (tc/in-minutes (tc/interval (tc/date-time 2000 5 20 20 00) now)))))))))
