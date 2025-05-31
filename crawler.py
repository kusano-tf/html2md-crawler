import argparse
from typing import Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from loguru import logger

from utils.http_utils import fetch_html


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def is_same_or_child(base_url: str, target_url: str, include_same: bool = True) -> bool:
    base_url_parsed = urlparse(base_url)
    target_url_parsed = urlparse(target_url)
    if (
        base_url_parsed.scheme != target_url_parsed.scheme
        or base_url_parsed.netloc != target_url_parsed.netloc
    ):
        return False

    base_path = base_url_parsed.path.rstrip("/")
    target_path = target_url_parsed.path.rstrip("/")

    # 親のディレクトリまで取得
    base_dir = base_path.rsplit("/", 1)[0] if "/" in base_path else ""
    target_dir = target_path.rsplit("/", 1)[0] if "/" in target_path else ""

    if target_dir == base_dir:
        return include_same
    elif target_dir.startswith(base_dir + "/"):
        return True
    else:
        return False


def extract_links(base_url: str, include_same: bool) -> Set[str]:
    logger.debug(f"Extracting links from {base_url}")

    try:
        html = fetch_html(base_url)
    except requests.exceptions.HTTPError:
        return set()

    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        full_url = urljoin(base_url, a["href"])
        links.add(normalize_url(full_url))
    return set(
        link
        for link in links
        if is_same_or_child(base_url, link, include_same=include_same)
    )


def extract_links_recursive(
    base_url: str, include_same: bool, has_checked: Set[str] = None
) -> Set[str]:
    if has_checked is None:
        has_checked = set()

    if base_url in has_checked:
        return set()

    links = extract_links(base_url, include_same)

    all_links = set([base_url]) | set(links)

    for link in links:
        if link in has_checked:
            continue
        all_links |= extract_links_recursive(link, False, has_checked)

    return all_links


def main(url: str, include_same: bool):
    links = extract_links_recursive(url, include_same)

    print("\n".join(sorted(links)))


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
        "-q", "--quiet", action="store_true", help="Suppress log output"
    )
    args = parser.parse_args()

    if args.quiet:
        logger.remove()

    logger.debug(f"{args=}")
    main(args.url, args.include_same_level)
