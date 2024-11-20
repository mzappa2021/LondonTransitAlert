import pytest
from main import TFLMonitor
from tfl_client import TFLClient
from telegram_client import TelegramClient

@pytest.mark.asyncio
async def test_tfl_monitor_initialization():
    """Test TFLMonitor initialization"""
    monitor = TFLMonitor()
    assert isinstance(monitor.tfl_client, TFLClient)
    assert isinstance(monitor.telegram_client, TelegramClient)

@pytest.mark.asyncio
async def test_schedule_jobs():
    """Test job scheduling"""
    monitor = TFLMonitor()
    monitor.schedule_jobs()
    jobs = monitor.scheduler.get_jobs()
    assert len(jobs) > 0  # Verify that jobs were scheduled

@pytest.mark.asyncio
async def test_tfl_client_initialization():
    """Test TFLClient initialization"""
    client = TFLClient()
    assert client.base_url == "https://api.tfl.gov.uk"
