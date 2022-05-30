import os
import json
import time
import logging
from datetime import datetime
from dataclasses import asdict
from collections import defaultdict

from statementdog.fetcher import fetch_stocks, fetch_exchange_report
from statementdog.utils.decorator import calc_time
from statementdog.storage import Storage
from statementdog import config

logger = logging.getLogger()


@calc_time(logging.INFO)
def proc_gain_top3_by_industry():
    today = datetime.today()
    target_date = today.strftime("%Y%m%d")
    stocks = fetch_stocks()
    industry_map = defaultdict(list)
    stocks_to_save = []
    logger.info(f"Num of stocks: {len(stocks)}")
    for stock in stocks:
        # WARNING: request limit is 3 requests per 5 seconds
        report = fetch_exchange_report(stock.ticker, target_date)
        logger.info(
            f"exchange report: {stock.ticker}, {stock.name}, {report.diff}"
        )
        industry_map[stock.industry].append(report)
        stocks_to_save.append(asdict(stock))
        time.sleep(config.SLEEP_TIME)

    # sort by diff
    for key, val in industry_map.items():
        val.sort(key=lambda x: x.diff, reverse=True)
        save_to_storage(
            date=target_date,
            filename=os.path.join(config.STOR_ROOT_DIR, f"{key}_top3.json"),
            content=json.dumps([i.to_result() for i in val[:3]]),
        )

    # save stocks
    save_to_storage(
        date=target_date,
        filename=os.path.join(config.STOR_ROOT_DIR, "listed.json"),
        content=json.dumps(stocks_to_save),
    )


def save_to_storage(date, filename, content):
    os.makedirs(config.STOR_ROOT_DIR, exist_ok=True)
    with open(filename, "w+") as f:
        f.write(content)
    s = Storage(dir_name=date)
    s.upload(filename)
