import hashlib
from ecdsa import SigningKey, SECP256k1, VerifyingKey, BadSignatureError

class Wallet:
    def __init__(self):
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.verifying_key
        self.address = hashlib.sha256(self.public_key.to_string()).hexdigest()[:10]

    def sign(self, message: str) -> str:
        return self.private_key.sign(message.encode()).hex()

    @staticmethod
    def verify(address_pub_key_hex: str, message: str, signature_hex: str) -> bool:
        try:
            pub_key = VerifyingKey.from_string(bytes.fromhex(address_pub_key_hex), curve=SECP256k1)
            return pub_key.verify(bytes.fromhex(signature_hex), message.encode())
        except (BadSignatureError, ValueError):
            return False

    def get_public_key_hex(self) -> str:
        return self.public_key.to_string().hex()

class Transaction:
    def __init__(self, sender, recipient, amount, sender_pub_key=None, signature=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.sender_pub_key = sender_pub_key
        self.signature = signature

    def to_dict(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount
        }

    def message(self):
        return f"{self.sender}{self.recipient}{self.amount}"

    def __repr__(self):
        return f"{self.sender[:6]} -> {self.recipient[:6]}: {self.amount} coins"
