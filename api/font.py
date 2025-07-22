from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os

# --- 1. 在函式啟動時，預先載入一次我們的 JSON 字型字典 ---
# 這個設計能確保大型 JSON 檔案只會被讀取一次，後續請求速度極快。
# os.path.dirname(__file__) 確保總能找到同資料夾下的檔案。
font_path = os.path.join(os.path.dirname(__file__), 'font_data.json')
font_data = None
load_error = None

try:
    # 使用 'utf-8-sig' 來自動處理和忽略檔案開頭可能存在的 BOM 隱藏字元。
    with open(font_path, 'r', encoding='utf-8-sig') as f:
        font_data = json.load(f)
except Exception as e:
    # 如果檔案讀取失敗，將錯誤記錄下來，以便在 API 請求時回報。
    load_error = e

# --- 2. 定義 Vercel 無伺服器函式的標準處理常式 ---
class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # --- 處理字型檔載入失敗的極端情況 ---
        if font_data is None:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Font dictionary (font_data.json) could not be loaded on the server.",
                "details": str(load_error)
            }, ensure_ascii=False).encode('utf-8'))
            return

        # --- 解析傳入的 URL 參數 ---
        query_components = parse_qs(urlparse(self.path).query)
        character = query_components.get('char', [''])[0]

        if not character:
            self.send_response(400)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Query parameter 'char' is required."}).encode('utf-8'))
            return

        # --- 在預先載入的字典中，用 O(1) 的極高效率查詢字元 ---
        bitmap_data = font_data.get(character)

        # --- 根據查詢結果，回傳對應的 JSON ---
        if bitmap_data:
            # 找到了字元
            response_data = {
                "character": character,
                "bitmap": bitmap_data
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        else:
            # 在我們的字典中找不到該字元
            self.send_response(404)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": f"Character '{character}' not found in font dictionary."
            }, ensure_ascii=False).encode('utf-8'))
        return