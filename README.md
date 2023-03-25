# AR Queue Watcher

[![PyPI Status](https://img.shields.io/pypi/status/arqueue?logo=PyPI)](https://pypi.python.org/pypi/arqueue)
[![PyPI version](https://img.shields.io/pypi/v/arqueue.svg?logo=PyPI)](https://pypi.python.org/pypi/arqueue)
[![Python Test](https://github.com/OMEGARAZER/arqueue/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/OMEGARAZER/arqueue/actions/workflows/test.yml)
[![linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json&label=linting)](https://github.com/charliermarsh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?logo=Python)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Automated downloading of queue items from AlphaRatio.

## Installation

### From pypi

Suggested to install via [pipx](https://pypa.github.io/pipx) with:

```bash
pipx install arqueue
```

or pip with:

```bash
pip install arqueue
```

### From repo

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

## Configuration

Configuration can be done in three ways:

1. Create a file with your auth_key, torrent_pass and your watch_dirs like they are in the `.env.sample` file and pass it to the script with `-c`.
2. Copy the `.env.sample` file to `.config/arqueue/config` and edit to contain your auth_key, torrent_pass and your watch_dirs.
3. Rename `.env.sample` to `.env` and edit to contain your auth_key, torrent_pass and your watch_dirs (not recommended unless installed from repo).

## Running

After configuring you can run it with:

```bash
arqueue
```

or if passing a config file:

```bash
arqueue -c <path to config>
```

You can increase the verbosity of the output by passing `-v` or `-vv`.

* `-v` enables debug output to show request responses and process updates.
* `-vv` enables trace output which shows debug output as well as requested urls (Which include the secrets, use only when required).

### Crontab

To run via crontab you can use this line, replacing {HOME} with your home directory.

```bash
* * * * * {HOME}/.local/bin/arqueue >/dev/null 2>&1
```

Unless [configured](#configuration) through option 3 you will need to pass your config as well.
