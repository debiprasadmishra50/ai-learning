"""
OpenAI Client Module

This module provides a pre-configured OpenAI client that can be imported
and used across different scripts. It handles API key loading and client
initialization with proper error handling.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


def get_openai_client():
    """
    Initialize and return an OpenAI client configured for Requesty.ai.

    Returns:
        OpenAI: Configured OpenAI client instance

    Raises:
        ValueError: If REQUESTY_API_KEY is not found in environment variables
        OpenAIError: If there's an issue initializing the OpenAI client
    """
    # Load environment variables from .env file
    load_dotenv()

    # Safely load your API key from environment
    requesty_api_key = os.getenv("REQUESTY_API_KEY")

    if not requesty_api_key:
        raise ValueError("REQUESTY_API_KEY not found in environment variables.")

    try:
        # Initialize OpenAI client
        client = OpenAI(
            api_key=requesty_api_key,
            base_url="https://router.requesty.ai/v1",
            # default_headers={
            #     "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional
            #     "X-Title": "<YOUR_SITE_NAME>",  # Optional
            # },
        )
        return client

    except Exception as e:
        raise OpenAIError(f"Failed to initialize OpenAI client: {e}") from e


# Create a global client instance for convenience
try:
    client = get_openai_client()

except (ValueError, OpenAIError) as e:
    print(f"Warning: Could not initialize OpenAI client: {e}")
    client = None
