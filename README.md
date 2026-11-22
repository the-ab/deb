# the-ab APT repository

[Deutsch](README.de.md)

Shared signed APT repository at **https://the-ab.github.io/deb/**.

## Client configuration

ODROID images from 1.0.1 already include the keyring and source entry. For another installation, download and inspect the public key before installing it:

```sh
curl -fsSLo the-ab-archive-keyring.gpg https://the-ab.github.io/deb/the-ab-archive-keyring.gpg
gpg --show-keys --with-fingerprint the-ab-archive-keyring.gpg
# Expected: E853 46CA 2461 E1FA 45AC 7C7C D85B C090 497C E8B9
sudo install -m 644 the-ab-archive-keyring.gpg /usr/share/keyrings/the-ab-archive-keyring.gpg
```

On an appropriate armhf U3 system, save this as `/etc/apt/sources.list.d/the-ab-odroid-u3.sources`:

```text
Types: deb
URIs: https://the-ab.github.io/deb/
Suites: stable
Components: main u3
Architectures: armhf
Signed-By: /usr/share/keyrings/the-ab-archive-keyring.gpg
```

Run `sudo apt update`. Select the component and architecture for your system. For ODROID-U3 updates and recovery, see the [kernel update guide](https://github.com/the-ab/ODROID/blob/main/docs/KERNEL-UPDATES.md).
