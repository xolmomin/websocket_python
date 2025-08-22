import asyncio
import json

import orjson

from websockets.asyncio.server import serve, ServerConnection
from urllib.parse import urlparse, parse_qs

connection_list = dict()
groups = dict()
# /join 30
{
    "type": "group",
    "action": "join",
    "to": "30"
}

# /leave 30
{
    "type": "group",
    "action": "leave",
    "to": "30"
}

# hello python @botir
{
    "message": "hello python",
    "type": "private",
    "to": "botir"
}


# /group salom gruppadagilar @30
{
    "message": "salom gruppadagilar",
    "type": "group",
    "to": "30"
}


#
# groups = {
#     "30": ['botir', 'shokir', 'valijon'],
#     "40": ['botir', 'shokir', 'sobir', 'gayrat'],
# }
#
# # c1
# {
#     "message": "hello python",
#     "type": "private",
#     "to": "botir"
# }
#
# {
#     "message": "hello python",
#     "type": "group",
#     "to": "30"
# }


async def send_group(msg, group_id, username, ws):
    if group_id not in groups:
        await ws.send(orjson.dumps({"message": "bunaqa gruppa yoq"}).decode())
        return

    if username not in groups[group_id]:
        await ws.send(orjson.dumps({"message": "bu gruppaga join bolmagansan"}).decode())
        return

    for _user in groups[group_id]:
        if _user != username:
            _ws = connection_list.get(_user)
            if _ws:
                await _ws.send(orjson.dumps(msg).decode())


async def join_group(group_id, username, ws):
    group = groups.get(group_id)
    if group is None:
        groups[group_id] = [username]
    else:
        msg = f"{username} gruppaga qoshildi"
        groups[group_id].append(username)
        await send_group(msg, group_id, username, ws)


async def leave_group(group_id, username):
    group = groups.get(group_id)
    if group:
        group.remove(username)


async def send_private(msg, username):
    _ws = connection_list.get(username)
    if _ws:
        await _ws.send(orjson.dumps(msg).decode())


async def validate_user(websocket):
    query_params = parse_qs(urlparse(websocket.request.path).query)

    name = query_params.get('name', [''])[0]
    if not (name or name.isalpha()):
        await websocket.send('name is required')
        await websocket.close()

    if connection_list.get(name):
        await websocket.send('this name is already in use')
        await websocket.close()

    return name


async def validate_msg(msg: dict):
    if 'type' not in msg:
        raise ValueError("'type' is required")

    if msg['type'] not in ('group', 'private'):
        raise ValueError("type must be 'private' or 'group'")

    # if 'message' not in msg:
    #     raise ValueError("'message' is required")
    #
    # if 'to' not in msg:
    #     raise ValueError("'to' is required")


async def connected(websocket, name):
    connection_list[name] = websocket


async def echo(websocket: ServerConnection):
    name = await validate_user(websocket)

    await connected(websocket, name)  # client is connected
    while True:
        message = await websocket.recv()

        # async for message in websocket:
        try:
            message = orjson.loads(message)
            await validate_msg(message)
            if message['type'] == 'private':
                await send_private(message, message['to'])

            elif message['type'] == 'group' and message.get('action') == 'join':
                await join_group(message['to'], name, websocket)

            elif message['type'] == 'group' and message.get('action') == 'leave_group':
                await leave_group(message['to'], name)

            elif message['type'] == 'group':
                message['from'] = name
                await send_group(message, message['to'], name, websocket)

        except json.decoder.JSONDecodeError:
            await websocket.send(orjson.dumps({"message": 'invalid json'}).decode())
        except Exception as e:
            await websocket.send(orjson.dumps({"error": str(e)}).decode())

        # await broadcast(message, name)


async def main():
    host = '0'
    port = 8765
    async with serve(echo, host, port) as server:
        print(f"{host}:{port} websocket server is running")
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())

"""

botir   shokir  gayrat  tohir


ws://localhost:8765?name=botir
{
    "message": "yangi gruppaga qoshil",
    "type": "private",
    "to": "gayrat"
}

ws://localhost:8765?name=shokir
{
    "action": "join",
    "to": "30",
    "type": "group"
}

ws://localhost:8765?name=gayrat
{
    "action": "join",
    "to": "30",
    "type": "group"
}

ws://localhost:8765?name=tohir
{
    "action": "join",
    "type": "group",
    "to": "30"
}

{
    "message": "salom gruppadagilar",
    "type": "group",
    "to": "30"
}

in-memory
redis
database

"""
