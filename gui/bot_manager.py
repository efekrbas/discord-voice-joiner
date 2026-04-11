import asyncio
import json
import aiohttp
import random
import logging
from discord_api import fetch_fingerprint

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BotManager")

class DiscordBot:
    def __init__(self, token, bot_manager):
        self.token = token
        self.bot_manager = bot_manager
        self.username = "Unknown"
        self.status = "Disconnected"
        self.ws = None
        self.heartbeat_task = None
        self.session_id = None
        self.guild_id = None
        self.channel_id = None
        self.self_mute = False
        self.self_deaf = False
        self.self_video = False
        self.self_stream = False
        self.should_reconnect = True

    async def connect(self, guild_id=None, channel_id=None):
        if guild_id: self.guild_id = guild_id
        if channel_id: self.channel_id = channel_id
        
        self.should_reconnect = True
        self.status = "Connecting..."
        
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Fetch fingerprint for Gateway
            f_print = await fetch_fingerprint(session, {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"})
            ws_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "X-Fingerprint": f_print if f_print else ""
            }
            
            while self.should_reconnect:
                try:
                    print(f"[LOG] {self.token[:10]}... Connecting to WebSocket...")
                    async with session.ws_connect(
                        'wss://gateway.discord.gg/?v=10&encoding=json',
                        proxy=None,
                        headers=ws_headers
                    ) as ws:
                        self.ws = ws
                        
                        msg = await asyncio.wait_for(ws.receive(), timeout=10)
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            hello_json = json.loads(msg.data)
                            heartbeat_interval = hello_json['d']['heartbeat_interval'] / 1000
                            print(f"[LOG] {self.token[:10]}... Hello received.")
                        else: break
                        
                        self.heartbeat_task = asyncio.create_task(self.heartbeat(heartbeat_interval))
                        
                        # Identify
                        await ws.send_json({
                            'op': 2,
                            'd': {
                                'token': self.token,
                                'capabilities': 16383,
                                'properties': {
                                    'os': 'Windows', 'browser': 'Discord Client', 'release_channel': 'stable',
                                    'client_version': '1.0.9142', 'os_version': '10.0.22631', 'os_arch': 'x64',
                                    'system_locale': 'tr-TR', 'client_build_number': 522553, 'native_build_number': '53018',
                                    'client_event_source': None, 'design_id': 0
                                },
                                'presence': {'status': 'online', 'since': 0, 'activities': [], 'afk': False},
                                'compress': False,
                                'client_state': {
                                    'guild_versions': {}, 'highest_last_message_id': '0', 'read_state_version': 0,
                                    'user_guild_settings_version': -1, 'user_settings_version': -1,
                                    'private_channels_version': '0', 'api_code_version': 0
                                },
                                'presence': {
                                    'status': self.presence_status, 
                                    'since': None, 
                                    'activities': [], 
                                    'afk': False
                                }
                            }
                        })
                        
                        ready_received = False
                        while self.should_reconnect:
                            res = await asyncio.wait_for(ws.receive(), timeout=20)
                            if res.type == aiohttp.WSMsgType.TEXT:
                                data = json.loads(res.data)
                                if data.get('t') == 'READY':
                                    self.session_id = data['d'].get('session_id')
                                    u = data['d'].get('user', {})
                                    self.username = u.get('username', 'Unknown')
                                    print(f"[LOG] {self.token[:10]}... READY! Hello {self.username}")
                                    self.status = "Connected"
                                    ready_received = True
                                    break
                                elif data.get('op') == 9: break
                            elif res.type in [aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR]: break
                        
                        if not ready_received: break
                        
                        if self.guild_id and self.channel_id:
                            await self.send_voice_state()
                        
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                data = json.loads(msg.data)
                                if data.get('op') == 7: break
                            elif msg.type in [aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.ERROR]: break
                            
                except Exception as e:
                    if self.should_reconnect:
                        self.status = f"Error: {str(e)[:15]}"
                        print(f"[ERR] {self.token[:10]}... Exception: {e}")
                        await asyncio.sleep(5)
                    else: break

    async def heartbeat(self, interval):
        while self.ws and not self.ws.closed:
            try:
                await asyncio.sleep(interval)
                await self.ws.send_json({'op': 1, 'd': random.randint(1, 1000000)})
            except: break

    async def send_voice_state(self):
        if self.ws and not self.ws.closed:
            payload = {
                'op': 4,
                'd': {
                    'guild_id': str(self.guild_id) if self.guild_id else None,
                    'channel_id': str(self.channel_id) if self.channel_id else None,
                    'self_mute': bool(self.self_mute),
                    'self_deaf': bool(self.self_deaf),
                    'self_video': bool(self.self_video)
                }
            }
            print(f"[LOG] {self.token[:10]}... Voice State Update -> Mute: {self.self_mute}, Deaf: {self.self_deaf}, Video: {self.self_video}")
            await self.ws.send_json(payload)

    async def update_audio(self, mute=None, deaf=None):
        if mute is not None: self.self_mute = mute
        if deaf is not None: self.self_deaf = deaf
        await self.send_voice_state()

    async def update_video(self, video=None):
        if video is not None: self.self_video = video
        await self.send_voice_state()

    async def update_stream(self, stream=None):
        if stream is not None: self.self_stream = stream
        if self.ws and not self.ws.closed and self.channel_id:
            op = 18 if self.self_stream else 19
            label = "CREATE" if self.self_stream else "DELETE"
            payload = {
                'op': op,
                'd': {
                    'type': 'guild',
                    'guild_id': str(self.guild_id) if self.guild_id else None,
                    'channel_id': str(self.channel_id) if self.channel_id else None,
                    'preferred_region': None
                }
            }
            print(f"[LOG] {self.token[:10]}... Sending Stream {label}...")
            try:
                await self.ws.send_json(payload)
                # DO NOT call send_voice_state here to avoid re-syncing voice
            except Exception as e:
                print(f"[ERR] {self.token[:10]}... Stream Sync Error: {e}")
        else:
            print(f"[WARN] {self.token[:10]}... Stream Fail: Bot not in channel or WS closed.")

    async def join_channel(self, guild_id, channel_id):
        self.guild_id = str(guild_id)
        self.channel_id = str(channel_id)
        if not self.ws or self.ws.closed:
            asyncio.create_task(self.connect())
        else:
            await self.send_voice_state()

    async def leave_channel(self):
        if self.ws and not self.ws.closed:
            print(f"[LOG] {self.token[:10]}... Leaving channel...")
            await self.ws.send_json({
                'op': 4,
                'd': {'guild_id': str(self.guild_id) if self.guild_id else None, 'channel_id': None, 'self_mute': False, 'self_deaf': False}
            })
            self.channel_id = None

    async def stop(self):
        self.should_reconnect = False
        await self.leave_channel()
        if self.ws: await self.ws.close()
        if self.heartbeat_task: self.heartbeat_task.cancel()
        self.status = "Disconnected"

class BotManager:
    def __init__(self):
        self.bots = {}

    def add_token(self, token):
        if token not in self.bots: self.bots[token] = DiscordBot(token, self)
        return self.bots[token]

    async def join_all(self, guild_id, channel_id):
        for bot in self.bots.values():
            asyncio.create_task(bot.join_channel(guild_id, channel_id))
            await asyncio.sleep(2.0)

    async def stop_all(self):
        for bot in self.bots.values(): await bot.stop()
