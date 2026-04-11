import hashlib
import time
import json

class MerkleTree:
    @staticmethod
    def compute_root(transactions):
        if not transactions:
            return hashlib.sha256(b"").hexdigest()
        
        hashes = [hashlib.sha256(json.dumps(tx.to_dict()).encode()).hexdigest() for tx in transactions]
        
        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])
            new_hashes = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i+1]
                new_hashes.append(hashlib.sha256(combined.encode()).hexdigest())
            hashes = new_hashes
        return hashes[0]

class Block:
    def __init__(self, index, prev_hash, transactions, timestamp=None, nonce=0):
        self.index = index
        self.prev_hash = prev_hash
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.merkle_root = MerkleTree.compute_root(transactions)
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.prev_hash}{self.merkle_root}{self.timestamp}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine(self, difficulty):
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
        return self.hash

    def __repr__(self):
        return f"Block #{self.index} [Hash: {self.hash[:10]}...]"

class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.mempool = []
        self.mining_reward = 1.0

    def create_genesis_block(self):
        return Block(0, "0"*64, [])

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        # In a real system, we'd verify the signature here
        self.mempool.append(transaction)

    def mine_pending_transactions(self, miner_address):
        block = Block(len(self.chain), self.get_latest_block().hash, list(self.mempool))
        start_time = time.time()
        block.mine(self.difficulty)
        duration = time.time() - start_time
        
        self.chain.append(block)
        # Reward transaction
        reward_tx = {"sender": "SYSTEM", "recipient": miner_address, "amount": self.mining_reward}
        self.mempool = [] # Clear mempool
        return block, duration

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                # Assuming transactions are dicts or objects with sender/recipient/amount
                if isinstance(tx, dict):
                    if tx["recipient"] == address: balance += tx["amount"]
                    if tx["sender"] == address: balance -= tx["amount"]
                else:
                    if tx.recipient == address: balance += tx.amount
                    if tx.sender == address: balance -= tx.amount
        return balance
