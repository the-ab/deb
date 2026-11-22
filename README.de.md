# the-ab APT-Repository

[English](README.md)

Gemeinsame signierte APT-Quelle **https://the-ab.github.io/deb/**.

## Client-Konfiguration

ODROID-Images ab 1.0.1 enthalten Archivschlüssel und APT-Quelle bereits. Bei einer anderen Installation den öffentlichen Schlüssel herunterladen und vor dem Einrichten prüfen.

```sh
curl -fsSLo the-ab-archive-keyring.gpg https://the-ab.github.io/deb/the-ab-archive-keyring.gpg
gpg --show-keys --with-fingerprint the-ab-archive-keyring.gpg
# Erwartet: E853 46CA 2461 E1FA 45AC 7C7C D85B C090 497C E8B9
sudo install -m 644 the-ab-archive-keyring.gpg /usr/share/keyrings/the-ab-archive-keyring.gpg
```

Auf einem ODROID-U3 mit `armhf` die Quelle speichern unter `/etc/apt/sources.list.d/the-ab-odroid-u3.sources`:

```text
Types: deb
URIs: https://the-ab.github.io/deb/
Suites: stable
Components: main u3
Architectures: armhf
Signed-By: /usr/share/keyrings/the-ab-archive-keyring.gpg
```

Anschließend `sudo apt update` ausführen. Komponente und Architektur passend zum System wählen. Updates und Wiederherstellung für ODROID-U3 beschreibt die [Kernelupdate-Anleitung](https://github.com/the-ab/ODROID/blob/main/docs/KERNEL-UPDATES.de.md).
