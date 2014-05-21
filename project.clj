(defproject pizzamaschine "0.3"
  :description "Pizza order collection service for the benevolent Subraum AI"
  :url "https://git.c3pb.de/gbe/pizzamaschine"
  :license {:name "ISC"
            :url "http://en.wikipedia.org/wiki/ISC_license"}
  :main pizzamaschine.core
  :aot [pizzamaschine.core]
  :dependencies [[org.clojure/clojure "1.5.1"]
                 [com.novemberain/langohr "2.8.2"]
                 [org.clojure/data.json "0.2.4"]
                 ])
