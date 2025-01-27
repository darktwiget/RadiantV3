import logging
import httpx
from httpx import AsyncClient
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from typing import Any

from interfaces.telegram import TelegramAgent  # Update handler logic in this module if necessary
# Removed AsyncHTTPBot usage, replaced with Application
from agents.core_agent import CoreAgent
import dotenv
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Removed the run_telegram method since we're replacing it with Application.run_polling()

class HTTPXRequest:
    def __init__(self):
        self.client = AsyncClient()
    async def do_request(self, method: str, url: str, **kwargs: Any):
        logger.info(f"Performing {method} request to {url} with params: {kwargs}")
        return await self.client.request(method, url, **kwargs)
    async def initialize(self):
        logger.info("Initializing HTTPXRequest...")
    async def shutdown(self):
        logger.info("Shutting down HTTPXRequest...")
        await self.client.aclose()
import asyncio
class MyHTTPXRequest(HTTPXRequest):
    def __init__(self):
        super().__init__()
        self.client = AsyncClient()
    async def do_request(self, method: str, url: str, **kwargs: Any):
        return await self.client.request(method, url, **kwargs)
    async def initialize(self):
        logger.info("MyHTTPXRequest initialization logic (if any).")
    async def shutdown(self):
        logger.info("Shutting down MyHTTPXRequest...")
        await self.client.aclose()

async def main():
    """
    Main entry point for the Heuman Agent Framework.
    Demonstrates both shared and standalone usage.
    """
    logger.info("Loading environment variables...")
    dotenv.load_dotenv()

    core_agent = CoreAgent()
    httpx_request = MyHTTPXRequest()
    application = Application.builder().token("TELEGRAM_BOT_TOKEN").build()

    async def start(update, context):
        await update.message.reply_text("Hello! I'm your bot.")


    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, core_agent.handle_message))

    try:
        await httpx_request.initialize()
        logger.info("HTTPXRequest initialized successfully.")
        logger.info("Starting Telegram bot application...")
        await application.run_polling()
    except KeyboardInterrupt:
        logger.warning("Application interrupted by the user.")
    except Exception as e:
        logger.critical("Fatal error occurred", exc_info=True)
        raise
    finally:
        logger.info("Cleaning up resources...")
        await httpx_request.shutdown()
        logger.info("Cleanup complete.")

if __name__ == "__main__":
    asyncio.run(main())
