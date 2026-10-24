# 架構與維護決策紀錄 (Decisions)

本文件記錄 `SanHsien/agy-staff` 維護型 fork 的重大架構決策與取捨。

---

## 2026-09-26

### 決策一：上游追蹤採用 Release 粒度優先（`track: release`）

- **背景**：上游 `keli-wen/agy-staff` 的 `master` 分支更新頻繁，但發行物與外掛安裝（Claude Code marketplace、Codex marketplace、Pi package）均以 SemVer tag（Release）為發布單位。
- **決定**：在 `tools/upstream_baseline.json` 採用 `track: "release"`，監控上游正式發行的版本標籤，同時持續全量記錄 PR 與 Issue 的水位。
- **理由**：若追蹤每次未發布的日常 commit，會導致排程檢查常態報紅，使巡檢訊號失去警示意義。追蹤 Release 能精準對齊上游正式釋出的功能與行為變更。

---

### 決策二：Windows 11 原生相容性修復與測試硬化

- **背景**：在 Windows 11 原生環境執行 `npm test` 時，發現數處測試失敗：
  1. `tests/windows.test.mjs` 中硬編碼呼叫 `which git`，在 Windows 原生終端下無此命令；產生無副檔名 `git` hashbang 腳本，在 Windows 下無法直接被 child_process 執行；PATH 分隔符假設為 `:`。
  2. `tests/pi-packaging.test.mjs` 中呼叫 `fs.symlinkSync`，在 Windows 一般使用者權限（非開發者模式或管理員）下直接拋出 `EPERM`。
  3. `tests/streaming.test.mjs` 中的 `cleanup-race` 測試在 Windows 下行程啟動較重，30 次輪詢容易觸發非預期超時。
- **決定**：
  1. `windows.test.mjs` 引入跨平台 Git 偵測（Windows 使用 `where.exe`，POSIX 使用 `which`）、自動生成 `git.cmd` 封裝腳本，並採用 `path.delimiter`。
  2. `pi-packaging.test.mjs` 對 `fs.symlinkSync` 加入 `EPERM` 例外捕獲，確保無提權環境亦能平穩過關。
  3. `streaming.test.mjs` 適度放寬輪詢次數至 80 次，防止慢速磁碟或高負載下行程競爭。
- **理由**：落實 Windows 11 原生開發環境原則，消除平台誤報。（當時未涵蓋 tar 問題，見決策四。）

---

### 決策三：繁體中文主說明文件與雙語鏡像

- **背景**：本 fork 主要面向繁體中文環境的 AI 代理人與開發者，上游預設為英文 `README.md` 與簡體中文 `README.zh-CN.md`。
- **決定**：將繁體中文設置為倉庫的預設說明文件 `README.md`，英文原版保留為 `README.en.md`，並在兩份文件頂部建立雙向超連結。
- **理由**：符合艦隊共通規範（SCAFFOLD.md），確保本地閱讀體驗清晰自然。
- **修訂（2026-09-26）**：README 只維持繁中與英文兩版。刪除 `README.zh-CN.md` 與 `docs/REFERENCE.zh-CN.md`，並移除社群、贊助與自我推廣類連結；只保留 MIT 授權要求的上游歸屬說明（README 與 `NOTICE.md`）。`docs/releases/` 為上游歷史發行紀錄，保持原文不改。

---

### 決策四：套件測試固定使用 Windows 內建 tar

- **背景**：`tests/pi-pack-helpers.mjs` 以 `tar -xzf` 解開 `npm pack` 產物。本機 PATH 中 Git for Windows 的 GNU tar 排在 `C:\Windows\System32\tar.exe`（bsdtar）之前，GNU tar 把 `C:\...` 解讀為 `host:path` 遠端封存，導致 `tests/pi-packaging.test.mjs` 在本機失敗；GitHub Windows runner 的 PATH 順序不同，所以 CI 綠燈。
- **決定**：Windows 上固定呼叫 `%SystemRoot%\System32\tar.exe`，找不到時才退回 PATH 上的 `tar`。其他平台不變。
- **理由**：改動最小、不新增依賴，且與 PATH 順序無關。

---

### 上游 issue 分流（2026-09-26）

| 項目 | 判定 | 理由 |
|---|---|---|
| #25 Idea: optional Adam Network channel for the staffer to post findings | Skip / 跟隨上游 | 功能提案，非錯誤；上游採納並發行後依 release 追蹤帶入。 |
| #26 请求加入opencode支持 | Skip / 跟隨上游 | 功能請求，非錯誤；上游採納並發行後依 release 追蹤帶入。 |

處理後 `tools/upstream_baseline.json` 的 `reviewed_issue_through` 由 `24` 提升為 `26`。

---

## 2026-10-24

### 上游分流：v0.7.4、PR #27–#41、issue #28–#40

