"""
07_chatbot.py

This module provides a utility function to interact with OpenAI's chat completion API using a list of message dictionaries.

It leverages the OpenAI client and model enums defined in the project to send messages to a specified LLM (default: GPT-4) and retrieve the generated response content.

The function is designed for chatbot and conversational AI use cases, supporting configurable model, temperature, and token limits.
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
from utils.openai_client import client
from enums.ai_models import OpenAIModels


def get_openai_completion_from_messages(
    messages, model=OpenAIModels.gpt4_1, temperature=0, max_tokens=500
):
    """
    Send a list of messages to the LLM and return the response content.

    Args:
        messages (list): List of message dicts with 'role' and 'content'.
        model (OpenAIModels): Model enum to use for completion.
        temperature (float): Sampling temperature.
        max_tokens (int): Maximum number of tokens in the response.

    Returns:
        str: The content of the LLM's response message.
    """
    response = client.chat.completions.create(
        model=model,  # Use the string value of the enum
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


context = [
    {
        "role": "system",
        "content": """
            You are OrderBot, an automated service to collect orders for a pizza restaurant. \
            You first greet the customer, then collects the order, \
            and then asks if it's a pickup or delivery. \
            You wait to collect the entire order, then summarize it and check for a final \
            time if the customer wants to add anything else. \
            If it's a delivery, you ask for an address. \
            Finally you collect the payment.\
            Make sure to clarify all options, extras and sizes to uniquely \
            identify the item from the menu.\
            You respond in a short, very conversational friendly style. \
            The menu includes \
            pepperoni pizza  12.95, 10.00, 7.00 \
            cheese pizza   10.95, 9.25, 6.50 \
            eggplant pizza   11.95, 9.75, 6.75 \
            fries 4.50, 3.50 \
            greek salad 7.25 \
            Toppings: \
            extra cheese 2.00, \
            mushrooms 1.50 \
            sausage 3.00 \
            canadian bacon 3.50 \
            AI sauce 1.50 \
            peppers 1.00 \
            Drinks: \
            coke 3.00, 2.00, 1.00 \
            sprite 3.00, 2.00, 1.00 \
            bottled water 5.00 \
            """,
    }
]
# accumulate messages

messages = context.copy()
messages.append(
    {
        "role": "system",
        "content": "create a json summary of the previous food order. Itemize the price for each item\
 The fields should be 1) pizza, include size 2) list of toppings 3) list of drinks, include size   4) list of sides include size  5)total price ",
    },
)

print("[+] Bot Starting...\n")
time.sleep(1)
os.system("cls" if os.name == "nt" else "clear")

# ASCII art for Pizza OrderBot
orderbot_art = r"""
 ____  _                   ____          _           ____        _
|  _ \(_)__________ _     / __ \_ __ __| | ___ _ ___| __ )  ___ | |_
| |_) | |_  /_  / _` |   | |  | | '__/ _` |/ _ \ '__|  _ \ / _ \| __|
|  __/| |/ / / / (_| |   | |__| | | | (_| |  __/ |  | |_) | (_) | |_
|_|   |_/___/___\__,_|    \____/|_|  \__,_|\___|_|  |____/ \___/ \__|
                                                                     
           🍕 Welcome to Pizza OrderBot! 🍕
"""
print(orderbot_art)
print("=" * 100)
print("[+] Bot: Hello, welcome to Pizza OrderBot! What would you like to order?")
while True:
    try:
        user_input = input("\n[+] Enter your message: ")
        messages.append({"role": "user", "content": user_input})
        response = get_openai_completion_from_messages(messages)
        print("[+] Bot:", response)
        messages.append({"role": "assistant", "content": response})
    except KeyboardInterrupt:
        print("\nExiting chat. Goodbye!")
        break
    except Exception as e:
        print(f"An error occurred: {e}")
