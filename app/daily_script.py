import os
import sys

# 將專案根目錄添加到 Python 路徑中，這樣我們就可以 'from app import ...'
# 這確保無論從哪裡執行此腳本，都能找到 app 模組。
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.google_services import create_daily_check_in

# 定義儲存最新 URL 的檔案路徑
LATEST_URL_FILE = os.path.join(project_root, 'latest_form_url.txt')

def run_daily_task():
    """
    執行每日任務：建立新的打卡表單並將其 URL 儲存到檔案中。
    """
    print("開始執行每日自動化腳本...")

    # 呼叫核心功能來建立表單和試算表
    form_url = create_daily_check_in()

    if form_url:
        print(f"成功取得新的表單連結: {form_url}")
        try:
            with open(LATEST_URL_FILE, 'w') as f:
                f.write(form_url)
            print(f"已將連結儲存到檔案: {LATEST_URL_FILE}")
        except IOError as e:
            print(f"錯誤：無法將連結寫入檔案: {e}")
    else:
        print("錯誤：無法建立新的表單，今日的連結未更新。")

if __name__ == "__main__":
    run_daily_task()
    print("\n每日自動化腳本執行完畢。")
