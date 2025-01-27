import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import dotenv
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, filters, Application
from telegram import Update
from agents.core_agent import CoreAgent
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.account import get_balance
from xrpl.models.transactions import Payment
from xrpl.transaction import safe_sign_and_autofill_transaction, send_reliable_submission
from xrpl.models.requests import AccountTx

JSON_RPC_URL = os.getenv("XRPL_RPC_URL", "https://s.altnet.rippletest.net:51234")
xrpl_client = JsonRpcClient(JSON_RPC_URL)

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Change to DEBUG for thorough logging
logger = logging.getLogger(__name__)
# Removed line to prevent clearing all environment variables
dotenv.load_dotenv()

# Constants
TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

if not TELEGRAM_API_TOKEN:
    logger.critical("TELEGRAM_API_TOKEN missing in environment variables.")
    raise ValueError("TELEGRAM_API_TOKEN not found in environment variables")
# Define bot command handlers

def start(update: Update, context: CallbackContext):
    """Handle the start message."""
    update.message.reply_text("Welcome to the XRPL bot! Use /help for commands.")


def help_command(update: Update, context: CallbackContext):
    """List available commands."""
    commands = (
        "/start - Start the bot\n"
/help - View commands\n "
/balance <address> - Check XRP balance for a given address\n
        "/balance <address> - Get balance for an XRPL address\n"
        "/pay <seed> <destination> <amount> - Send XRP payment\n"
        "/history <address> - Get transaction history\n"
    )
    update.message.reply_text(f"Available commands:\n{commands}")


def balance_command(update: Update, context: CallbackContext):
    """Fetch the balance of an account."""
try:
    if not context.args:
        update.message.reply_text("Please provide an address. Usage: /balance <address>")
        return
    address = context.args[0]
    balance = get_account_balance(address)
    update.message.reply_text(f"The balance for {address} is {balance} XRP.")
    except Exception as e:
        logger.error(f"Failed to fetch balance for address {address}: {e}")
        update.message.reply_text("Failed to fetch the balance. Please try again.")


def payment_command(update: Update, context: CallbackContext):
    """Send a payment via XRPL."""
    if len(context.args) < 3:
        update.message.reply_text("Usage: /pay <seed> <destination> <amount>")
        return
    try:
        seed = context.args[0]
        destination = context.args[1]
        amount = float(context.args[2])
        result = send_payment(seed, destination, amount)
        update.message.reply_text(f"Payment successful! Transaction: {result['hash']}")
    except ValueError as ve:
        logger.error(f"Invalid input: {ve}")
        update.message.reply_text(f"Error: {ve}")
    except Exception as e:
        logger.error(f"Payment failed for destination {destination} with amount {amount}: {e}")
        update.message.reply_text("Payment failed. Ensure valid details and try again.")


def history_command(update: Update, context: CallbackContext):
    """Fetch transaction history for an account."""
try:
    if not context.args:
        update.message.reply_text("Please provide an address. Usage: /history <address>")
        return
    address = context.args[0]
        history = get_transaction_history(address)
        update.message.reply_text(f"Transaction history: {history}")
    except Exception as e:
logger.error(f"Failed to fetch transaction history for address {address} due to error: {e}")
        update.message.reply_text("Failed to fetch transaction history. Please try again.")

class TelegramAgent(CoreAgent):
    def __init__(self, core_agent=None):
        if isinstance(core_agent, CoreAgent):
            super().__setattr__('_parent',core_agent)
        else:
            # Need to set _parent = self first before super().__init__()
            super().__setattr__('_parent', self)  # Bypass normal __setattr__
            super().__init__()
            
        # Initialize telegram specific stuff
        self.app = Application.builder().token(TELEGRAM_API_TOKEN).build()
