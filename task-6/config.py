
import os

# Gateway Settings
GATEWAY_HOST = "0.0.0.0"
GATEWAY_PORT = 8000

# Redis Settings
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# News Article Server Routes
ROUTES = {
    "/api/news": "http://localhost:4001",
    "/api/articles": "http://localhost:4002",
    "/api/weather": "http://localhost:4003",
}

# Performance Settings
DEFAULT_RATE_LIMIT = 30  # requests per minute
CACHE_TTL = 60  # seconds
FAILURE_THRESHOLD = 5
RECOVERY_TIMEOUT = 30
