import logging
from app.models.log import Log, LogLevel

class SQLAlchemyHandler(logging.Handler):
    """
    Un handler de logging qui écrit les enregistrements dans une base de données
    via SQLAlchemy.
    """
    def __init__(self, session):
        super().__init__()
        self.session = session

    def emit(self, record):
        """
        Écrit un enregistrement de log dans la base de données.
        """
        try:
            # Map le niveau de log du record à notre énumération
            level = LogLevel[record.levelname]
            
            # Crée une entrée de log
            log_entry = Log(
                level=level,
                message=self.format(record), # Formate le message
                module=record.module,
                funcName=record.funcName,
                lineNo=record.lineno
            )
            
            # Ajoute à la session
            self.session.add(log_entry)
            # Le commit sera géré par l'application principale
            # pour éviter les interférences de transaction.
            self.session.flush()

        except Exception:
            self.handleError(record)
