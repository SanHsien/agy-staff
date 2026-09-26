# 證據式覆核報告 (Review)

- **覆核時間**：2026-09-26
- **覆核對象**：`SanHsien/agy-staff` @ `db8b4ef`（fork of `keli-wen/agy-staff` v0.7.3 / `f00d149`）
- **執行環境**：Windows 11 原生（PowerShell 5.1 + PowerShell 7 / Node.js v26.7.0 / Python 3.14.7 / Git for Windows 2.55.0，`tar` 為 Git for Windows 附帶的 GNU tar 1.35，排在 PATH 中 `C:\Windows\System32\tar.exe` 之前）

---

## 1. 覆核結論

**不通過，推翻前一份 REVIEW.md 的「全數通過 (Ship Ready) / 100% 綠燈」結論。**

在這台符合本 repo 自身文件（`docs/DEVELOPMENT.md`：需要 Git for Windows 2.40+）所述設定的 Windows 11 原生機器上，`tools\dev_check.ps1` 兩次獨立完整執行（含腳本內建重試）**均以非零 exit code 結束**，卡在同一個測試：`tests/pi-packaging.test.mjs` 的 `actual npm archive contains resources and runs ask + detached job collection outside checkout`。GitHub Actions 上的 Windows CI（`db8b4ef`, run `36172147919`）顯示綠燈，但那是因為 GitHub 代管的 `windows-latest` runner 上 `tar` 解析順序與本機不同，並非這個 bug 已修好；本地被文件宣稱要覆蓋的「Windows 11 原生環境」實際上仍會撞到它。

---

## 2. 實跑證據

### 2.1 `tools\dev_check.ps1`（兩次獨立全跑，含腳本自動重試批次）

第一次：`Total: 1154.4s`，第二次：`Total: 828.8s`。兩次 `Platform-Packaging` 批次的第一次嘗試與重試皆失敗，結果一致：

```text
==> [Batch: Platform-Packaging] running 3 file(s): tests/windows.test.mjs tests/pi-packaging.test.mjs tests/upstream-checker.test.mjs
...
✖ actual npm archive contains resources and runs ask + detached job collection outside checkout (13424.8291ms)
...
✖ failing tests:

test at tests\pi-packaging.test.mjs:139:1
✖ actual npm archive contains resources and runs ask + detached job collection outside checkout (13424.8291ms)
  Error: tar -xzf C:\Users\SanHsien\AppData\Local\Temp\agy-staff-test-pi-pack-Nahm6w\agy-staff-0.7.3.tgz -C C:\Users\SanHsien\AppData\Local\Temp\agy-staff-test-pi-pack-Nahm6w\extracted failed (2):

  tar (child): Cannot connect to C: resolve failed

  gzip: stdin: unexpected end of file
  tar: Child returned status 128
  tar: Error is not recoverable: exiting now

      at exec (file:///C:/GitHub/agy-staff/tests/pi-pack-helpers.mjs:9:34)
      at pack (file:///C:/GitHub/agy-staff/tests/pi-pack-helpers.mjs:23:3)
      at TestContext.<anonymous> (file:///C:/GitHub/agy-staff/tests/pi-packaging.test.mjs:142:29)
...
================ Batch Summary (Total: 828.8s) ================
[FAIL   ] Platform-Packaging         19.8s
[PASS   ] Companion-Core            135.4s
[PASS   ] Jobs-Observation          199.8s
[PASS   ] Modes-Continuation        213.4s
[PASS   ] Regressions-Recovery      222.5s
================================================================

Test suite incomplete or failed in batches: Platform-Packaging: FAIL
DEV_CHECK_EXIT=1
```

其餘四個批次（Companion-Core / Jobs-Observation / Modes-Continuation / Regressions-Recovery，共 172 個測試）兩次都全數通過；skipped 2 項（`recovery-regressions.test.mjs`、`windows.test.mjs` 各一項，皆為原上游即有、平台條件式跳過，非本 fork 新增）。第一次跑 `Jobs-Observation` 批次曾出現一次計時敏感測試（`hard deadline keeps init metadata...`）失敗、重試後通過，屬於單次偶發，非本次覆核重點，但列為待觀察項。

### 2.2 根因（已獨立重現，非測試環境雜訊）

用 Node `spawnSync('tar', ['-xzf', 'C:\...\x.tgz', '-C', 'C:\...\extracted'])`（與 `tests/pi-pack-helpers.mjs:23` 完全相同的呼叫方式）單獨重現：GNU tar（`C:\Program Files\Git\usr\bin\tar.exe`，因 Git for Windows 安裝將自身 bin 目錄排在 PATH 較前）把 `C:\...` 開頭、冒號在第一個斜線之前的路徑，誤判成 `host:path` 遠端封存語法，因此嘗試連線到主機 `C`。這台機器同時也有 Windows 內建的 `C:\Windows\System32\tar.exe`（bsdtar，無此問題），但 PATH 順序讓 Git 版本先被找到。

