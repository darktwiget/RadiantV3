
from typing import Dict, Any, Optional, Union

import aiohttp
import logging
import secrets
import os
from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

class APIError(Exception):
    """
    Raised when the API returns an error response.
    Includes an optional status_code for detailed error handling.
    """
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code

class PromptEnhancementError(Exception):
    """
    Raised when there's an error enhancing a prompt.
    Typically used to identify issues during request parameter preparation.
    """
    pass

class SmartGen:
    """
    SmartGen provides interaction with a smart image generation API.
    Includes methods for request preparation, session management, and error handling.
    """
    def __init__(self, api_key: str, base_url: str = os.getenv("HEURIST_SEQUENCER_URL")):
        """
        :param api_key: API key for authentication
        :param base_url: Base URL for the API (default from environment variable)
        """
        self.api_key = api_key
        self.base_url = base_url
        self._session: Optional[aiohttp.ClientSession] = None
        logger.info("SmartGen initialized with base_url=%s", self.base_url)

    async def __aenter__(self):
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_session()

    async def _create_session(self):
        """Create aiohttp session if it doesn't exist."""
        if self._session is None:
            logger.debug("Creating aiohttp session...")
            self._session = aiohttp.ClientSession(headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
            logger.debug("Aiohttp session created successfully")

    async def _close_session(self):
        """Close the aiohttp session."""
        if self._session:
            logger.debug("Closing aiohttp session...")
            await self._session.close()
            self._session = None
            logger.debug("Aiohttp session closed")

    async def _ensure_session(self):
        """Ensure session exists before making requests."""
        if self._session is None:
            logger.debug("No active session found. Creating a new session...")
            await self._create_session()

    async def generate_image(
        self,
        description: str,
        image_model: str = "Aurora",
        width: int = 1024,
        height: int = 768,
        stylization_level: Optional[int] = None,
        detail_level: Optional[int] = None,
        color_level: Optional[int] = None,
        lighting_level: Optional[int] = None,
        must_include: Optional[str] = None,
        quality: str = "normal",
        param_only: bool = False
    ) -> Dict[str, Any]:
        try:
            logger.info("Preparing to generate image...")
            await self._ensure_session()
            
            # Generate a random job ID using secrets module
            job_id = f"sdk-image-{secrets.token_hex(5)}"
            logger.debug("Generated job_id: %s", job_id)

            # Prepare model input parameters
            model_input = {
                "prompt": description.strip(),
                "width": width,
                "height": height,
            }
            logger.debug("Initial model input: %s", model_input)

            if stylization_level is not None:
                model_input["stylization_level"] = stylization_level
            if detail_level is not None:
                model_input["detail_level"] = detail_level
            if color_level is not None:
                model_input["color_level"] = color_level
            if lighting_level is not None:
                model_input["lighting_level"] = lighting_level
            if must_include:
                model_input["must_include"] = must_include

            # Prepare the full request parameters
            params = {
                "job_id": job_id,
                "model_input": {
                    "SD": model_input
                },
                "model_type": "SD",
                "model_id": image_model,
                "deadline": 50,
                "priority": 1
            }
            logger.debug("Prepared parameters for job submission: %s", params)

            if param_only:
                logger.info("Returning parameters without execution (param_only=True)")
                return {"parameters": params}

            # Generate the image
            async with self._session.post(
                f"{self.base_url}/submit_job",
                json=params
            ) as response:
                logger.debug("Received response with status: %s", response.status)
                if response.status != 200:
                    error_text = await response.text()
                    logger.error("API returned an error: %s", error_text)
                    raise APIError(f"Generate image error: {response.status} {error_text}")
                
                url = await response.text()
                # Remove quotes from the URL if present
                url = url.strip('"')
                logger.info("Generated image URL: %s", url)

                return {
                    "url": url,
                    "parameters": model_input
                }

        except Exception as e:
            logger.exception("Exception occurred during image generation")
            if isinstance(e, (PromptEnhancementError, APIError)):
                raise e
            raise APIError(f"Failed to generate image: {str(e)}")
