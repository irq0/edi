(defproject thehonestbookoftruth "0.1.0"
  :description "EDI MQ User presence, eta, etc. "
  :url "https://git.c3pb.de/irq0/thehonestbookoftruth"
  :main thehonestbookoftruth.core
  :aot [thehonestbookoftruth.core]
  :dependencies [[org.clojure/clojure "1.6.0"]
                 [com.novemberain/langohr "2.9.0"]
                 [clj-time "0.6.0"]
                 [com.taoensso/timbre "3.2.1"]
                 [clojurewerkz/serialism "1.2.0"]])
