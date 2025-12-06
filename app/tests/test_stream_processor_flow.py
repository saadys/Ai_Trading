import sys
import os
import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

# Add project root to sys.path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Mocking Logger before importing StreamProcessor to avoid side effects
sys.modules['app.core.Logger'] = MagicMock()
from app.core.Logger import Logger
Logger.info = MagicMock()
Logger.error = MagicMock()

# Mock Config to avoid missing imports in Config.py (os, Path) and DB dependencies
sys.modules['app.core.Config'] = MagicMock()


# Now import StreamProcessor
from app.stream_processor.StreamProcessor import StreamProcessor

class TestStreamProcessorFlow(unittest.IsolatedAsyncioTestCase):
    async def test_flow(self):
        print("\n--- Starting StreamProcessor Flow Test ---")
        
        # 1. Setup Mocks
        symbol = "btcusdt"
        
        # Mock BinanceStream
        mock_binance_stream = MagicMock()
        mock_binance_stream.connect_to_binance_stream = AsyncMock()
        mock_binance_stream.disconnect = AsyncMock()
        mock_binance_stream.on_message_callback = None
        
        # Mock MarketDataCollector
        mock_market_data_collector = MagicMock()
        mock_queue_manager = MagicMock()
        mock_queue_manager.connect = AsyncMock()
        mock_queue_manager.setup_broker = AsyncMock()
        mock_market_data_collector.queue = mock_queue_manager
        mock_market_data_collector._process_raw_message = AsyncMock()

        # 2. Initialize StreamProcessor
        processor = StreamProcessor(symbol, mock_binance_stream, mock_market_data_collector)
        print("[Test] StreamProcessor instantiated.")

        # 3. Test Initialisation
        await processor.initialisation()
        print("[Test] initialisation() called.")
        
        # Verify QueueManager connection
        mock_queue_manager.connect.assert_awaited_once()
        mock_queue_manager.setup_broker.assert_awaited_once()
        print("[Test] QueueManager connected and broker setup verified.")
        
        # Verify Callback setup
        self.assertEqual(mock_binance_stream.on_message_callback, processor._buffer_message)
        print("[Test] on_message_callback set correctly.")

        # 4. Test Start (Background)
        start_task = asyncio.create_task(processor.start())
        # Give it a moment to start up and enter the loop
        await asyncio.sleep(0.1)
        print("[Test] start() task created.")
        
        # Verify Binance connection started
        mock_binance_stream.connect_to_binance_stream.assert_awaited_once()
        self.assertTrue(processor.is_running)
        print("[Test] Binance stream connection verified.")

        # 5. Simulate Incoming Messages
        test_messages = ["msg1", "msg2", "msg3"]
        print(f"[Test] Simulating {len(test_messages)} incoming messages...")
        
        for msg in test_messages:
            # Simulate the callback that BinanceStream would call
            await processor._buffer_message(msg)
            
        # Allow some time for the loop to process messages
        await asyncio.sleep(0.1)
        
        # Verify messages were processed
        self.assertEqual(mock_market_data_collector._process_raw_message.await_count, 3)
        mock_market_data_collector._process_raw_message.assert_any_await("msg1")
        mock_market_data_collector._process_raw_message.assert_any_await("msg3")
        print("[Test] All messages processed by market_data_collector.")
        
        # Check status
        status = await processor.status()
        print(f"[Test] Status check: {status}")
        self.assertTrue(status['is_running'])
        self.assertEqual(status['symbol'], symbol)

        # 6. Test Stop
        print("[Test] Stopping processor...")
        await processor.stop()
        
        # Verify Stop sequence
        self.assertFalse(processor.is_running)
        mock_binance_stream.disconnect.assert_awaited_once()
        self.assertIsNone(mock_binance_stream.on_message_callback)
        print("[Test] Processor stopped, disconnected, and callback cleared.")
        
        # Wait for start task to finish (it should exit the loop)
        await start_task
        print("[Test] start() task finished.")

        print("--- StreamProcessor Flow Test Passed Successfully ---")

if __name__ == '__main__':
    unittest.main()
