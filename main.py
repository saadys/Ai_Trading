import asyncio

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.auth.routes import router as auth_router

# Core
from app.core.config import Settings, get_settings
from app.core.logger import Logger, logger

# Pipeline
from app.services.streaming.QueueManager import QueueManager
from app.aggregators.ContextAggregator import ContextAggregator

# Stream, Indicators & Data
from app.executors.DataSaver import DataSaver
from app.services.streaming.BinanceStream import BinanceStream
from app.stream_processor.StreamProcessor import StreamProcessor
from app.analytics.IndicatorService import IndicatorService
from app.pipeline.collectors.MarketDataCollector import MarketDataCollector
from app.models.enums.SymbolEnum import SymbolEnum
from app.models.enums.KlineIntervalEnum import KlineIntervalEnum

# Sentiment
from app.processors.SentimentProcessor.SentimentStrategypattern import SentimentStrategyFinbert
from app.processors.SentimentProcessor.SentimentProcessor import SentimentProcessor
from app.processors.SentimentProcessor.SentimentProviderFactory import SentimentStrategyFactory
from app.processors.SentimentProcessor.SentimentEnum import SentimentStrategy
from app.pipeline.collectors.NewsCollector import NewsCollector


# LLM
from app.stores.LLM.PromptBuilder import PromptBuilder
from app.stores.LLM.LLMEnum import LLMEnum
from app.stores.LLM.LLMProviderFactory import LLMProviderFactory
from app.models.pydantic.LLMResponseValidator import LLMResponseValidator
from pydantic import ValidationError
from app.routers.streaming_routers import streaming_router
from app.routers.LLMRouters import llm_router
from app.routers.base import base_router
from app.routers.PredLSTMRouters import router as pred_lstm_router
from app.models.db_schemas.mini_Trading.schemas import SQLAlchemyBase

app = FastAPI()

app.include_router(streaming_router)
app.include_router(llm_router)
app.include_router(pred_lstm_router, prefix="/api/v1")
settings = get_settings()


#  LLM appelée par le scheduler toutes les 15 minutes
async def AGG_Decision_LLM():
    try:
        context = app.context_aggregator.aggregate_functions()
        if not context:
            logger.warning("[LLM] Contexte vide — décision ignorée pour ce cycle.")
            return

        prompt_text = app.prompt_builder.Construire_Prompt(context)
        decision = await app.llm_provider.aggregate_responses(prompt_text)

        if decision:
            try:
                raw_decision = app.llm_provider.Text_To_JSON(decision) if isinstance(decision, str) else decision
                
                # Double vérification via Pydantic pour s'assurer que la structure est parfaite
                validated_decision = LLMResponseValidator(**raw_decision)
                final = validated_decision.model_dump()
            except ValidationError as e:
                logger.error(f"[LLM] Erreur de validation Pydantic dans main.py : {e}")
                final = {"action": "HOLD", "confidence_score": 0.0, "risk_assessment": "EXTREME", "reasoning": "Validation Error in main.py"}
            except Exception as e:
                logger.error(f"[LLM] Erreur inattendue lors de la validation : {e}")
                final = {"action": "HOLD", "confidence_score": 0.0, "risk_assessment": "EXTREME", "reasoning": "Unexpected Error in Validation"}

            logger.info(
                f"\n{'='*50}\n"
                f" DÉCISION IA FINALE (GEMINI + LSTM) \n"
                f"Action    : {final.get('action')}\n"
                f"Confiance : {final.get('confidence_score')} %\n"
                f"Risque    : {final.get('risk_assessment')}\n"
                f"Raison    : {final.get('reasoning')}\n"
                f"{'='*50}\n"
            )
        else:
            logger.warning("[LLM] Aucune décision reçue du provider.")

    except Exception as e:
        logger.error(f"[LLM] Erreur dans aggregate_and_decide : {e}")


