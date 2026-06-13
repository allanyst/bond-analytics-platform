from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import patch, MagicMock
from ingestion.fred_client import fetch_series


MOCK_OBSERVATIONS = [
    {"date": "2024-01-01", "value": "3.5", "realtime_start": "2024-01-01", "realtime_end": "9999-01-01"},
    {"date": "2024-02-01", "value": "3.7", "realtime_start": "2024-02-01", "realtime_end": "9999-01-01"},
]


def test_fetch_series_returns_observations():
    mock_response = MagicMock()
    mock_response.json.return_value = {"observations": MOCK_OBSERVATIONS}
    mock_response.raise_for_status.return_value = None

    with patch("ingestion.fred_client.requests.get", return_value=mock_response) as mock_get:
        result = fetch_series("BAMLH0A0HYM2")

    assert result == MOCK_OBSERVATIONS
    mock_get.assert_called_once()
    call_params = mock_get.call_args[1]["params"]
    assert call_params["series_id"] == "BAMLH0A0HYM2"
    assert call_params["file_type"] == "json"


def test_fetch_series_raises_on_http_error():
    import requests
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")

    with patch("ingestion.fred_client.requests.get", return_value=mock_response):
        with pytest.raises(requests.exceptions.HTTPError):
            fetch_series("INVALID_SERIES")


def test_fetch_series_uses_api_key_from_env():
    mock_response = MagicMock()
    mock_response.json.return_value = {"observations": MOCK_OBSERVATIONS}
    mock_response.raise_for_status.return_value = None

    with patch("ingestion.fred_client.requests.get", return_value=mock_response) as mock_get:
        with patch.dict(os.environ, {"FRED_API_KEY": "test-key-123"}):
            fetch_series("BAMLH0A0HYM2")

    call_params = mock_get.call_args[1]["params"]
    assert call_params["api_key"] == "test-key-123"
