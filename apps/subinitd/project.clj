(defproject edinitd "0.1.0-SNAPSHOT"
  :description "FIXME: write description"
  :url "http://example.com/FIXME"
  :license {:name "Eclipse Public License"
            :url "http://www.eclipse.org/legal/epl-v10.html"}
  :main subinitd.core
  :aot [subinitd.core]
  :dependencies [[org.clojure/clojure "1.5.1"]
                 [com.novemberain/langohr "2.3.2"]
                 [com.taoensso/timbre "3.0.1"]
                 [clojurewerkz/serialism "1.0.1"]])
