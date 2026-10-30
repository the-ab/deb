# the-ab APT repository

[Deutsch](README.de.md)

Shared signed APT repository at **https://the-ab.github.io/deb/** for ODROID and future the-ab projects. GitHub Pages serves `main` at `/`; `.nojekyll` preserves the repository layout. The tested ODROID-U3 kernels **7.3.1-1** and **6.12.114-1** are published. The tracking metapackage selects 7.3.1; the 6.12 kernel remains available for fallback. [Package/source manifest](publications/u3-2026-10-30.json) · [Matching sources](https://github.com/the-ab/ODROID/releases/tag/u3-kernels-2026.10.30).

Components: `main` for shared packages, `u3` for ODROID-U3. Initial architecture: `armhf`. The [ODROID kernel update guide](https://github.com/the-ab/ODROID/blob/codex/u3-ubuntu26-v1/docs/KERNEL-UPDATES.md) describes the board tools, native update/rollback tests and recovery.

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

Run `sudo apt update`. No `apt-key`, `trusted=yes` or unauthenticated mode is required. On Ubuntu 26.04 armhf ODROID-U3, install or update with `sudo apt install linux-image-odroid-u3`, inspect `odroid-kernel status`, and reboot deliberately. The versioned 6.12 package is `linux-image-6.12.114-odroidu3-v1`. Packages do not update boot0 or reboot automatically. The board tools require Python 3.11 or newer; the supported/tested distribution is Ubuntu 26.04 armhf. Select only the component and architecture appropriate to each future project.

## Maintainer workflow

1. Add a project component and supported architectures to `repository.json`. Extend shared `main` architecture coverage when needed. Preserve other projects' directories.
2. Obtain the relevant product's binary release approval and exact matching sources/licenses/checksums. Keep image and large source assets in product Releases.
3. Copy reviewed `.deb` files into `pool/COMPONENT/`, preserving previous package versions and filenames. Shared keyring packages belong in `main`.
4. Run `python3 scripts/build-repository.py --root . --gpg-home /private/signing/home --signing-key E85346CA2461E1FA45AC7C7CD85BC090497CE8B9`. The signing key must be outside this repository. The builder creates relative package URLs, SHA256/SHA512, compressed lists, retained by-hash files and signed Release metadata. It rejects packages of 95 MiB or more; also watch the overall Pages site size.
5. Review indices and package provenance, test downloads and hash/signature failures, commit and push the approved contents. Check the Pages build and HTTPS signature after deployment. Never overwrite a published version with different package bytes.

Private signing material is managed separately and is never committed. Keep a separate protected backup; losing the archive signing key requires a client trust migration. Normal project development does not automatically publish packages.

Official references: [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages), [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits), [APT source format](https://manpages.debian.org/unstable/apt/sources.list.5.en.html).
