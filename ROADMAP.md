# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-10-29 依 `main` `c21308df24ec` 查的快照，開工前先重查 GitHub。

## 現況

Windows 優先維護 fork（上游 `keli-wen/agy-staff`，預設分支 `master`），把 Google Antigravity CLI（`agy`）當「小弟」委派的外掛，支援 Claude Code、Codex CLI、Pi；與上游無共同祖先是 2026-10-24 單一 commit 的已知結果，不是缺陷。審查水位在 `tools/upstream_baseline.json`（release v0.7.4、PR 41、issue 40）。健康：2026-10-29 查到 open PR 0、Dependabot 與 Code scanning 告警各 0，`CI`、`CodeQL`、`Dependency freshness`、`Generated skills consistency`、`Upstream check` 在 `main` 最近一次皆 success；issues 在此 repo 停用，所以 issue 數是「未查到」；沒有 release（2026-10-29 `gh` 查詢）。**使用限制**：維護者 2026-10-27 政策禁止第三方 agent 經 `agy -p` 使用 Antigravity 個人訂閱，因此本 repo 的測試一律用假的 `agy`（`tests/continuation.test.mjs:85` 的 `FAKE_AGY`），任何 agent 都不得為了驗證而實際呼叫 `agy`。

## 近期：可以直接動手
| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 查清 Full gate 的時序敏感測試是環境問題還是真缺陷 | 在高負載機器上 Jobs-Observation 失敗、Modes-Continuation 與 Regressions-Recovery 批次逾時，連乾淨 base 也失敗；沒有在閒置機器上確認過 | 在閒置機器（或遠端 CI）以 `powershell.exe -NoProfile -File tools/dev_check.ps1` 跑 Full：exit 0，或對每個失敗測試給出根因並加固；`BatchTimeoutSec`、`OverallTimeoutSec` 參數維持可設定（`tools/dev_check.ps1:4-5`） | Claude Opus | 深掃報告（2026-10-26）「本機測試證據與限制」 |

## 中期：等條件成立再做
| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 同步上游新 release 或新 PR／issue | `Upstream check` workflow 在 `main` 轉為 failure（上游有未審項目，不是工具壞） | 逐筆判斷寫進 `docs/UPSTREAM.md` 與 `docs/DECISIONS.md`；`python tools/check_upstream_updates.py --strict` exit 0；完整 gate 綠後才推進 `tools/upstream_baseline.json`；PR 只打 `SanHsien/agy-staff` | Claude Sonnet | `tools/upstream_baseline.json`；`docs/DECISIONS.md` 決策一（`track: release`）；`Upstream check` workflow 結果（見現況段） |
| 以真實 `agy` 做端到端驗收 | 維護者改用 `GEMINI_API_KEY` 或 Vertex 作為驗收通道，或另行明確決定允許 | 由維護者本人在互動環境以該通道跑一次委派，結果與日期寫進 `docs/DEVELOPMENT.md`；不得由 agent 自動呼叫 `agy -p` | 維護者 | 維護者 2026-10-27 政策；`tests/continuation.test.mjs:85`（假 agy） |
| 採用停放的 Windows 非阻塞 CIM 行程查詢 patch | 在閒置機器或 CI 重現 worker 啟動被 CIM 查詢拖慢，或有使用者回報 | 重現步驟與修前耗時記錄；修正後同情境耗時下降；cancel 與清理識別測試全綠；patch 由維護者另存，完整 SHA-256 `48C72715FFFE8D8B85A98DE78C28AAB3CC80C6A04433C8D11ADB74832D21713B`；拿不到 patch 時從頭重寫 | Claude Opus | 接續開發報告（2026-10-26）「找到的未完成線索」 |
| 評估引進 OpenCode host 與 bench | 維護者核准產品範圍，要把這些納入 fork | 範圍決定寫進 `docs/DECISIONS.md`；引進後 `dev_check` Full 與 CI 綠，README 雙語同步 | 維護者 | `docs/UPSTREAM.md:93`（defer，未承諾 OpenCode host） |

## 刻意不做
| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 由 agent 自動經 `agy -p` 呼叫 Antigravity 個人訂閱（含 CI、排程、驗收腳本） | 維護者 2026-10-27 政策禁止第三方 agent 使用個人訂閱；測試以假 `agy` 覆蓋行為 | 改用 `GEMINI_API_KEY` 或 Vertex，或維護者另行明確決定 |
| 對上游提 PR、issue 或留言 | 所有對外寫入只指向 `SanHsien/agy-staff`；回貢需維護者當次對話明確授權 | 維護者在對話中明說要回貢 |
| 改寫歷史或強推以接回上游祖先 | 單一 commit 是既定做法，同步靠逐筆審查 | 不重新考慮 |
| 把帶 `freshness-hold` 的 action 顯示為 HELD 而非 NO FLOOR | 既有測試明確釘住此設計 | 維護者要求報表區分兩者 |

## 維護方式

fork：以 release 為粒度追蹤上游（`track: release`），`Upstream check` 轉紅即有待審項目，逐筆判斷後才推進水位。依賴由 Dependabot 與 `Dependency freshness` 追蹤；在 `main` 直推前跑 `tools/dev_check.ps1`，Full 逾時視為未完成，不是綠燈。
