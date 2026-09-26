# 關於這份 fork

上游：[`keli-wen/agy-staff`](https://github.com/keli-wen/agy-staff)（MIT License）。

`agy-staff` 是一套將 Google Antigravity CLI（`agy`）封裝為 Agent Plugin 的工具，讓 Claude Code、OpenAI Codex CLI 與 Pi 能夠隨時呼喚 `agy` 作為小弟（staffer / reviewer / researcher / implementer / lead / ask），實現高速且可靠的 Gemini 背景交付與多代理協作。

本 repo 為 **SanHsien 的 Windows 原生維護型 fork**，確保在 Windows 11 原生環境（非 WSL）下的穩定運作、自動化水位追蹤與健全治理。

---

## 為什麼 fork

1. **Windows 11 原生相容性修復**：
   上游原先在 Windows 環境下部分測試未完全跑通（例如 `which` 指令缺失、PATH 分隔符號假設為 `:`、`fs.symlinkSync` 在非提權環境觸發 EPERM、以及批次子行程執行與超時競爭）。本 fork 補齊 Windows 11 原生修復，確保全套測試在 Windows 原生環境綠燈通過。
2. **完整維護門禁與自動化**：
   建立 `tools/dev_check.ps1` 一鍵式驗證門禁，整合 Pi 技能一致性校驗、全套單元測試、工具語法編譯、文件相對連結檢查與上游水位巡檢。
3. **上游水位雙軌追蹤**：
   建立 `tools/upstream_baseline.json` 與 `tools/check_upstream_updates.py`，完整涵蓋 commit、PR 與 issue 三個維度的水位監控。
4. **AI 治理與多 Agent 規範**：
   落地 `AGENTS.md` 單一真相源，並提供 `CLAUDE.md`、`GEMINI.md` 以及 `.cursor/rules/no-upstream-pr.mdc`，防止誤向上游提交 PR。
5. **雙語文件、無推廣性連結**：
   README 僅維持繁體中文主文（`README.md`）與英文鏡像（`README.en.md`）兩個版本，移除簡體中文版與非產品性質的連結（例如社群/贊助/自我推廣類連結），只保留必要的上游歸屬連結（MIT 授權要求）。

---

## 與上游的差異

| 項目 | 本 fork (`SanHsien/agy-staff`) | 上游 (`keli-wen/agy-staff`) |
|---|---|---|
| **預設說明文件** | 繁體中文主文（`README.md`）＋英文鏡像（`README.en.md`），僅兩版本 | 英文（`README.md`）＋簡體中文（`README.zh-CN.md`） |
| **Windows 原生支援** | 修正 `tests/windows.test.mjs`（`where.exe`、`.cmd` wrapper、`path.delimiter`）、`tests/pi-packaging.test.mjs`（EPERM 防禦）、`tests/streaming.test.mjs` | 原測試偏向 Linux / macOS / WSL 環境 |
| **一鍵式驗證 Gate** | `tools/dev_check.ps1`（支援 `-Quick`，全綠才能提交） | 無單一腳本一鍵門禁 |
| **上游追蹤水位** | `tools/upstream_baseline.json` + `tools/check_upstream_updates.py`（每週 Actions） | 無 |
| **AI 代理規範** | `AGENTS.md`、`CLAUDE.md`、`GEMINI.md`、`.cursor/rules/no-upstream-pr.mdc` | 僅 `.agents/` 提示詞範本 |
| **連結檢查** | `tools/check_links.py` | 無 |
| **CI 測試** | 包含 Windows 與 Ubuntu 雙平台完整測試，含 CodeQL 靜態分析 | 上游 Windows 測試受手動審查環境限制 |

---

## Remote 與分支規範

每個本機 clone 請確認以下 remote 配置：

- `origin`：`https://github.com/SanHsien/agy-staff.git`（主要工作與交付目標）
- `upstream`：`https://github.com/keli-wen/agy-staff.git`（上游對照目標）

```powershell
gh repo set-default SanHsien/agy-staff   # 每個 clone 先跑一次
gh repo set-default --view               # 必須顯示 SanHsien/agy-staff
```

### 對外邊界與 PR 守則

- **所有 PR、push、release 一律只打 `SanHsien/agy-staff`，絕不打上游。**
- `gh` 工具在 fork clone 下的預設 repo 會指向母 repo，必須使用 `gh repo set-default SanHsien/agy-staff` 覆蓋。
- 建立 PR 時請明確指定：
  ```powershell
  gh pr create --repo SanHsien/agy-staff --base master --head <分支>
  ```
  建完**務必讀取輸出 URL**，確認 owner 為 `SanHsien`。
- **唯一例外**：維護者在**當次對話**明確指示回貢上游通用 bug 修復時，才開立上游 PR。

---

## 本機開發與日常驗收

本專案需要 Node.js 20+（建議 Node 22 或 24+）與 Python 3.10+。

```powershell
# 執行 Windows 一鍵式驗證門禁
.\tools\dev_check.ps1

# 快速驗證通道（快速單元測試與關鍵檢查）
.\tools\dev_check.ps1 -Quick

# 檢查上游最新 release / commit / PR / issue
python tools\check_upstream_updates.py --strict
```
