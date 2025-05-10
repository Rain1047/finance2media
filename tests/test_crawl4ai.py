import asyncio
from crawl4ai import *
import os


async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.coinglass.com/pro/i/alt-coin-season",
        )
        print(result.markdown)
        os.makedirs("./data", exist_ok=True)  # 使用相对路径
        with open("./data/result.md", "w", encoding="utf-8") as file:
            file.write(result.markdown)
        # save result.markdown to markdown files in ./data folder


if __name__ == "__main__":
    asyncio.run(main())