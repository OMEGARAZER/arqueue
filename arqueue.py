#!/usr/bin/env python3
"""Automated downloading of queue items from AlphaRatio."""

import json
import sys
from pathlib import Path

import click
from environs import Env, EnvError
from httpx import Client, Headers
from loguru import logger

__version__ = "1.1.1"


def _check_version(context: click.core.Context, _param: click.core.Option, value: bool) -> None:  # noqa: FBT001
    if not value or context.resilient_parsing:
        return
    logger.configure(handlers=[{"sink": sys.stdout, "format": "{message}", "level": "INFO"}])
    try:
        client = Client(http2=True)
        latest = client.get("https://pypi.org/pypi/arqueue/json").json()["info"]["version"]
        logger.info("You are currently using v{} the latest is v{}", __version__, latest)
        client.close()
    except TimeoutError:
        logger.exception("Timeout reached fetching current version from Pypi - ARQueue v{}", __version__)
        raise
    context.exit()


def set_logging(context: click.core.Context) -> None:
    """Set logging level."""
    if not context.params["verbose"]:
        level = "INFO"
    elif context.params["verbose"] == 1:
        level = "DEBUG"
    elif context.params["verbose"] >= 2:
        level = "TRACE"
    logger.configure(
        handlers=[
            {"sink": sys.stdout, "format": "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", "level": level},
        ],
    )


def get_config(context: click.core.Context) -> dict:
    """Gather config data."""
    config = {}
    config_path = None
    if context.params["config"]:
        logger.info("Setting config location to {}", context.params["config"])
        config_path = context.params["config"]
        if not Path(config_path).expanduser().exists():
            logger.error("Config file not found at {}", config_path)
            sys.exit(5)
    elif Path("~/.config/arqueue/config").expanduser().is_file():
        logger.debug("Using config at {}", Path("~/.config/arqueue/config").expanduser())
        config_path = Path("~/.config/arqueue/config").expanduser()
    elif Path(".env").is_file() and not config_path:
        logger.debug("Using config at {}", Path(Path(), ".env"))
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


@click.command()
@click.option("-c", "--config", "config", type=str, default=None, help="Specify a config file to use.")
@click.help_option("-h", "--help")
@click.option("-v", "--verbose", count=True, default=None, help="Increase verbosity of output.")
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_check_version,
    help="Check version and exit.",
)
@click.pass_context
def main(context: click.Context, **_) -> None:
    """Automated downloading of queue items from AlphaRatio."""
    set_logging(context)
    config = get_config(context)
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
    try:
        queue = result["response"]
        logger.debug("Queue length: {}", len(queue))
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
