import re

import logging
import re

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def strip_tweet_text(text: str) -> str:
    logger.debug("Entering strip_tweet_text function.")
    if not isinstance(text, str):
        logger.warning("Invalid input: expected a string but got %s", type(text))
       return ""
    # Remove URLs
    logger.debug("Original text: %s", text)
    text_cleaned = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    logger.debug("Text after URL removal: %s", text_cleaned)
    # Remove @ mentions
    text_cleaned = re.sub(r'@\w+', '', text_cleaned).strip()
    logger.debug("Text after removing mentions: %s", text_cleaned)
    logger.debug("Exiting strip_tweet_text function.")
    return text_cleaned
