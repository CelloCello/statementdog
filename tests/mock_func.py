from dataclasses import dataclass, field

from .data.twse import FAKE_TWSE
from statementdog.fetcher import StockInfo, ExchangeReport
from statementdog.parser import parse_exchange_result


@dataclass
class MockResponse:
    text: str = ""
    data_dict: dict = field(default_factory=dict)

    def json(self):
        return self.data_dict


def mock_request_stocks(url, headers, *args, **kwargs):
    with open("./tests/data/stock_result.html", "r") as f:
        result_text = f.read()
    return MockResponse(text=result_text)


def mock_request_exchange_report(url, headers, *args, **kwargs):
    stock_no = kwargs["params"]["stockNo"]
    return MockResponse(data_dict=FAKE_TWSE[stock_no])


def mock_fetch_stocks() -> list[StockInfo]:
    results = []
    for key, val in FAKE_TWSE.items():
        results.append(
            StockInfo(
                ticker=key,
                name=val["title"].split(' ')[2],
                listed_at="2022/05/24",
                industry="水泥工業",
            )
        )
    return results


def mock_fetch_exchange_report(ticker, date, retry_times=1) -> ExchangeReport:
    return parse_exchange_result(ticker, FAKE_TWSE[ticker])
