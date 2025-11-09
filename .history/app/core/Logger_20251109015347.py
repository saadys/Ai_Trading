import logging

_logger_instance = None

class LoggerConfig:
    """
    Une classe dédiée à la CONFIGURATION du logger.
    On ne l'instancie qu'une seule fois.
    """
    def __init__(self, db_session, log_level=logging.INFO):
        global _logger_instance
class Logger():
    pass

