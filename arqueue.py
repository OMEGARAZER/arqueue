#!/usr/bin/env python3
"""Automated downloading of queue items from AlphaRatio."""

import json
import sys
from pathlib import Path

from environs import Env, EnvError
from httpx import Client, Headers
from loguru import logger

__version__ = "0.9.0"

logger.configure(
    # Change level to DEBUG to verify keys and responses are as expected. WILL DISPLAY SECRETS FROM ENV FILE.
    handlers=[{"sink": sys.stdout, "format": "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", "level": "INFO"}],
)

if not Path(Path(__file__).parent, ".env").is_file():
    logger.error(".env file not found at {}", Path(__file__).parent)
    sys.exit(5)

config = Env()
config.read_env(recurse=False)
try:
    auth_key = config("auth_key")
    torr_pass = config("torrent_pass")
    watch_dirs = config.dict("watch_dirs")
except EnvError:
    logger.exception("Key error in .env")
    sys.exit(11)


def main() -> None:
    """Automated downloading of queue items from AlphaRatio."""
    headers = Headers({"User-Agent": "AlphaRatio Queue"})
    client = Client(headers=headers, http2=True, base_url="https://alpharatio.cc")
    url = f"/torrents.php?action=getqueue&authkey={auth_key}&torrent_pass={torr_pass}"
    logger.debug("Queue request URL: https://alpharatio.cc{}", url)
    response = client.get(url)
    result = json.loads(response.text)
    logger.debug("Queue length: {}", len(result))
    logger.debug("Queue response: {}", result)

    if result["status"] == "error":
        logger.debug("No torrents queued for download")
        sys.exit()
    try:
        queue = result["response"]
    except KeyError:
        logger.exception("No response key found and status is not error")
        sys.exit(18)

    for item in queue:
        logger.debug("Processing queue item: {}", item)
        torrent_id = item["TorrentID"]
        download_link = f"/torrents.php?action=download&id={torrent_id}&authkey={auth_key}&torrent_pass={torr_pass}"
        if int(item["FreeLeech"]):
            download_link = f"{download_link}&usetoken=1"
            logger.debug("FREELEECH!")
        logger.debug("Download link: https://alpharatio.cc{}", download_link)
        category = item["Category"]
        try:
            watch_dir = watch_dirs[category]
        except KeyError:
            watch_dir = watch_dirs["Default"]
        logger.debug("Watch dir: {} with category {}", watch_dir, category)
        torrent_response = client.get(download_link)
        filename = torrent_response.headers["Content-Disposition"].split('filename="')[1][:-1]
        torrent_path = Path(watch_dir, filename)
        Path.open(torrent_path, mode="wb").write(torrent_response.read())
        logger.info("Downloaded {} to {} successfully", filename[:-8], watch_dir)

    client.close()


if __name__ == "__main__":
    main()
