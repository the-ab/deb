# APT repository maintenance

## Maintainer workflow

1. Add a project component and supported architectures to `repository.json`. Extend shared `main` architecture coverage when needed. Preserve other projects' directories.
2. Obtain the relevant product's binary release approval and exact matching sources/licenses/checksums. Keep image and large source assets in product Releases.
3. Copy reviewed `.deb` files into `pool/COMPONENT/`, preserving previous package versions and filenames. Shared keyring packages belong in `main`.
4. Run `python3 scripts/build-repository.py --root . --gpg-home /private/signing/home --signing-key E85346CA2461E1FA45AC7C7CD85BC090497CE8B9`. The signing key must be outside this repository. The builder creates relative package URLs, SHA256/SHA512, compressed lists, retained by-hash files and signed Release metadata. The ordinary Git pool keeps its 95 MiB limit. Declare release-backed pool packages with exact paths, byte counts and SHA256 in `release-assets.json`. Materialize and verify every pinned pool package before signing. Record links to the corresponding sources in the publication manifest. Never add these materialized files to Git.
5. Review indices and package provenance, test downloads and hash/signature failures, then commit and push the approved contents. Assemble the complete public site with `python3 scripts/repository_assets.py assemble --root . --site /new/public/site`. This verifies the signed indices, every package and release asset, public-file allowlist and total Pages size, preserving all components and historical by-hash files.
6. After the reviewed signed commit reaches `main`, dispatch `Publish signed APT site` with its full `expected_sha` on the scoped `deb-pages` self-hosted runner. Its required tools are Python 3.11+, Git, `gpg`, `gpgv`, tar, gzip and HTTPS CA certificates. The workflow downloads only pinned public assets, assembles and verifies the site again, uploads the Pages artifact and deploys it atomically. It has no signing key or NAS/ODROID access. The runner may be ephemeral; no persistent VM is needed. Confirm the completed workflow and public HTTPS signatures/package hashes. Never overwrite a published version with different package bytes.

Private signing material is managed separately and is never committed. Keep a separate protected backup; losing the archive signing key requires a client trust migration. Normal project development does not automatically publish packages.

Official references: [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages), [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits), [APT source format](https://manpages.debian.org/unstable/apt/sources.list.5.en.html).

Tools 1.0.3 install versioned files directly under `/boot`. Never overwrite an existing package version with different bytes. Retirement of obsolete versions requires explicit owner scope and a verified replacement; it never removes installed kernels on clients.
