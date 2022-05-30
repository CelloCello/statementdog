from cloudstorage import get_driver_by_name

from statementdog import config


class Storage:
    def __init__(self, dir_name=""):
        self.driver = get_driver_by_name(config.STOR_TYPE)
        storage = self.driver(key=config.STOR_KEY, secret=config.STOR_SECRET)
        self.container = storage.create_container(f"stock-reports/{dir_name}")

    def upload(self, filename):
        self.container.upload_blob(filename)
