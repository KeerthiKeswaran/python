import json
from db import get_last_messages

rooms = {}  # room_name -> set(users)
users = {}  # websocket -> User


async def register(user):
    users[user.websocket] = user


async def unregister(user):
    if user.room and user.room in rooms:
        rooms[user.room].remove(user)
        await broadcast_room_info(user.room)

    users.pop(user.websocket, None)
    await broadcast_presence()


async def join_room(user, room):
    user.room = room
    rooms.setdefault(room, set()).add(user)

    # Broadcast join
    await broadcast(room, json.dumps({
        "type": "message",
        "room": room,
        "text": f"{user.username} joined {room}",
        "sender": "System"
    }))

    # Send last N messages
    history = get_last_messages(room, 50)
    for msg in history:
        await user.websocket.send(json.dumps({
            "type": "message",
            "room": room,
            "text": msg["message"],
            "sender": msg["user"],
            "timestamp": msg["timestamp"]
        }))
    
    await broadcast_room_info(room)
    await broadcast_presence()

async def broadcast_room_info(room):
    if room in rooms:
        count = len(rooms[room])
        await broadcast(room, json.dumps({
            "type": "room_info",
            "room": room,
            "count": count
        }))

async def private_event(target_name, message):
    for user in users.values():
        if user.username == target_name:
            try:
                await user.websocket.send(message)
            except Exception:
                pass


async def broadcast(room, message):
    if room not in rooms:
        return

    for user in rooms[room]:
        try:
            await user.websocket.send(message)
        except Exception:
            pass


async def broadcast_presence():
    # Send user statuses to everyone
    presence_data = {
        u.username: u.status for u in users.values()
    }
    msg = json.dumps({
        "type": "presence",
        "data": presence_data
    })
    for user in users.values():
        try:
            await user.websocket.send(msg)
        except Exception:
            pass


async def private_message(sender, target_name, text):
    msg = json.dumps({
        "type": "dm",
        "sender": sender,
        "text": text
    })
    for user in users.values():
        if user.username == target_name:
            try:
                await user.websocket.send(msg)
            except Exception:
                pass