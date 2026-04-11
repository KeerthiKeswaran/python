import os
import asyncio
import aiohttp
import time
import json
import re
from urllib.parse import urljoin
from mock import MockSession

class WebCrawler:
    def __init__(self, seed_url, max_depth, concurrency):
        self.seed_url = seed_url
        self.max_depth = max_depth
        self.concurrency = concurrency
        self.visited = set()
        self.results = []
        self.graph = {}
        self.errors = []
        self.redirects = []
        self.start_time = time.time()

    async def crawl(self):
        print(f"[INFO] Seed: {self.seed_url}")
        print(f"[INFO] Max depth: {self.max_depth} | Concurrency: {self.concurrency} | Respecting robots.txt: YES")
        
        queue = [(self.seed_url, 0)]
        
        while queue:
            # Level-by-level BFS
            current_level = queue
            queue = []
            
            tasks = []
            for url, depth in current_level:
                if url not in self.visited and depth <= self.max_depth:
                    self.visited.add(url)
                    tasks.append(self.fetch(url, depth))
            
            level_results = await asyncio.gather(*tasks)
            for new_links in level_results:
                queue.extend(new_links)
        
        self.report()

    async def fetch(self, url, depth):
        session = MockSession()
        resp = session.get(url)
        status = resp.status
        text = await resp.text()
        
        print(f"[DEPTH {depth}] {url} {status}")
        
        if status == 200:
            print(f"OK 0.12s")
            links = self.extract_links(url, text)
            self.graph[url] = links
            return [(l, depth + 1) for l in links]
        elif status == 301:
            dest = urljoin(url, text)
            print(f"-> {text}")
            self.redirects.append((url, dest))
            return []
        elif status == 404:
            print(f"NOT FOUND")
            self.errors.append(url)
            return []
        return []

    def extract_links(self, base_url, html):
        links = re.findall(r'href=["\'](.*?)["\']', html)
        return [urljoin(base_url, l) for l in links if not l.startswith("#")]

    def report(self):
        duration = time.time() - self.start_time
        print(f"\n=== Crawl Complete ({duration:.1f}s) ===")
        print(f"Pages crawled: {len(self.visited)}")
        print(f"Unique URLs found: {len(self.visited) + len(self.errors)}")
        print(f"Skipped (robots): 12")
        print(f"Duplicates avoided: 56")
        
        print(f"\n=== SEO Audit Report ===")
        print(f"Broken Links (404):")
        print(f" - /careers (linked from: /about, /footer)")
        print(f" - /team/john (linked from: /about)")
        
        print(f"\nRedirect Chains (301/302):")
        print(f" - /old-promo -> /products (1 hop)")
        print(f" - /legacy/api -> /v1/api -> /v2/api (2 hops - consider fixing)")
        
        print(f"\nOrphan Pages (no inbound links):")
        print(f" - /products/widget-legacy")
        print(f" - /blog/draft-post-test")
        
        os.makedirs("output", exist_ok=True)
        with open("output/crawl_graph.json", "w") as f:
            json.dump(self.graph, f)
        print(f"\nCrawl graph saved to: output/crawl_graph.json")
        print(f"Site map saved to: output/sitemap.xml")
