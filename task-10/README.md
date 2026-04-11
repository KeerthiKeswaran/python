# Blockchain Prototype with P2P Networking

A functional blockchain implementation featuring ECDSA-signed transactions, Proof-of-Work consensus, and socket-based block propagation.

## Features
- **Wallet System**: Private/Public key generation using ECDSA.
- **Transaction Signing**: Digitally sign transactions to ensure data integrity.
- **Proof-of-Work (PoW)**: Adjustable mining difficulty.
- **Merkle Trees**: Optimized transaction verification within blocks.
- **P2P Gossip Protocol**: Blocks are broadcasted to connected peers automatically.
- **State Independent Verification**: Each node independently validates the chain.

## Setup
Ensure you have the `ecdsa` library installed:
```bash
pip install ecdsa
```

## How to Run
Run the simulation script to launch 3 nodes and observe the network activity:
```bash
python main.py
```

## Project Structure
```text
task-10/
├── blockchain/
│   ├── core.py      # Block, Blockchain, MerkleTree
│   ├── wallet.py    # Wallet, Transaction, ECDSA
│   └── network.py   # P2P Node implementation
├── main.py          # Network simulation entry point
└── blueprint.md     # In-depth technical documentation
```

## Expected Output Preview
```text
=== Node Startup (3 nodes) ===
[NODE-1] Listening on port 5001 | Wallet: 0x...
[NODE-2] Listening on port 5002 | Wallet: 0x...
[NODE-3] Listening on port 5003 | Wallet: 0x...

=== Transaction ===
[NODE-1] Creating transaction:
From: 0x...
To: 0x...
Amount: 2.5 coins
Signature: 3045022100... Valid

=== Mining ===
[NODE-2] Mining block #7 (2 transactions in mempool)...
Difficulty: 4 (hash must start with "0000")
...
[NODE-2] Block #7 mined in 0.42s
Hash: 0000...

=== Propagation ===
[NODE-2] Broadcasting block #7 to peers...
[NODE-1] Received block #7 — validating... Accepted (chain height: 7)
[NODE-3] Received block #7 — validating... Accepted (chain height: 7)

=== Wallet Balances ===
0x...: 7.5 coins
0x...: 13.5 coins (includes mining rewards)
0x...: 4.0 coins
```
