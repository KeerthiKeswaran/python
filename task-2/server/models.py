import secrets

class User:
    def __init__(self, username, websocket):
        self.username = username
        self.websocket = websocket
        self.room = None
        self.status = "online"
        self.session_id = secrets.token_hex(3)