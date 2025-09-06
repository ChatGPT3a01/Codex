import os
import io
import base64
from flask import Flask, render_template

# 建立 Flask 應用程式實例
# template_folder 指向 'app/templates'
app = Flask(__name__, template_folder='templates')

# 取得專案根目錄
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LATEST_URL_FILE = os.path.join(project_root, 'latest_form_url.txt')


@app.route('/')
def index():
    """
    主頁面路由，負責產生並顯示 QR Code。
    """
    form_url = None
    error_message = None
    qr_code_image = None

    try:
        # 從檔案中讀取最新的 Google 表單 URL
        with open(LATEST_URL_FILE, 'r') as f:
            form_url = f.read().strip()

        if not form_url:
            error_message = "錯誤：找不到表單連結。請先執行每日自動化腳本。"
    except FileNotFoundError:
        error_message = "錯誤：'latest_form_url.txt' 檔案不存在。請執行每日腳本以產生連結。"
    except Exception as e:
        error_message = f"讀取連結時發生未知錯誤: {e}"

    if form_url:
        try:
            # 如果有 URL，就動態生成 QR Code
            import qrcode

            # 產生 QR Code 圖片
            img = qrcode.make(form_url)

            # 將圖片儲存到記憶體中的 byte buffer
            buf = io.BytesIO()
            img.save(buf, format='PNG')

            # 將 buffer 中的資料進行 Base64 編碼，以便在 HTML 中直接顯示
            qr_code_image = base64.b64encode(buf.getvalue()).decode('utf-8')

        except Exception as e:
            error_message = f"產生 QR Code 時發生錯誤: {e}"

    # 渲染 HTML 樣板，並傳入 QR Code 圖片資料或錯誤訊息
    return render_template('index.html', qr_code_image=qr_code_image, error_message=error_message)


if __name__ == '__main__':
    # 啟動 Flask 開發伺服器
    # host='0.0.0.0' 讓伺服器可以從區域網路中的其他裝置存取
    app.run(debug=True, host='0.0.0.0', port=5000)
