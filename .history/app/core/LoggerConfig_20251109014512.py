


class LoggerConfig(logging.INFO):
    def __init__(self,db_session):
        _logger = None
        self._logger = logging.getLogger(__name__)
