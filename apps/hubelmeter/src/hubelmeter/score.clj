(ns hubelmeter.score
  (:require
    [clojure.data.json :as json]))

(def +hubel-data+ (ref '{}))
(def +state-path+ (or (System/getenv "EDI_HUBEL_FILE") "/tmp/hubel-score.json"))

(defn store
  ([] (store +state-path+))
  ([path]
   (try
     (dosync
       (spit path (str (json/write-str @+hubel-data+)))
       true)
     (catch Exception e
       (println (str "Could not store state in " path ":\n"
                     (.getMessage e)))
       false))))

(defn load!
  ([] (load! +state-path+))
  ([path]
   (dosync
     (try
       (let [data (json/read-str (slurp path))]
         (alter +hubel-data+
                (fn [x] data))
         true)
       (catch Exception e
         (println (str "Could not load state from " path ":\n"
                       (.getMessage e)))
         false)))))

(defn inc-datapoint! [user item]
  (dosync
    (alter +hubel-data+
           #(let [userdata (get % user {})]
              (assoc % user
                     (assoc userdata item
                            (inc (get userdata item 0))))))
    (store)))

(defn inc-hubel! [user]
  (inc-datapoint! user :hubel))

(defn inc-linecount! [user]
  (inc-datapoint! user :lines))

(defn get-score [user]
  ; according to cmile, a score >= 1 leads to hubelplosion. Be careful.
  (dosync
    (let [data (get @+hubel-data+ user {})]
      (float (/ (get data :hubel 0)
                (get data :lines 1))))))
