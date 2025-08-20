import asyncio
import os
from websockets.asyncio.client import connect


async def main(ws_server_url, x_user):
    nickname = input("nikizni kiriting: ")
    async with connect(ws_server_url, additional_headers={'X-user': x_user, 'X-nickname': nickname}) as websocket:
        await websocket.send(f"{x_user} chatga qoshildi, niki {nickname}")

        async def send_msg():
            while True:
                msg = await asyncio.to_thread(input, '')
                await websocket.send(msg)

        async def receive_msg():
            while True:
                msg = await websocket.recv()
                print(msg)

        await asyncio.gather(send_msg(), receive_msg())


if __name__ == "__main__":
    host = '10.30.9.26'
    x_user = os.getenv('USER')

    websocket_server_url = f"ws://{host}:8765"
    asyncio.run(main(websocket_server_url, x_user))
