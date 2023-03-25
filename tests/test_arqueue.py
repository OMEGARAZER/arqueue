"""Testing of arqueue."""

from pathlib import Path
from sys import platform

import pytest
from click.testing import CliRunner

from arqueue import main


def create_config(tmp_path: Path) -> None:
    """Create test config file."""
    default = Path(tmp_path, "watch")
    test_free = Path(tmp_path, "testFree")
    test_multi = Path(tmp_path, "testMulti")
    config_values = [
        'auth_key = "alpharatioalpharatioalpharatioal"\n',
        'torrent_pass = "alpharatioalpharatioalpharatioal"\n',
        f'watch_dirs = "Default={default},testFree={test_free},testMulti={test_multi}"',
    ]
    with Path(tmp_path, "config").open(mode="w") as config_file:
        config_file.writelines(config_values)


def create_args(verbosity: str, tmp_path: Path) -> list:
    """Create test args."""
    create_config(tmp_path)
    if verbosity:
        return ["--config", f"{tmp_path}/config", verbosity]
    return ["--config", f"{tmp_path}/config"]


@pytest.mark.block_network()
@pytest.mark.default_cassette("test_queue_empty.yaml")
@pytest.mark.vcr(filter_query_parameters=["authkey", "torrent_pass"])
@pytest.mark.parametrize(
    ("verbosity", "expected_output"),
    [
        ("", ""),
        ("-v", "No torrents queued for download"),
        ("-vv", "Queue request URL"),
    ],
)
def test_queue_empty(verbosity: str, expected_output: str, tmp_path: Path) -> None:
    """Tests for empty queue."""
    runner = CliRunner()
    args = create_args(verbosity, tmp_path)
    result = runner.invoke(main, args)
    assert result.exit_code == 0
    if expected_output:
        assert expected_output in result.output
    else:
        assert "No torrents queued for download" not in result.output


@pytest.mark.skipif(platform == "win32", reason="Broken on Windows")
@pytest.mark.block_network()
@pytest.mark.default_cassette("test_queue_one.yaml")
@pytest.mark.vcr(filter_query_parameters=["authkey", "torrent_pass"])
@pytest.mark.parametrize(
    ("verbosity", "expected_output"),
    [
        ("", "Downloaded "),
        ("-v", "Processing queue item"),
        ("-vv", "Download link"),
    ],
)
def test_queue_one(verbosity: str, expected_output: str, tmp_path: Path) -> None:
    """Tests for queue with single item."""
    runner = CliRunner()
    args = create_args(verbosity, tmp_path)
    result = runner.invoke(main, args)
    assert result.exit_code == 0
    assert expected_output in result.output
    assert result.output.count(expected_output) == 1


@pytest.mark.skipif(platform == "win32", reason="Broken on Windows")
@pytest.mark.block_network()
@pytest.mark.default_cassette("test_queue_multi.yaml")
@pytest.mark.vcr(filter_query_parameters=["authkey", "torrent_pass"])
@pytest.mark.parametrize(
    ("verbosity", "expected_output"),
    [
        ("", "Downloaded"),
        ("-v", "Processing queue item"),
        ("-vv", "Download link"),
    ],
)
def test_queue_multi(verbosity: str, expected_output: str, tmp_path: Path) -> None:
    """Tests for queue with multiple items."""
    runner = CliRunner()
    args = create_args(verbosity, tmp_path)
    result = runner.invoke(main, args)
    assert result.exit_code == 0
    assert expected_output in result.output
    assert result.output.count(expected_output) > 1


@pytest.mark.skipif(platform == "win32", reason="Broken on Windows")
@pytest.mark.block_network()
@pytest.mark.default_cassette("test_queue_free.yaml")
@pytest.mark.vcr(filter_query_parameters=["authkey", "torrent_pass"])
def test_queue_free(tmp_path: Path) -> None:
    """Tests for queue with free item."""
    runner = CliRunner()
    args = create_args("-v", tmp_path)
    result = runner.invoke(main, args)
    assert result.exit_code == 0
    assert "Freeleech download" in result.output
