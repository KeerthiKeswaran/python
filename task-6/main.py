
import time
import json
from fastapi import FastAPI, Request, Response
from core.circuit_breaker import CircuitBreaker, State
from core.gateway import AsyncReverseProxy
from core.cache import RedisCache
from core.middleware import RedisRateLimiter
from config import ROUTES, GATEWAY_HOST, GATEWAY_PORT, REDIS_URL, CACHE_TTL, DEFAULT_RATE_LIMIT

app = FastAPI(title="Async News API Gateway")

# Initialize real stacks
proxy = AsyncReverseProxy(ROUTES)
cache = RedisCache(REDIS_URL)
limiter = RedisRateLimiter(cache.client) # Reuse redis client from cache

@app.on_event("startup")
async def startup():
    print("=== Gateway Startup ===")
    print(f"[INFO] API Gateway running on http://{GATEWAY_HOST}:{GATEWAY_PORT}")
    print("[INFO] Routes loaded:")
    for path, target in ROUTES.items():
        print(f" {path}/** -> {target}")
    print("=== Request Log ===")

@app.on_event("shutdown")
async def shutdown():
    await proxy.close()
    await cache.close()

@app.middleware("http")
async def gateway_logic(request: Request, call_next):
    path = request.url.path
    
    # Bypass middleware for internal gateway routes
    if path in ["/health", "/api/health-metrics", "/docs", "/openapi.json"]:
        return await call_next(request)

    client_id = request.headers.get("x-api-key", "anonymous")
    method = request.method
    start_time = time.time()

    # 1. Rate Limiting Check
    allowed, rate_status = await limiter.is_allowed(client_id, limit=DEFAULT_RATE_LIMIT)
    if not allowed:
        print(f"[BLOCK] {method} {path} | client: {client_id} | reason: RATE_LIMIT_EXCEEDED ({rate_status})")
        return Response(content='{"error": "Too Many Requests"}', status_code=429, media_type="application/json")

    # 2. Cache Check (Only for GET)
    if method == "GET":
        cached_data = await cache.get(path)
        if cached_data:
            ttl = await cache.get_ttl(path)
            latency = int((time.time() - start_time) * 1000)
            print(f"[CACHE] GET {path} | client: {client_id} | hit (ttl: {ttl}s) | latency: {latency}ms")
            return Response(content=json.dumps(cached_data), media_type="application/json")

    # 3. Proxy to Downstream Service
    response = await proxy.forward(request)
    latency = int((time.time() - start_time) * 1000)
    
    # 4. Save to Cache if successful GET
    if method == "GET" and response.status_code == 200:
        try:
            data = json.loads(response.body)
            await cache.set(path, data, CACHE_TTL)
        except:
            pass

    # Structured Logging
    status_msg = "SUCCESS" if response.status_code < 400 else "ERROR"
    if response.status_code == 503: status_msg = "CIRCUIT_OPEN"
    print(f"[PROXY] {method} {path} | client: {client_id} | status: {response.status_code} ({status_msg}) | latency: {latency}ms")

    return response

@app.get("/api/health-metrics")
async def health_metrics():
    # JSON endpoint for programmatic health checks
    data = []
    for path, target in ROUTES.items():
        breaker = proxy.breakers.get(target)
        status = "UP" if not breaker or breaker.state != State.OPEN else "DOWN"
        data.append({
            "service": path.split('/')[-1],
            "status": status,
            "circuit": breaker.state.value if breaker else "CLOSED",
            "failures": breaker.failures if breaker else 0
        })
    return data

@app.get("/health")
async def health():
    # Premium Health Dashboard HTML
    service_rows = ""
    for path, target in ROUTES.items():
        name = path.split('/')[-1].capitalize()
        breaker = proxy.breakers.get(target)
        status = "UP" if not breaker or breaker.state != State.OPEN else "DOWN"
        color = "#22c55e" if status == "UP" else "#ef4444"
        circuit_color = "#3b82f6" if status == "UP" else "#f97316"
        
        service_rows += f"""
        <div class="service-card">
            <div class="service-name">{name}</div>
            <div class="status-tag" style="background: {color}">{status}</div>
            <div class="details">
                <p>Endpoint: <code>{target}</code></p>
                <p>Circuit: <span style="color: {circuit_color}">{breaker.state.value if breaker else 'CLOSED'}</span></p>
                <p>Failures: {breaker.failures if breaker else 0}</p>
            </div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API Gateway Dashboard</title>
        <style>
            :root {{ --bg: #0f172a; --card: #1e293b; --text: #f8fafc; }}
            body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 2rem; }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            h1 {{ font-weight: 800; letter-spacing: -0.025em; margin-bottom: 2rem; background: linear-gradient(to right, #60a5fa, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }}
            .service-card {{ background: var(--card); padding: 1.5rem; border-radius: 1rem; border: 1px solid #334155; position: relative; }}
            .service-name {{ font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; }}
            .status-tag {{ position: absolute; top: 1.5rem; right: 1.5rem; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }}
            .details {{ font-size: 0.875rem; color: #94a3b8; margin-top: 1rem; }}
            code {{ background: #000; padding: 0.2rem 0.4rem; border-radius: 0.25rem; font-family: monospace; color: #cbd5e1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Gateway Health Dashboard</h1>
            <div class="grid">{service_rows}</div>
        </div>
    </body>
    </html>
    """
    return Response(content=html_content, media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=GATEWAY_HOST, port=GATEWAY_PORT)