- **背景**：上游發行 v0.7.4（OpenCode 外掛支援），並新增一批 bench（評測框架）相關 PR 與 issue，`Tests (Windows)` 的上游檢查因此轉紅，連帶擋住只改 job 名稱的 PR #1。
- **決定**：本輪只做紀錄，不引進任何程式碼。凡本來會判為「採用」的項目，一律寫成「延後，由既有的上游同步工作處理」：v0.7.4、PR #41、issue #40 的引進候選已在另一條同步工作中進行，這裡重做會與之衝突。明顯無關的項目判為不採用。
- **理由**：分流紀錄與實際引進分屬兩件事；紀錄先落地才能讓巡檢回到有意義的訊號，引進則留給同步工作做完整的合併與測試。
- **基準推進**：`reviewed_through` 推進到 v0.7.4 tag 的 commit `9a30e07`，`reviewed_release` 為 `v0.7.4`。追蹤模式為 `track: release`，待審 commit 只有這一個，已在下表記錄。上游 `master` 在 v0.7.4 之後的其餘 commit（含 PR #29、#33、#35–#38、#41）尚未發行，依 release 追蹤等其發行時再審，這些 PR 與 issue 本身已在下表記錄判定。

#### 上游 release／commit

| 項目 | 判定 | 理由 |
|---|---|---|
| v0.7.4 `9a30e07` feat: add OpenCode plugin support (0.7.4) (#27) | 延後，由既有的上游同步工作處理 | 新增 OpenCode 外掛（30 個檔案、約 +994/-63），需連同產生器、測試與 Windows 硬化一併合併驗證；已有同步工作承接。 |

#### 上游 pull request

| 項目 | 判定 | 理由 |
|---|---|---|
| #27 feat: add OpenCode plugin support (0.7.4) | 延後，由既有的上游同步工作處理 | 即 v0.7.4 本體，同上；關閉上游 issue #26。 |
| #29 docs: add DESIGN.md, the portable bash + skills design | 延後，由既有的上游同步工作處理 | 新增 `docs/DESIGN.md` 並改動兩份 README；本 fork 的 README 只維持繁中與英文，需改寫後引進，留待同步工作。 |
| #33 docs(bench): publish agy-staff Bench v1 results table | 延後，由既有的上游同步工作處理 | bench v1 結果表與資料，是 #35–#38、#41 的同一系列，須整批引進才一致。 |
| #35 feat(bench): add the grading and analysis pipeline | 延後，由既有的上游同步工作處理 | bench 評分管線，#41 的前置；引進 #41 時必然一起帶入，不在此單獨處理。 |
| #36 feat(bench): add the trial runner | 延後，由既有的上游同步工作處理 | bench 試驗執行器，#41 的前置，同上。 |
| #37 feat(bench): add the cost, tokens and solved-vs-cost charts | 延後，由既有的上游同步工作處理 | bench 圖表，與 v1 資料同一系列，同上。 |
| #38 fix(bench): v1 erratum: cost accounting, SymPy test-name grading, the 0118 rule violation | 延後，由既有的上游同步工作處理 | 修正 bench v1 的成本計算與評分勘誤，與 #33 的資料綁在一起，須同批引進。 |
| #41 fix(bench): preserve startup errors and complete Codex native v1 results | 延後，由既有的上游同步工作處理 | 保留環境啟動錯誤並補齊 Codex native v1 結果，關閉 #40；引進候選已在別處進行。 |

#### 上游 issue

| 項目 | 判定 | 理由 |
|---|---|---|
| #28 docs: add DESIGN.md — the portable bash + skills design behind agy-staff | 延後，由既有的上游同步工作處理 | 已由 #29 處理並關閉，隨 #29 一併判定。 |
| #31 Prélèvements non autorisés | 不採用 | 法文的扣款退費申訴，內容與 agy-staff 無關（提到的是另一個 WhatsApp 助理服務），上游已關閉。 |
| #34 Bench: agy-staff Harness & Orchestration Bench (tracking) | 不採用 | 上游評測框架的長期追蹤 issue，本身不含需要引進的變更；實際內容由 #33–#41 各 PR 承載，已於上表判定。 |
| #39 Bench v1: the native-subagent setup beats agy on host spend for SWE-bench — worth a line in "What v1 says"? | 不採用 | 對上游 bench README 敘述的建議，屬上游文案決定，與本 fork 的維護範圍無關；若上游修改文案，會隨 bench 同步帶入。 |
| #40 bug(bench): preserve environment startup errors instead of reporting egress failure | 延後，由既有的上游同步工作處理 | bench 診斷錯誤，由 #41 修正；引進候選已在別處進行。 |

處理後 `tools/upstream_baseline.json` 的 `reviewed_pr_through` 由 `24` 提升為 `41`，`reviewed_issue_through` 由 `26` 提升為 `40`，`reviewed_through` 與 `reviewed_release` 推進到 v0.7.4。
