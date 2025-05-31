import argparse
import asyncio
import os
from typing import List

import dotenv
from loguru import logger
from openai import AsyncOpenAI

from utils.http_utils import fetch_html

dotenv.load_dotenv()

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM_PROMPT = """\
下記の条件に従って、できるだけ正確にHTMLをMarkdownへ変換してください。

- 与えられたHTMLから、メニュー・ナビゲーション等の補助的要素（<nav>, <menu>, <header>, <footer>, サイドバーなど）を除外し、メインコンテンツのみを変換対象としてください。
- 文章やリスト、画像、テーブルなどはMarkdownに適切に変換してください。
- 変換の際、見出しの階層構造はできるだけ維持してください。
- コードブロックや引用等も適切にMarkdown記法にしてください。
- 出力はMarkdownテキストのみにしてください（解説や説明は不要です）。
"""


async def html_to_md(html: str) -> str:
    response = await client.responses.create(
        model="gpt-4.1-mini",
        temperature=0.0,
        store=False,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": html},
        ],
    )

    logger.debug(f"{response.usage=}")
    return response.output[0].content[0].text


async def fetch_and_convert(url: str) -> str:
    logger.debug(f"Converting {url}")
    html = fetch_html(url)
    md = await html_to_md(html)
    return md


async def main(urls: List[str], output: str = None):
    mds = await asyncio.gather(*(fetch_and_convert(url) for url in urls))

    md = "\n\n".join(mds)

    if output:
        with open(output, "w") as f:
            f.write(md)
    else:
        print(md)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", nargs="+", help="URLs to convert to Markdown")
    parser.add_argument(
        "-o", "--output", help="Output file to save the links", default=None
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Suppress log output"
    )
    args = parser.parse_args()

    if args.quiet:
        logger.remove()

    logger.debug(f"{args=}")
    asyncio.run(main(args.urls, args.output))
