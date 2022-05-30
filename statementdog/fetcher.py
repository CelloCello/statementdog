import logging
import time

import requests

from statementdog.utils.decorator import calc_time
from statementdog.parser import (
    parse_stock_info,
    parse_exchange_result,
    StockInfo,
    ExchangeReport,
)
from statementdog import config


logger = logging.getLogger()
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 "
        "Safari/537.36 Edg/101.0.1210.47"
    )
}


@calc_time(logging.INFO)
def fetch_stocks() -> list[StockInfo]:
    try:
        url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
        resp = requests.get(url, headers=HEADERS)
        return parse_stock_info(resp.text)
    except Exception as e:
        logger.warning(f"fetch error: {repr(e)}")
        import traceback

        traceback.print_exc()
    return []


@calc_time()
def fetch_exchange_report(
    ticker, date, retry_times=config.RETRY_TIMES
) -> ExchangeReport:
    """date format: 20220512"""
    for i in range(retry_times):
        url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
        params = {
            "date": date,
            "stockNo": ticker,
            "response": "json",
        }
        try:
            resp = requests.get(url, headers=HEADERS, params=params)
            return parse_exchange_result(ticker, resp.json())
        except Exception as e:
            logger.warning(f"fetch error ({ticker} - {i}): {date} {repr(e)}")
            time.sleep(config.SLEEP_TIME ** (i + 1))
    return ExchangeReport()
