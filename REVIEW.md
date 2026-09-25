# 證據式覆核報告 (Review)

- **覆核時間**：2026-09-26
- **覆核對象**：`SanHsien/agy-staff` (forked from `keli-wen/agy-staff` @ `v0.7.3` / `f00d149`)
- **執行環境**：Windows 11 原生 (PowerShell 7.5 / Node.js 26.7.0 / Python 3.14.7 / Git 2.55.0.windows.3)

---

## 1. 覆核結論

✅ **全數通過 (Ship Ready)**。所有維護基礎設施、Windows 11 原生相容性修復、上游水位巡檢、Pi 技能一致性及單元測試均 100% 綠燈，各項合約與對外防線已機械式落地。

---

## 2. 測試與門禁實跑輸出證據

### 2.1 Windows 門禁一鍵執行 (`tools/dev_check.ps1`)

```text
==> Checking Pi skills consistency (npm run check:pi)
Pi skills verified: 11 files (0 changed).

==> Full test suite (node --test --test-timeout=60000 --test-concurrency=1 tests/*.test.mjs)
ℹ tests 195
ℹ suites 28
ℹ pass 193
ℹ fail 0
ℹ cancelled 0
ℹ skipped 2
ℹ todo 0
ℹ duration_ms 149457.7725

==> Compiling Python tools
Listing 'tools'...

==> Checking fork document links
OK   FORK.md
OK   NOTICE.md
OK   REVIEW.md
OK   CLAUDE.md
OK   GEMINI.md
OK   SECURITY.md
OK   CONTRIBUTING.md
OK   README.md
OK   README.en.md
OK   docs\DECISIONS.md
OK   docs\DEVELOPMENT.md
OK   docs\UPSTREAM.md

共 12 份 overlay 文件，0 份有缺檔。

==> Checking upstream updates
# Upstream review report
- Upstream: `https://github.com/keli-wen/agy-staff.git` (`master`)
- Tracking: release
- Reviewed through: `f00d149` (v0.7.3)
- Last review date: 2026-09-26

## Result
No upstream release past the reviewed one. Nothing to review.

## Upstream pull requests
Triaged through `#24`.
No new items above that number.

## Upstream issues
Triaged through `#24`.
No new items above that number.

WINDOWS DEV CHECK GREEN
```

---

## 3. 本次交付改動清單

1. **核心相容性修復**：
   - [`tests/windows.test.mjs`](tests/windows.test.mjs)：加入跨平台 Git 偵測（Windows `where.exe`）、`.cmd` wrapper 與 `path.delimiter`。
   - [`tests/pi-packaging.test.mjs`](tests/pi-packaging.test.mjs)：處理 Windows 無管理員權限下 `fs.symlinkSync` 之 `EPERM` 防護。
   - [`tests/streaming.test.mjs`](tests/streaming.test.mjs)：放寬 Windows 背景行程輪詢次數，避免超時競爭。
2. **維護與門禁工具**：
   - [`tools/dev_check.ps1`](tools/dev_check.ps1)：Windows 一鍵驗證門禁。
   - [`tools/upstream_baseline.json`](tools/upstream_baseline.json)：記錄 commit / PR / issue 三重水位。
   - [`tools/check_upstream_updates.py`](tools/check_upstream_updates.py)：自動化上游變動巡檢器。
   - [`tools/check_links.py`](tools/check_links.py)：Markdown 相對連結有效性檢查器。
3. **規範與治理手冊**：
   - [`FORK.md`](FORK.md)：詳細記錄 fork 理由、架構差異、remote 配置與邊界規範。
   - [`AGENTS.md`](AGENTS.md)：AI 代理人單一真相源。
   - [`CLAUDE.md`](CLAUDE.md) & [`GEMINI.md`](GEMINI.md)：薄封裝指引。
   - [`.cursor/rules/no-upstream-pr.mdc`](.cursor/rules/no-upstream-pr.mdc)：防止誤向上游開立 PR 的 Cursor 規則。
   - [`NOTICE.md`](NOTICE.md)、[`CONTRIBUTING.md`](CONTRIBUTING.md)、[`SECURITY.md`](SECURITY.md)。
4. **雙語說明文件**：
   - [`README.md`](README.md)：全新繁體中文主說明文件。
   - [`README.en.md`](README.en.md)：保留上游英文完整鏡像。
   - [`docs/DECISIONS.md`](docs/DECISIONS.md)、[`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)、[`docs/UPSTREAM.md`](docs/UPSTREAM.md)。
