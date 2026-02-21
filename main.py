from app.services.streaming.QueueManager import QueueManager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from core.Config import Settings, get_settings
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI
from processors.SentimentProcessor.SentimentStrategypattern import SentimentStrategyFinbert
from processors.SentimentProcessor.SentimentProcessor import SentimentProcessor
from processors.SentimentProcessor.SentimentProviderFactory import SentimentStrategyFactory
from processors.SentimentProcessor.SentimentEnum import SentimentStrategy
from app.aggregators.ContextAggregator import ContextAggregator
from app.core.Logger import Logger
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from app.aggregators.ContextAggregator import ContextAggregator
from app.core.Logger import Logger  
app = FastAPI() 
settings = get_settings()

@app.on_event("startup")
async def startup_event(app: FastAPI):
    try:
        #Base de donnees POstgresSQl
        postgres_url= f"postgresql+asyncpg://{settings.Postgres_User}:{settings.Postgres_Password}@{settings.Postgres_Host}:{settings.Postgres_Port}/{settings.Postgres_DBName}"
        app.async_engine = create_async_engine(
            postgres_url
        )
        app.database_client = sessionmaker(
                    bind=app.async_engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                    ) 
        #RabbitMQ 
        app.queue_manager = QueueManager(settings)
        await app.queue_manager.connect()
        await app.queue_manager.setup_broker()
        Logger.info("Connexion à RabbitMQ établie et broker configuré.")
            
        #  DataSaver (Worker de fond)
        app.data_saver = DataSaver(app.queue_manager, app.database_client)
        await app.data_saver.start()
        Logger.info("DataSaver démarré.")

        symbol_value = SymbolEnum.BTCUSDT.value.lower()
        interval_value = KlineIntervalEnum.MIN_1.value
        
        socket_url = f"wss://stream.binance.com:9443/ws/{symbol_value}@kline_{interval_value}"
        binance_stream = BinanceStream(socket_url)

        data_collector = MarketDataCollector(binance_stream, app.queue_manager, "Binance")

        app.stream_processor = StreamProcessor(symbol_value.upper(), binance_stream, data_collector)
        await app.stream_processor.initialisation()
        Logger.info(f"StreamProcessor initialisé pour {symbol_value.upper()}.")
        asyncio.create_task(app.stream_processor.start())
        
        app.indicator_service = IndicatorService(app.queue_manager, SymbolEnum.BTCUSDT)
        Logger.info(f"IndicatorService initialisé pour {symbol_value.upper()}.")
        asyncio.create_task(app.indicator_service.calculate_indicators())
        Logger.info(f"Flux et calcul d'indicateurs lancés pour {symbol_value.upper()}.")

        # La partie Sentiment :
        strategy_type = SentimentStrategy.FINBERT.value
        app.sentiment_processor = SentimentProcessor(app.queue_manager, SentimentStrategyFactory.get_strategy(strategy_type), app.database_client)
        asyncio.create_task(app.sentiment_processor.start())
        Logger.info("SentimentProcessor démarré.")

        # ContextAggregator (accumule toutes les données: OHLCV, indicateurs, sentiment, ML)
        app.context_aggregator = ContextAggregator(app.queue_manager)
        asyncio.create_task(app.context_aggregator.start())
        Logger.info("ContextAggregator démarré et en écoute de la queue.")

        # Scheduler APScheduler pour déclencher aggregate() tous les 15min
        app.scheduler = BackgroundScheduler()
        app.scheduler.add_job(
            func=app.context_aggregator.aggregate,
            trigger='interval',
            minutes=15,
            id='aggregate_15min',
            name='Agrégation contexte toutes les 15 minutes'
        )
        app.scheduler.start()
        Logger.info("Scheduler APScheduler démarré - aggregate() chaque 15 minutes.")

        # ContextAggregator
        app.context_aggregator = ContextAggregator(app.queue_manager)
        asyncio.create_task(app.context_aggregator.start())
        Logger.info("ContextAggregator démarré et en écoute.")

        # Scheduler pour déclencher aggregate() tous les 15min
        app.scheduler = Scheduler()
        app.scheduler.add_job(
            func=app.context_aggregator.aggregate,
            trigger='interval',
            minutes=15,
            id='aggregate_15min'
        )
        app.scheduler.start()
        Logger.info("Scheduler démarré - aggregate() tous les 15min.")
    except Exception as e:
        Logger.error(f"Erreur critique lors du démarrage : {str(e)}")
        raise e


@app.on_event("shutdown")
async def shutdown_event():
    Logger.info("Arrêt de l'application...")
    
    # Arrêter le scheduler
    if hasattr(app, 'scheduler') and app.scheduler.running:
        app.scheduler.shutdown()
        Logger.info("Scheduler arrêté.")
    
    await app.queue_manager.disconnect()
    await app.database_client.dispose()
    await app.async_engine.dispose()
    


app.include_router(base_router)
app.include_router(streaming_router)
