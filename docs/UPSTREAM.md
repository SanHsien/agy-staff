# 上游同步指南 (Upstream Sync)

本文件說明如何安全地同步上游 [`keli-wen/agy-staff`](https://github.com/keli-wen/agy-staff) 的更新與發行版本。

---

## 1. 水位追蹤機制

本 fork 在 `tools/upstream_baseline.json` 中記錄了當前已審閱的上游水位：

```json
{
  "repo": "https://github.com/keli-wen/agy-staff.git",
  "branch": "master",
  "reviewed_through": "<commit-sha>",
  "reviewed_release": "<tag>",
  "reviewed_date": "YYYY-MM-DD",
  "reviewed_pr_through": <number>,
  "reviewed_issue_through": <number>,
  "track": "release",
  "decision_log": "docs/DECISIONS.md"
}
```

- **Commit 水位**：`reviewed_through` 記錄已審核的最後一個 commit SHA。
- **PR 水位**：`reviewed_pr_through` 記錄已審核的最高 PR 編號。
- **Issue 水位**：`reviewed_issue_through` 記錄已審核的最高 Issue 編號。

---

## 2. 巡檢上游更新

在 PowerShell 中執行：

```powershell
python tools\check_upstream_updates.py --strict
```

- 若無新 release 或新 ticket，工具將返回 0 並輸出無變更報告。
- 若有新 release 或新 ticket，工具將列出待審項目，在 `--strict` 模式下返回 1。

---

## 3. 同步標準流程

當發現上游釋出新版本需要同步時，請依循以下步驟：

1. **建立同步分支**：
   ```powershell
   git checkout -b sync/upstream-vX.Y.Z
   ```

2. **取得上游最新提交**：
   ```powershell
   git fetch upstream master --tags
   ```

3. **審閱變更差異**：
   ```powershell
   git log HEAD..upstream/master --oneline
   git diff HEAD..upstream/master
   ```

4. **進行合併（Merge，切勿 Rebase）**：
   ```powershell
   git merge upstream/master
   ```
   *注意：保留 merge commit 有助於維持歷史追蹤；切勿使用 rebase 抹除共同祖先。*

5. **解決衝突並保留本 fork 的 Windows 硬化增強**：
   若遇衝突，請確認本 fork 的 Windows 修復（如 `windows.test.mjs` 中的 `where.exe`、`pi-packaging.test.mjs` 中的 EPERM 防護等）未被抹除。

6. **本地門禁驗收**：
   ```powershell
   .\tools\dev_check.ps1
   ```

7. **推進水位線**：
   更新 `tools/upstream_baseline.json` 中的 `reviewed_through`、`reviewed_release`、`reviewed_date`、`reviewed_pr_through` 與 `reviewed_issue_through`。

8. **紀錄決策並提交**：
   在 `docs/DECISIONS.md` 記錄本次同步引用的變更與理由，合併回 `main`。

---

## 4. 已完成的審查快照

2026-10-26 的審查將 release、PR、issue 與 branch 分開處理；水位代表已**審閱覆蓋**，
不表示每個上游項目都被合併。來源 endpoint、採用判斷與重新評估條件見
[`DECISIONS.md`](DECISIONS.md#2026-10-26複審-10-24-的上游分流取代由既有同步工作處理)。

- Release：`v0.7.4`／`9a30e0774de09e0815c4fc5caf456472f8fc3509` 已審閱，判定為
  defer；此 Windows 維護型 fork 未承諾 OpenCode host。
- PR：已逐筆審閱至 #41（#27–#41 皆已 merge）；issue：已逐筆審閱至 #40，包括已關閉項目。
- Branch：上游 `master` 為 `7925452`；GitHub branches endpoint 只回傳 `master`，
  沒有額外分支可採用。

目前的 strict checker 會 fail-closed 地讀取 release、PR 與 issue 水位；branch
沒有被它持久追蹤，因此本項是人工快照，下一輪仍須重查 branches endpoint。

## 2026-11-13：v0.8.1 修正移植

只讀取本機既有 Git objects：`9ddec3e..883003a7b433508d46b19b10d80bae75186c59a0`，
包含 #49 `029eb7be41c61d19851a6aab1e66881c206d15a9`（issue #48）及
#52 `883003a7b433508d46b19b10d80bae75186c59a0`（issue #51）。沒有 fetch、push、PR 或上游寫入。
採用原生診斷保留、共用 persona 規則、job ID 接續及離線回歸測試；保留 fork 的 Pi-only
產生器、Windows 測試與雙語文件。未採用 #53 brain、OpenCode、bench 或版本號。
本輪依使用者要求直接在 `main` 修改，不執行本文件第 3 節的分支／merge 流程。

水位維持 2026-11-08 已審閱的 v0.8.2／PR 53／issue 51；本次不是新一輪上游巡檢，
不得把移植結果宣稱為最新遠端狀態。驗收限制與採用判斷見 `DECISIONS.md` 的同日條目。

## 2026-11-13：v0.9.0～v0.9.2 審查

來源為已取得的本機 Git objects，範圍 `d90bac7..2b78b4548070af6b8ff154379aecfca6b6762907`；
共 4 筆 squash commit：#55 `1f66a8d`、#56 `105de09`、#58 `8a69f0a`、#60 `2b78b45`。
PR／issue 於 2026-11-13 以 gh 查詢：PR #55、#56、#58、#60 已合併，issue #54、#57、#59 已關閉；strict 上游檢查 current。

- v0.9.0／#55、issue #54：skip DeepSeek Harness 外掛、像素側欄與相關打包／素材；屬新 host。
- #56：skip 宣傳截圖更新，沒有現有功能修復。
- v0.9.1／#58、issue #57：adopt 現有角色的 Carbon／Argon 明確選模與診斷；skip brain、DSH 與圖示。
- v0.9.2／#60、issue #59：adopt Hydrogen 預設、xhigh、舊 Flash／job 相容與模型建議；skip brain 專用自動 fallback／cache、DSH、素材與版本號。

水位推進為 v0.9.2／`2b78b4548070af6b8ff154379aecfca6b6762907`、PR 60、issue 59，日期 2026-11-13。
此水位是審查覆蓋，不是全數採用。
這批照慣例直接在預設分支做功能移植，不執行第 3 節的 branch／merge 流程。
逐筆證據、fallback 邊界與重新評估條件見 `DECISIONS.md` 同日 v0.9.0～v0.9.2 條目。
