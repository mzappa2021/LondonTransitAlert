import aiohttp
import asyncio
import logging
from typing import Dict, List
from config import TFL_API_BASE_URL, TFL_APP_KEY, MAX_RETRIES, RETRY_DELAY

logger = logging.getLogger(__name__)

class TFLClient:
    def __init__(self):
        self.base_url = TFL_API_BASE_URL
        self.app_key = TFL_APP_KEY

    async def get_line_status(self, line: str, session: aiohttp.ClientSession) -> Dict:
        """Fetch status for a specific line with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                url = f"{self.base_url}/Line/{line}/Status"
                params = {"app_key": self.app_key}
                
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return self._process_line_status(data)
                    
            except Exception as e:
                logger.error(f"Error fetching status for {line}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    return {
                        "line": line,
                        "status": "Unknown",
                        "reason": f"Failed to fetch after {MAX_RETRIES} attempts"
                    }

    async def get_all_line_statuses(self, lines: List[str]) -> List[Dict]:
        """Fetch status for all specified lines concurrently."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_line_status(line, session) for line in lines]
            return await asyncio.gather(*tasks)

    def _process_line_status(self, data: List[Dict]) -> Dict:
        """Process the raw API response into a simplified status format."""
        if not data or not isinstance(data, list):
            return {"status": "Unknown", "reason": "Invalid data received"}

        line_data = data[0]
        line_statuses = line_data.get("lineStatuses", [])
        
        if not line_statuses:
            return {
                "line": line_data.get("id", "Unknown"),
                "status": "Unknown",
                "reason": "No status data available"
            }

        status = line_statuses[0]
        return {
            "line": line_data.get("id", "Unknown"),
            "status": status.get("statusSeverityDescription", "Unknown"),
            "reason": status.get("reason", "No disruption")
        }
