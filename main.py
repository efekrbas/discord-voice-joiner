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

   _____ _____ _______ _    _ _    _ ____   _____ ____  __  __     ________ ______ ______ _  _______  ____           _____ 
  / ____|_   _|__   __| |  | | |  | |  _ \ / ____/ __ \|  \/  |   / /  ____|  ____|  ____| |/ /  __ \|  _ \   /\    / ____|
 | |  __  | |    | |  | |__| | |  | | |_) | |   | |  | | \  / |  / /| |__  | |__  | |__  | ' /| |__) | |_) | /  \  | (___  
 | | |_ | | |    | |  |  __  | |  | |  _ <| |   | |  | | |\/| | / / |  __| |  __| |  __| |  < |  _  /|  _ < / /\ \  \___ \ 
 | |__| |_| |_   | |  | |  | | |__| | |_) | |___| |__| | |  | |/ /  | |____| |    | |____| . \| | \ \| |_) / ____ \ ____) |
  \_____|_____|  |_|  |_|  |_|\____/|____(_)_____\____/|_|  |_/_/   |______|_|    |______|_|\_\_|  \_\____/_/    \_\_____/ 
                                                                                                                           
                                                                                                                                                                                                                                                                                                            
                                                                      
                                                                      
                                    > Press Enter                                         
'''

Anime.Fade(Center.Center(intro), Colors.red_to_yellow, Colorate.Vertical, interval=.035, enter=_C)

print(fr"""{Fore.LIGHTBLUE_EX}
                                                                                                                                                
   _____ _____ _______ _    _ _    _ ____   _____ ____  __  __     ________ ______ ______ _  _______  ____           _____ 
  / ____|_   _|__   __| |  | | |  | |  _ \ / ____/ __ \|  \/  |   / /  ____|  ____|  ____| |/ /  __ \|  _ \   /\    / ____|
 | |  __  | |    | |  | |__| | |  | | |_) | |   | |  | | \  / |  / /| |__  | |__  | |__  | ' /| |__) | |_) | /  \  | (___  
 | | |_ | | |    | |  |  __  | |  | |  _ <| |   | |  | | |\/| | / / |  __| |  __| |  __| |  < |  _  /|  _ < / /\ \  \___ \ 
 | |__| |_| |_   | |  | |  | | |__| | |_) | |___| |__| | |  | |/ /  | |____| |    | |____| . \| | \ \| |_) / ____ \ ____) |
  \_____|_____|  |_|  |_|  |_|\____/|____(_)_____\____/|_|  |_/_/   |______|_|    |______|_|\_\_|  \_\____/_/    \_\_____/ 
                                                                                                                           
                                                                                                                                                                                                                                                                           
                                                                      
""")
time.sleep(1)

Write.Print('\nWhich option do you want to choose: ', Colors.red_to_yellow)
Write.Print('\n> 1 - join voice ', Colors.red_to_yellow)
Write.Print('\n> 2 - exit ', Colors.red_to_yellow)

askim = int(input('\nchoice: '))

# Tokenları toplu işlemek için max bağlantı sayısını sınırla
MAX_WORKERS = 20  # İnterneti korumak için eşzamanlı bağlantı sınırı
RECONNECT_DELAY = 10  # Hata sonrası yeniden bağlanma gecikmesi (saniye)
HEARTBEAT_MULTIPLIER = 1.5  # Heartbeat aralığını artırarak yükü azalt

if askim == 1:
    print(_I)
    with open(_J, 'r') as token_file:
        tokens = [t.strip() for t in token_file.readlines() if t.strip()]
    server_id = input(_K)
    channel_id = input(_L)

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
                            print(f"Token {token[:10]}... için heartbeat başarısız, yeniden bağlanıyor.")
                            break
            except Exception as e:
                print(f"Token {token[:10]}... bağlantı hatası: {e}, {RECONNECT_DELAY} saniye sonra yeniden deniyor.")
                await asyncio.sleep(RECONNECT_DELAY)

    async def main():
        tasks = []
        for token in tokens[:MAX_WORKERS]:  # Token sayısını sınırla
            task = asyncio.create_task(connect(token))
            tasks.append(task)
            await asyncio.sleep(0.5)  # Rate limit için gecikme
        await asyncio.gather(*tasks, return_exceptions=True)

    asyncio.run(main())

elif askim == 2:
    print('Exiting the program...')
else:
    print('You have entered invalid. Please try again.')