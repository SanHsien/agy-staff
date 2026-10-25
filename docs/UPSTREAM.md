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
   在 `docs/DECISIONS.md` 記錄本次同步引用的變更與理由，合併回 `master`。

---

## 4. 已完成的審查快照

2026-10-26 的審查將 release、PR、issue 與 branch 分開處理；水位代表已**審閱覆蓋**，
不表示每個上游項目都被合併。來源 endpoint、採用判斷與重新評估條件見
[`DECISIONS.md`](DECISIONS.md#2026-10-26複審-10-24-的上游分流取代由既有同步工作處理)。

- Release：`v0.7.4`／`9a30e0774de09e0815c4fc5caf456472f8fc3509` 已審閱，判定為
  defer；此 Windows 維護型 fork 未承諾 OpenCode host。
- PR：已逐筆審閱至 #41（皆已 merge）；issue：已逐筆審閱至 #40，包括已關閉項目。
- Branch：上游 `master` 為 `7925452`；GitHub branches endpoint 只回傳 `master`，
  沒有額外分支可採用。

目前的 strict checker 會 fail-closed 地讀取 release、PR 與 issue 水位；branch
沒有被它持久追蹤，因此本項是人工快照，下一輪仍須重查 branches endpoint。
