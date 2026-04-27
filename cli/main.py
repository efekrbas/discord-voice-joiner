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
import time, asyncio, json, websockets, sys
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

with open(_J, 'r') as token_file:
    tokens = []
    for t in token_file.readlines():
        token = t.strip()
        if not token or token.startswith('//'):
            continue
        token = token.strip('"').strip("'").strip()
        if token:
            tokens.append(token)

if not tokens:
    print(f"{Fore.RED}[!] The program did not start because no token was entered in tokens.txt.{Fore.RESET}")
    sys.exit()
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
random_event = ask_yn("> Random Event (Manual selection will be disabled) (y/n): ")
if random_event:
    deafen = "random"
    mute = "random"
    stream = "random"
    video = "random"
else:
    deafen = ask_yn("> Deafen: (y/n) ")
    mute = ask_yn("> Mute: (y/n) ")
    stream = ask_yn("> Stream: (y/n) ")
    video = ask_yn("> Video: (y/n) ")

print_lock = asyncio.Lock()

first_log = True

async def typewrite_log(token_str, m, d, v, s):
    global first_log
    m_str = "ON" if m else "OFF"
    d_str = "ON" if d else "OFF"
    v_str = "ON" if v else "OFF"
    s_str = "ON" if s else "OFF"
    full_text = f"[+] {token_str} | Mute: {m_str}, Deafen: {d_str}, Video: {v_str}, Stream: {s_str}"
    if not first_log:
        print()
    else:
        first_log = False
        
    print(Fore.GREEN, end='', flush=True)
    for char in full_text:
        print(char, end='', flush=True)
        await asyncio.sleep(0.01)
    print(" " + Fore.RESET, end='', flush=True)

active_sessions = []
connected_count = 0

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
                session_record = {'ws': websocket, 'server_id': server_id}
                active_sessions.append(session_record)
                try:
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
                            msg = await asyncio.wait_for(websocket.recv(), timeout=60)
                            data = json.loads(msg)
                            if data.get('t') == 'READY':
                                ready_received = True
                                break
                        except Exception:
                            break

                    if not ready_received:
                        raise Exception("READY event not received (Token may be invalid or expired)")

                    token_mute = random.choice([True, False]) if mute == "random" else mute
                    token_deafen = random.choice([True, False]) if deafen == "random" else deafen
                    token_video = random.choice([True, False]) if video == "random" else video
                    token_stream = random.choice([True, False]) if stream == "random" else stream

                    await websocket.send(json.dumps({
                        _B: 4,
                        _A: {_E: server_id, _F: channel_id, _G: token_mute, _H: token_deafen, 'self_video': token_video}
                    }))
                    if not logged:
                        async with print_lock:
                            await typewrite_log(token, token_mute, token_deafen, token_video, token_stream)
                        logged = True
                        global connected_count
                        connected_count += 1

                    if token_stream:
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
                finally:
                    if session_record in active_sessions:
                        active_sessions.remove(session_record)
        except Exception as e:
            print(f"Token {token[:10]}... connection error: {e}, retrying in {RECONNECT_DELAY} seconds.")
            await asyncio.sleep(RECONNECT_DELAY)

import win32api
import time

main_loop = None

def console_handler(ctrl_type):
    global main_loop
    if ctrl_type in (2, 5, 6) and main_loop is not None:
        future = asyncio.run_coroutine_threadsafe(kick_all(), main_loop)
        try:
            future.result(timeout=5)
        except Exception:
            pass
        time.sleep(0.5)
        return True
    return False

win32api.SetConsoleCtrlHandler(console_handler, True)

async def kick_all():
    global _C
    _C = False
    tasks = []
    for session in active_sessions:
        ws = session.get('ws')
        if ws:
            try:
                tasks.append(ws.send(json.dumps({
                    'op': 4,
                    'd': {
                        'guild_id': session.get('server_id'),
                        'channel_id': None,
                        'self_mute': False,
                        'self_deaf': False
                    }
                })))
            except Exception:
                pass
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

async def main():
    global main_loop
    main_loop = asyncio.get_running_loop()
    print()
    tasks = []
    for token in tokens[:MAX_WORKERS]:  # Limit number of tokens
        task = asyncio.create_task(connect(token))
        tasks.append(task)
        await asyncio.sleep(0.5)  # Delay for rate limit
    target_count = len(tokens[:MAX_WORKERS])
    while connected_count < target_count:
        await asyncio.sleep(0.1)

    try:
        print(f"\n{Fore.CYAN}[!] All accounts connected. If you want to kick tokens from voice, type 'exit' (This process closes the program.){Fore.RESET}")
        while True:
            cmd = await asyncio.to_thread(input, "\n> ")
            if cmd.strip().lower() == 'exit':
                break
    finally:
        await kick_all()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
