import asyncio
from main import TFLMonitor
import logging

async def test_telegram_integration():
    try:
        monitor = TFLMonitor()
        await monitor.startup_check()
        return True
    except Exception as e:
        logging.error(f"Error in telegram integration test: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_telegram_integration())
