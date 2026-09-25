<p align="center"><img src="assets/logo/gemini-agy.svg" width="440" alt="AGY-STAFF"></p>

<p align="center"><strong>繁體中文</strong> | <a href="README.en.md">English</a> | <a href="README.zh-CN.md">Simplified Chinese</a></p>

<p align="center"><a href="https://antigravity.google/product/antigravity-cli"><img src="assets/badges/powered-by-antigravity.svg" height="20" alt="powered by: Antigravity"></a> <img src="assets/badges/model-gemini-3-8-flash.svg" height="20" alt="model: Gemini 3.8 Flash"></p>

<p align="center"><a href="https://claude.com/claude-code"><img src="assets/badges/claude-code-plugin.svg" height="20" alt="Claude Code plugin"></a> <a href="https://developers.openai.com/codex/"><img src="assets/badges/codex-plugin.svg" height="20" alt="Codex plugin"></a> <a href="LICENSE"><img src="assets/badges/license-mit.svg" height="20" alt="license: MIT"></a></p>

把 Google 的 Antigravity CLI (`agy`) 當作小弟，直接在 **Claude Code**、**OpenAI Codex** 與 **Pi** 中呼喚它起來做事！

![agy-staff design](assets/design.png)

**[安裝指南](#安裝指南) · [常見情境 (CUJs)](#常見情境-cujs) · [核心設計](#核心設計) · [升級方式](#升級方式) · [Fork 維護說明](FORK.md)**

---

## 為什麼需要它？(What & Why)

`agy-staff` 讓主代理人（資深 Agent）將具體工作委派給 `agy`，享受極速的 **Gemini 3.8 Flash** 模型支援。
它提供五種角色（Personas）：
- `staffer`（全能小弟，通用任務與產圖）
- `researcher`（調研程式庫與架構）
- `reviewer`（代碼審閱與方案評估）
- `implementer`（邊界修復與功能實作）
- `ask`（免工具快速諮詢）
- 以及一個主導任務編排的 `lead` 與模型專用的工作管理系統（Jobs）。

在 Claude Code 中使用 `/agy:<persona>`，在 Codex 中使用 `$agy:<persona>`。

如果你用過 Codex，你一定深有同感：GPT-5.6-Sol 即使開啟 fast 模式依然不快；Claude Code 雖然較快，但額度珍貴，你更希望它負責統籌與決策，而不是耗費額度去翻遍整個 repo 或審查長篇改動。
呼喚一個 `agy` 小弟，為你開闢一條**極速通道**——數秒內獲得跨模型二審、以 Flash 速度完成技術調研，並把邊界修復丟到背景執行，主代理人可以繼續往下走。即便不談速度，**讓第二個獨立的模型家族審閱同一段程式碼**，也能帶來單一模型無法自查的覆蓋度與健全性！

![two overloaded senior agents hand the baton to one fast agy worker](assets/why.png)

---

## 使用方式 (How)

### 喚起角色 (Invoke a persona)

在 Claude Code 中輸入 `/agy:`，所有角色隨叫隨到：

![Claude Code 中的 /agy: 命令選單](assets/claude-code-screenshot.png)

在 Codex 中以 `$agy` 喚起外掛：

![Codex 中的 $agy 技能選單](assets/codex-desktop-screenshot.png)

---

## 安裝指南 (Install)

### 人類安裝

**步驟 1** — 安裝 Antigravity CLI（[官方文件](https://antigravity.google/docs/cli/install)），並確認 `agy --version` 運作正常（需要 Node.js 20+）：

```bash
# Linux / macOS / WSL
curl -fsSL https://antigravity.google/cli/install.sh | bash
```
> Windows 原生環境請依 Google Antigravity 官方指示安裝並將 `agy` 加入 PATH。

**步驟 2** — 將外掛安裝至您的編程 Harness：

- **Claude Code**：
  ```bash
  claude plugin marketplace add keli-wen/agy-staff
  claude plugin install agy@agy-staff
  ```
- **OpenAI Codex**：
  ```bash
  codex plugin marketplace add https://github.com/keli-wen/agy-staff
  codex plugin add agy@agy-staff
  ```

<details>
<summary>使用 Pi 嗎？</summary>

安裝：`pi install git:github.com/keli-wen/agy-staff`。
技能前綴為 `/skill:agy-<persona>`（例如 `/skill:agy-ask reply with OK`），並以 `/skill:agy-jobs` 進行工作管理。
更新時執行 `pi update --extension git:github.com/keli-wen/agy-staff` 後執行 `/reload`。

</details>

安裝後請重啟 Claude Code 或 Codex。初次執行可先測試：
- Claude Code：`/agy:ask reply with OK`
- Codex：`$agy:ask reply with OK`
`ask` 角色免用本機工具，無需額外配置即可回應。

> [!IMPORTANT]
> **沒有強制的設定步驟。** `staffer`、`researcher`、`reviewer` 與 `implementer` 預設以 **unrestricted** 模式運行：`agy` 具有讀取 repo、執行指令與修改檔案的能力。

### 給 Agent 的安裝指令

直接複製以下提示詞丟給任何 Coding Agent：

```text
Read the raw text of https://raw.githubusercontent.com/keli-wen/agy-staff/master/docs/INSTALL_FOR_AGENTS.md (curl it — do not
work from a summary) and follow it to install and verify the agy-staff plugin for the harness you are running in.
Respond in the user's language.
```

---

## 常見情境 (CUJs)

下列範例以 Claude Code 的 `/agy:…` 為例；Codex 請使用 `$agy:…`。

| 使用情境 | 呼叫方式 |
|---|---|
| **主導進行中的任務** | `/agy:lead investigate the options, draft a proposal, and revise it with my feedback` |
| **快速二審諮詢** | `/agy:ask what's your backend model` |
| **一般委派任務** | `/agy:staffer summarize the open TODOs in this repo` |
| **生成圖片** | `/agy:staffer generate a pixel-art robot mascot, save it as assets/mascot.png` |
| **審閱工作區改動** | `/agy:reviewer Review the current working tree` |
| **審閱 Pull Request** | `/agy:reviewer Review PR #730` |
| **挑戰方案或設計決策** | `/agy:reviewer Challenge the migration plan in docs/plan.md` |
| **主題調研與架構梳理** | `/agy:researcher how does auth work in this repo` |
| **實作邊界修復** | `/agy:implementer fix the flaky retry test` |
| **工作運維 (wait/status/cancel/continue)** | 自然語言即可："is the agy job done?", "continue: also check the error path" |

`reviewer` 完全基於提示詞：您只需說明對象，`agy` 會自行蒐集證據（`gh pr view`、`git diff`、閱讀檔案）——不需手動傳 diff。
`staffer` 同時涵蓋了 `agy` 的原生工具，包括**圖像生成**（`generate_image`）。在 agy v1.1.15 上實測約 30 秒內即可產出 1024×1024 PNG 圖檔。

---

## 核心設計 (Core design)

- `lead` 為主代理人提供任務編排指引。先定位並拆解目標，將實質工作委派給 `staffer`，等待結果並評估吸收。
- `ask` 在同一次呼叫中直接同步回應。其他角色會回傳 job id 與收集指令（如 `wait <id> --timeout 10m`），在背景執行。
- 主代理人預設等待最終結果，必要時可使用 `observe` 查看近期工具動態與部分產出快照。任務完成後，`wait` 或 `result` 會遞送完整成果報告。

[![背景任務執行流程圖](assets/integration.png)](assets/integration.svg)

---

## 本 Fork 維護特色 (SanHsien Maintenance Fork)

本倉庫為 [`SanHsien/agy-staff`](https://github.com/SanHsien/agy-staff) 維護型 fork，特別加強：

1. **Windows 11 原生環境全面修復**：修正 Git 偵測（`where.exe`）、路徑分隔符號（`path.delimiter`）與檔案權限防禦，全套 190+ 測試 100% 綠燈。
2. **一鍵驗收門禁**：提供 [`tools/dev_check.ps1`](tools/dev_check.ps1)，整合測試、技能校驗、連結檢查與上游水位巡檢。
3. **自動化上游水位追蹤**：配備 [`tools/upstream_baseline.json`](tools/upstream_baseline.json) 與 [`tools/check_upstream_updates.py`](tools/check_upstream_updates.py)，監控 upstream commit、PR 與 issue。
4. **AI 代理單一真相源**：完備的 [`AGENTS.md`](AGENTS.md)、[`FORK.md`](FORK.md)、[`CLAUDE.md`](CLAUDE.md) 與 [`GEMINI.md`](GEMINI.md)。

---

## 相關文件

- [Fork 維護手冊與架構差異 (`FORK.md`)](FORK.md)
- [AI 代理維護與開發規範 (`AGENTS.md`)](AGENTS.md)
- [Windows 開發指南 (`docs/DEVELOPMENT.md`)](docs/DEVELOPMENT.md)
- [架構決策紀錄 (`docs/DECISIONS.md`)](docs/DECISIONS.md)
- [上游同步手冊 (`docs/UPSTREAM.md`)](docs/UPSTREAM.md)
- [驗證覆核報告 (`REVIEW.md`)](REVIEW.md)
- [官方完整手冊 (`docs/REFERENCE.md`)](docs/REFERENCE.md)

---

## 授權條款

MIT License — 詳見 [LICENSE](LICENSE)。
