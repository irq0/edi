(ns thehonestbookoftruth.state-test
  (:require [clojure.test :refer :all]
            [clj-time.core :as tc]
            [thehonestbookoftruth.state :refer :all]))

(defn with-mock-db
  [f]
  (let [*db* (atom {})]
    (f)))

(use-fixtures :each with-mock-db)

(deftest login-test
  (let [usr "Malaclypse_the_Younger"]
      (login! usr)
      (is (logged-in? usr))
      (is (not (has-eta? usr)))))

(deftest logout-test
  (let [usr "Malaclypse_the_Younger"]
    (testing "login logout"
      (login! usr)
      (is (logged-in? usr))
      (logout! usr)
      (is (not (logged-in? usr))))))

(deftest eta-test
  (let [usr "Malaclypse_the_Younger"
        eta (tc/date-time 2000 5 20 20 00)]
    (testing "set eta"
      (set-eta! usr eta)
      (is (has-eta? usr))
      (unset-eta! usr)
      (is (not (has-eta? usr))))

    (testing "login removes eta"
      (set-eta! usr eta)
      (login! usr)
      (is (not (has-eta? usr))))

    (testing "logged in = no eta"
      (login! usr)
      (is (not (has-eta? usr)))
      (logout! usr)
      (is (not (has-eta? usr))))))

(deftest clear-test
  (let [usrs ["a" "b" "c"]
        eta (tc/date-time 2000 5 20 20 00)]
    (testing "login some users, clear, db should be clean afterwards"
      (doseq [u usrs]
        (login! (str "login_" u)))
      (doseq [u usrs]
        (set-eta! (str "eta_" u) eta))
      (clear!)
      (doseq [u usrs]
        (is (not (has-eta? (str "eta_" u))))
        (is (not (logged-in? (str "login_" u)))))
      (is (empty? (:user @*db*))))))
