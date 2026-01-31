"""
This script classifies customer service queries into primary and secondary categories using the Requesty API (OpenAI-compatible endpoint).
It loads the API key from a .env file, constructs a system prompt, sends the user query to the LLM, and prints the classification result in JSON format.
"""

import os
import sys

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from enums.ai_models import OpenAIModels

load_dotenv()  # read local .env file

# Safely load your API key from environment
requesty_api_key = os.getenv("REQUESTY_API_KEY")

if not requesty_api_key:
    print("Error: REQUESTY_API_KEY not found in environment variables.")
    sys.exit(1)

client = OpenAI(
    api_key=requesty_api_key,
    base_url="https://router.requesty.ai/v1",
)


def get_openai_completion_from_messages(
    messages, model=OpenAIModels.gpt4_1, temperature=0, max_tokens=500
):
    """
    Send a list of messages to the LLM and return the response content.

    Args:
        messages (list): List of message dicts with 'role' and 'content'.
        model (str): Model name to use for completion.
        temperature (float): Sampling temperature.
        max_tokens (int): Maximum number of tokens in the response.

    Returns:
        str: The content of the LLM's response message.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Check if the response is successful
        if not response.choices:
            raise Exception("No response choices found.")

        return response.choices[0].message.content

    except OpenAIError as e:
        print(f"OpenAI API error: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


DELIMETER = "#" * 32

system_message = f"""
You will be provided with customer service queries. \
The customer service query will be delimited with \
{DELIMETER} characters.
Classify each query into a primary category \
and a secondary category. 
Provide your output in json format with the \
keys: primary and secondary.

Primary categories: Billing, Technical Support, \
Account Management, or General Inquiry.

Billing secondary categories:
Unsubscribe or upgrade
Add a payment method
Explanation for charge
Dispute a charge

Technical Support secondary categories:
General troubleshooting
Device compatibility
Software updates

Account Management secondary categories:
Password reset
Update personal information
Close account
Account security

General Inquiry secondary categories:
Product information
Pricing
Feedback
Speak to a human

"""

user_message = "I want you to delete my profile and all of my user data"

messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": f"{DELIMETER}{user_message}{DELIMETER}"},
]

response = get_openai_completion_from_messages(messages)

print(response)

print("=" * 50)

user_message = "Tell me more about your flat screen tvs"
messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": f"{DELIMETER}{user_message}{DELIMETER}"},
]
response = get_openai_completion_from_messages(messages)

print(response)
