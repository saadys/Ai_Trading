import logging

_logger_instance = None

class LoggerConfig:
    """
    Une classe dédiée à la CONFIGURATION du logger.
    On ne l'instancie qu'une seule fois.
    """
    def __init__(self, db_session, log_level=logging.INFO):
        global _logger_instance
        
        if _logger_instance is not None:
            return

        logger = logging.getLogger('trading_ai_logger')
        logger.setLevel(log_level)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        #pour local
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        #SQlAlchemy:
        if db_session:
            db_handler = SQLAlchemyHandler(session=db_session)
            db_handler.setFormatter(formatter)
            logger.addHandler(db_handler)

        _logger_instance = logger


class Logger():
    @staticmethod
    def _get_logger():
        if not _logger_instance :
            raise Exception("Logger instance is not initialized")
        return _logger_instance

    @staticmethod
    def debug(message):
        Logger._get_logger().debug(message)