`tests/pi-pack-helpers.mjs` 這支測試輔助檔**在本 fork 完全沒有改過**（`git diff upstream/master..HEAD -- tests/pi-pack-helpers.mjs` 為空）——換句話說，`docs/DECISIONS.md`「決策二：Windows 11 原生相容性修復與測試硬化」聲稱已讓「全套測試在 Windows 原生環境綠燈通過」，但漏掉了同一個 `pi-packaging.test.mjs` 檔案裡的這個測試。這不是本次交付新增的迴歸，而是先前三次 Windows 相容性修復（`windows.test.mjs` 的 `where.exe`/`.cmd` 封裝、`fs.symlinkSync` 的 EPERM 防護、`streaming.test.mjs` 輪詢次數）都沒有覆蓋到的既有缺口，且與「Windows 原生 100% 綠燈」的宣稱直接矛盾。

嘗試的修復方向（`--force-local`、正斜線路徑）在本機測試中仍會因 Git 版 tar 的 MSYS 路徑轉譯而以另一種方式失敗，未能在本次覆核時間內驗證出一個可靠的最小修復，因此**未直接修改測試碼**，改列為待決問題（見第 4 節）。

---

## 3. CI 現況

```
gh run list --limit 3
completed  success  ci(gate): implement fresh-process batches and remove file-level test …  CI                            master  push  36172147919  10m52s  2026-09-25T18:14:26Z
completed  success  ci(gate): implement fresh-process batches and remove file-level test …  Generated skills consistency  master  push  36172147796     8s   2026-09-25T18:14:26Z
completed  success  ci(gate): implement fresh-process batches and remove file-level test …  CodeQL                        master  push  36172147716  1m29s  2026-09-25T18:14:25Z
```

`master`（`db8b4ef`）上三個 required workflow 皆綠燈，包含 `test-windows`（GitHub `windows-latest` runner）。但如第 2.2 節所述，GitHub runner 上這個測試沒有觸發同一個 PATH 排序問題，不代表這個 bug 不存在。

---

## 4. 待決問題（需維護者決定，本次未動）

1. **（中）`tests/pi-packaging.test.mjs` 的 tar 解壓在本機 Windows 環境會失敗**，見第 2 節。建議方向二選一（或都做）：
   - 讓 `tests/pi-pack-helpers.mjs` 明確呼叫 `C:\Windows\System32\tar.exe`（bsdtar）而非依賴 PATH 中第一個 `tar`；
   - 或改用 Node 內建 zlib + 一個不吃 GNU tar 遠端語法的最小 tar 解包（或 `npm` 套件如 `tar`）取代外部 `tar.exe` 呼叫。
   兩個方向都需要在真正的 Windows 機器上重新驗證，本次覆核時間內未能收斂出可信的一行修復，故未直接改動。
2. **（低）`Jobs-Observation` 批次首跑出現一次計時敏感測試失敗、重試後通過**（`hard deadline keeps init metadata and recovery configuration despite unrelated state.last`，位於 `tests/streaming.test.mjs` 或 `tests/observation.test.mjs` 家族，重試通過代表非穩定重現，未進一步鎖定行號）。建議觀察是否為時序 flaky，非本次修復範圍。

---

## 5. 本次已修復

- `AGENTS.md`「常用指令」區塊仍列著舊的 `node --test --test-timeout=60000 --test-concurrency=1 tests/*.test.mjs`，與目前 `package.json` 的 `npm test`（`node --test --test-concurrency=1 tests/*.test.mjs`，已移除 `--test-timeout`）及 `tools/dev_check.ps1` 的 fresh-process 批次機制不一致，已同步修正為與 `npm test` 一致的指令。

---

## 6. Dependabot 建議

- `.github/dependabot.yml` 已存在（上游繼承），涵蓋 `github-actions` 與 `npm` 兩個 ecosystem 的每週更新掃描。
- `gh api repos/SanHsien/agy-staff/vulnerability-alerts` 回傳 `204 No Content`，代表本 fork 的 Dependabot 安全性警示（vulnerability alerts）**已經是啟用狀態**，不需要額外開啟。
- `package.json` 目前無任何 `dependencies` / `devDependencies`（零依賴專案），因此 npm 生態的 Dependabot 警示短期內預期不會有實際觸發項；主要價值在 `github-actions` 這個 ecosystem（`actions/checkout`、`actions/setup-node` 等）。建議維持現狀即可，不需調整設定。
