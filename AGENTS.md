# APT repository maintenance

Keep package components isolated. Never remove another project component when publishing one project. Only public archive keys, verified package files, signed indices and documentation belong here. Private signing keys live outside Git. Match package/source provenance and obtain the applicable product release approval before publishing binaries. Do not enable a trust bypass. Preserve historical package versions needed for rollback. The initial empty signed repository is infrastructure setup.
