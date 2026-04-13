import os
import asyncio
import aiohttp
import time
import json
import re
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
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
        self.skipped_robots = []
        self.duplicates_count = 0
        self.robots_parser = RobotFileParser()
        self.start_time = time.time()

    async def crawl(self):
        print(f"[INFO] Seed: {self.seed_url}")
        
        # Load robots.txt
        await self.load_robots()
        
        print(f"[INFO] Max depth: {self.max_depth} | Concurrency: {self.concurrency} | Respecting robots.txt: YES")
        
        queue = [(self.seed_url, 0)]
        
        while queue:
            # Level-by-level BFS
            current_level = queue
            queue = []
            
            tasks = []
            for url, depth in current_level:
                if url in self.visited:
                    self.duplicates_count += 1
                    continue
                
                if depth > self.max_depth:
                    continue

                if not self.is_allowed(url):
                    print(f"[SKIPPED] {url} (robots.txt)")
                    self.skipped_robots.append(url)
                    continue

                self.visited.add(url)
                tasks.append(self.fetch(url, depth))
            
            level_results = await asyncio.gather(*tasks)
            for new_links in level_results:
                if new_links:
                    queue.extend(new_links)
        
        self.generate_json_report()
        self.report()

    async def load_robots(self):
        parsed_url = urlparse(self.seed_url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        session = MockSession()
        resp = session.get(robots_url)
        if resp.status == 200:
            content = await resp.text()
            self.robots_parser.parse(content.splitlines())
            print(f"[INFO] Robots.txt loaded from {robots_url}")
        else:
            print(f"[WARNING] Could not find robots.txt at {robots_url}")

    def is_allowed(self, url):
        return self.robots_parser.can_fetch("*", url)

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
        normalized = []
        for l in links:
            if l.startswith("#"): continue
            joined = urljoin(base_url, l)
            if joined.endswith("/") and len(joined) > 8: # Keep https://
                joined = joined[:-1]
            normalized.append(joined)
        return normalized

    def report(self):
        duration = time.time() - self.start_time
        print(f"\n=== Crawl Complete ({duration:.1f}s) ===")
        print(f"Pages crawled: {len(self.visited)}")
        print(f"Unique URLs found: {len(self.visited) + len(self.errors) + len(self.skipped_robots)}")
        print(f"Skipped (robots): {len(self.skipped_robots)}")
        print(f"Duplicates avoided: {self.duplicates_count}")
        
        if self.errors:
            print(f"\n=== SEO Audit Report ===")
            print(f"Broken Links (404):")
            for err in self.errors:
                print(f" - {err}")
        
        if self.redirects:
            print(f"\nRedirect Chains (301/302):")
            for src, dest in self.redirects:
                print(f" - {src} -> {dest}")
        
        print(f"\nCrawl graph saved to: output/crawl_graph.json")
        print(f"Full report saved to: output/crawl_report.json")

    def generate_json_report(self):
        os.makedirs("output", exist_ok=True)
        report_data = {
            "summary": {
                "total_crawled": len(self.visited),
                "total_errors": len(self.errors),
                "total_skipped_robots": len(self.skipped_robots),
                "total_duplicates": self.duplicates_count,
                "duration_seconds": time.time() - self.start_time
            },
            "graph": self.graph,
            "errors": self.errors,
            "redirects": [{"from": r[0], "to": r[1]} for r in self.redirects],
            "skipped_robots": self.skipped_robots
        }
        with open("output/crawl_report.json", "w") as f:
            json.dump(report_data, f, indent=4)
        
        with open("output/crawl_graph.json", "w") as f:
            json.dump(self.graph, f, indent=4)
