(ns hubelmeter.classifier
  (:require [judgr.core     :as jc]
            [judgr.settings :as js]
            [judgr.db.base  :as jb]

            [clojure.string    :as str]
            [clojure.data.json :as json]))

(defprotocol Persistence
  (store-state [db])
  (load-state [db]))

(deftype PersistentDB [settings items features]
  Persistence
  (store-state [db]
    (let [path  (-> settings :database :path)
          state (dosync (json/write-str {:items (vector @items)
                                         :features (hash @features)}))]
      (try
        (spit path state)
        (catch Exception e
          (println (format "Failed to write state to %s: %s"
                           path (.getMessage e)))))))

  (load-state [db]
    (let [path (-> settings :database :path)
          state (try
                 (json/read-str (slurp path))
                 (catch Exception e
                   (println "Could not read from" path ":" (.getMessage e))
                   {:items [] :features {}}))]
      (dosync
        (ref-set items (:items state))
        (ref-set features (:features state)))))

  jb/FeatureDB
  (add-item! [db item class]
    (jb/ensure-valid-class
      settings class
      (let [data {:item item :class class}]
        (dosync (alter items conj data))
        (store-state db)
        data)))

  (clean-db! [db]
    (dosync
      (ref-set items [])
      (ref-set features {}))
    (store-state db))

  (add-feature! [db item feature class]
    (jb/ensure-valid-class
      settings class
      (let [f (.get-feature db feature)
            r (if (nil? f)
                (let [data {:feature features
                            :total 1
                            :classes {class 1}}]
                  (dosync (alter features assoc feature data))
                  data)
                (let [total-count (or (-> f :total) 0)
                      class-count (or (-> f :classes class) 0)
                      data (assoc-in (assoc f :total (inc total-count))
                                     [:classes class] (inc class-count))]
                  (dosync (alter features assoc feature data))
                  data))]
        (store-state db)
        r)
      ))

  (get-feature [db feature]
    (try
      (@features feature)
      (catch Exception e
        nil)))

  (count-features [db]
    (count @features))

  (get-items [db]
    @items)

  (count-items [db]
    (count @items))

  (count-items-of-class [db class]
    (count (filter #(= (:class %) class) @items)))
)

(defmethod jc/db-from :persistent [settings]
  (let [items (ref [])
        features (ref {})
        db (PersistentDB. settings items features)]
    (.load-state db)
    db))

(defn make-classifier [path]
  (let [s (js/update-settings js/settings
                              [:database :path] path
                              [:database :type] :persistent)
        c (jc/classifier-from s)]
    ; Bootstrap classifier
    (.train-all! c ["jemand" "muesste" "man"] :negative)
    (.train-all! c ["ich" "?"] :positive)
    c))

(defn probabilities [classifier msg]
  (.probabilities classifier msg))

(defn learn! [classifier msg category]
  (if (> (.length msg) 0)
    (do
      (.train! classifier msg category)
      true)
    false))

(defn classify [classifier msg]
  (.classify classifier msg))
