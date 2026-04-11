from typing import List, Dict, Any
from models import OrderPlaced, OrderAggregate

class EventStore:
    def __init__(self):
        self.events = {} # aggregate_id -> [events]
        self.all_events = []

    def append(self, aggregate_id, events):
        if aggregate_id not in self.events:
            self.events[aggregate_id] = []
        self.events[aggregate_id].extend(events)
        self.all_events.extend(events)
        
        print("[EVENT STORE] Appended events:")
        for i, event in enumerate(events, 1):
            if isinstance(event, OrderPlaced):
                print(f"  {i}. OrderPlaced      {{order_id: \"{event.order_id}\", customer: \"{event.customer_id}\", total: ${event.total}}}")
            else:
                print(f"  {i}. {type(event).__name__}    {{sku: \"{event.sku}\", qty: {event.qty}}}")

    def get_events(self, aggregate_id):
        return self.events.get(aggregate_id, [])

    def replay(self, aggregate_id):
        events = self.get_events(aggregate_id)
        agg = OrderAggregate(aggregate_id)
        for e in events:
            agg.apply(e)
        return agg

class ReadStore:
    def __init__(self):
        self.orders = {} # order_id -> summary

    def update_summary(self, order_id, customer, total, status, items):
        self.orders[order_id] = {
            "order_id": order_id,
            "customer_id": customer,
            "status": status,
            "total": total,
            "item_count": sum(i['qty'] for i in items),
            "placed_at": "2026-02-24T14:32:01Z"
        }
        print(f"  Read DB: INSERT INTO order_summary (id, customer, total, status, item_count)")
        print(f"           VALUES ('{order_id}', '{customer}', {total}, '{status}', {sum(i['qty'] for i in items)})")

    def get_summary(self, order_id):
        return self.orders.get(order_id)
