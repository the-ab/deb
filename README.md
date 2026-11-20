# the-ab APT repository

[Deutsch](README.de.md)

Shared signed APT repository at **https://the-ab.github.io/deb/**. Current ODROID-U3 server kernel: **7.3.1-odroidu3-v32 / 7.3.1-33**, tools **1.0.3**. The previous **7.3.1-odroidu3-v3 / 7.3.1-4** kernel, metapackage and tools remain in the pool for rollback. [Current package/source manifest](publications/u3-server-2026-11-06.json) · [Matching sources](https://github.com/the-ab/ODROID/releases/tag/u3-kernel-7.3.1-33).

Components: `main` for shared packages, `u3` for ODROID-U3 (`armhf`), and `nas-manager` for the NAS setup test package and iGPU dependencies (`amd64`, plus architecture-independent headers). The [ODROID kernel update guide](https://github.com/the-ab/ODROID/blob/main/docs/KERNEL-UPDATES.md) describes the board tools, native update/rollback tests and recovery.

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

Run `sudo apt update`. No `apt-key`, `trusted=yes` or unauthenticated mode is required. On Ubuntu 26.04 armhf ODROID-U3, install or update with `sudo apt install linux-image-odroid-u3`, inspect `odroid-kernel status`, and reboot deliberately. Keep previously installed fallback kernels locally; the current pool also retains the previous 7.3.1-4 release. Packages do not update boot0 or reboot automatically. The board tools require Python 3.11 or newer; the supported/tested distribution is Ubuntu 26.04 armhf. Select only the component and architecture appropriate to each future project.

## Maintainer workflow

1. Add a project component and supported architectures to `repository.json`. Extend shared `main` architecture coverage when needed. Preserve other projects' directories.
2. Obtain the relevant product's binary release approval and exact matching sources/licenses/checksums. Keep image and large source assets in product Releases.
3. Copy reviewed `.deb` files into `pool/COMPONENT/`, preserving previous package versions and filenames. Shared keyring packages belong in `main`.
4. Run `python3 scripts/build-repository.py --root . --gpg-home /private/signing/home --signing-key E85346CA2461E1FA45AC7C7CD85BC090497CE8B9`. The signing key must be outside this repository. The builder creates relative package URLs, SHA256/SHA512, compressed lists, retained by-hash files and signed Release metadata. The ordinary Git pool keeps its 95 MiB limit. Larger reviewed packages and corresponding sources use immutable release assets declared with exact paths, byte counts and SHA256 in `release-assets.json`; materialize and verify all of them before signing. Never add these materialized files to Git.
5. Review indices and package provenance, test downloads and hash/signature failures, then commit and push the approved contents. Assemble the complete public site with `python3 scripts/repository_assets.py assemble --root . --site /new/public/site`. This verifies the signed indices, every package and release asset, public-file allowlist and total Pages size, preserving all components and historical by-hash files.
6. After the reviewed signed commit reaches `main`, dispatch `Publish signed APT site` with its full `expected_sha` on the scoped `deb-pages` self-hosted runner. Its required tools are Python 3.11+, Git, `gpg`, `gpgv`, tar, gzip and HTTPS CA certificates. The workflow downloads only pinned public assets, assembles and verifies the site again, uploads the Pages artifact and deploys it atomically. It has no signing key or NAS/ODROID access. The runner may be ephemeral; no persistent VM is needed. Confirm the completed workflow and public HTTPS signatures/package hashes. Never overwrite a published version with different package bytes.

Private signing material is managed separately and is never committed. Keep a separate protected backup; losing the archive signing key requires a client trust migration. Normal project development does not automatically publish packages.

Official references: [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages), [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits), [APT source format](https://manpages.debian.org/unstable/apt/sources.list.5.en.html).

Tools 1.0.3 install versioned files directly under `/boot`. Never overwrite an existing package version with different bytes. Retirement of obsolete versions requires explicit owner scope and a verified replacement; it never removes installed kernels on clients.

## NAS Manager clean-install test

The `nas-manager-setup` test package `0.5.10~apt-test.3` is tracked directly
in `pool/nas-manager/` and available for `amd64` in `stable nas-manager`.
APT installs Git and Git LFS as dependencies. Setup reuses an equivalent
active signed source and uses `the-ab.sources` when creating one for the host
or guest. Use the shared `/usr/share/keyrings/the-ab-archive-keyring.gpg`
keyring. After APT installs the package, start setup explicitly with the
separately supplied private unlock file. Run setup again after an APT package upgrade to advance a clean checkout to the verified Git successor.
[Source configuration and commands](README.de.md#nas-manager-clean-install-prüfpaket)

## NAS-Manager dependency updates

[Package, source and copyright manifest](publications/nas-manager-dependencies-2026-11-15.json).
The six original payloads replace seven installer LFS references with identical
bytes. The initial guest kernel remains `6.17.13+deb13-amd64`, Debian version
`6.17.13-1~bpo13+1`; the installed driver remains `2026.09.16`. The older
`2026.08.02` driver is preserved, not selected for new installations.

The canonical NAS installer sets up the signed `main nas-manager` source for
`amd64` and installs `nas-manager-igpu-host` or `nas-manager-igpu-guest`. Future
qualified metapackage versions depend on an exact compatible driver/kernel set.
After that one-time installer migration, `sudo apt update` followed by
`sudo apt upgrade` also installs newly named kernel dependencies. Keep fallback
kernels and reboot deliberately after a kernel/driver update, then run the
existing hardware checks. This updates iGPU dependencies; it does not replace
the NAS application's canonical installer.

Matching Debian source archives (including the signed kernel's `Built-Using`
Linux source) and immutable upstream DKMS source archives are mirrored alongside
the packages. Their original copyright files remain in `publications/licenses/`;
the source and package hashes are in the publication manifest. Five original
dependency packages and both metapackages are tracked in `pool/nas-manager/`.
The 161.6 MiB kernel image and the matching source archives use the existing
release asset pins. The generated
metapackages contain only dependencies and target metadata, with no maintainer
scripts or automatic reboot; their complete builder is in this repository.
