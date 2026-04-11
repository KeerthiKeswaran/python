import os
import sys

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graphdb.shell import GraphDBShell
import time

def main():
    shell = GraphDBShell()
    commands = [
        'CREATE NODE (alice:Person {name: "Alice", age: 30, city: "Austin"})',
        'CREATE NODE (bob:Person {name: "Bob", age: 28, city: "Dallas"})',
        'CREATE NODE (acme:Company {name: "Acme Corp", industry: "Tech"})',
        'CREATE EDGE (alice)-[:FRIENDS_WITH {since: 2021}]->(bob)',
        'CREATE EDGE (bob)-[:WORKS_AT {role: "Engineer"}]->(acme)',
        'MATCH (p:Person)-[:FRIENDS_WITH]->()-[:WORKS_AT]->(c:Company) WHERE c.name = "Acme Corp" RETURN p.name, c.name',
        'SHORTEST_PATH (alice)-[*1..4]->(acme)',
        'STATS'
    ]
    
    print("=== Graph DB Shell ===")
    for cmd in commands:
        print(f"graphdb> {cmd}")
        shell.execute(cmd)

if __name__ == "__main__":
    main()
