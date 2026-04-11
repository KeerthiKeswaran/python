class MockResponse:
    def __init__(self, url, status=200, text="", headers=None):
        self.url = url
        self.status = status
        self._text = text
        self.headers = headers or {"Content-Type": "text/html"}
    
    async def text(self): return self._text
    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): pass

class MockSession:
    def __init__(self):
        self.site_map = {
            "https://example.com": (200, '<a href="/about">About</a> <a href="/products">Products</a> <a href="/blog">Blog</a>'),
            "https://example.com/about": (200, '<a href="/team/john">John</a> <a href="/careers">Careers</a>'),
            "https://example.com/products": (200, '<a href="/products/widget-pro">Widget Pro</a> <a href="/old-promo">Old Promo</a>'),
            "https://example.com/blog": (200, '<a href="/blog/post-1">Post 1</a>'),
            "https://example.com/products/widget-pro": (200, ''),
            "https://example.com/blog/post-1": (200, '<a href="/blog/post-1/comments">Comments</a>'),
            "https://example.com/old-promo": (301, '/products'),
            "https://example.com/careers": (404, 'Not Found'),
            "https://example.com/blog/post-1/comments": (200, '')
        }
    
    def get(self, url):
        status, text = self.site_map.get(url, (404, "Not Found"))
        return MockResponse(url, status, text)
    
    async def close(self): pass
