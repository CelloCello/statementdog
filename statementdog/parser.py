from asyncio.log import logger
from dataclasses import dataclass

from pyquery import PyQuery as pq


@dataclass
class StockInfo:
    ticker: str = ""
    name: str = ""
    listed_at: str = ""
    industry: str = ""


@dataclass
class ExchangeReport:
    ticker: str = ""
    diff: float = 0.0

    def to_result(self):
        return {
            "ticker": self.ticker,
            "diff": f"{round(self.diff, 2)}%",
        }


def parse_stock_info(raw) -> list[StockInfo]:
    doc = pq(raw)
    stocks_table_obj = doc(".h4").eq(0)
    stocks_tr_objs = list(stocks_table_obj.items("tr"))

    results = []
    for s in stocks_tr_objs[2:]:
        stock_infos = s.text().split("\n")
        if stock_infos[0] == "上市認購(售)權證":
            break
        ticker, name = stock_infos[0].split("\u3000")
        results.append(
            StockInfo(
                ticker=ticker,
                name=name,
                listed_at=stock_infos[2],
                industry=stock_infos[4],
            )
        )
    return results


def parse_exchange_result(ticker, raw) -> ExchangeReport:
    try:
        latest_data = raw["data"][-1]
        open = (
            float(latest_data[3].replace(",", ""))
            if latest_data[3] != "--"
            else 0.0
        )
        close = (
            float(latest_data[6].replace(",", ""))
            if latest_data[3] != "--"
            else 0.0
        )
        diff = close - open
        return ExchangeReport(ticker=ticker, diff=diff)
    except Exception as e:
        logger.warning(f"exchange parse failed: {ticker}, {repr(e)}")
        raise e
