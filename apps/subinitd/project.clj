(defproject edinitd "0.1.0-SNAPSHOT"
  :description "EDI init system"
  :license {:name "GPLv3"
            :url "http://www.gnu.org/licenses/gpl-3.0-standalone.html"}
  :main subinitd.core
  :aot [subinitd.core]
  :dependencies [[org.clojure/clojure "1.5.1"]
                 [com.novemberain/langohr "2.3.2"]
                 [com.taoensso/timbre "3.0.1"]
                 [clojurewerkz/serialism "1.0.1"]])