# Startup
@app.on_event("startup")
async def startup_event():
    try:
        #Base de donnees POstgresSQl
        postgres_url= f"postgresql+asyncpg://{settings.Postgres_User}:{settings.Postgres_Password}@{settings.Postgres_Host}:{settings.Postgres_Port}/{settings.Postgres_DBName}"
        app.async_engine = create_async_engine(
            postgres_url
        )
        
        async with app.async_engine.begin() as conn:
            await conn.run_sync(SQLAlchemyBase.metadata.create_all)
        Logger.info("Tables de la base de données analysées/créées avec succès.")

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

        # --- BinanceStream + StreamProcessor ---
        symbol_value = SymbolEnum.BTCUSDT.value.lower()
        interval_value = KlineIntervalEnum.MIN_15.value
        socket_url = f"wss://stream.binance.com:9443/ws/{symbol_value}@kline_{interval_value}"
        binance_stream = BinanceStream(socket_url)
        data_collector = MarketDataCollector(binance_stream, app.queue_manager, "Binance")
        app.stream_processor = StreamProcessor(symbol_value, binance_stream, data_collector)
        await app.stream_processor.initialisation()
        Logger.info(f"StreamProcessor initialisé pour {symbol_value}.")
        asyncio.create_task(app.stream_processor.start())

        app.indicator_service = IndicatorService(app.queue_manager, SymbolEnum.BTCUSDT)
        Logger.info(f"IndicatorService initialisé pour {symbol_value.upper()}.")
        asyncio.create_task(app.indicator_service.calculate_indicators())
        Logger.info(f"Flux et calcul d'indicateurs lancés pour {symbol_value.upper()}.")

        # La partie Sentiment :
        app.news_collector = NewsCollector(app.queue_manager, exchange_name='market_data_exchange', api_key=settings.NewsApi_Key)
        asyncio.create_task(app.news_collector.start_collection_loop())
        Logger.info(" Scraper d'Actualités (NewsCollector) CONNECTÉ à l'API.")

        # Démarrer l'analyseur (NLP FinBERT)
        strategy_type = SentimentStrategy.FINBERT.value
        app.sentiment_processor = SentimentProcessor(app.queue_manager, SentimentStrategyFactory.get_strategy(strategy_type), app.database_client)
        asyncio.create_task(app.sentiment_processor.start())
        Logger.info("Module d'Analyse NLP des Vraies Nouvelles (FinBERT) PRÊT.")

        # ContextAggregator (accumule toutes les données: OHLCV, indicateurs, sentiment, ML)
        app.context_aggregator = ContextAggregator(app.queue_manager)
        asyncio.create_task(app.context_aggregator.start())
        Logger.info("ContextAggregator démarré et en écoute de la queue.")

        #  LLM : PromptBuilder + Provider actif 
        app.prompt_builder = PromptBuilder()
        app.llm_provider = LLMProviderFactory(settings).create(LLMEnum.GEMINI)
        Logger.info(f"LLM Provider initialisé : {LLMEnum.GEMINI.name}")

        #  Scheduler Asynchrone 
        app.scheduler = AsyncIOScheduler()
        app.scheduler.add_job(
            func=AGG_Decision_LLM,
            trigger='interval',
            minutes=15,
            id='llm_decision_15min',
            name='Décision LLM toutes les 15 minutes'
        )
        app.scheduler.start()
        Logger.info("AsyncIOScheduler démarré — AGG_Decision_LLM() toutes les 15 minutes.")

    except Exception as e:
        Logger.error(f"Erreur critique lors du démarrage : {str(e)}")
        raise e

# Shutdown
@app.on_event("shutdown")
async def shutdown_event():
    Logger.info("Arrêt de l'application...")

    if hasattr(app, 'scheduler') and app.scheduler.running:
        app.scheduler.shutdown()
        Logger.info("Scheduler arrêté.")

    await app.queue_manager.disconnect()
    # await app.database_client.dispose()
    await app.async_engine.dispose()


app.include_router(base_router)
app.include_router(streaming_router)
app.include_router(auth_router)