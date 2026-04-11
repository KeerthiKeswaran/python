import asyncio

class MessageBus:
    def __init__(self):
        self.handlers = []

    def register(self, handler):
        self.handlers.append(handler)

    async def dispatch(self, command, event_store, read_store):
        from models import OrderPlaced, InventoryReserved
        print("[WRITE] PlaceOrderCommand received")
        order_id = "ORD-1087"
        print(f"[WRITE] Aggregate Order#{order_id} created")
        
        # Calculate total
        total = sum(i['qty'] * i['price'] for i in command.items)
        
        # Create events
        events = [
            OrderPlaced(order_id, command.customer_id, total, command.items)
        ]
        for item in command.items:
            events.append(InventoryReserved(item['sku'], item['qty'], order_id))
            
        event_store.append(order_id, events)
        print(f"[BUS] Published {len(events)} events to \"orders\" topic")
        
        # Async handers
        print("\n=== Event Handlers (Async) ===")
        for handler in self.handlers:
            await handler(events, read_store)
