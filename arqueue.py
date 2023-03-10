#!/usr/bin/env python3
"""Automated downloading of queue items from AlphaRatio."""

import json
import sys
from pathlib import Path

from environs import Env, EnvError
from httpx import Client, Headers
from loguru import logger

__version__ = "1.0.0-1"


def set_logging() -> None:
    """Set logging level."""
    level = "INFO"
    if "-vv" in sys.argv:
        level = "TRACE"
        sys.argv.remove("-vv")
    if "-v" in sys.argv:
        level = "DEBUG"
        sys.argv.remove("-v")
    logger.configure(
        handlers=[
            {"sink": sys.stdout, "format": "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", "level": level},
        ],
    )


def get_config() -> dict:
    """Gather config data."""
    config = {}
    config_path = None
    if "-c" in sys.argv:
        sys.argv.remove("-c")
        logger.info("Setting config location to {}", sys.argv[0])
        config_path = sys.argv[0]
        if not Path(config_path).exists():
            logger.error("Config file not found at {}", config_path)
            sys.exit(5)
    elif Path("~/.config/arqueue/config").expanduser().is_file():
        logger.info("Using config at {}", Path("~/.config/arqueue/config").expanduser())
        config_path = Path("~/.config/arqueue/config").expanduser()
    elif Path(".env").is_file() and not config_path:
        logger.info("Using config at {}", Path(Path(), ".env"))
        config_path = ".env"
    elif not Path(Path(__file__).parent, ".env").is_file() and not config_path:
        logger.error(".env file not found at {}", Path(Path(__file__).parent, ".env"))
        sys.exit(5)
    env = Env()
    env.read_env(path=config_path, recurse=False)
    try:
        config["auth_key"] = env("auth_key")
        config["torr_pass"] = env("torrent_pass")
        config["watch_dirs"] = env.dict("watch_dirs")
    except EnvError:
        logger.exception("Key error in .env")
        sys.exit(11)
    return config


def main() -> None:
    """Automated downloading of queue items from AlphaRatio."""
    set_logging()
    config = get_config()
    headers = Headers({"User-Agent": "AlphaRatio Queue"})
    client = Client(headers=headers, http2=True, base_url="https://alpharatio.cc")
    url_keys = f"&authkey={config['auth_key']}&torrent_pass={config['torr_pass']}"
    url = f"/torrents.php?action=getqueue{url_keys}"
    logger.trace("Queue request URL: https://alpharatio.cc{}", url)
    response = client.get(url)
    result = json.loads(response.text)
    logger.debug("Queue response: {}", result)

    if result["status"] == "error":
        logger.debug("No torrents queued for download")
        sys.exit()
    logger.debug("Queue length: {}", len(result))
    try:
        queue = result["response"]
    except KeyError:
        logger.exception("No response key found and status is not error")
        sys.exit(18)

    for item in queue:
        logger.debug("Processing queue item: {}", item)
        torrent_id = item["TorrentID"]
        download_link = f"/torrents.php?action=download&id={torrent_id}{url_keys}"
        if int(item["FreeLeech"]):
            download_link = f"{download_link}&usetoken=1"
            logger.debug("Freeleech download")
        logger.trace("Download link: https://alpharatio.cc{}", download_link)
        category = item["Category"]
        watch_dirs = config["watch_dirs"]
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
