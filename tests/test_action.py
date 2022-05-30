import os
import json
import shutil
from unittest import mock

# import statementdog.action.fetch
from statementdog.action import proc_gain_top3_by_industry
from statementdog import config
from .mock_func import mock_fetch_stocks, mock_fetch_exchange_report


@mock.patch(
    "statementdog.action.fetch_exchange_report", mock_fetch_exchange_report
)
@mock.patch("statementdog.action.fetch_stocks", mock_fetch_stocks)
def test_proc_top3():
    # case: success
    shutil.rmtree(config.STOR_ROOT_DIR)
    proc_gain_top3_by_industry()

    target_filename = os.path.join(config.STOR_ROOT_DIR, "listed.json")
    assert os.path.exists(target_filename)
    with open(target_filename, "r") as f:
        saved_data = json.loads(f.read())
    assert saved_data[1]["ticker"] == "1102"
