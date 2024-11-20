import pytest
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock
from main import TFLMonitor
from tfl_client import TFLClient
from telegram_client import TelegramClient
from config import MONITORED_LINES

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
    assert len(jobs) == 2  # Verify both 15:45 and 16:00 jobs are scheduled

@pytest.mark.asyncio
async def test_tfl_client_initialization():
    """Test TFLClient initialization"""
    client = TFLClient()
    assert client.base_url == "https://api.tfl.gov.uk"

@pytest.mark.asyncio
async def test_telegram_message_formatting():
    """Test Telegram message formatting"""
    client = TelegramClient()
    test_statuses = [
        {
            "line": "northern",
            "status": "Good Service",
            "reason": "No disruption",
            "disruptions": []
        }
    ]
    message = client._format_status_message(test_statuses)
    assert "🚇 <b>TFL Line Status Update</b>" in message
    assert "<b>Northern</b>" in message
    assert "✅" in message

@pytest.mark.asyncio
async def test_telegram_send_status_update():
    """Test sending status updates via Telegram"""
    with patch('telegram.Bot.send_message', new_callable=AsyncMock) as mock_send:
        client = TelegramClient()
        test_statuses = [
            {
                "line": "victoria",
                "status": "Minor Delays",
                "reason": "Signal failure",
                "disruptions": ["Delays of 10 minutes"]
            }
        ]
        await client.send_status_update(test_statuses)
        assert mock_send.called
        args, kwargs = mock_send.call_args
        assert kwargs['parse_mode'] == 'HTML'
@pytest.mark.asyncio
async def test_tfl_make_request():
    """Test TFLClient _make_request method"""
    client = TFLClient()
    
    # Create mock response with test data
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_data = {'test': 'data'}
    mock_response.json = AsyncMock(return_value=mock_data)
    mock_response.raise_for_status = AsyncMock()
    
    # Create mock session with proper async context manager
    mock_session = AsyncMock()
    mock_session.get.return_value = AsyncMock()
    mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
    mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)
    
    result = await client._make_request("test_url", mock_session)
    assert result == mock_data
    
    # Verify the request was made correctly
    mock_session.get.assert_called_once_with("test_url")

@pytest.mark.asyncio
async def test_tfl_get_line_status():
    """Test TFLClient get_line_status method"""
    client = TFLClient()
    mock_data = [{
        'id': 'northern',
        'lineStatuses': [{
            'statusSeverityDescription': 'Good Service',
            'reason': None
        }]
    }]
    
    async def mock_request(*args, **kwargs):
        return mock_data
        
    with patch.object(TFLClient, '_make_request', new=mock_request):
        async with aiohttp.ClientSession() as session:
            result = await client.get_line_status('northern', session)
            assert result['line'] == 'northern'
            assert result['status'] == 'Good Service'

@pytest.mark.asyncio
async def test_tfl_get_all_line_statuses():
    """Test TFLClient get_all_line_statuses method"""
    client = TFLClient()
    mock_data = {
        'line': 'test_line',
        'status': 'Good Service',
        'reason': 'No disruption',
        'disruptions': []
    }
    
    async def mock_info(*args, **kwargs):
        return mock_data
        
    with patch.object(TFLClient, 'get_northern_line_info', new=mock_info), \
         patch.object(TFLClient, 'get_victoria_line_info', new=mock_info), \
         patch.object(TFLClient, 'get_overground_info', new=mock_info):
        result = await client.get_all_line_statuses(MONITORED_LINES)
        assert len(result) == len(MONITORED_LINES)
        assert all(status['status'] == 'Good Service' for status in result)

@pytest.mark.asyncio
async def test_check_and_notify():
    """Test TFLMonitor check_and_notify method"""
    monitor = TFLMonitor()
    mock_statuses = [{
        'line': 'northern',
        'status': 'Good Service',
        'reason': 'No disruption',
        'disruptions': []
    }]
    
    async def mock_get_statuses(*args, **kwargs):
        return mock_statuses

    async def mock_send_update(statuses):
        pass

    with patch.object(TFLClient, 'get_all_line_statuses', new=mock_get_statuses), \
         patch.object(TelegramClient, 'send_status_update', new=mock_send_update):
        await monitor.check_and_notify()
