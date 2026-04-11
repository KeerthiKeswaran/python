# Task 12: Graph Database Engine

## Description
An in-memory graph database engine with typed nodes and edges, a custom query language (DSL), hash-based indexing, and durability via Write-Ahead Logging (WAL).

## Features
- **Typed Graph Models**: Nodes with labels (e.g., `Person`, `Company`) and directed edges with types (e.g., `FRIENDS_WITH`).
- **Graph DSL**: Supports `CREATE NODE`, `CREATE EDGE`, and pattern matching `MATCH`.
- **Shortest Path**: Implements Dijkstra's algorithm for finding the most efficient route between nodes.
- **Persistence**: Transactions are logged to `graph.wal` for recovery on restart.
- **Indexing**: Automatic indexing of node properties for fast retrieval.

## How to Run
```bash
python main.py
```

## Output
```text
=== Graph DB Shell ===
graphdb> CREATE NODE (alice:Person {name: "Alice", age: 30, city: "Austin"})
Node created: Person#1
graphdb> CREATE NODE (bob:Person {name: "Bob", age: 28, city: "Dallas"})
Node created: Person#2
graphdb> CREATE NODE (acme:Company {name: "Acme Corp", industry: "Tech"})
Node created: Company#3
graphdb> CREATE EDGE (alice)-[:FRIENDS_WITH {since: 2021}]->(bob)
Edge created: Person#1 —FRIENDS_WITH-> Person#2
graphdb> CREATE EDGE (bob)-[:WORKS_AT {role: "Engineer"}]->(acme)
Edge created: Person#2 —WORKS_AT-> Company#3
graphdb> MATCH (p:Person)-[:FRIENDS_WITH]->()-[:WORKS_AT]->(c:Company) WHERE c.name = "Acme Corp" RETURN p.name, c.name
+----------+-----------+
| p.name   | c.name    |
+----------+-----------+
| Alice    | Acme Corp |
+----------+-----------+
1 row returned (traversal: 3 nodes, 2 edges) in 0.4ms
graphdb> SHORTEST_PATH (alice)-[*1..4]->(acme)
Path: Alice —FRIENDS_WITH-> Bob —WORKS_AT-> Acme Corp
Length: 2 hops | Total weight: 2.0
graphdb> STATS
Nodes: 3 | Edges: 2 | Indexes: 2 (Person.name, Company.name)
WAL: 5 entries | Disk snapshot: healthy
```
