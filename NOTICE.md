# NOTICE

This repository is a maintained fork of [agy-staff](https://github.com/keli-wen/agy-staff).

- Original Author: [keli-wen](https://github.com/keli-wen)
- Upstream Repository: https://github.com/keli-wen/agy-staff
- License: MIT License (see [LICENSE](LICENSE))

Modifications and fork maintenance infrastructure by SanHsien:
- Windows-first verification tooling and dev check gates (`tools/dev_check.ps1`)
- Upstream synchronization review ledger and automation (`tools/upstream_baseline.json`, `tools/check_upstream_updates.py`)
- Cross-platform test fixes for Windows execution (path delimiter handling, `.cmd` git wrapper support, EPERM handling)
- Dual-platform AI governance policies and documentation (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `FORK.md`)
- Traditional Chinese documentation and localization (`README.md`, `docs/`)
