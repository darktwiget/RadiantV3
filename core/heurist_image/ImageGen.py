from typing import Dict, Any, Optional
import aiohttp
import secrets
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()  # Load environment variables from .env file

class APIError(Exception):
    """
    Custom exception to handle API errors.
    Raised when the API returns an error response.
    """
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code

class ImageGen:
    """
    A class to generate images by interacting with an API.
    Provides methods to manage a client session and make API requests.
    """

class ImageGen:
    """
    A class to generate images by interacting with an API.
    Provides methods to manage a client session and make API requests.
    Refactored with logging and improved exception handling.
    """
        """
        Initialize the ImageGen class with API key and base URL.
        Falls back to environment variable if base URL is not provided.
        """
        base_url = base_url or os.getenv("HEURIST_SEQUENCER_URL")

    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        logging.info("ImageGen class initialized.")
        self.base_url = base_url or os.getenv("HEURIST_SEQUENCER_URL")
        self.base_url = base_url
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_session()

    async def _create_session(self):
        logging.info("Creating a new aiohttp session.")
        """
        Create a new aiohttp session if it doesn't already exist.
        Sets default headers for API requests.
        """
        if self._session is None:
            self._session = aiohttp.ClientSession(headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
                logging.info("aiohttp session created successfully.")
        """
        Close and clean up an existing aiohttp session.
        Ensures proper resource management.
        """
        """Close the aiohttp session."""
            logging.info("Closing aiohttp session.")
            await self._session.close()
            logging.info("aiohttp session closed successfully.")
            await self._session.close()
            self._session = None

        """
        Ensure that an aiohttp session is available.
        Creates one if it doesn't exist.
        logging.debug("Ensuring aiohttp session exists before making requests.")
        """
        """Ensure session exists before making requests."""
        if self._session is None:
            await self._create_session()

        """
        Send an image generation request to the API.
        
        Args:
            params (Dict[str, Any]): Parameters for the image generation request.
        
        Returns:
            Dict[str, Any]: API response, including image URL and other information.
        
        Raises:
            APIError: When there is an issue with the API response or request.
        """
        try:
            logging.info("Starting image generation request.")
            await self._ensure_session()

            job_id = f"sdk-image-{secrets.token_hex(5)}"
            logging.debug(f"Generated job ID: {job_id}")

            # Extract and set generation query parameters
            prompt = params.get('prompt', '')
            neg_prompt = params.get('neg_prompt')
            num_iterations = params.get('num_iterations')
            guidance_scale = params.get('guidance_scale')
            width = params.get('width')
            height = params.get('height')
            seed = params.get('seed')
            model = params.get('model')
            job_id_prefix = params.get('job_id_prefix', 'sdk-image')

            # Handle special model cases
            # Handle specific cases for 'Zeek' and 'Philand' models
            logging.debug(f"Handling special cases for model: {model}")
            elif model == 'Philand':
                prompt = prompt.replace('Philand', 'ph1land').replace('philand', 'ph1land')

            # Prepare model input
            model_input = {
                "prompt": prompt
            }
            if neg_prompt:
                model_input["neg_prompt"] = neg_prompt
            if num_iterations:
                logging.debug(f"Setting num_iterations: {num_iterations}")
                model_input["num_iterations"] = num_iterations
            if guidance_scale:
                logging.debug(f"Setting guidance_scale: {guidance_scale}")
                model_input["guidance_scale"] = guidance_scale
            if width:
                logging.debug(f"Setting width: {width}")
                model_input["width"] = width

                logging.debug(f"Setting height: {height}")
                model_input["height"] = height
                model_input["height"] = height
            if seed:
                # Process seed values to ensure compatibility
                seed_int = int(seed)
                if seed_int > 9007199254740991:  # Number.MAX_SAFE_INTEGER
                    seed_int = seed_int % 9007199254740991
                logging.debug(f"Setting seed: {seed_int}")
                model_input["seed"] = seed_int

            # Prepare the full request parameters
            request_params = {
                "job_id": f"{job_id_prefix}-{secrets.token_hex(5)}",
                "model_input": {
                    "SD": model_input
                },
                "model_type": "SD",  # Static model type
                "model_id": model,  # Specify model to use
                "deadline": 30,  # Request processing deadline
                "priority": 1,  # Set request priority
                "neg_prompt": "(worst quality: 1.4), bad quality"  # Default negative prompt
            }

            # Send the prepared request payload to the API endpoint
            async with self._session.post(
                f"{self.base_url}/submit_job",
                json=request_params
            ) as response:
                logging.info(f"Request sent to URL: {self.base_url}/submit_job")
                logging.debug(f"Request payload: {request_params}")

                # Check for successful response
                if not response.ok:
                    logging.error(f"API returned an error. Status code: {response.status}")
                    if str(response.status).startswith(('4', '5')):
                        raise APIError("Generate image error. Please try again later")
                    raise APIError(f"HTTP error! status: {response.status}")
                    raise APIError(f"HTTP error! Received status: {response.status}")

                # Extract image URL from response
                url = await response.text()
                url = url.strip('"')  # Remove extra quotes (if any)
                logging.info(f"Image generated successfully. URL: {url}")

                return {
                    "url": url,
                    "model": model,
                    **model_input
                }

                logging.error(f"Error occurred during image generation: {str(e)}")
                raise e  # Re-raise known API errors
                raise APIError(f"Generate image error: {str(e)}")  # Wrap unknown exceptions
                raise APIError(f"Generate image error: {str(e)}")  # Wrap unknown exceptions