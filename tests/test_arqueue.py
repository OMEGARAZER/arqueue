"""Testing of arqueue."""

import pytest
from click.testing import CliRunner

from arqueue import main


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
def test_queue_empty(verbosity: str, expected_output: str):
    """Tests for empty queue."""
    runner = CliRunner()
    result = runner.invoke(main, verbosity)
    assert result.exit_code == 0
    if expected_output:
        assert expected_output in result.output
    else:
        assert "No torrents queued for download" not in result.output
