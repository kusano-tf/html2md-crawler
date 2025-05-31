import argparse
import asyncio

from loguru import logger

from crawler import extract_links_recursive
from html2md import fetch_and_convert


async def main(url: str, include_same_level: bool, output: str = None):
    urls = extract_links_recursive(url, include_same_level)
    logger.debug(f"Extracted {len(urls)} URLs from {url}")

    mds = await asyncio.gather(*(fetch_and_convert(url) for url in urls))

    md = "\n\n".join(mds)

    if output:
        with open(output, "w") as f:
            f.write(md)
    else:
        print(md)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL to start crawling from")
    parser.add_argument(
        "-i",
        "--include_same_level",
        action="store_true",
        help="Include links at the same level as the base URL",
    )
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
    asyncio.run(main(args.url, args.include_same_level, args.output))
