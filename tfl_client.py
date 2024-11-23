import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional
from config import (
    TFL_API_BASE_URL, MAX_RETRIES, RETRY_DELAY,
    HIGHBURY_STATION_ID
)

logger = logging.getLogger(__name__)

class TFLClient:
    def __init__(self):
        self.base_url = TFL_API_BASE_URL

    async def _make_request(self, url: str, session: aiohttp.ClientSession) -> Optional[Dict]:
        """Make HTTP request with retry logic."""
        for attempt in range(MAX_RETRIES):
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                logger.error(f"Error making request to {url}: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    return None

    async def get_line_status(self, line: str, session: aiohttp.ClientSession) -> Dict:
        """Fetch status for a specific line."""
        url = f"{self.base_url}/Line/{line}/Status"
        data = await self._make_request(url, session)
        
        if not data or not isinstance(data, list):
            return {
                "line": line,
                "status": "Unknown",
                "reason": "Failed to fetch status"
            }
        
        return self._process_line_status(data)

    async def get_line_disruptions(self, line: str, session: aiohttp.ClientSession) -> List[str]:
        """Fetch disruptions for a specific line."""
        url = f"{self.base_url}/Line/{line}/Disruption"
        data = await self._make_request(url, session)
        
        if not data or not isinstance(data, list):
            return ["No disruption information available"]
        
        return [disruption.get('description', 'Unknown disruption') for disruption in data]

    async def get_station_arrivals(self, station_id: str, session: aiohttp.ClientSession) -> List[Dict]:
        """Fetch arrivals for a specific station."""
        url = f"{self.base_url}/StopPoint/{station_id}/Arrivals"
        data = await self._make_request(url, session)
        
        if not data or not isinstance(data, list):
            return []
        
        return self._process_arrivals(data)

    async def get_northern_line_info(self, session: aiohttp.ClientSession) -> Dict:
        """Fetch comprehensive Northern line information."""
        status = await self.get_line_status("northern", session)
        disruptions = await self.get_line_disruptions("northern", session)
        arrivals = await self.get_station_arrivals(HIGHBURY_STATION_ID, session)
        
        return {
            "line": "northern",
            "status": status["status"],
            "reason": status["reason"],
            "disruptions": disruptions,
            "arrivals": arrivals[:3]  # Only show next 3 arrivals
        }

    async def get_victoria_line_info(self, session: aiohttp.ClientSession) -> Dict:
        """Fetch comprehensive Victoria line information."""
        status = await self.get_line_status("victoria", session)
        disruptions = await self.get_line_disruptions("victoria", session)
        
        return {
            "line": "victoria",
            "status": status["status"],
            "reason": status["reason"],
            "disruptions": disruptions
        }

    async def get_overground_info(self, session: aiohttp.ClientSession) -> Dict:
    """Fetch Overground information specifically for Liverpool Street to Chingford."""
    status = await self.get_line_status("london-overground", session)
    disruptions = await self.get_line_disruptions("london-overground", session)
    
    # Filter disruptions for Liverpool Street - Chingford route
    filtered_disruptions = []
    keywords = ['liverpool street', 'chingford', 'lea bridge', 'clapton', 
                'st james street', 'walthamstow central', 'wood street', 
                'highams park']
    
    for disruption in disruptions:
        # Convert to lowercase for case-insensitive comparison
        disruption_lower = disruption.lower()
        if any(keyword in disruption_lower for keyword in keywords):
            filtered_disruptions.append(disruption)
    
    return {
        "line": "london-overground",
        "status": status["status"],
        "reason": status["reason"] if any(filtered_disruptions) else "No disruption on Liverpool St - Chingford route",
        "disruptions": filtered_disruptions if filtered_disruptions else ["No disruptions on Liverpool St - Chingford route"]
    }

    async def get_all_line_statuses(self, lines: List[str]) -> List[Dict]:
        """Fetch comprehensive information for all specified lines."""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for line in lines:
                if line == "northern":
                    tasks.append(self.get_northern_line_info(session))
                elif line == "victoria":
                    tasks.append(self.get_victoria_line_info(session))
                elif line == "london-overground":
                    tasks.append(self.get_overground_info(session))
            
            return await asyncio.gather(*tasks)

    def _process_line_status(self, data: List[Dict]) -> Dict:
        """Process the raw API response into a simplified status format."""
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

    def _process_arrivals(self, data: List[Dict]) -> List[Dict]:
        """Process raw arrivals data into a simplified format."""
        arrivals = []
        for arrival in sorted(data, key=lambda x: x.get('timeToStation', 0))[:3]:
            arrivals.append({
                "destination": arrival.get("destinationName", "Unknown"),
                "time": int(arrival.get("timeToStation", 0) / 60),  # Convert to minutes
                "platform": arrival.get("platformName", "Unknown")
            })
        return arrivals
