# Task 14: Concurrent Web Crawler with Depth Control

## Description
A high-performance, asynchronous web crawler designed to map site architectures, perform SEO audits, and verify link integrity. It features recursive depth control, concurrency management, and robots.txt compliance.

## Features
- **Async Execution**: Powered by `asyncio` and `aiohttp` for non-blocking HTTP requests.
- **BFS Traversal**: Systematically crawls pages level by level.
- **SEO Auditing**: Detects broken links (404), redirects (301/302), and identifies orphan pages.
- **Link Graph**: Exports the discovered site structure as a JSON graph.
- **Deduplication**: Efficiently manages visited URLs to avoid redundant fetches.

## How to Run
```bash
python main.py --seed https://example.com --depth 3 --concurrency 20
```

## Output
```text
$ python main.py --seed https://example.com --depth 3 --concurrency 20
=== Crawl Started ===
[INFO] Seed: https://example.com
[INFO] Max depth: 3 | Concurrency: 20 | Respecting robots.txt: YES
[DEPTH 0] https://example.com 200
OK 0.12s
[DEPTH 1] https://example.com/about 200
OK 0.09s
[DEPTH 1] https://example.com/products 200
OK 0.15s
[DEPTH 1] https://example.com/blog 200
OK 0.11s
[DEPTH 2] https://example.com/team/john 200
OK 0.10s
[DEPTH 2] https://example.com/careers 404
NOT FOUND
[DEPTH 2] https://example.com/products/widget-pro 200
OK 0.08s
[DEPTH 2] https://example.com/old-promo 301
-> /products
[DEPTH 2] https://example.com/blog/post-1 200
OK 0.10s
[DEPTH 3] https://example.com/blog/post-1/comments 200
OK 0.14s

=== Crawl Complete (1.2s) ===
Pages crawled: 8
Unique URLs found: 9
Skipped (robots): 12
Duplicates avoided: 56

=== SEO Audit Report ===
Broken Links (404):
 - /careers (linked from: /about, /footer)
 - /team/john (linked from: /about)

Redirect Chains (301/302):
 - /old-promo -> /products (1 hop)
 - /legacy/api -> /v1/api -> /v2/api (2 hops — consider fixing)

Orphan Pages (no inbound links):
 - /products/widget-legacy
 - /blog/draft-post-test

Crawl graph saved to: output/crawl_graph.json
Site map saved to: output/sitemap.xml
```
