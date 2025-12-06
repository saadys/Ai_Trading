from app.core.Config import get_settings, Settings

class BaseDataModel:

<<<<<<< HEAD
    def __init__(self, db_client: object):
        self.db_client = db_client
        self.app_setting = get_settings()
=======
    def __init__(self, database_client: object):
        self.database_client = database_client
        self.app_setting = get_settings()
>>>>>>> c0f2d1f (feat: Implement streaming market data collection, processing, and persistence pipeline with new models, services, and tests.)