self._setup_handlers()  # Initialize handlers for all Telegram commands and messages
if not hasattr(self, "app"):
    logger.critical("Telegram Application is not initialized.")
    raise ValueError("Telegram Application configuration is missing.")
        if hasattr(self, 'register_interface'):
            self.register_interface('telegram', self)
            # Removed duplicate registration of telegram interface
        AsyncHTTPHandler.__init__(self)  # Initialize HTTP handler
    def __getattr__(self, name):
        # Delegate to the parent instance for missing attributes/methods
        return getattr(self._parent, name)
        
    def __setattr__(self, name, value):
        if not hasattr(self, '_parent'):
            # During initialization, before _parent is set
            super().__setattr__(name, value)
        elif name == "_parent" or self is self._parent or name in self.__dict__:
            # Set local attributes (like _parent or already existing attributes)
            super().__setattr__(name, value)
        else:
            # Delegate attribute setting to the parent instance
            super().__getattribute__('_parent').__setattr__(name, value)
def _setup_handlers(self):  # Set up Telegram command and message handlers
        # Register the /start command handler
        self.app.add_handler(CommandHandler("start", self.start))
        # Ensure asynchronous registration of command handlers
        self.app.add_handler(CommandHandler("image", self.image))
        # Register a handler for voice messages
        self.app.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        # Register a handler for echoing messages
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message))
        # Register a handler for getting the chat id
        self.app.add_handler(CommandHandler("get_id", self.get_id))

    async def start(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text("Hello World! I'm not a bot... I promise... ")
        
    async def get_id(self, update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        await update.message.reply_text(f"Your Chat ID is: {chat_id}")

async def image(self, update: Update, context: CallbackContext) -> None:
    # Ensure the /image command includes text
    if not context.args:
        await update.message.reply_text("Usage: /image <prompt>")
        return
    prompt = ' '.join(context.args)
        
        if not prompt:
            await update.message.reply_text("Please provide a prompt after /image command")
            return

        # Generate image using the prompt
        try:
            result = await self.handle_image_generation(prompt=prompt)
            if result:
                # Send the generated image as a photo using the URL
                await update.message.reply_photo(photo=result)
                await update.message.reply_text("Here is your generated image!")
            else:
                await update.message.reply_text("Failed to generate image")
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            await update.message.reply_text("Sorry, there was an error generating the image")

    async def message(self, update: Update, context: CallbackContext):
        """Handle incoming messages."""
        text_response, image_url, _ = await self.handle_message(
            update.message.text,
            source_interface='telegram'
        )
        logger.info(f"Telegram message: {update.message.text}")
        if self._parent != self:
            logger.info("Operating in shared mode with core agent")
        else:
            logger.info("Operating in standalone mode")
            
        if image_url:
            await update.message.reply_photo(photo=image_url)
        if text_response:
            await update.message.reply_text(text_response)

    async def send_message(self, chat_id: int, message: str, image_url: str = None) -> None:
        """
        Send a message to a specific chat ID after validating the bot's membership.
        
        Args:
            chat_id (int): The Telegram chat ID to send the message to
            message (str): The message text to send
            
        Raises:
            TelegramError: If bot is not a member of the chat or other Telegram API errors
        """
        try:
            logger.info(f"Send message to telegram")
            logger.info(f"Sending message to chat {chat_id}")
            logger.info(f"Message: {message}")
            # Ensure bot membership in the target chat
            bot_member = await context.bot.get_chat_member(
                chat_id=chat_id, 
                user_id=await context.bot.id
            )
            
            # Check if bot is a member/admin in the chat
            if bot_member.status not in ['member', 'administrator']:
                logger.error(f"Bot is not a member of chat {chat_id}")
                return
            
            if image_url:
                await self.app.bot.send_photo(chat_id=chat_id, photo=image_url, caption="")
            else:
                message = message.replace('"', '')
                await self.app.bot.send_message(chat_id=chat_id, text=message)
            
        except Exception as e:
            logger.error(f"Failed to send message to chat {chat_id}: {str(e)}")
            raise

    async def handle_voice(self, update: Update, context: CallbackContext) -> None:
        if update.message.voice:
            # Get the file ID of the voice note
            file_id = update.message.voice.file_id

            # Get the file from Telegram's servers
            file = await context.bot.get_file(file_id)

            project_root = Path(__file__).parent.parent
            audio_dir = project_root / "audio"
            audio_dir.mkdir(exist_ok=True)
            
            # Define the file path where the audio will be saved
            file_path = audio_dir / f"{file_id}.ogg"

            # Download the file
            await file.download_to_drive(file_path)

            # Notify the user
            await update.message.reply_text("Voice note received. Processing...")
            user_message = await self.transcribe_audio(file_path)
            text_response, image_url,_ = await self.handle_message(user_message)
        
            if image_url:
                await update.message.reply_photo(photo=image_url)
            if text_response:
                await update.message.reply_text(text_response.replace('"', ''))
    def run(self):
        """Start the bot"""
        logger.info("Starting Telegram bot...")
        self.app.run_polling()

class CoreAgent():
    def handle_image_generation(self, prompt: str) -> str:
logger.debug(f"Prompt received for image generation: {prompt}")
return "https://example.com/sample-image.png"

    def handle_message(self, text: str, source_interface: Optional[str] = None):
        return "Processed message response", None, None

def main():
    agent = TelegramAgent()
    agent.run()

from httpx import AsyncClient

class AsyncHTTPHandler:
    def __init__(self):
        self.client = None
        self.initialized = False

    async def initialize(self):
        if not self.initialized:
            self.client = AsyncClient()
            self.initialized = True
            logger.info("HTTP client initialized.")

    async def shutdown(self):
        if self.client:
            await self.client.aclose()
            self.client = None
            self.initialized = False
            logger.info("HTTP client shutdown.")

    async def do_request(self, method: str, url: str, **kwargs) -> Any:
        if not self.initialized:
            raise RuntimeError("HTTP client is not initialized.")

        try:
            if not self.client:
                self.client = AsyncClient()
            logger.info(f"Executing {method} request to {url}.")
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            logger.debug(f"Response from {url}: {response.text}")
            return response
        except Exception as e:
            logger.error(f"HTTP request failed for {url}: {str(e)}")
            raise

async def create_wallet() -> Wallet:
    return Wallet.create()
    pass

def get_account_balance(address: str) -> float:
    try:
response = get_balance(address, xrpl_client)
logger.debug(f"Balance response for {address}: {response}")
return response / 1_000_000
    except Exception as e:
        logger.error(f"Error fetching balance: {str(e)}")
        raise

def send_payment(seed: str, destination: str, amount: float) -> str:
    try:
        wallet = Wallet(seed, 0)
        if not wallet.classic_address:
            raise ValueError("Invalid wallet seed")

        payment = Payment(
            account=wallet.classic_address,
            destination=destination,
            amount=str(int(amount * 1_000_000)),  # Ensure amount is string for XRPL API
        )
        signed_tx = safe_sign_and_autofill_transaction(payment, wallet, xrpl_client)
        response = send_reliable_submission(signed_tx, xrpl_client)

        if response.result["engine_result"] == "tesSUCCESS":
            return response.result["tx_json"]["hash"]
        else:
            raise ValueError(f"Transaction failed: {response.result['engine_result_message']}")
    except Exception as e:
        logger.error(f"Error sending payment: {e}")
        raise

def get_transaction_history(address: str) -> List[Dict[str, Any]]:
    try:
        response = xrpl_client.request(AccountTx(account=address))
logger.debug(f"Transaction history response: {response}")
if response.is_successful():
            return response.result["transactions"]
        else:
            raise ValueError(f"Error fetching history: {response.result}")
    except Exception as e:
        logger.error(f"Error fetching transaction history: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(http_handler.initialize())
    logging.basicConfig(level=logging.DEBUG)
    try:
        logger.info("Initializing HTTP resources...")
        asyncio.run(AsyncHTTPHandler().initialize())
        logger.info("Starting Telegram agent...")
        main()
    except KeyboardInterrupt:
        logger.info("Telegram agent execution interrupted by user.")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
    finally:
        logger.info("Shutting down HTTP handler...")
        asyncio.run(http_handler.shutdown())
