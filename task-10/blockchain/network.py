import socket
import threading
import pickle
import time
from blockchain.core import Blockchain, Block
from blockchain.wallet import Wallet

class Node:
    def __init__(self, port, neighbors=None):
        self.port = port
        self.neighbors = neighbors or []
        self.blockchain = Blockchain()
        self.wallet = Wallet()
        self.peers = set()
        
        # Start server thread
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1', self.port))
        self.server.listen(5)
        
        self.active = True
        threading.Thread(target=self.listen_for_peers, daemon=True).start()

    def listen_for_peers(self):
        while self.active:
            try:
                client, addr = self.server.accept()
                data = client.recv(1024**2) # Capacity for a block
                if data:
                    item = pickle.loads(data)
                    if isinstance(item, Block):
                        self.handle_received_block(item)
                client.close()
            except:
                break

    def handle_received_block(self, block):
        latest = self.blockchain.get_latest_block()
        if block.prev_hash == latest.hash and block.hash.startswith("0" * self.blockchain.difficulty):
            self.blockchain.chain.append(block)
            return True
        else:
            # print(f"[DEBUG] Block rejected. Prev: {block.prev_hash[:10]}, Latest: {latest.hash[:10]}")
            return False

    def broadcast(self, item):
        for peer_port in self.neighbors:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('127.0.0.1', peer_port))
                s.send(pickle.dumps(item))
                s.close()
            except ConnectionRefusedError:
                pass

    def stop(self):
        self.active = False
        self.server.close()
