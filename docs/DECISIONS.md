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
- **理由**：落實 Windows 11 原生開發環境原則，消除平台誤報，確保在 Windows 上達到 100% 綠燈通過。

---

### 決策三：繁體中文主說明文件與雙語鏡像

- **背景**：本 fork 主要面向繁體中文環境的 AI 代理人與開發者，上游預設為英文 `README.md` 與簡體中文 `README.zh-CN.md`。
- **決定**：將繁體中文設置為倉庫的預設說明文件 `README.md`，英文原版保留為 `README.en.md`，並在兩份文件頂部建立雙向超連結，同時保留原有的 `README.zh-CN.md`。
- **理由**：符合艦隊共通規範（SCAFFOLD.md），確保本地閱讀體驗清晰自然。
