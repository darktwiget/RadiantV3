
import logging
from logging.handlers import RotatingFileHandler
import dotenv
import threading
import asyncio
from interfaces.api import FlaskAgent
from interfaces.telegram import TelegramAgent
from interfaces.farcaster_post import FarcasterAgent
from interfaces.twitter_post import TwitterAgent
from agents.core_agent import CoreAgent
import os
import signal
import dotenv
# Set up logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        RotatingFileHandler("radiantv3.log", maxBytes=5000000, backupCount=5),
        logging.StreamHandler()
    ],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_flask(flask_agent, stop_event):
    """Runs the Flask API agent in a separate thread."""
    try:
        port = int(os.getenv('FLASK_PORT', 5005))
        logger.info(f"Starting Flask API agent on port {port}...")
    """Runs the (blocking) Flask API agent in a separate thread."""
    try:
        logger.info("Starting Flask API agent...")
        flask_agent.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Flask API agent error: {str(e)}")

async def run_telegram(telegram_agent):
    """Runs the Telegram agent asynchronously."""
    try:
        logger.info("Starting Telegram agent asynchronously...")
    """Run the Telegram agent"""
    try:
        logger.info("Starting Telegram agent...")
        await telegram_agent.run()
    except Exception as e:
        logger.error(f"Telegram agent error: {str(e)}")

async def run_twitter(twitter_agent):
    """Runs the Twitter agent asynchronously."""
    try:
        logger.info("Starting Twitter agent asynchronously...")
    """Run the Twitter agent"""
    try:
        logger.info("Starting Twitter agent...")
        await twitter_agent.run()
    except Exception as e:
        logger.error(f"Twitter agent error: {str(e)}")

def reload_environment():
    """Reload environment variables without clearing the existing ones."""
    """Reload environment variables"""
    dotenv.load_dotenv(override=True)
    dotenv.load_dotenv(override=True)
    logger.info("Environment variables reloaded")

async def main():
    """Main entry point with async event loop and graceful shutdown support."""
    """Main entry point"""
    try:
        # Initial load of environment variables
        reload_environment()
        
        # Create shared core agent and interfaces
        core_agent = CoreAgent()
        flask_agent = FlaskAgent(core_agent)
        telegram_agent = TelegramAgent(core_agent)
        twitter_agent = TwitterAgent(core_agent)
        farcaster_agent = FarcasterAgent(core_agent)

        # Start Flask in a separate thread with stop signal handling
        stop_event = threading.Event()
        flask_thread = threading.Thread(
            target=run_flask,
            args=(flask_agent, stop_event),
            target=run_flask,
            args=(flask_agent,),
            daemon=True
        )
        flask_thread.start()

        # Start async tasks
        loop = asyncio.get_event_loop()
        twitter_task = loop.create_task(run_twitter(twitter_agent))
        telegram_task = loop.create_task(run_telegram(telegram_agent))

        twitter_thread.start()

        # Run asyncio event loop
        loop.run_until_complete(asyncio.gather(twitter_task, telegram_task))

        # Wait for other threads
        flask_thread.join()
        twitter_thread.join()

    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        stop_event.set()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s, f: logger.info("Signal SIGINT received. Shutting down."))
    signal.signal(signal.SIGTERM, lambda s, f: logger.info("Signal SIGTERM received. Shutting down."))
    asyncio.run(main())
