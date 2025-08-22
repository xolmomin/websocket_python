import asyncio

from websockets.asyncio.server import serve

connection_list = {}


async def broadcast(msg, ws):
    try:
        current_user = connection_list[ws]

        for user_ws, _ in connection_list.items():
            await user_ws.send(
                f"[{current_user['host']}] |{current_user['user']} - {current_user['nickname']}| - {msg}")
    except Exception as e:
        connection_list.pop(ws)
        print(e)
    except KeyError as e:
        print(e)


async def echo(websocket):
    connection_list[websocket] = {
        'host': websocket.remote_address[0],
        'user': websocket.request.headers.get('X-user', ''),
        'nickname': websocket.request.headers.get('X-nickname', '')
    }
    async for message in websocket:
        await broadcast(message, websocket)
        # await websocket.send(message)


async def main():
    host = '0'
    port = 8765
    async with serve(echo, host, port) as server:
        print(f"{host}:{port} websocket server is running")
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())


"""


server

client1

client2

http://olx.uz
https://olx.uz

ws://localhost:8765

"""