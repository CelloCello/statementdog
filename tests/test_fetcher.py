from unittest import mock

from statementdog.fetcher import fetch_stocks, fetch_exchange_report
from .mock_func import mock_request_stocks, mock_request_exchange_report


def test_fetch_stocks():
    # case: success
    with mock.patch("requests.get", mock_request_stocks):
        results = fetch_stocks()
        assert len(results) == 5
        assert results[-1].ticker == "1108"

    # case: fetch failed
    with mock.patch("requests.get") as req:
        req.return_value = "error"
        results = fetch_stocks()
        assert len(results) == 0


def test_fetch_exchange_report():
    date = "20220525"

    # case: success
    ticker = "1102"
    with mock.patch("requests.get", mock_request_exchange_report):
        result = fetch_exchange_report(ticker, date, retry_times=1)
        assert result.ticker == ticker
        assert round(result.diff, 2) == 0.7

    # case: no exchanging, diff will be 0
    ticker = "1103"
    with mock.patch("requests.get", mock_request_exchange_report):
        result = fetch_exchange_report(ticker, date, retry_times=1)
        assert result.ticker == ticker
        assert result.diff == 0.0

    # case: fetch failed
    ticker = "1101"
    with mock.patch("requests.get") as req:
        req.return_value = "error"
        result = fetch_exchange_report(ticker, date, retry_times=1)
        assert result.ticker == ''
