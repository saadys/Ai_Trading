import logging


class Logger;

def setup_logger(db_session, log_level=logging.INFO):
    """
    Configure et retourne une instance du logger pour l'application.
    Le logger est configuré pour écrire dans la base de données via SQLAlchemy.
    """
    global _logger
    if _logger:
        return _logger

    logger = logging.getLogger('trading_ai_logger')
    logger.setLevel(log_level)

    # --- Formateur ---
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # --- Handler pour la console (utile pour le développement) ---
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # --- Handler SQLAlchemy pour la base de données ---
    if db_session:
        db_handler = SQLAlchemyHandler(session=db_session)
        db_handler.setFormatter(formatter)
        logger.addHandler(db_handler)

    _logger = logger
    return _logger
