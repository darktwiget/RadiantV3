from typing import List, Dict, Any, Optional, Callable
import logging
from agents.tool_decorator import get_tool_schemas, tool
import aiohttp
logger = logging.getLogger(__name__)
## YOUR TOOLS GO HERE
import os
from aiohttp import ClientSession
import asyncio

class AsyncHTTPHandler:
    """Placeholder base class for handling asynchronous HTTP tasks."""
    pass

class ToolBox:
    """Base class containing tool configurations and handlers"""

class ToolBox(AsyncHTTPHandler):
    """Base class containing tool configurations and handlers"""

    def __init__(self):
        # Base tools configuration
        # Can be used to add tools by defining a function schema explicitly if needed
        self.tools_config = [
            # {
            #     "type": "function",
            #     "function": {
            #         "name": "generate_image",
            #         "description": "Generate an image based on a text prompt, any request to create an image should be handled by this tool, only use this tool if the user asks to create an image",
            #         "parameters": {
            #             "type": "object",
            #             "properties": {
            #                 "prompt": {"type": "string", "description": "The prompt to generate the image from"}
            #             },
            #             "required": ["prompt"]
            #         }
            #     }
            # },
        ]

        # Base handlers
        # Can be used to add handlers for schemas that were defined explicitly
        self.tool_handlers = {
            #"generate_image": self.handle_image_generation
        }

        self.decorated_tools = [self.get_crypto_price, self.handle_image_generation, self.get_dexscreener_price, self.monitor_token_purchases]

    @staticmethod
    @tool("Generate an image based on a text prompt")
    #async def handle_image_generation(self, args: Dict[str, Any], agent_context: Any) -> Dict[str, Any]: #example for explicitly defined schema
    async def handle_image_generation(prompt: str, agent_context: Any) -> Dict[str, Any]:
        """Generate an image based on a text prompt. Use this tool only when the user explicitly requests to create an image."""
        logger.info(prompt)
        try:
            image_url = await agent_context.handle_image_generation(prompt) #args['prompt'] for explicitly defined schema
            return {"image_url": image_url}
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    @tool("Get the price of a token using Dexscreener API")
    async def get_dexscreener_price(pair_address: str) -> Dict[str, Any]:
        """
        Fetch the price of a token in USD using the Dexscreener API.

        Args:
            pair_address: The token pair address.

        Returns:
            dict: Current price in USD or an error message.
        """
        url = f"https://api.dexscreener.com/latest/dex/pairs/{pair_address}"
        try:
            async with ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = data["pair"]["priceUsd"]
                        logger.info(f"Current price for {pair_address}: ${price}")
                        return {"price": price}
                    else:
                        error_msg = "Failed to fetch price from Dexscreener API"
                        logger.error(error_msg)
                        return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error fetching price: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    @tool("Get the current price of a cryptocurrency in USD")
    async def get_crypto_price(ticker: str) -> float:
        """
        Get the current price of a cryptocurrency in USD from Binance.

        Args:
            ticker: The cryptocurrency ticker symbol (e.g., BTC, ETH, SOL)

        Returns:
            float: Current price in USD
        """
        try:
            normalized_ticker = f"{ticker.upper()}USDT"
            async with aiohttp.ClientSession() as session:
                url = f"https://api.binance.com/api/v3/ticker/price?symbol={normalized_ticker}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        price = float(data['price'])
                        logger.info(f"The current price for {normalized_ticker}: ${price:.2f}")
                        return {"message": f"The current price for {normalized_ticker}: ${price:.2f}"}
                    else:
                        error_msg = f"Failed to get price for {normalized_ticker}"
                        logger.error(error_msg)
                        return {"message": error_msg}

        except Exception as e:
            error_msg = f"Error getting crypto price: {str(e)}"
    @staticmethod
    @tool("Monitor token purchases and send Telegram notifications")
    async def monitor_token_purchases(pair_address: str, telegram_chat_id: str, telegram_bot_token: str) -> Dict[str, Any]:
        """
        Monitor token transactions from Dexscreener API and send purchase details via Telegram.

        Args:
            pair_address: The token pair address.
            telegram_chat_id: Telegram chat ID to send notifications.
            telegram_bot_token: Telegram bot token for sending messages.

        Returns:
            dict: Success or an error message.
        """
        url = f"https://api.dexscreener.com/latest/dex/pairs/{pair_address}"
        last_transaction_id = None  # Track the last seen transaction

        while True:
            try:
                async with ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            transactions = data["pair"]["transactions"]["buys"]

                            for tx in transactions[::-1]:  # Process older transactions first.
                                transaction_id = tx["transactionHash"]
                                if transaction_id == last_transaction_id:
                                    break
                                last_transaction_id = transaction_id

                                amount_usd = tx["amountUsd"]
                                message = f"💰 Token Purchase Detected:\n\n- Amount: ${amount_usd}\n- Pair: {pair_address}"

                                # Send notification to Telegram.
                                telegram_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
                                payload = {
                                    "chat_id": telegram_chat_id,
                                    "text": message
                                }
                                await session.post(telegram_url, json=payload)
                                logger.info("Telegram notification sent")

                await asyncio.sleep(30)  # Wait before next poll

            except Exception as e:
                error_msg = f"Error monitoring token purchases: {str(e)}"
                logger.error(error_msg)
                return {"error": error_msg}

            return {"error": error_msg}