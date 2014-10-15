(defproject hubelmeter "1"
  :description "Hubelmeter for the benevolent almighty subraum AI"
  :url "https://git.c3pb.de/gbe/hubelmeter"
  :license {:name "ISC License"
            :url "http://en.wikipedia.org/wiki/ISC_license" }
  :main hubelmeter.core
  :aot [hubelmeter.core]
  :dependencies [[org.clojure/clojure "1.6.0"]
                 [com.novemberain/langohr "2.8.2"]
                 [org.clojure/data.json "0.2.4"]
                 [judgr "0.3.0"]])
