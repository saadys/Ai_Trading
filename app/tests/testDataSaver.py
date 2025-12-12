import sys
import os
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, text

# 1. Setup Environment
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from app.services.streaming.QueueManager import QueueManager
from app.services.streaming.BinanceStream import BinanceStream
from app.pipeline.collectors.MarketDataCollector import MarketDataCollector
from app.executors.DataSaver import DataSaver
from app.core.Config import Settings
from app.core.Logger import LoggerConfig
from app.models.db_schemas.mini_Trading.schemas.MarketData import MarketData
from app.models.db_schemas.mini_Trading.schemas.IndicatorTechnique import IndicatorTechnique

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IntegrationPipeline")

class TestPipelineIntegration:
    def __init__(self):
        # Initialize App Logger (required by other components)
        LoggerConfig(db_session=None)
        
        self.settings = Settings()
        
        self.queue_manager = None
        self.binance_stream = None
        self.collector = None
        self.data_saver = None
        self.database_engine = None
        self.session_maker = None

    async def setup_database(self):
        """Initialise la connexion à la base de données (comme dans main.py)"""
        logger.info("Setting up Database connection...")
        postgres_url= f"postgresql+asyncpg://{self.settings.Postgres_User}:{self.settings.Postgres_Password}@{self.settings.Postgres_Host}:{self.settings.Postgres_Port}/{self.settings.Postgres_DBName}"
        
        self.database_engine = create_async_engine(postgres_url, echo=False)
        self.session_maker = sessionmaker(
            bind=self.database_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info("Database connection established.")

    async def ensure_database_exists(self):
        """Vérifie et crée la base de données si nécessaire"""
        logger.info("Checking if database exists...")
        # Connexion à la base 'postgres' par défaut pour créer la nôtre
        root_url = f"postgresql+asyncpg://{self.settings.Postgres_User}:{self.settings.Postgres_Password}@{self.settings.Postgres_Host}:{self.settings.Postgres_Port}/postgres"
        engine = create_async_engine(root_url, isolation_level="AUTOCOMMIT")
        
        try:
            async with engine.connect() as conn:
                # Vérifier si la BD existe
                query = text("SELECT 1 FROM pg_database WHERE datname = :dbname")
                result = await conn.execute(query, {"dbname": self.settings.Postgres_DBName})
                exists = result.scalar() is not None
                
                if not exists:
                    logger.info(f"Database {self.settings.Postgres_DBName} not found. Creating...")
                    await conn.execute(func.text(f'CREATE DATABASE "{self.settings.Postgres_DBName}"'))
                    logger.info("Database created successfully.")
                else:
                    logger.info("Database already exists.")
                    
                # Vérifier/Créer les tables
                # Note: Dans un vrai setup, on utiliserait Alembic. Ici on fait un create_all rapide avec le bon engine
                await self.create_tables()

        except Exception as e:
            logger.error(f"Database creation failed: {e}")
            raise
        finally:
            await engine.dispose()

    async def create_tables(self):
        """Crée les tables nécessaires via SQLAlchemy"""
        logger.info("Creating tables...")
        # On utilise l'engine configuré pour la bonne DB
        async with self.database_engine.begin() as conn:
            from app.models.db_schemas.mini_Trading.schemas.Base_Trading import SQLAlchemyBase
            await conn.run_sync(SQLAlchemyBase.metadata.create_all)
        logger.info("Tables created.")

    async def setup_pipeline(self):
        """Initialise RabbitMQ, Collector et DataSaver"""
        logger.info("Setting up Pipeline components...")
        
        # 1. Queue Manager
        self.queue_manager = QueueManager(settings=self.settings)
        await self.queue_manager.connect()
        
        # CLEANUP: Delete incompatible queues from previous runs
        try:
            logger.info("Cleaning up old queues...")
            await self.queue_manager.channel.queue_delete("database_saver_queue")
        except Exception as e:
            logger.warning(f"Could not delete queue (might not exist): {e}")

        await self.queue_manager.setup_broker()
        
        # 2. Data Saver (Consumer)
        if not self.session_maker:
            raise RuntimeError("Database must be setup before pipeline")
            
        # TEST MODE: Batch size of 1 to save immediately
        self.data_saver = DataSaver(self.queue_manager, self.session_maker, batch_size=1)
        await self.data_saver.start() # Start listening
        
        # 3. Binance Stream (Producer Source)
        # Using BTCUSDT 1s interval for frequent updates
        binance_url = "wss://stream.binance.com:9443/ws/btcusdt@kline_1s"
        self.binance_stream = BinanceStream(binance_url)
        
        # 4. Collector (Producer)
        self.collector = MarketDataCollector(self.binance_stream, self.queue_manager, "binance")
        
        logger.info("Pipeline components ready.")

    async def verify_data(self):
        """Vérifie si des données ont été insérées"""
        logger.info("Verifying data in Database...")
        async with self.session_maker() as session:
            result = await session.execute(select(func.count(MarketData.id_OHLCV)))
            count = result.scalar()
            logger.info(f"--- VERIFICATION RESULT: Found {count} rows in table OHLCV ---")
            
            if count > 0:
                # Show last row
                stmt = select(MarketData).order_by(MarketData.id_OHLCV.desc()).limit(1)
                result = await session.execute(stmt)
                last_row = result.scalar_one_or_none()
                if last_row:
                    logger.info(f"Last saved data: {last_row.symbol} time={last_row.open_time} price={last_row.open_price}")
            else:
                logger.warning("No data found in database! Pipeline might be broken.")

    async def run_test(self, duration_seconds: int = 15):
        """Exécute le test d'intégration"""
        logger.info(f"--- STARTING INTEGRATION TEST ({duration_seconds}s) ---")
        
        try:
            await self.setup_database() # Configure l'engine
            await self.ensure_database_exists() # Crée la DB et les tables
            await self.setup_pipeline() # Configure le reste
            
            # Start collecting (connects to Binance)
            await self.collector.start_collecting()
            
            logger.info(f"Collecting data for {duration_seconds} seconds...")
            await asyncio.sleep(duration_seconds)
            
            # Verify results
            await self.verify_data()
            
        except Exception as e:
            logger.error(f"Integration Test Error: {e}")
            raise
        finally:
            await self.teardown()

    async def teardown(self):
        """Nettoie les ressources"""
        logger.info("Tearing down resources...")
        if self.binance_stream:
            # Note: BinanceStream might not have a disconnect method exposed clearly, closing connection manually if needed
            pass 
            
        if self.queue_manager:
            await self.queue_manager.close()
            
        if self.database_engine:
            await self.database_engine.dispose()
            
        logger.info("--- TEST FINISHED ---")

# Entry point for running as a script
if __name__ == "__main__":
    test = TestPipelineIntegration()
    try:
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(test.run_test(duration_seconds=20))
    except KeyboardInterrupt:
        pass