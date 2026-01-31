"""
Example Usage of OpenAI Client Module

This file demonstrates different ways to use the openai_client module.
"""

from openai import OpenAIError

# Method 1: Import the pre-initialized client
from utils.openai_client import client

# Method 2: Import the function to create a new client instance
from utils.openai_client import get_openai_client


def example_with_global_client():
    """Example using the global client instance."""
    if not client:
        print("Error: OpenAI client is not available.")
        return

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": "Hello! How are you today?"}],
        )

        if response.choices:
            print("Response using global client:")
            print(response.choices[0].message.content)

    except OpenAIError as e:
        print(f"OpenAI API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def example_with_function_client():
    """Example creating a new client instance using the function."""
    try:
        # Create a new client instance
        my_client = get_openai_client()

        response = my_client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": "Tell me a fun fact about Python programming.",
                }
            ],
        )

        if response.choices:
            print("\nResponse using function-created client:")
            print(response.choices[0].message.content)

    except ValueError as e:
        print(f"Configuration error: {e}")
    except OpenAIError as e:
        print(f"OpenAI API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    print("OpenAI Client Module Usage Examples")
    print("=" * 40)

    # Run both examples
    example_with_global_client()
    example_with_function_client()
