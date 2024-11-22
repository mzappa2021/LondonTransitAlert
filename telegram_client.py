import logging
from telegram import Bot
from telegram.error import TelegramError
from telegram.constants import ParseMode
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, MAX_RETRIES, RETRY_DELAY
import asyncio
from typing import Dict, List

logger = logging.getLogger(__name__)

class TelegramClient:
    def __init__(self):
        self.token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.bot = Bot(token=self.token)

    async def initialize(self):
        """Initialize the bot instance"""
        try:
            # Test the bot token by getting bot information
            await self.bot.get_me()
            logger.info("Successfully initialized Telegram bot")
        except TelegramError as e:
            logger.error(f"Failed to initialize Telegram bot: {str(e)}")
            raise

    async def send_status_update(self, statuses: List[Dict]):
        """Send formatted status update to Telegram channel."""
        try:
            await self.initialize()
            message = self._format_status_message(statuses)
            
            for attempt in range(MAX_RETRIES):
                try:
                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=message,
                        parse_mode=ParseMode.HTML
                    )
                    logger.info("Status update sent successfully to Telegram")
                    break
                except TelegramError as e:
                    logger.error(f"Failed to send Telegram message: {str(e)}")
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(RETRY_DELAY)
                    else:
                        logger.error("Max retries reached for sending Telegram message")
                        raise
        except Exception as e:
            logger.error(f"Error in send_status_update: {str(e)}")
            raise

    def _format_status_message(self, statuses: List[Dict]) -> str:
        """Format the status update as a readable message with detailed information."""
        message_parts = ["🚇 <b>TFL Line Status Update Mr Lorenzo</b>\n"]
        
        for status in sorted(statuses, key=lambda x: x['line']):
            emoji = self._get_status_emoji(status['status'])
            line_name = status['line'].replace('-', ' ').title()
            
            message_parts.append(f"{emoji} <b>{line_name}</b>")
            message_parts.append(f"Status: {status['status']}")
            
            if status['reason'] and status['reason'] != "No disruption":
                message_parts.append(f"Reason: {status['reason']}")
            
            # Add disruptions if available
            if 'disruptions' in status and status['disruptions']:
                message_parts.append("\nDisruptions:")
                for disruption in status['disruptions']:
                    message_parts.append(f"• {disruption}")
            
            # Add arrivals if available
            if 'arrivals' in status and status['arrivals']:
                message_parts.append("\nNext Arrivals:")
                for arrival in status['arrivals']:
                    time_str = f"{arrival['time']} min" if arrival['time'] > 0 else "Due"
                    message_parts.append(
                        f"• {arrival['destination']} - {time_str} "
                        f"(Platform {arrival['platform']})"
                    )
            
            message_parts.append("")  # Add blank line between sections
        
        return "\n".join(message_parts)

    def _get_status_emoji(self, status: str) -> str:
        """Return appropriate emoji for the status."""
        status_emojis = {
            "Good Service": "✅",
            "Minor Delays": "⚠️",
            "Severe Delays": "🔴",
            "Part Suspended": "⛔️",
            "Suspended": "🚫",
            "Part Closure": "⚠️",
            "Planned Closure": "🔧",
            "Unknown": "❓"
        }
        return status_emojis.get(status, "❓")
