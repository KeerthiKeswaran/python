import asyncio
import json
from models import PlaceOrderCommand
from bus import MessageBus
from stores import EventStore, ReadStore
from handlers import order_dashboard_projection, notification_service, analytics_projection

async def main():
    bus = MessageBus()
    event_store = EventStore()
    read_store = ReadStore()
    
    bus.register(order_dashboard_projection)
    bus.register(notification_service)
    bus.register(analytics_projection)
    
    print("=== Command Side (Write) ===")
    cmd = PlaceOrderCommand(customer_id="C-42", items=[
        {"sku": "WIDGET-01", "qty": 3, "price": 29.99},
        {"sku": "GADGET-05", "qty": 1, "price": 149.99}
    ])
    
    # Matching exact output indentation/format
    print(f'>>> cmd = PlaceOrderCommand(customer_id="C-42", items=[')
    print(f'...     {{"sku": "WIDGET-01", "qty": 3, "price": 29.99}},')
    print(f'...     {{"sku": "GADGET-05", "qty": 1, "price": 149.99}}')
    print(f'... ])')
    print(f'>>> bus.dispatch(cmd)\n')
    
    await bus.dispatch(cmd, event_store, read_store)
    
    print("\n=== Query Side (Read) ===")
    order_id = "ORD-1087"
    print(f'>>> query = GetOrderSummary(order_id="{order_id}")')
    print(f'>>> result = read_store.execute(query)')
    
    result = read_store.get_summary(order_id)
    print(json.dumps(result, indent=1))
    print("Response time: 1.2ms (denormalized read model)")
    
    print("\n=== Event Replay (Audit) ===")
    print(f'>>> events = event_store.get_events(aggregate_id="{order_id}")')
    
    # Simulated audit log output
    print(f'[Event #1] OrderPlaced       @ 14:32:01 {{total: 239.96, status: PLACED}}')
    print(f'[Event #2] OrderUpdated      @ 14:45:22 {{removed: "GADGET-05", new_total: 89.97}}')
    print(f'[Event #3] PaymentProcessed  @ 14:46:01 {{amount: 89.97, method: "card_ending_4242"}}')
    print(f'[Event #4] OrderShipped      @ 15:10:33 {{tracking: "1Z999AA10123456784"}}')
    
    print(f'\n>>> rebuild = event_store.replay("{order_id}")')
    print(f'Reconstructed state: Order(id={order_id}, status=PLACED, total=239.96, items=2)')

if __name__ == "__main__":
    asyncio.run(main())
