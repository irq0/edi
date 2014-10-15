(ns hubelmeter.constants)

(def +warnings+
  '("Hubeln entfernt Ihre Gesundheit."
    "Hubler sterben früher."
    "Hubeln kann tödlich sein."
    "Hubeln lässt ihre Haut altern."
    "Hubeln kann die Spermatozoen schädigen und schränkt die Fruchtbarkeit ein."
    "Hubeln in der Schwangerschaft schadet Ihrem Kind."
    "Schützen Sie Kinder – lassen Sie sie nicht Ihr Rumgehubel hören!"
    "Hubeln macht sehr schnell abhängig: Fangen Sie gar nicht erst an!"
    "Wer das Hubeln aufgibt, verringert das Risiko tödlicher Prokrastination."
    "Hubeln kann zu einem langsamen und schmerzhaften Tod führen."
    "Hubeln kann die Spermatozoen schädigen und schränkt die Fruchtbarkeit ein."
    "Hubeln fügt ihnen und den Nerds in ihrer Umgebung erheblichen Schaden zu."
    ))

(defn get-warning []
  (rand-nth +warnings+))
