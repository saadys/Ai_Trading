
import logging


class LoggerConfig():
    def __init__(self,db_session):
        _logger = None
        self._logger = logging.getLogger(__name__)

        def setup_logger(db_session, log_level=logging.INFO)
            logger = logging.getLogger('trading_ai_logger')
            logger.setLevel(log_level)

            formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
            )
            if db_session:
                db_handler = SQLAlchemyHandler(session=db_session)
                db_handler.setFormatter(formatter)
                logger.addHandler(db_handler)

            _logger = logger
            return _logger
