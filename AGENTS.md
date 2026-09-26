> **SanHsien 維護型 fork overlay。** `origin` 是 [`SanHsien/agy-staff`](https://github.com/SanHsien/agy-staff)，`upstream` 是 [`keli-wen/agy-staff`](https://github.com/keli-wen/agy-staff)。
> 本 fork 的維護規則以 [`FORK.md`](FORK.md) 為準；與下文衝突時以 FORK.md 優先。
> 不要推 `upstream`、不要對上游開 PR（除非維護者在這次對話明確同意回貢）。
> 產品行為與架構規範遵守下文說明。

# agy-staff - Agent 指南與維護規範

`agy-staff` 是一套將 Google Antigravity CLI（`agy`）封裝為跨 Harness（Claude Code, OpenAI Codex CLI, Pi）Agent Plugin 的 companion 執行期架構。

---

## 核心硬閘門（所有代理人必讀）

1. **Windows 11 原生環境假設**：
   本機環境為 Windows 11 原生（PowerShell / cmd），非 WSL。嚴禁依賴 POSIX 特有指令（如 `which`、`touch`、路徑冒號分隔符等）。
2. **對外邊界硬閘門**：
   PR、push、release 一律指向 `SanHsien/agy-staff`。每個 clone 先跑 `gh repo set-default SanHsien/agy-staff`。
3. **驗證憑真實輸出**：
   回報「完成／修好／測試通過」之前，必須實際在終端機中執行檢查並貼出完整輸出。不准註解掉測試、吞掉例外、或回傳固定值偽造通過。
4. **一鍵門禁必須全綠**：
   交付任何改動前，必須執行 `powershell -File tools\dev_check.ps1` 並確保無任何報錯。

---

## 專案架構與職責邊界

| 目錄 / 檔案 | 職責 | 編輯規範 |
|---|---|---|
| `companion/` | companion 執行期程式碼（Node.js ESM） | `agy-companion.mjs`（進入點與 CLI 處理）、`stream-worker.mjs`（背景排程與行程串流）、`observation.mjs`、`state-lock.mjs` |
| `skills/` | **Canonical Skills 單一真相源** | 編輯角色（personas）一律在此目錄，嚴禁手動編輯 `pi-skills/` |
| `pi-skills/` | 由 `skills/` 自動產生的 Pi 適配檔案 | 只能透過 `npm run generate:pi` 產生；送出前用 `npm run check:pi` 驗證 |
| `templates/` | 共用提示詞範本 | 提供各 persona 專屬的引導提示詞 |
| `tests/` | Node.js 原生測試套件（`node --test`） | 保持回歸測試獨立於本機網路與個人憑證，使用 `tests/fake-agy.mjs` |
| `tools/` | Windows 維護門禁與上游巡檢工具 | `dev_check.ps1`、`check_upstream_updates.py`、`check_links.py`、`upstream_baseline.json` |
| `docs/` | 架構決策與參考文件 | `docs/DECISIONS.md`、`docs/DEVELOPMENT.md`、`docs/UPSTREAM.md`、`docs/REFERENCE.md` |

---

## 常用指令

```powershell
# 執行 Windows 一鍵驗收門禁
.\tools\dev_check.ps1

# 快速測試通道
.\tools\dev_check.ps1 -Quick

# 單元測試全套執行（Node.js 原生測試器，等同 npm test）
node --test --test-concurrency=1 tests/*.test.mjs

# 重新生成 Pi skills 並驗證一致性
npm run generate:pi
npm run check:pi

# 文件連結與上游水位巡檢
python tools\check_links.py
python tools\check_upstream_updates.py --strict
```
