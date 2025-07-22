from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os

# 在函式啟動時，預先載入一次我們的 JSON 字型字典
font_path = os.path.join(os.path.dirname(__file__), 'font_data.json')
with open(font_path, 'r', encoding='utf-8') as f:
    font_data = json.load(f)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        character = query_components.get('char', [''])[0]

        if not character:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Character not provided"}).encode())
            return

        bitmap_data = font_data.get(character)

        if bitmap_data:
            response_data = {
                "character": character,
                "bitmap": bitmap_data
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Character '{character}' not found"}).encode())
        return