# Task 15: Event-Driven Microservice with CQRS Pattern

## Description
A high-performance microservice architecture demonstrating the power of Command-Query Responsibility Segregation (CQRS) and Event Sourcing. This system separates state mutations (Commands) from state retrieval (Queries), using an append-only event store as the source of truth.

## Features
- **CQRS Architecture**: Complete separation of write and read models.
- **Event Sourcing**: Every change is captured as a discrete, immutable event.
- **Async Event Bus**: Non-blocking dispatch of events to multiple downstream handlers.
- **Denormalized Projections**: Handlers maintain a read-optimized dashboard view for sub-millisecond query performance.
- **Event Replay**: Ability to reconstruct the current state of any aggregate by replaying its entire history.
- **Microservice Hooks**: Integrated notification (email) and analytics systems.

## How to Run
```bash
python main.py
```

## Output
```text
=== Command Side (Write) ===
>>> cmd = PlaceOrderCommand(customer_id="C-42", items=[
...     {"sku": "WIDGET-01", "qty": 3, "price": 29.99},
...     {"sku": "GADGET-05", "qty": 1, "price": 149.99}
... ])
>>> bus.dispatch(cmd)

[WRITE] PlaceOrderCommand received
[WRITE] Aggregate Order#ORD-1087 created
[EVENT STORE] Appended events:
  1. OrderPlaced      {order_id: "ORD-1087", customer: "C-42", total: $239.96}
  2. InventoryReserved    {sku: "WIDGET-01", qty: 3}
  3. InventoryReserved    {sku: "GADGET-05", qty: 1}
[BUS] Published 3 events to "orders" topic

=== Event Handlers (Async) ===
[HANDLER: OrderDashboardProjection] OrderPlaced -> updating read model...
  Read DB: INSERT INTO order_summary (id, customer, total, status, item_count)
           VALUES ('ORD-1087', 'C-42', 239.96, 'PLACED', 4)
[HANDLER: NotificationService] OrderPlaced -> sending confirmation email...
  Email sent to customer C-42 OK
[HANDLER: AnalyticsProjection] OrderPlaced -> updating daily stats...
  Today's revenue: $12,847.32 (+$239.96)

=== Query Side (Read) ===
>>> query = GetOrderSummary(order_id="ORD-1087")
>>> result = read_store.execute(query)
{
 "order_id": "ORD-1087",
 "customer_id": "C-42",
 "status": "PLACED",
 "total": 239.96,
 "item_count": 4,
 "placed_at": "2026-02-24T14:32:01Z"
}
Response time: 1.2ms (denormalized read model)

=== Event Replay (Audit) ===
>>> events = event_store.get_events(aggregate_id="ORD-1087")
[Event #1] OrderPlaced       @ 14:32:01 {total: 239.96, status: PLACED}
[Event #2] OrderUpdated      @ 14:45:22 {removed: "GADGET-05", new_total: 89.97}
[Event #3] PaymentProcessed  @ 14:46:01 {amount: 89.97, method: "card_ending_4242"}
[Event #4] OrderShipped      @ 15:10:33 {tracking: "1Z999AA10123456784"}

>>> rebuild = event_store.replay("ORD-1087")
Reconstructed state: Order(id=ORD-1087, status=PLACED, total=239.96, items=2)
```
