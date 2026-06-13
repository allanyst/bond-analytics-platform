from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import patch, MagicMock, call
from ingestion.loaders import load_to_bronze


OBSERVATIONS = [
    {"date": "2024-01-01", "value": "3.5", "realtime_start": "2024-01-01", "realtime_end": "9999-01-01"},
    {"date": "2024-02-01", "value": ".",   "realtime_start": "2024-02-01", "realtime_end": "9999-01-01"},
    {"date": "2024-03-01", "value": "3.8", "realtime_start": "2024-03-01", "realtime_end": "9999-01-01"},
]


@patch("ingestion.loaders.psycopg2.connect")
def test_load_to_bronze_skips_dot_values(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    load_to_bronze("BAMLH0A0HYM2", OBSERVATIONS)

    # 3 observaciones pero la del "." debe saltarse → solo 2 INSERTs
    assert mock_cursor.execute.call_count == 2


@patch("ingestion.loaders.psycopg2.connect")
def test_load_to_bronze_inserts_correct_values(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    load_to_bronze("BAMLH0A0HYM2", OBSERVATIONS)

    first_call_args = mock_cursor.execute.call_args_list[0][0][1]
    assert first_call_args[0] == "BAMLH0A0HYM2"
    assert first_call_args[1] == "2024-01-01"
    assert first_call_args[2] == "3.5"


@patch("ingestion.loaders.psycopg2.connect")
def test_load_to_bronze_commits_and_closes(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    load_to_bronze("BAMLH0A0HYM2", OBSERVATIONS)

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
