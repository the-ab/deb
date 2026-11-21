# the-ab APT-Repository

[English](README.md)

Gemeinsame signierte APT-Quelle **https://the-ab.github.io/deb/**. Aktueller ODROID-U3-Serverkernel: **7.3.1-odroidu3-v32 / 7.3.1-33**, Werkzeuge **1.0.3**. Der vorherige Kernel **7.3.1-odroidu3-v3 / 7.3.1-4**, sein Metapaket und die Werkzeuge bleiben für Rückfälle im Pool erhalten. [Aktuelles Paket-/Quellmanifest](publications/u3-server-2026-11-06.json) · [Passende Quellen](https://github.com/the-ab/ODROID/releases/tag/u3-kernel-7.3.1-33).

Komponenten: `main` für gemeinsame Pakete, `u3` für ODROID-U3 (`armhf`) und `nas-manager` für NAS-iGPU-Abhängigkeiten (`amd64`, zusätzlich architekturunabhängige Header). Einrichtung und Pflegebefehle stehen vollständig in der [englischen Anleitung](README.md). Für U3 beschreibt die [Kernelupdate-Anleitung](https://github.com/the-ab/ODROID/blob/main/docs/KERNEL-UPDATES.de.md) die Boardwerkzeuge, den erfolgreichen echten Paketwechsel/Rückfall und Wiederherstellung.

ODROID-Images ab 1.0.1 enthalten Archivschlüssel und APT-Quelldatei bereits. Öffentlicher Fingerabdruck: `E85346CA2461E1FA45AC7C7CD85BC090497CE8B9`. Dies ist kein SSH-Zugangsschlüssel. Keine privaten Signaturschlüssel in Git ablegen und die Signaturprüfung nicht umgehen.

Weitere Projekte erhalten eigene Komponenten in `repository.json` und passende Architekturlisten. Gemeinsames `main` bei Bedarf um diese Architekturen erweitern. Geprüfte freigegebene DEBs nach `pool/KOMPONENTE/` kopieren, vorhandene Versionen und fremde Komponenten erhalten, Listen mit `scripts/build-repository.py` signieren und vor dem Push prüfen. Große Images und Quellarchive bleiben in den Produkt-Releases. Das Erstellen eines Repositories oder neuer Images veröffentlicht keine Pakete automatisch.

Auf Ubuntu 26.04 armhf ODROID-U3: `sudo apt update`, danach `sudo apt install linux-image-odroid-u3` und `odroid-kernel status`. Anschließend zu einem passenden Zeitpunkt neu starten. Der im Pool erhaltene vorherige Kernel heißt `linux-image-7.3.1-odroidu3-v3` (Version `7.3.1-4`). Bereits installierte Rückfallkernel lokal behalten. Kein automatischer Neustart und keine boot0-Änderung. Die Boardwerkzeuge benötigen Python 3.11 oder neuer; Ubuntu 26.04 armhf ist das unterstützte und getestete Ziel.

Werkzeuge 1.0.3 legen versionierte Dateien direkt unter `/boot` ab. Vorhandene Paketversionen niemals mit anderen Bytes überschreiben. Entfernen alter Versionen erfordert ausdrücklichen Nutzerumfang und geprüften Ersatz; installierte Clientkernel werden dadurch nicht gelöscht.

NAS-Manager: [Paket-/Quell-/Lizenzmanifest](publications/nas-manager-dependencies-2026-11-15.json).
Die sechs unveränderten Originalpakete ersetzen sieben Git-LFS-Pfade. Der
kanonische Installer registriert die signierte `main nas-manager`-Quelle für
`amd64` und installiert `nas-manager-igpu-host` beziehungsweise
`nas-manager-igpu-guest`. Nach dieser einmaligen Umstellung genügen für später
veröffentlichte geprüfte Paketstände `sudo apt update` und `sudo apt upgrade`.
Die Metapakete nehmen auch neue Kernelpaketnamen mit. Rückfallkernel erhalten,
Neustart gezielt planen und danach die bisherigen Hardwareprüfungen ausführen.
Die NAS-Anwendung bleibt im kanonischen Installerweg.

Fünf originale NAS-Abhängigkeiten und beide Metapakete liegen direkt in
`pool/nas-manager/`. Das 161,6 MiB große Kernelpaket und die zugehörigen
Quellarchive werden mit exakten SHA256-Pins aus dem bestehenden GitHub-Release
in die signierte Pages-Veröffentlichung übernommen.
Die normale Git-Poolgrenze von 95 MiB bleibt bestehen. Die manuell ausgelöste
Workflow-Veröffentlichung bindet sich an den geprüften vollständigen Main-SHA;
der begrenzte `deb-pages`-Runner benötigt weder privaten Archivschlüssel noch
Zugang zu NAS oder ODROID und kann nach dem Lauf entfernt werden.

## NAS Manager Clean-Install-Prüfpaket

Das Paket `nas-manager-setup` stellt eine Testinstallation für einen frischen
Proxmox-Host mit Debian-VM100 bereit. APT installiert Git, Git LFS und die
weiteren Voraussetzungen mit. Das Setup verwendet eine bereits vorhandene,
gleichwertige signierte Quelle weiter. Auf einem frisch eingerichteten Host
oder Gast legt es die Quelldatei unter diesem Namen an.

`/etc/apt/sources.list.d/the-ab.sources`

```text
Types: deb
URIs: https://the-ab.github.io/deb/
Suites: stable
Components: main nas-manager
Architectures: amd64
Signed-By: /usr/share/keyrings/the-ab-archive-keyring.gpg
```

Der öffentliche Schlüsselbund liegt im Wurzelverzeichnis dieses APT-Archivs.
Seinen Fingerabdruck vor dem Einrichten der Quelle mit dem oben genannten Wert
abgleichen. Die separat bereitgestellte Entsperrdatei gehört mit Modus `0600`
nach `/root/nas-manager-setup.key`.

```sh
apt update
apt install nas-manager-setup=0.5.10~apt-test.8
nas-manager-setup --unlock-file /root/nas-manager-setup.key
```

Nach einem APT-Upgrade den Setup-Befehl erneut ausführen. Der Starter prüft den verifizierten Git-Nachfolger und übernimmt einen sauberen Checkout.

Nach der Host-Übergabe folgt in VM100 `/root/setup-guest.sh`.
Das Paket startet bei der APT-Installation keine VM und führt keinen
Neustart aus. Der private Installer-Quellstand liegt verschlüsselt vor.
