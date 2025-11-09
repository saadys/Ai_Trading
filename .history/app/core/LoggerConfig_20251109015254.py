
import logging

_logger_instance = None
class LoggerConfig():
    def __init__(self,db_session,log_level):
        global _logger_instance

        if _logger_instance:
            return

    def setup_logger(self,db_session, log_level=logging.INFO):
        logger = logging.getLogger('trading_ai_logger')
        logger.setLevel(log_level)

        formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
        )
        if self.db_session:
            db_handler = SQLAlchemyHandler(session=self.db_session)
            db_handler.setFormatter(formatter)
            logger.addHandler(db_handler)

        _logger = logger
        return _logger
