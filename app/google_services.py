import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# -- 設定 --
# Google API 存取範圍
# 如果修改這些範圍，請刪除 token.json 檔案。
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/forms",
    "https://www.googleapis.com/auth/spreadsheets"
]

# 您的 Google 雲端硬碟資料夾 ID
# 從資料夾 URL https://drive.google.com/drive/folders/YOUR_FOLDER_ID 中提取
DRIVE_FOLDER_ID = "1SrtoTcNA-dVlbmjf6Af5JhB1EJqbXPr0"

# 憑證檔案路徑
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'


def get_google_services():
    """
    執行 Google API 認證並回傳 Drive, Forms, Sheets 的服務物件。
    如果 token.json 不存在或無效，會啟動瀏覽器要求使用者手動授權。
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        drive_service = build('drive', 'v3', credentials=creds)
        forms_service = build('forms', 'v1', credentials=creds)
        sheets_service = build('sheets', 'v4', credentials=creds)
        return drive_service, forms_service, sheets_service
    except HttpError as error:
        print(f"建立服務時發生錯誤: {error}")
        return None, None, None


def create_daily_check_in():
    """
    建立每日打卡用的 Google 表單和對應的 Google 試算表。
    1. 取得 Google API 服務。
    2. 建立 Google 試算表作為回應目的地。
    3. 建立 Google 表單。
    4. 將表單連結到試算表。
    5. 回傳表單的公開作答連結。
    """
    drive_service, forms_service, sheets_service = get_google_services()
    if not all([drive_service, forms_service, sheets_service]):
        return None

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    form_title = f"【{today_str}】學生到校打卡"
    sheet_title = f"【{today_str}】打卡回應"

    try:
        # 1. 建立 Google 試算表
        print(f"正在建立試算表: {sheet_title}...")
        sheet_metadata = {
            'properties': {'title': sheet_title},
            'parents': [DRIVE_FOLDER_ID] # 指定父資料夾
        }
        sheet = sheets_service.spreadsheets().create(body=sheet_metadata).execute()
        sheet_id = sheet['spreadsheetId']
        sheet_url = sheet['spreadsheetUrl']
        print(f"試算表建立成功！URL: {sheet_url}")

        # 2. 建立 Google 表單
        print(f"正在建立表單: {form_title}...")
        form_metadata = {
            "info": {
                "title": form_title,
                "documentTitle": form_title
            },
            "parents": [DRIVE_FOLDER_ID] # 指定父資料夾
        }

        # 建立一個新的表單
        new_form = forms_service.forms().create(body=form_metadata).execute()
        form_id = new_form['formId']
        form_url = new_form['responderUri']

        # 3. 更新表單，加入問題並連結試算表
        update_request = {
            "requests": [
                # 新增一個問題 (例如：學號)
                {
                    "createItem": {
                        "item": {
                            "title": "請輸入您的學號",
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "textQuestion": {}
                                }
                            }
                        },
                        "location": {"index": 0}
                    }
                },
                # 設定表單描述
                {
                    "updateFormInfo": {
                        "info": {
                            "description": "請輸入學號後提交，完成打卡。"
                        },
                        "updateMask": "description"
                    }
                },
                # 連結到已建立的試算表
                {
                    "updateFormSettings": {
                        "settings": {
                            "linkedSheetId": sheet_id
                        },
                        "updateMask": "linkedSheetId"
                    }
                }
            ]
        }

        forms_service.forms().batchUpdate(formId=form_id, body=update_request).execute()

        # 移動表單到指定資料夾 (Create API v3 似乎不直接支援 parent)
        # 我們在建立時已指定 parent，但如果不行，可以用這個備用方法
        file = drive_service.files().get(fileId=form_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        drive_service.files().update(
            fileId=form_id,
            addParents=DRIVE_FOLDER_ID,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()

        print(f"表單建立並設定成功！公開連結: {form_url}")
        return form_url

    except HttpError as error:
        print(f"在建立過程中發生錯誤: {error}")
        return None

if __name__ == '__main__':
    # 這段程式碼只在直接執行此檔案時才會運行，方便進行單獨測試
    print("正在測試建立每日打卡表單...")
    # 提醒：執行前請確認您已將 credentials.json 放在專案根目錄
    if not os.path.exists(CREDENTIALS_FILE):
        print("錯誤：找不到 credentials.json 檔案！")
        print("請根據 README.md 的說明，將憑證檔案放到專案根目錄。")
    else:
        public_url = create_daily_check_in()
        if public_url:
            print("\n測試成功！")
            print(f"取得的表單公開連結為: {public_url}")
        else:
            print("\n測試失敗。請檢查上面的錯誤訊息。")
