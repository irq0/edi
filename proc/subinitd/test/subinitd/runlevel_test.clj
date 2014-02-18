(ns subinitd.runlevel-test
  (:require [clojure.test :refer :all]
            [subinitd.runlevel :refer :all]))

(deftest change-level-test
  (testing "5->2 should stop 5,4,3"
    (is (= (change-seq 5 2) (seq '([5 "stop"] [4 "stop"] [3 "stop"])))))
  (testing "2->2 should stop nothing"
    (is (= (change-seq 2 2) '())))
  (testing "2->5 should start 3,4,5"
    (is (= (change-seq 2 5) (seq '([3 "start"] [4 "start"] [5 "start"])))))
  (testing "2->2 should start nothing"
    (is (= (change-seq 2 2) '())))
  (testing "1->0 should stop 1"
    (is (= (change-seq 1 0) (seq '([1 "stop"])))))
  (testing "0->1 should start 1"
    (is (= (change-seq 0 1) (seq '([1 "start"]))))))
