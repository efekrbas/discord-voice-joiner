_S='desktop'
_R='Discord'
_Q='windows'
_P=''
_O=''
_N='properties'
_M='heartbeat_interval'
_L='Channel ID: '
_K='Server ID: '
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

Anime.Fade(Center.Center(intro), Colors.blue_to_purple, Colorate.Vertical, interval=.035, enter=_C)

print(fr"""{Fore.LIGHTBLUE_EX}
                                                                                                                                                
 
                                                                                                                           
                                                                                                                                                                                                                                                                           
                                                                      
""")
time.sleep(1)

# Tokenları toplu işlemek için max bağlantı sayısını sınırla
MAX_WORKERS = 20  # İnterneti korumak için eşzamanlı bağlantı sınırı
RECONNECT_DELAY = 10  # Hata sonrası yeniden bağlanma gecikmesi (saniye)
HEARTBEAT_MULTIPLIER = 1.5  # Heartbeat aralığını artırarak yükü azalt

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

server_id = ask_id(_K)
channel_id = ask_id(_L)

async def connect(token):
    while _C:
        try:
            async with websockets.connect(
                'wss://gateway.discord.gg/?v=9&encoding=json',
                ping_interval=30,
                ping_timeout=60,
                max_size=2**20,  # Daha düşük veri boyutu
                max_queue=16  # Kuyruk boyutunu sınırla
            ) as websocket:
                hello = await websocket.recv()
                hello_json = json.loads(hello)
                heartbeat_interval = hello_json[_A][_M] * HEARTBEAT_MULTIPLIER
                await websocket.send(json.dumps({
                    _B: 2,
                    _A: {'token': token, _N: {'': _Q, _O: _R, _P: _S}}
                }))
                await websocket.send(json.dumps({
                    _B: 4,
                    _A: {_E: server_id, _F: channel_id, _G: _D, _H: _D}  # self_mute ve self_deaf False - açık kalacak
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
    tasks = []
    for token in tokens[:MAX_WORKERS]:  # Token sayısını sınırla
        task = asyncio.create_task(connect(token))
        tasks.append(task)
        await asyncio.sleep(0.5)  # Rate limit için gecikme
    await asyncio.gather(*tasks, return_exceptions=True)

asyncio.run(main())