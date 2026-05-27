import os
import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Determine which file to read based on the requested endpoint path
        filename = ""
        if self.path.endswith('/events'):
            filename = "live-events.json"
        elif self.path.endswith('/sports'):
            filename = "sports.json"
        elif self.path.endswith('/categories'):
            filename = "categories.json"

        if not filename:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found. Use /events, /sports, or /categories"}).encode('utf-8'))
            return

        # Safe directory path resolution for Vercel deployment
        base_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(base_dir, "..", filename), # Root folder fallback
            os.path.join(base_dir, filename)        # API folder fallback
        ]

        file_content = None
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        file_content = json.load(f)
                    break
                except Exception:
                    pass

        if file_content is None:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Failed to load local data file: {filename}"}).encode('utf-8'))
            return

        # Serve clean plain JSON output with CORS headers enabled
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Output clean sorted/un-sorted JSON structure directly to the response
        self.wfile.write(json.dumps(file_content, indent=4, ensure_ascii=False).encode('utf-8'))
