# the-ab APT-Repository

[English](README.md)

Gemeinsame signierte Paketquelle unter **https://the-ab.github.io/deb/** für ODROID und weitere Projekte. GitHub Pages stellt `main` aus dem Wurzelverzeichnis bereit; `.nojekyll` erhält die APT-Struktur. Zunächst sind die signierten Paketlisten leer. Binärpakete werden nach der Abnahme und Freigabe des jeweiligen Produkts veröffentlicht.

Komponenten: `main` für gemeinsame Pakete, `u3` für ODROID-U3. Erste Architektur: `armhf`. Einrichtung und Pflegebefehle stehen vollständig in der [englischen Anleitung](README.md). Für U3 beschreibt die [Kernelupdate-Anleitung](https://github.com/the-ab/ODROID/blob/codex/u3-ubuntu26-v1/docs/KERNEL-UPDATES.de.md) die Boardwerkzeuge und die noch offene echte Paketupdate-Abnahme.

ODROID-Images ab 1.0.1 enthalten Archivschlüssel und APT-Quelldatei bereits. Öffentlicher Fingerabdruck: `E85346CA2461E1FA45AC7C7CD85BC090497CE8B9`. Dies ist kein SSH-Zugangsschlüssel. Keine privaten Signaturschlüssel in Git ablegen und die Signaturprüfung nicht umgehen.

Weitere Projekte erhalten eigene Komponenten in `repository.json` und passende Architekturlisten. Gemeinsames `main` bei Bedarf um diese Architekturen erweitern. Geprüfte freigegebene DEBs nach `pool/KOMPONENTE/` kopieren, vorhandene Versionen und fremde Komponenten erhalten, Listen mit `scripts/build-repository.py` signieren und vor dem Push prüfen. Große Images und Quellarchive bleiben in den Produkt-Releases. Das Erstellen eines Repositories oder neuer Images veröffentlicht keine Pakete automatisch.
