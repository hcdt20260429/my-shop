import os
import json
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 從環境變數獲取 Google 服務帳戶憑證
creds_json = os.environ.get("GOOGLE_CREDENTIALS")
if not creds_json:
    raise ValueError("GOOGLE_CREDENTIALS environment variable not set.")

# 將 JSON 字串轉換為字典
creds_info = json.loads(creds_json)

# 設置 Google Drive API 範圍
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# 構建憑證對象
creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)

# 構建 Drive API 服務對象
service = build("drive", "v3", credentials=creds)

# 您的 Google Drive 資料夾 ID
# 請替換為您的實際資料夾 ID
FOLDER_ID = "1GPHOg02T2ABewVAtFgIUiSBeiwmqgGK6"

products = []
page_token = None

# 提取檔名前綴：只保留「字母+數字」部分
def extract_product_code(filename):
    match = re.match(r"^([A-Za-z]+\d+)", filename)
    return match.group(1) if match else filename

while True:
    # 查詢資料夾中的圖片檔案
    results = service.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType contains 'image/' and trashed = false",
        fields="nextPageToken, files(id, name)",
        pageSize=100, # 每次最多獲取 100 個檔案
        pageToken=page_token
    ).execute()
    
    items = results.get("files", [])

    for item in items:
        file_name = item["name"]
        file_id = item["id"]
        # 過濾掉非圖片檔案，雖然查詢已經篩選，但再次確認更安全
        if file_name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")):
            products.append({
                "name": extract_product_code(file_name),
                "id": file_id
            })
    
    page_token = results.get("nextPageToken", None)
    if not page_token:
        break

# 將結果寫入 products.json 檔案
with open("products.json", "w", encoding="utf-8") as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"Successfully updated products.json with {len(products)} items.")
