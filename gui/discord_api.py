import aiohttp
import asyncio
import json
import base64
import random
import re

async def fetch_fingerprint(session, headers):
    # REAL April 2026: Fetching fingerprint from experiments is mandatory for joins
    url = "https://discord.com/api/v10/experiments"
    try:
        async with session.get(url, headers=headers) as resp:
            f_print = resp.headers.get("X-Discord-Fingerprint")
            if f_print:
                return f_print
    except:
        pass
    return None

async def get_mobile_headers(token):
    # REAL April 3, 2026 Build 522553 stable (Android level)
    props = {
        "os": "Android",
        "browser": "",
        "device": "SM-G998B",
        "system_locale": "tr-TR",
        "client_version": "322.11",
        "release_channel": "stable",
        "device_advertiser_id": "00000000-0000-0000-0000-000000000000",
        "os_version": "14",
        "client_build_number": 322110,
        "native_build_number": "322110",
        "client_state_version": 42,
        "client_event_source": None
    }
    props_json = json.dumps(props, separators=(',', ':'))
    props_b64 = base64.b64encode(props_json.encode()).decode()
    
    context = base64.b64encode(json.dumps({"location": "Invite Link"}).encode()).decode()
    
    return {
        "Authorization": token,
        "User-Agent": "Discord-Android/322110; SM-G998B; Android/14",
        "Content-Type": "application/json",
        "X-Super-Properties": props_b64,
        "X-Context-Properties": context,
        "X-Discord-Locale": "tr",
        "X-Discord-Timezone": "Europe/Istanbul",
        "Accept-Language": "tr-TR,en-US;q=0.9",
        "Accept": "*/*"
    }

async def get_desktop_headers(token):
    # REAL April 3, 2026 Build 522553 stable (Final Integrity Fix)
    props = {
        "os": "Windows", "browser": "Discord Client", "release_channel": "stable",
        "client_version": "1.0.9015", "os_version": "10.0.22631", "os_arch": "x64",
        "system_locale": "tr-TR", "client_build_number": 522553,
        "native_build_number": "53018", "client_state_version": 42,
        "client_event_source": None
    }
    props_json = json.dumps(props, separators=(',', ':'))
    props_b64 = base64.b64encode(props_json.encode()).decode()
    context = base64.b64encode(json.dumps({"location": "Invite Link"}).encode()).decode()
    return {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "X-Super-Properties": props_b64,
        "X-Context-Properties": context,
        "X-Discord-Locale": "tr",
        "Referer": "https://discord.com/channels/@me",
        "Origin": "https://discord.com"
    }

async def join_server(token, invite_code, session_id=None):
    match = re.search(r"(?:discord\.gg/|discord\.com/invites/|discord\.com/api/v10/invites/)?([a-zA-Z0-9-]+)", invite_code)
    if match: invite_code = match.group(1)
    
    url_experiments = "https://discord.com/api/v10/experiments"
    url_join = f"https://discord.com/api/v10/invites/{invite_code}"
    
    jar = aiohttp.CookieJar(unsafe=True)
    async with aiohttp.ClientSession(cookie_jar=jar) as session:
        headers = await get_desktop_headers(token) # Desktop integrity is more robust in v11
        try:
            # 1. Fetch valid Fingerprint from Experiments (Mandatory April 2026)
            print(f"[API] {token[:10]}... Fetching experiments fingerprint...")
            f_print = await fetch_fingerprint(session, headers)
            if f_print:
                headers["X-Discord-Fingerprint"] = f_print
                print(f"[API] {token[:10]}... Experiments Fingerprint acquired.")
            
            await asyncio.sleep(random.uniform(5.0, 8.5))
            
            # 2. Join POST 
            payload = {"client_state_version": 42}
            if session_id: payload["session_id"] = str(session_id)

            async with session.post(url_join, headers=headers, json=payload) as resp:
                status = resp.status
                data = await resp.json()
                
                if status in [200, 201]:
                    print(f"[API] {token[:10]}... SUCCESS! (v11 Accepted)")
                    return True, "Success"
                else:
                    msg = data.get('message', 'Unknown Error')
                    if 'captcha_key' in data:
                        # If we STILL get this, it's a hard IP limit or token flag
                        msg = f"Integrity Block: {data['captcha_key'][0]}"
                    
                    print(f"[API DEBUG] Full Response: {data}")
                    return False, f"{msg} ({status})"
                    
        except Exception as e:
            return False, f"Exception: {str(e)}"

async def check_token(token):
    url = "https://discord.com/api/v9/users/@me"
    headers = await get_desktop_headers(token)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as resp:
                return resp.status == 200
        except: return False
