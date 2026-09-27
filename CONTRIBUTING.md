# 貢獻與維護指南

歡迎為 `SanHsien/agy-staff` 提出改進與建議。

本專案為維護型 fork，旨在提供 Windows 11 原生環境下的健全執行能力、水位巡檢及開發工具鏈。

---

## 提交變更原則

1. **對外邊界**：
   所有 Pull Request、issue 與分支操作預設僅限於本倉庫：
   ```powershell
   gh repo set-default SanHsien/agy-staff
   gh pr create --repo SanHsien/agy-staff --base master --head <分支>
   ```
   請確認建立完成後的 URL owner 為 `SanHsien`。

2. **本機驗證門禁**：
   在提交 commit 或建立 PR 之前，請務必在 Windows 11 原生 PowerShell 中執行門禁檢查：
   ```powershell
   .\tools\dev_check.ps1
   ```
   門禁包含全套測試、Pi 技能一致性核對、Python 工具語法編譯、文件連結有效性與上游水位巡檢，全數綠燈方可合併。

3. **角色（Persona）維護規範**：
   - 角色定義檔單一真相源位於 `skills/` 目錄。
   - 嚴禁直接手動編輯 `pi-skills/` 目錄下的檔案。
   - 修改 `skills/` 後，請執行 `npm run generate:pi` 更新對應的 Pi 檔案，並以 `npm run check:pi` 確認無遺漏。

4. **回貢上游判準**：
   - 通用相容性修復或上游明確 bug：經評估後可由維護者整理為獨立分支回貢至上游 [`keli-wen/agy-staff`](https://github.com/keli-wen/agy-staff)。
   - 本 fork 獨有的維護腳本、Windows 門禁、繁體中文文檔與 governance 規則保留在本倉庫。
