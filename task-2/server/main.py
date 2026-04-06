import asyncio
import websockets
import json
import traceback

from manager import register, unregister, join_room, broadcast, private_message, broadcast_presence, private_event
from models import User
from db import save_message


async def handler(websocket):
    user = None

    try:
        # First message must be username
        try:
            init_msg = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            data = json.loads(init_msg)
            if "type" not in data or "username" not in data:
                await websocket.send(json.dumps({"type": "error", "text": "Missing 'type' or 'username'"}))
                return
            username = data["username"]
        except (json.JSONDecodeError, KeyError) as e:
            print("[ERROR] Invalid JSON received during initialization")
            await websocket.send(json.dumps({"type": "error", "text": "Invalid JSON or missing fields"}))
            return
        except asyncio.TimeoutError:
            print("[ERROR] Timeout waiting for init message")
            return

        user = User(username, websocket)
        await register(user)

        print(f"[INFO] User \"{username}\" connected (session: {user.session_id})")

        async for msg in websocket:
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                print(f"[ERROR] Invalid JSON received from {username}")
                await websocket.send(json.dumps({"type": "error", "text": "Invalid JSON"}))
                continue

            if "type" not in data:
                print(f"[ERROR] Missing 'type' in message from {username}")
                await websocket.send(json.dumps({"type": "error", "text": "Missing 'type' field"}))
                continue

            # Heartbeat / Keep-alive
            if data["type"] == "ping":
                await websocket.send(json.dumps({"type": "pong"}))
                continue

            elif data["type"] == "join":
                room = data.get("room")
                if room:
                    if not room.startswith("#"):
                        room = "#" + room
                    await join_room(user, room)
                    print(f"[INFO] {username} joined room {room}")

            elif data["type"] == "message":
                if not user.room:
                    await websocket.send(json.dumps({"type": "warning", "text": "You must join a room first"}))
                    continue
                text = data.get("text", "")
                save_message(user.username, user.room, text)
                
                msg_out = json.dumps({
                    "type": "message",
                    "room": user.room,
                    "text": text,
                    "sender": user.username
                })
                await broadcast(user.room, msg_out)

            elif data["type"] == "dm":
                to = data.get("to")
                text = data.get("text", "")
                if to and text:
                    await private_message(user.username, to, text)
                    print(f"[INFO] DM sent from {username} to {to}")
            
            elif data["type"] == "dm_typing":
                to = data.get("to")
                if to:
                    msg_out = json.dumps({
                        "type": "dm_typing",
                        "sender": user.username
                    })
                    await private_event(to, msg_out)

            elif data["type"] == "typing":
                if user.room:
                    msg_out = json.dumps({
                        "type": "typing",
                        "sender": user.username
                    })
                    await broadcast(user.room, msg_out)

            elif data["type"] == "status":
                status = data.get("status", "online")
                user.status = status
                await broadcast_presence()

    except websockets.exceptions.ConnectionClosed:
        pass # Expected when client disconnects
    except Exception as e:
        print("[ERROR] Unexpected error in handler:")
        traceback.print_exc()

    finally:
        close_code = websocket.close_code
        if user:
            await unregister(user)
            print(f"[DISCONNECT] User \"{user.username}\" (code: {close_code})")
        else:
            print(f"[DISCONNECT] Unknown user (code: {close_code})")


async def main():
    # websockets handles ping/pong automatically (ping_interval=20, ping_timeout=20 default)
    # We also added manual 'ping' handling for client keep-alive if needed.
    server = await websockets.serve(handler, "0.0.0.0", 8765, ping_interval=20, ping_timeout=20)
    print("[INFO] Chat server started on ws://0.0.0.0:8765")

    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())