# the-ab APT-Repository

[English](README.md)

Gemeinsame signierte APT-Quelle **https://the-ab.github.io/deb/**. Aktueller ODROID-U3-Serverkernel: **7.3.1-odroidu3-v32 / 7.3.1-33**, Werkzeuge **1.0.3**. Der vorherige Kernel **7.3.1-odroidu3-v3 / 7.3.1-4**, sein Metapaket und die Werkzeuge bleiben für Rückfälle im Pool erhalten. [Aktuelles Paket-/Quellmanifest](publications/u3-server-2026-11-06.json) · [Passende Quellen](https://github.com/the-ab/ODROID/releases/tag/u3-kernel-7.3.1-33).

Komponenten: `main` für gemeinsame Pakete, `u3` für ODROID-U3. Erste Architektur: `armhf`. Einrichtung und Pflegebefehle stehen vollständig in der [englischen Anleitung](README.md). Für U3 beschreibt die [Kernelupdate-Anleitung](https://github.com/the-ab/ODROID/blob/main/docs/KERNEL-UPDATES.de.md) die Boardwerkzeuge, den erfolgreichen echten Paketwechsel/Rückfall und Wiederherstellung.

ODROID-Images ab 1.0.1 enthalten Archivschlüssel und APT-Quelldatei bereits. Öffentlicher Fingerabdruck: `E85346CA2461E1FA45AC7C7CD85BC090497CE8B9`. Dies ist kein SSH-Zugangsschlüssel. Keine privaten Signaturschlüssel in Git ablegen und die Signaturprüfung nicht umgehen.

Weitere Projekte erhalten eigene Komponenten in `repository.json` und passende Architekturlisten. Gemeinsames `main` bei Bedarf um diese Architekturen erweitern. Geprüfte freigegebene DEBs nach `pool/KOMPONENTE/` kopieren, vorhandene Versionen und fremde Komponenten erhalten, Listen mit `scripts/build-repository.py` signieren und vor dem Push prüfen. Große Images und Quellarchive bleiben in den Produkt-Releases. Das Erstellen eines Repositories oder neuer Images veröffentlicht keine Pakete automatisch.

Auf Ubuntu 26.04 armhf ODROID-U3: `sudo apt update`, danach `sudo apt install linux-image-odroid-u3` und `odroid-kernel status`. Anschließend zu einem passenden Zeitpunkt neu starten. Der im Pool erhaltene vorherige Kernel heißt `linux-image-7.3.1-odroidu3-v3` (Version `7.3.1-4`). Bereits installierte Rückfallkernel lokal behalten. Kein automatischer Neustart und keine boot0-Änderung. Die Boardwerkzeuge benötigen Python 3.11 oder neuer; Ubuntu 26.04 armhf ist das unterstützte und getestete Ziel.

Werkzeuge 1.0.3 legen versionierte Dateien direkt unter `/boot` ab. Vorhandene Paketversionen niemals mit anderen Bytes überschreiben. Entfernen alter Versionen erfordert ausdrücklichen Nutzerumfang und geprüften Ersatz; installierte Clientkernel werden dadurch nicht gelöscht.
