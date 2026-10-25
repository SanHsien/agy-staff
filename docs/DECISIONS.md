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

---

## 2026-10-26：複審 10-24 的上游分流（取代「由既有同步工作處理」）

10-24 的分流把多數項目寫成「延後，由既有的上游同步工作處理」，但該同步工作已停止，
沒有任何程式碼被引進，那句話不再成立。本輪重新以實際 diff 逐項判定（來源：GitHub API
`--state all` 讀取 releases／pulls／issues／branches，與 `git diff HEAD 9a30e07`
對本 fork 的 `companion/`、`skills/`、`package.json`、`tests/`）。上游 `master` 現為
`7925452`（#41 已 merge，比 10-24 記錄的 `044c695` 多這一個 merge）。水位不變：
release `v0.7.4`、PR 至 #41、issue 至 #40。水位表示已審閱覆蓋，不表示採用。

| 項目 | 判定 | 證據與本 fork 的對照 | 重新評估條件 |
| --- | --- | --- | --- |
| `v0.7.4`／#27／`9a30e07` | defer | 30 檔、+994/-63；新增 `opencode.mjs`、11 份 `opencode-skills/**`、雙 target generator 與 OpenCode 測試。`companion/` 與 `skills/` 在 `HEAD..9a30e07` 沒有任何差異，即沒有 runtime 修復可單獨移植。本 fork 的 `package.json` 只發佈 `skills/`、`pi-skills/`，沒有 OpenCode host 驗收。 | 維護者明確要求 OpenCode 支援並核准 product scope（`package.json`、generator、`opencode.mjs`、安裝文件、OpenCode 測試與 Windows package smoke）。 |
| #29／`65a1ab4` | reject | 3 檔、+204/-2，只新增跨 host／Bash 設計說明與 README 導覽，不修正本 fork 的 Windows runtime 或治理契約。 | fork 需要公開設計文件，且內容可改寫進現有雙語／Windows 範圍。 |
| #33／`41a775f`、#35／`0c1ed19`、#36／`9494617`、#37／`edf96c9`、#38／`044c695` | reject | 同一組 `bench/` 評測系列（+4090、+2983、+1681、+1007、+444 行）：結果資料、Python grading、Harbor runner、圖表與勘誤。本 fork 沒有 bench runtime／依賴；runner 還會擴大外部執行與憑證邊界。 | 明確成立受維護的 benchmark product，核准 Python toolchain 與 runner 安全設計後整批評估。 |
| #41／`bbacf6d`（merge `7925452`） | reject | 現已 merge、21 檔、+1303/-99，全在 `bench/`、`tests/bench-*`；對 merge 後差量掃描長空白後程式、`eval`／`new Function(`、`global.require`、長 base64／hex，無命中。不涉及 `companion/`、canonical skills 或 Windows package gate。 | 同上。 |
| #31 | reject | 已關閉，法文扣款申訴，與本專案無關。 | 無。 |
| #34、#39 | monitor | 仍 open 的 bench 追蹤與結果解讀討論，沒有可移植的修復。 | bench 被納入本 fork 的產品範圍，或上游結論影響 companion 行為。 |
| #40 | monitor | 現已關閉（由 #41 修）；只觸及未採用的 bench runner。 | fork 採用 Harbor runner。 |
| branches | no action | `GET /repos/keli-wen/agy-staff/branches` 只回傳 `master`。checker 尚未讀 branch 水位，每輪須人工重查。 | 每次上游審查重讀。 |

另有一個 Windows 處理 patch（process-table 非阻塞查詢，約 18 KB，涉及 `agy-companion.mjs`、
`stream-worker.mjs` 與兩份測試）曾在 10-24 被提出，但從未通過原碼 Quick 門禁；上游 v0.7.4 沒有對應變更，
`main` 上 Windows CI 為綠，也沒有可重現的使用者缺陷支持這個 runtime 改動，故不引進。
