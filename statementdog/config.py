import os

from dotenv import load_dotenv

load_dotenv()

# exchange report handling
SLEEP_TIME = 3  # second
RETRY_TIMES = 3

# storage
STOR_ROOT_DIR = os.getenv("STOR_ROOT_DIR", "./results")
STOR_TYPE = os.getenv("STOR_TYPE", "LOCAL")
STOR_KEY = os.getenv("STOR_KEY", "./results")
STOR_SECRET = os.getenv("STOR_SECRET", "test-secret")
