
import aiohttp
from fastapi import Request, Response
from typing import Dict
from .circuit_breaker import CircuitBreaker, State

class AsyncReverseProxy:
    def __init__(self, routes: Dict[str, str]):
        self.routes = routes
        self.session: aiohttp.ClientSession = None
        self.breakers: Dict[str, CircuitBreaker] = {
            target: CircuitBreaker() for target in routes.values()
        }

    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    def get_target(self, path: str) -> tuple[str, str]:
        for prefix, target in self.routes.items():
            if path.startswith(prefix):
                # Return (target_url, base_service_url)
                return target + path[len(prefix):], target
        return None, None

    async def forward(self, request: Request) -> Response:
        path = request.url.path
        target_url, base_url = self.get_target(path)
        
        if not target_url:
            return Response(content='{"error": "Path not mapped to any downstream service"}', 
                            status_code=404, media_type="application/json")

        breaker = self.breakers.get(base_url)
        if not breaker:
             breaker = CircuitBreaker()
             self.breakers[base_url] = breaker

        if not breaker.can_execute():
            return Response(
                content='{"error": "Service temporarily unavailable (Circuit Open)", "retry_after": 30}',
                status_code=503,
                media_type="application/json"
            )

        # Simulation: Trigger failure if API key is 'broken'
        if request.headers.get("x-api-key") == "broken":
            breaker.record_failure()
            return Response(
                content='{"error": "Simulated Downstream Failure (Key: broken)"}',
                status_code=500,
                media_type="application/json"
            )

        session = await self.get_session()
        method = request.method
        headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}
        body = await request.body()

        try:
            async with session.request(method, target_url, headers=headers, data=body, timeout=5) as resp:
                content = await resp.read()
                breaker.record_success()
                return Response(
                    content=content,
                    status_code=resp.status,
                    headers=dict(resp.headers)
                )
        except Exception as e:
            breaker.record_failure()
            return Response(
                content=f'{{"error": "Downstream service connectivity issue", "details": "{str(e)}"}}',
                status_code=502,
                media_type="application/json"
            )

    async def close(self):
        if self.session:
            await self.session.close()
