"""
Customer Service Assistant Script

This script provides a function to interact with an LLM (Large Language Model) for customer service tasks using a chat completion API.

Steps to use this tool:
1. Ensure you have a compatible OpenAI or OpenAI-compatible API endpoint and credentials.
2. Place your API key in an environment variable or .env file as required by your setup.
3. Import and use the `get_openai_completion_from_messages` function to send a list of messages (with 'role' and 'content') to the LLM.
4. Handle the returned response or any errors as needed in your application.

Steps followed in the tool:
1. Check the input to see if it flags in the moderation API
2. If it doesn't, we will extract the list of products
3. If the products are foung, we will try to look them up
4. We'll answer the user's question with the model
5. We'll put the anseer through the mdoeration API, if it is not flagged, we will return it to the user


Typical usage:
- Prepare a list of messages (system/user/assistant roles).
- Call the function with your messages and desired parameters.
- Use the returned string as the LLM's response to the customer.
"""

import panel as pn  # GUI
from openai import OpenAIError

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# sys.path.append("../..")
import utils


pn.extension()

from utils.openai_client import client
from enums.ai_models import OpenAIModels


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


"""
System of chained prompts for processing the user query
"""


def process_user_message(user_input, all_messages, debug=True):
    delimiter = "```"

    # Step 1: Check input to see if it flags the Moderation API or is a prompt injection
    response = client.moderations.create(input=user_input)
    moderation_output = response["results"][0]

    if moderation_output["flagged"]:
        print("Step 1: Input flagged by Moderation API.")
        return "Sorry, we cannot process this request."

    if debug:
        print("Step 1: Input passed moderation check.")

    category_and_product_response = utils.find_category_and_product_only(
        user_input, utils.get_products_and_category()
    )
    # print(print(category_and_product_response)
    # Step 2: Extract the list of products
    category_and_product_list = utils.read_string_to_list(category_and_product_response)
    # print(category_and_product_list)

    if debug:
        print("Step 2: Extracted list of products.")

    # Step 3: If products are found, look them up
    product_information = utils.generate_output_string(category_and_product_list)
    if debug:
        print("Step 3: Looked up product information.")

    # Step 4: Answer the user question
    system_message = """
    You are a customer service assistant for a large electronic store. \
    Respond in a friendly and helpful tone, with concise answers. \
    Make sure to ask the user relevant follow-up questions.
    """
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"{delimiter}{user_input}{delimiter}"},
        {
            "role": "assistant",
            "content": f"Relevant product information:\n{product_information}",
        },
    ]

    final_response = get_openai_completion_from_messages(all_messages + messages)
    if debug:
        print("Step 4: Generated response to user question.")
    all_messages = all_messages + messages[1:]

    # Step 5: Put the answer through the Moderation API
    response = client.moderations.create(input=final_response)
    moderation_output = response["results"][0]

    if moderation_output["flagged"]:
        if debug:
            print("Step 5: Response flagged by Moderation API.")
        return "Sorry, we cannot provide this information."

    if debug:
        print("Step 5: Response passed moderation check.")

    # Step 6: Ask the model if the response answers the initial user query well
    user_message = f"""
    Customer message: {delimiter}{user_input}{delimiter}
    Agent response: {delimiter}{final_response}{delimiter}

    Does the response sufficiently answer the question?
    """
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    evaluation_response = get_openai_completion_from_messages(messages)
    if debug:
        print("Step 6: Model evaluated the response.")

    # Step 7: If yes, use this answer; if not, say that you will connect the user to a human
    if (
        "Y" in evaluation_response
    ):  # Using "in" instead of "==" to be safer for model output variation (e.g., "Y." or "Yes")
        if debug:
            print("Step 7: Model approved the response.")
        return final_response, all_messages
    else:
        if debug:
            print("Step 7: Model disapproved the response.")
        neg_str = "I'm unable to provide the information you're looking for. I'll connect you with a human representative for further assistance."
        return neg_str, all_messages


user_input = "tell me about the smartx pro phone and the fotosnap camera, the dslr one. Also what tell me about your tvs"
response, _ = process_user_message(user_input, [])
print(response)


"""
Function that collects user and assistant messages over time

"""


def collect_messages(debug=False):
    user_input = inp.value_input
    if debug:
        print(f"User Input = {user_input}")
    if user_input == "":
        return
    inp.value = ""
    global context
    # response, context = process_user_message(user_input, context, utils.get_products_and_category(),debug=True)
    response, context = process_user_message(user_input, context, debug=False)
    context.append({"role": "assistant", "content": f"{response}"})
    panels.append(pn.Row("User:", pn.pane.Markdown(user_input, width=600)))
    panels.append(
        pn.Row(
            "Assistant:",
            pn.pane.Markdown(
                response, width=600, style={"background-color": "#F6F6F6"}
            ),
        )
    )

    return pn.Column(*panels)


"""
Chat with the chatbot!
Note that the system message includes detailed instructions about what the OrderBot should do.
"""
panels = []  # collect display

context = [{"role": "system", "content": "You are Service Assistant"}]

inp = pn.widgets.TextInput(placeholder="Enter text here…")
button_conversation = pn.widgets.Button(name="Service Assistant")

interactive_conversation = pn.bind(collect_messages, button_conversation)

dashboard = pn.Column(
    inp,
    pn.Row(button_conversation),
    pn.panel(interactive_conversation, loading_indicator=True, height=300),
)

dashboard
