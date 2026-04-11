import json
import os
import time
import heapq
from typing import Dict, List, Any, Optional, Set
from graphdb.models import Node, Edge

class GraphEngine:
    def __init__(self, wal_path="graph.wal"):
        self.nodes: Dict[int, Node] = {}
        self.edges: List[Edge] = []
        self.adj: Dict[int, List[Edge]] = {}
        self.indexes: Dict[str, Dict[Any, List[int]]] = {}
        
        self.next_node_id = 1
        self.next_edge_id = 1
        
        self.wal_path = os.path.join(os.path.dirname(__file__), wal_path)
        self.wal_handle = open(self.wal_path, "a", encoding="utf-8")
        self._recover()

    def _recover(self):
        if os.path.exists(self.wal_path):
            with open(self.wal_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        cmd = json.loads(line)
                        self._apply(cmd, write_to_wal=False)
                    except: continue

    def _write_wal(self, cmd):
        self.wal_handle.write(json.dumps(cmd) + "\n")
        self.wal_handle.flush()

    def _apply(self, cmd, write_to_wal=True):
        op = cmd["op"]
        if op == "CREATE_NODE":
            node = Node(cmd["id"], cmd["label"], cmd["props"])
            self.nodes[node.id] = node
            self.adj[node.id] = []
            self._update_index(node)
            self.next_node_id = max(self.next_node_id, node.id + 1)
        elif op == "CREATE_EDGE":
            edge = Edge(cmd["id"], cmd["type"], cmd["from"], cmd["to"], cmd["props"])
            self.edges.append(edge)
            if edge.from_node in self.adj:
                self.adj[edge.from_node].append(edge)
            self.next_edge_id = max(self.next_edge_id, edge.id + 1)
        
        if write_to_wal:
            self._write_wal(cmd)

    def _update_index(self, node):
        for prop, val in node.properties.items():
            key = f"{node.label}.{prop}"
            if key not in self.indexes: self.indexes[key] = {}
            if val not in self.indexes[key]: self.indexes[key][val] = []
            self.indexes[key][val].append(node.id)

    def create_node(self, label, props):
        node_id = self.next_node_id
        cmd = {"op": "CREATE_NODE", "id": node_id, "label": label, "props": props}
        self._apply(cmd)
        return node_id

    def create_edge(self, from_id, to_id, edge_type, props):
        edge_id = self.next_edge_id
        cmd = {"op": "CREATE_EDGE", "id": edge_id, "from": from_id, "to": to_id, "type": edge_type, "props": props}
        self._apply(cmd)
        return edge_id

    def shortest_path(self, start_id, end_id):
        pq = [(0, start_id, [])]
        visited = set()
        
        while pq:
            (dist, current, path) = heapq.heappop(pq)
            if current in visited: continue
            visited.add(current)
            
            if current == end_id:
                return path, dist
            
            for edge in self.adj.get(current, []):
                if edge.to_node not in visited:
                    new_dist = dist + 1.0
                    new_path = path + [edge]
                    heapq.heappush(pq, (new_dist, edge.to_node, new_path))
        return None, 0

    def stats(self):
        wal_size = os.path.getsize(self.wal_path) if os.path.exists(self.wal_path) else 0
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "indexes": list(self.indexes.keys()),
            "wal_size": wal_size
        }
