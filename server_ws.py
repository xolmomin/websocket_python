import asyncio

from websockets.asyncio.server import serve

user_websockets = {}


async def broadcast(msg, ws):
    try:
        current_user = user_websockets[ws]

        for user_ws, _ in user_websockets.items():
            await user_ws.send(
                f"[{current_user['host']}] |{current_user['user']} - {current_user['nickname']}| - {msg}")
    except Exception as e:
        user_websockets.pop(ws)
        print(e)


async def echo(websocket):
    user_websockets[websocket] = {
        'host': websocket.remote_address[0],
        'user': websocket.request.headers.get('X-user', ''),
        'nickname': websocket.request.headers.get('X-nickname', '')
    }
    async for message in websocket:
        print(message)
        await broadcast(message, websocket)
        # await websocket.send(message)


async def main():
    host = 'localhost'
    port = 8765
    async with serve(echo, host, port) as server:
        print(f"{host}:{port} websocket server is running")
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
