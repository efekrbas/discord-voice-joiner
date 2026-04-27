_S='desktop'
_R='Discord'
_Q='windows'
_P=''
_O=''
_N='properties'
_M='heartbeat_interval'
_L='> Channel ID: '
_K='> Server ID: '
_J='tokens.txt'
_I="Don't forget to put your tokens in Tokens.txt"
_H='self_deaf'
_G='self_mute'
_F='channel_id'
_E='guild_id'
_D=False
_C=True
_B='op'
_A='d'

from pystyle import *
import os
from colorama import *
import time, asyncio, json, websockets
import random

os.system('clear' if os.name == 'posix' else 'cls')

intro = r'''

  ___ ___ ___  ___ ___  ___ ___   __   _____ ___ ___ ___      _  ___ ___ _  _ ___ ___ 
 |   \_ _/ __|/ __/ _ \| _ \   \  \ \ / / _ \_ _/ __| __|  _ | |/ _ \_ _| \| | __| _ \
 | |) | |\__ \ (_| (_) |   / |) |  \ V / (_) | | (__| _|  | || | (_) | || .` | _||   /
 |___/___|___/\___\___/|_|_\___/    \_/ \___/___\___|___|  \__/ \___/___|_|\_|___|_|_\

                         (github.com/efekrbas/discord-voice-joiner)                                             
                                                                                                                           
                                                                                                                                                                                                                                                                                                            
                                                                      
                                                                      
                                    > Press Enter                                         
'''

Anime.Fade(Center.Center(intro), Colors.cyan_to_blue, Colorate.Vertical, interval=.035, enter=_C)

print(fr"""{Fore.LIGHTBLUE_EX}
                                                                                                                                                
  ___ ___ ___  ___ ___  ___ ___   __   _____ ___ ___ ___      _  ___ ___ _  _ ___ ___ 
 |   \_ _/ __|/ __/ _ \| _ \   \  \ \ / / _ \_ _/ __| __|  _ | |/ _ \_ _| \| | __| _ \
 | |) | |\__ \ (_| (_) |   / |) |  \ V / (_) | | (__| _|  | || | (_) | || .` | _||   /
 |___/___|___/\___\___/|_|_\___/    \_/ \___/___\___|___|  \__/ \___/___|_|\_|___|_|_\

                         (github.com/efekrbas/discord-voice-joiner)                                             
                                                                        
                                                                                                                           
                                                                                                                                                                                                                                                                           
                                                                      
""")
time.sleep(1)

# Limit max connections to process tokens in bulk
MAX_WORKERS = 20  # Limit concurrent connections to protect internet
RECONNECT_DELAY = 10  # Reconnection delay after error (seconds)
HEARTBEAT_MULTIPLIER = 1.5  # Increase heartbeat interval to reduce load

print(_I)
with open(_J, 'r') as token_file:
    tokens = []
    for t in token_file.readlines():
        token = t.strip()
        if not token or token.startswith('//'):
            continue
        token = token.strip('"').strip("'").strip()
        if token:
            tokens.append(token)
def ask_id(prompt):
    while True:
        value = input(prompt).strip()
        if value.isdigit():
            return value
        os.system('clear' if os.name == 'posix' else 'cls')

def ask_yn(prompt):
    while True:
        value = input(prompt).strip().lower()
        if value in ['y', 'n']:
            return value == 'y'


server_id = ask_id(_K)
channel_id = ask_id(_L)
deafen = ask_yn("> Deafen: (y/n) ")
mute = ask_yn("> Mute: (y/n) ")
stream = ask_yn("> Stream: (y/n) ")
video = ask_yn("> Video: (y/n) ")

print_lock = asyncio.Lock()

first_log = True

async def typewrite_log(token_str):
    global first_log
    full_text = f"[+] {token_str}"
    if not first_log:
        print()
    else:
        first_log = False
        
    print(Fore.GREEN, end='', flush=True)
    for char in full_text:
        print(char, end='', flush=True)
        await asyncio.sleep(0.01)
    print(Fore.RESET, end='', flush=True)

async def connect(token):
    logged = False
    while _C:
        try:
            async with websockets.connect(
                'wss://gateway.discord.gg/?v=10&encoding=json',
                ping_interval=30,
                ping_timeout=60,
                max_size=None
            ) as websocket:
                hello = await websocket.recv()
                hello_json = json.loads(hello)
                heartbeat_interval = hello_json[_A][_M] * HEARTBEAT_MULTIPLIER
                await websocket.send(json.dumps({
                    _B: 2,
                    _A: {'token': token, _N: {'': _Q, _O: _R, _P: _S}}
                }))

                ready_received = False
                while True:
                    try:
                        msg = await asyncio.wait_for(websocket.recv(), timeout=20)
                        data = json.loads(msg)
                        if data.get('t') == 'READY':
                            ready_received = True
                            break
                    except Exception:
                        break

                if not ready_received:
                    raise Exception("READY event not received")

                await websocket.send(json.dumps({
                    _B: 4,
                    _A: {_E: server_id, _F: channel_id, _G: mute, _H: deafen, 'self_video': video}
                }))
                if not logged:
                    async with print_lock:
                        await typewrite_log(token)
                    logged = True

                if stream:
                    await asyncio.sleep(1)
                    await websocket.send(json.dumps({
                        'op': 18,
                        'd': {
                            'type': 'guild',
                            'guild_id': server_id,
                            'channel_id': channel_id,
                            'preferred_region': None
                        }
                    }))

                while _C:
                    await asyncio.sleep(heartbeat_interval / 1000)
                    try:
                        await websocket.send(json.dumps({
                            _B: 1,
                            _A: random.randint(1, 1000000)
                        }))
                    except Exception:
                        break
        except Exception as e:
            print(f"Token {token[:10]}... connection error: {e}, retrying in {RECONNECT_DELAY} seconds.")
            await asyncio.sleep(RECONNECT_DELAY)

async def main():
    print()
    tasks = []
    for token in tokens[:MAX_WORKERS]:  # Limit number of tokens
        task = asyncio.create_task(connect(token))
        tasks.append(task)
        await asyncio.sleep(0.5)  # Delay for rate limit
    await asyncio.gather(*tasks, return_exceptions=True)

asyncio.run(main())
