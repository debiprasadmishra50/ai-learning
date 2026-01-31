"""
This script demonstrates a chain-of-thought prompt for answering customer queries about specific products using an LLM.
It defines a multi-step system prompt, sends user queries to the LLM, and prints the step-by-step reasoning and response.
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


delimiter = "#" * 32

system_message = f"""
Follow these steps to answer the customer queries.
The customer query will be delimited with four hashtags,\
i.e. {delimiter}. 

Step 1:{delimiter} First decide whether the user is 
asking a question about a specific product or products. 
Product cateogry doesn't count. 

Step 2:{delimiter} If the user is asking about 
specific products, identify whether 
the products are in the following list.
All available products: 
1. Product: TechPro Ultrabook
   Category: Computers and Laptops
   Brand: TechPro
   Model Number: TP-UB100
   Warranty: 1 year
   Rating: 4.5
   Features: 13.3-inch display, 8GB RAM, 256GB SSD, Intel Core i5 processor
   Description: A sleek and lightweight ultrabook for everyday use.
   Price: $799.99

2. Product: BlueWave Gaming Laptop
   Category: Computers and Laptops
   Brand: BlueWave
   Model Number: BW-GL200
   Warranty: 2 years
   Rating: 4.7
   Features: 15.6-inch display, 16GB RAM, 512GB SSD, NVIDIA GeForce RTX 3060
   Description: A high-performance gaming laptop for an immersive experience.
   Price: $1199.99

3. Product: PowerLite Convertible
   Category: Computers and Laptops
   Brand: PowerLite
   Model Number: PL-CV300
   Warranty: 1 year
   Rating: 4.3
   Features: 14-inch touchscreen, 8GB RAM, 256GB SSD, 360-degree hinge
   Description: A versatile convertible laptop with a responsive touchscreen.
   Price: $699.99

4. Product: TechPro Desktop
   Category: Computers and Laptops
   Brand: TechPro
   Model Number: TP-DT500
   Warranty: 1 year
   Rating: 4.4
   Features: Intel Core i7 processor, 16GB RAM, 1TB HDD, NVIDIA GeForce GTX 1660
   Description: A powerful desktop computer for work and play.
   Price: $999.99

5. Product: BlueWave Chromebook
   Category: Computers and Laptops
   Brand: BlueWave
   Model Number: BW-CB100
   Warranty: 1 year
   Rating: 4.1
   Features: 11.6-inch display, 4GB RAM, 32GB eMMC, Chrome OS
   Description: A compact and affordable Chromebook for everyday tasks.
   Price: $249.99

Step 3:{delimiter} If the message contains products \
in the list above, list any assumptions that the \
user is making in their \
message e.g. that Laptop X is bigger than \
Laptop Y, or that Laptop Z has a 2 year warranty.

Step 4:{delimiter}: If the user made any assumptions, \
figure out whether the assumption is true based on your \
product information. 

Step 5:{delimiter}: First, politely correct the \
customer's incorrect assumptions if applicable. \
Only mention or reference products in the list of \
5 available products, as these are the only 5 \
products that the store sells. \
Answer the customer in a friendly tone.

Use the following format:
Step 1:{delimiter} <step 1 reasoning>
Step 2:{delimiter} <step 2 reasoning>
Step 3:{delimiter} <step 3 reasoning>
Step 4:{delimiter} <step 4 reasoning>
Response to user:{delimiter} <response to customer>

Make sure to include {delimiter} to separate every step.
"""


user_message = (
    """by how much is the BlueWave Chromebook more expensive than the TechPro Desktop"""
)

messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": f"{delimiter}{user_message}{delimiter}"},
]

response = get_openai_completion_from_messages(messages)
print(response)

print("=" * 100)

user_message = """do you sell tvs"""
messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": f"{delimiter}{user_message}{delimiter}"},
]
response = get_openai_completion_from_messages(messages)
print(response)


try:
    final_response = response.split(delimiter)[-1].strip()
except Exception as e:
    final_response = (
        "Sorry, I'm having trouble right now, please try asking another question."
    )
print("\n", final_response)
