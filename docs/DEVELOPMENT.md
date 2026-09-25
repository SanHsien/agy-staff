# Windows 11 原生開發指南 (Development)

本文件說明在 Windows 11 原生環境（非 WSL）下建置、測試與驗收 `SanHsien/agy-staff` 的完整流程。

---

## 1. 系統需求與環境準備

- **作業系統**：Windows 11 原生環境（PowerShell 7 或 Windows PowerShell 5.1）
- **Node.js**：20.x 或更高版本（建議 22.x / 24.x / 26.x）
- **Python**：3.10 或更高版本（用於維護門禁與水位追蹤工具）
- **Git**：Git for Windows 2.40+
- **GitHub CLI (`gh`)**：已登入 `SanHsien` 帳號

### 檢查環境工具

在 PowerShell 中執行以下命令確認工具齊全：

```powershell
node --version
npm --version
python --version
git --version
gh auth status
```

---

## 2. 核心驗證門禁 (`dev_check.ps1`)

本倉庫遵循「改完必在目標平台上驗證」的原則，所有改動合併前必須執行門禁腳本：

```powershell
# 完整門禁（包含所有單元測試、Pi 一致性、語法編譯、連結檢查、上游水位）
.\tools\dev_check.ps1

# 快速通道（執行核心相容性測試與關鍵校驗）
.\tools\dev_check.ps1 -Quick
```

### 門禁包含之檢查步驟

1. **Pi 技能一致性**：執行 `npm run check:pi`，驗證 `pi-skills/` 與 `skills/` 一致。
2. **單元測試套件**：透過 Node.js 原生測試器（`node --test`）執行全套 190+ 個黑盒測試與回歸測試。
3. **Python 語法編譯**：使用 `python -m compileall -q tools` 確保維護工具無語法錯誤。
4. **文件連結檢查**：使用 `python tools/check_links.py` 驗證所有文件相對路徑。
5. **上游水位巡檢**：使用 `python tools/check_upstream_updates.py --strict` 比對上游變動。

---

## 3. 開發規範與注意事項

- **角色修改規範**：修改或新增 Persona 時，請直接編輯 `skills/<persona>/SKILL.md`。完成後執行 `npm run generate:pi` 更新對應的 Pi 擴充，再以 `npm run check:pi` 確認無遺漏。
- **測試隔離**：測試執行使用 `tests/fake-agy.mjs` 與暫存目錄，不應依賴本機網路或個人認證金鑰。
- **對外防護**：每個 clone 請確保執行 `gh repo set-default SanHsien/agy-staff`，避免意外向母倉庫送出 Pull Request。
