

import asyncio
import logging
from traceback import format_exc
from dotenv import load_dotenv
from interfaces.twitter_reply import TwitterReplyAgent

async def main():
    """
    Main function to run the Twitter Reply Agent.

    This function initializes the Twitter agent, starts monitoring,
    and runs workers to process tasks. Includes proper error
    handling and logging.
    """

    try:
        load_dotenv()
        logging.info("Environment variables loaded successfully")
    except Exception as dotenv_error:
        logging.error(f"Error loading environment variables: {dotenv_error}")
        return
    
    # Initialize agent
    agent = TwitterReplyAgent()
    
    try:
        logging.info("Initializing the Twitter Reply Agent...")

        logging.info("Starting monitoring in a background thread")
        monitor_thread = agent.start_monitoring()
        logging.info("Background monitoring initialized successfully")
        
        logging.info("Starting workers. Use Ctrl+C to terminate the process.")
        await agent.run_workers(num_workers=2)
            
    except KeyboardInterrupt:
        logging.info("Shutting down gracefully...")
    except Exception as error:
        logging.error("An unexpected exception occurred:")
        logging.error(format_exc())

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    asyncio.run(main())
