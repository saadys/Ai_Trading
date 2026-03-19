import logging

_logger_instance = None

class LoggerConfig:
    def __init__(self, db_session, log_level=logging.INFO):
        global _logger_instance
        
        if _logger_instance is not None:
            return

        import sys
        
        logger = logging.getLogger('trading_ai_logger')
        logger.setLevel(log_level)
        logger.propagate = False  # Empêche uvicorn de supprimer ou de dupliquer les logs

        if not logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            # pour local (affichage forcé dans la console uvicorn)
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            # SQlAlchemy (si implémenté plus tard)
            if db_session:
                try:
                    db_handler = SQLAlchemyHandler(session=db_session)
                    db_handler.setFormatter(formatter)
                    logger.addHandler(db_handler)
                except NameError:
                    pass

        _logger_instance = logger


class Logger():
    @staticmethod
    def _get_logger():
        if not _logger_instance :
            LoggerConfig(db_session=None)
        return _logger_instance

    @staticmethod
    def debug(message):
        Logger._get_logger().debug(message)

    @staticmethod
    def info(message):
        Logger._get_logger().info(message)

    @staticmethod
    def error(message):
        Logger._get_logger().error(message)
    
    @staticmethod
    def warning(message):
        Logger._get_logger().warning(message)

    @staticmethod
    def critical(message):
        Logger._get_logger().critical(message)


logger = Logger



