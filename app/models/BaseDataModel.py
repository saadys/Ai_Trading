from app.core.config import get_settings, Settings

class BaseDataModel:

    def __init__(self, database_client: object):
        self.database_client = database_client
        self.app_setting = get_settings()