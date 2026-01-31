"""
OpenAI API Demo Script

This script demonstrates how to use the OpenAI API through Requesty.ai
to make chat completion requests. It loads API credentials from environment
variables for security.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


def main():
    """Main function to demonstrate OpenAI API usage."""
    # Load environment variables from .env file
    load_dotenv()

    # Safely load your API key from environment
    requesty_api_key = os.getenv("REQUESTY_API_KEY")

    if not requesty_api_key:
        print("Error: REQUESTY_API_KEY not found in environment variables.")
        return

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

        # Example request
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "user", "content": "tell me a new joke everytime"}]
        )

        # Check if the response is successful
        if not response.choices:
            raise ValueError("No response choices found in API response.")

        # Print the result
        print(response.choices[0].message.content)

    except OpenAIError as e:
        print(f"OpenAI API error: {e}")
    except ValueError as e:
        print(f"Response validation error: {e}")
    except KeyError as e:
        print(f"Missing required data in response: {e}")
    except (ConnectionError, TimeoutError) as e:
        print(f"Network error: {e}")
    except (TypeError, AttributeError) as e:
        print(f"Data processing error: {e}")


if __name__ == "__main__":
    main()
