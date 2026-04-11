import asyncio
from models import OrderPlaced

async def order_dashboard_projection(events, read_store):
    for e in events:
        if isinstance(e, OrderPlaced):
            print(f"[HANDLER: OrderDashboardProjection] OrderPlaced -> updating read model...")
            read_store.update_summary(e.order_id, e.customer_id, e.total, "PLACED", e.items)
            await asyncio.sleep(0.1)

async def notification_service(events, _):
    for e in events:
        if isinstance(e, OrderPlaced):
            print(f"[HANDLER: NotificationService] OrderPlaced -> sending confirmation email...")
            print(f"  Email sent to customer {e.customer_id} OK")
            await asyncio.sleep(0.1)

async def analytics_projection(events, _):
    for e in events:
        if isinstance(e, OrderPlaced):
            print(f"[HANDLER: AnalyticsProjection] OrderPlaced -> updating daily stats...")
            print(f"  Today's revenue: $12,847.32 (+${e.total})")
            await asyncio.sleep(0.1)
