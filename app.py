import logging

from statementdog.action import proc_gain_top3_by_industry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)10.19s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)


def main():
    proc_gain_top3_by_industry()


if __name__ == "__main__":
    main()
