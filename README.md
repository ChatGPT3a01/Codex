# 學生到校打卡系統 (Student Check-in System)

這是一個自動化的學生打卡系統。它會每天自動生成一個新的 Google 表單，並透過一個簡單的網頁顯示該表單的 QR Code，方便學生掃描打卡。

## 核心功能

- **每日自動更新**：每天自動建立一個新的 Google 表單和對應的 Google 試算表。
- **動態 QR Code**：網頁上顯示的 QR Code 會自動指向當天最新的打卡表單。
- **簡易部署**：專為在伺服器或無伺服器環境（如 Google Cloud Functions）中運行而設計。
- **Google 服務整合**：使用 Google Drive API 和 Google Forms API 進行全自動化管理。

## 專案結構

```
/student-check-in
|-- app/
|   |-- __init__.py
|   |-- app.py                # Flask 網頁應用程式
|   |-- daily_script.py       # 每日自動化腳本
|   |-- google_services.py    # Google API 互動模組
|   |-- templates/
|   |   |-- index.html        # 前端顯示頁面
|-- credentials.json          # Google API 憑證 (需要手動建立)
|-- token.json                # 自動產生的授權權杖
|-- latest_form_url.txt       # 儲存最新的表單連結
|-- requirements.txt          # Python 依賴項目
|-- .gitignore                # Git 忽略清單
|-- README.md                 # 專案說明文件
```

## 設定步驟

### 1. 取得 Google API 憑證 (`credentials.json`)

為了讓此專案能夠存取您的 Google 雲端硬碟並代表您建立檔案，您需要設定一個 Google Cloud 專案並取得 OAuth 2.0 憑證。

**步驟如下：**

1.  **前往 Google Cloud Console**：
    - 打開 [Google Cloud Console](https://console.cloud.google.com/)。
    - 如果您還沒有專案，請建立一個新專案。

2.  **啟用必要的 API**：
    - 在您的專案儀表板中，前往「API 和服務」>「已啟用的 API 和服務」。
    - 點擊「+ 啟用 API 和服務」。
    - 搜尋並啟用以下三個 API：
        - **Google Drive API**
        - **Google Forms API**
        - **Google Sheets API**

3.  **設定 OAuth 同意畫面**：
    - 前往「API 和服務」>「OAuth 同意畫面」。
    - 選擇「外部」，然後點擊「建立」。
    - **應用程式名稱**：填寫一個您認得出的名稱（例如："學生打卡系統"）。
    - **使用者支援電子郵件**：選擇您的電子郵件地址。
    - **開發人員聯絡資訊**：再次輸入您的電子郵件地址。
    - 點擊「儲存並繼續」。
    - **範圍**：點擊「新增或移除範圍」，然後手動新增以下三個範圍 (第三個是為了Sheets API)：
        - `https://www.googleapis.com/auth/drive`
        - `https://www.googleapis.com/auth/forms`
        - `https://www.googleapis.com/auth/spreadsheets`
    - 點擊「更新」，然後「儲存並繼續」。
    - **測試使用者**：點擊「+ 新增使用者」，然後輸入您自己的 Google 帳號。在開發階段，只有測試使用者可以授權應用程式。
    - 點擊「儲存並繼續」。

4.  **建立 OAuth 2.0 用戶端 ID**：
    - 前往「API 和服務」>「憑證」。
    - 點擊「+ 建立憑證」，然後選擇「OAuth 用戶端 ID」。
    - **應用程式類型**：選擇「桌面應用程式」。
    - **名稱**：可以保留預設名稱，或自訂一個。
    - 點擊「建立」。

5.  **下載憑證檔案**：
    - 建立成功後，會彈出一個視窗顯示您的用戶端 ID 和密鑰。點擊「下載 JSON」。
    - 將下載的檔案重新命名為 `credentials.json`，並將其放置在專案的根目錄下。

### 2. 安裝專案依賴

首先，建議建立一個 Python 虛擬環境：

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

然後，安裝 `requirements.txt` 中列出的所有函式庫：

```bash
pip install -r requirements.txt
```

### 3. 首次執行以取得授權 (`token.json`)

在您第一次執行腳本之前，需要先進行一次性的手動授權，讓應用程式可以存取您的 Google 帳號。

執行每日腳本：

```bash
python app/daily_script.py
```

- 程式會自動在瀏覽器中打開一個 Google 授權頁面。
- 請登入您在「測試使用者」中設定的 Google 帳號。
- 同意應用程式存取您的 Google 雲端硬碟和表單。
- 授權成功後，腳本會自動在專案根目錄下建立一個 `token.json` 檔案。這個檔案儲存了您的授權憑證，未來的執行將不再需要手動授權。

**注意**：首次執行可能會因為還沒有 `latest_form_url.txt` 而在網頁端報錯，這是正常的。成功產生 `token.json` 和 `latest_form_url.txt` 即可。

## 使用方法

### 1. 每日自動執行

設定一個排程任務（例如 Linux 的 `cron` job 或 Windows 的工作排程器），每天定時執行 `daily_script.py`。

例如，設定一個 `cron` job 在每天早上 6 點執行：

```cron
0 6 * * * /path/to/your/project/venv/bin/python /path/to/your/project/app/daily_script.py
```

這會自動建立新的 Google 表單和試算表，並更新 `latest_form_url.txt`。

### 2. 啟動網頁應用程式

執行 `app.py` 來啟動 Flask 網頁伺服器：

```bash
python app/app.py
```

伺服器預設會在 `http://127.0.0.1:5000` 上運行。打開這個網址，您就會看到當天最新的打卡 QR Code。

## 部署

此專案可以輕易地部署到各種平台。

### 部署到 Google Cloud Functions

1.  **HTTP 觸發器**：建立一個 HTTP 觸發的 Cloud Function，將 `app.py` 中的邏輯作為其進入點。
2.  **排程觸發器**：建立一個由 Cloud Scheduler 觸發的 Cloud Function，將 `daily_script.py` 的邏輯作為其進入點。
3.  **檔案儲存**：`credentials.json` 和 `token.json` 可以使用 Secret Manager 進行安全儲存。`latest_form_url.txt` 則可以改用一個簡單的雲端儲存服務（如 Google Cloud Storage）或資料庫（如 Firestore）來存放。

---

**重要提示**：請務必保護好您的 `credentials.json` 和 `token.json` 檔案，不要將它們上傳到公開的 GitHub 儲存庫中。建議將它們加入 `.gitignore` 檔案。
