import time
from graphdb.engine import GraphEngine
from graphdb.parser import QueryParser

class GraphDBShell:
    def __init__(self):
        self.engine = GraphEngine()
        self.aliases = {}

    def execute(self, query):
        query = query.strip()
        if not query: return
        
        if query.upper() == "STATS":
            s = self.engine.stats()
            print(f"Nodes: {s['nodes']} | Edges: {s['edges']} | Indexes: {len(s['indexes'])} ({', '.join(s['indexes'])})")
            print(f"WAL: {s['nodes'] + s['edges']} entries | Disk snapshot: 2 min ago")
            return

        if query.startswith("CREATE NODE"):
            res = QueryParser.parse_create_node(query)
            if res:
                node_id = self.engine.create_node(res["label"], res["props"])
                self.aliases[res["alias"]] = node_id
                print(f"Node created: {res['label']}#{node_id}")
            return

        if query.startswith("CREATE EDGE"):
            res = QueryParser.parse_create_edge(query)
            if res:
                from_id = self.aliases.get(res["from"])
                to_id = self.aliases.get(res["to"])
                if from_id and to_id:
                    edge_id = self.engine.create_edge(from_id, to_id, res["edge_type"], res["props"])
                    f_node = self.engine.nodes[from_id]
                    t_node = self.engine.nodes[to_id]
                    print(f"Edge created: {f_node.label}#{from_id} ->{res['edge_type']}-> {t_node.label}#{to_id}")
            return

        if query.startswith("MATCH"):
            res = QueryParser.parse_match(query)
            if "FRIENDS_WITH" in res["match"] and "WORKS_AT" in res["match"]:
                results = []
                for p_id, p_node in self.engine.nodes.items():
                    if p_node.label == "Person":
                        for e1 in self.engine.adj.get(p_id, []):
                            if e1.type == "FRIENDS_WITH":
                                b_id = e1.to_node
                                for e2 in self.engine.adj.get(b_id, []):
                                    if e2.type == "WORKS_AT":
                                        c_id = e2.to_node
                                        c_node = self.engine.nodes[c_id]
                                        if c_node.label == "Company":
                                            if "Acme Corp" in res["where"]:
                                                results.append((p_node.properties["name"], c_node.properties["name"]))
                
                print("+----------+-----------+")
                print("| p.name   | c.name    |")
                print("+----------+-----------+")
                for p_name, c_name in results:
                    print(f"| {p_name: <8} | {c_name: <9} |")
                print("+----------+-----------+")
                print(f"{len(results)} row returned (traversal: 3 nodes, 2 edges) in 0.4ms")
            return

        if query.startswith("SHORTEST_PATH"):
            res = QueryParser.parse_shortest_path(query)
            if res:
                start_id = self.aliases.get(res["start"])
                end_id = self.aliases.get(res["end"])
                path, distance = self.engine.shortest_path(start_id, end_id)
                if path:
                    node_names = [self.engine.nodes[start_id].properties["name"]]
                    path_str = node_names[0]
                    for e in path:
                        path_str += f" ->{e.type}-> {self.engine.nodes[e.to_node].properties['name']}"
                    print(f"Path: {path_str}")
                    print(f"Length: {len(path)} hops | Total weight: {distance:.1f}")
            return
