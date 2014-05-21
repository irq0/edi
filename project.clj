(defproject pizzamaschine "0.1.0-SNAPSHOT"
  :description "FIXME: write description"
  :url "http://example.com/FIXME"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}
  :main pizzamaschine.core
  :aot [pizzamaschine.core]
  :dependencies [[org.clojure/clojure "1.5.1"]
                 [com.novemberain/langohr "2.8.2"]
                 [cheshire "5.3.1"] ; We don't need this anymore. I think.
                 [org.clojure/data.json "0.2.4"]
                 ])
