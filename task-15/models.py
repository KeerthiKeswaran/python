from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class PlaceOrderCommand:
    customer_id: str
    items: List[Dict[str, Any]]

@dataclass
class OrderPlaced:
    order_id: str
    customer_id: str
    total: float
    items: List[Dict[str, Any]]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

@dataclass
class InventoryReserved:
    sku: str
    qty: int
    order_id: str

@dataclass
class OrderStatus:
    order_id: str
    status: str

class OrderAggregate:
    def __init__(self, order_id):
        self.order_id = order_id
        self.status = "CREATED"
        self.items = []
        self.total = 0.0

    def apply(self, event):
        if isinstance(event, OrderPlaced):
            self.customer_id = event.customer_id
            self.total = event.total
            self.items = event.items
            self.status = "PLACED"
