from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os

# 在函式啟動時，預先載入一次我們的 JSON 字型字典
font_path = os.path.join(os.path.dirname(__file__), 'font_data.json')
with open(font_path, 'r', encoding='utf-8-sig') as f:
    font_data = json.load(f)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        # 【升級】讀取 "string" 參數，而不是 "char"
        input_string = query_components.get('string', [''])[0]

        if not input_string:
            self.send_response(400)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Query parameter 'string' is required."}).encode('utf-8'))
            return

        # 【升級】遍歷字串中的每一個字，建立一個結果列表
        bitmap_list = []
        for character in input_string:
            bitmap_data = font_data.get(character)
            # 如果在字典中找到了字，就加入到結果列表中
            if bitmap_data:
                bitmap_list.append({
                    "char": character,
                    "bitmap": bitmap_data
                })
        
        # 準備最終的回傳資料
        response_data = {
            "string": input_string,
            "bitmaps": bitmap_list
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        return