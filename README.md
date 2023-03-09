# AR Queue Watcher

[![linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json&label=linting)](https://github.com/charliermarsh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?logo=Python)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Automated downloading of queue items from AlphaRatio.

## Installation

Clone the repo with:

```bash
git clone https://github.com/OMEGARAZER/arqueue.git
cd ./arqueue
```

Suggested to install via [pipx](https://pypa.github.io/pipx) with:

```bash
pipx install -e .
```

or pip with:

```bash
pip install -e .
```

### Configuration

Configuration can be done in three ways:

1. Create a file with your auth_key, torrent_pass and your watch_dirs like they are in the `.env` file and pass it to the script with `-c`.
2. Copy the `.env` file to `.config/arqueue/config` and edit to contain your auth_key, torrent_pass and your watch_dirs.
3. Edit the `.env` file to contain your auth_key, torrent_pass and your watch_dirs.

### Running

After settings are stored in `.env` you can run it with:

```bash
arqueue
```

### Crontab

To run via crontab once installed and setup you can use this line, replacing {HOME} with your home directory.

```bash
* * * * * {HOME}/.local/bin/arqueue >/dev/null 2>&1
```

## Running without installing

The script can be run without installing at all, you simply lose the ability to run with `arqueue` and will need to be run directly.
You will still need to go through the steps in [configuration](#configuration) before running.
