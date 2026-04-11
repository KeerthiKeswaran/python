from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class Node:
    id: int
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self):
        return f"{self.label}#{self.id} {self.properties}"

@dataclass
class Edge:
    id: int
    type: str
    from_node: int
    to_node: int
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __repr__(self):
        return f"{self.from_node} -[:{self.type}]-> {self.to_node} {self.properties}"
