import asyncio
import argparse
from crawler import WebCrawler

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", required=True)
    parser.add_argument("--depth", type=int, default=3)
    parser.add_argument("--concurrency", type=int, default=20)
    args = parser.parse_args()

    print("=== Crawl Started ===")
    crawler = WebCrawler(args.seed, args.depth, args.concurrency)
    await crawler.crawl()

if __name__ == "__main__":
    asyncio.run(main())
