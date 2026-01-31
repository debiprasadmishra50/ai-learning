"""
Demo script for using LangChain with OpenAI's Chat models.
This script demonstrates basic usage of the ChatOpenAI class from langchain_openai.
"""

import os
import sys

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from enums.ai_models import OpenAIModels

# Load environment variables
load_dotenv()

# Safely load your API key from environment
requesty_api_key = os.getenv("REQUESTY_API_KEY")

if not requesty_api_key:
    raise ValueError("REQUESTY_API_KEY not found in environment variables.")

try:
    # Initialize OpenAI client
    chat = ChatOpenAI(
        api_key=requesty_api_key,
        base_url="https://router.requesty.ai/v1",
        model=OpenAIModels.gpt4o,
        temperature=0,
    )
    print(chat, end="\n" * 2)

except Exception as e:
    print(f"Warning: Could not initialize OpenAI client: {e}")
    chat = None

style = """Indian English \
in a calm and respectful tone
"""

template_string = """Translate the text that is delimited by triple backticks \
into a style that is {style}. \
text: ```{text}```
"""

prompt_template = ChatPromptTemplate.from_template(template_string)
print(prompt_template.messages[0].prompt, end="\n" * 2)
print(prompt_template.messages[0].prompt.input_variables, end="\n" * 2)

customer_style = """American English \
in a calm and respectful tone
"""

customer_email = """
Arrr, I be fuming that me blender lid \
flew off and splattered me kitchen walls \
with smoothie! And to make matters worse, \
the warranty don't cover the cost of \
cleaning up me kitchen. I need yer help \
right now, matey!
"""

customer_messages = prompt_template.format_messages(
    style=customer_style, text=customer_email
)

print(type(customer_messages), end="\n" * 2)
print(type(customer_messages[0]), end="\n" * 2)

print(customer_messages[0], end="\n" * 2)

# Call the LLM to translate to the style of the customer message
customer_response = chat.invoke(customer_messages)
print(customer_response.content, end="\n")

#
print("=" * 100)
#

service_reply = """Hey there customer, the warranty does not cover cleaning expenses for your kitchen because it's your fault that you misused your blender by forgetting to put the lid on before starting the blender. Tough luck! See ya!
"""

service_style_pirate = """\
a polite tone \
that speaks in English Pirate\
"""

service_messages = prompt_template.format_messages(
    style=service_style_pirate, text=service_reply
)

print(service_messages[0].content)
service_response = chat.invoke(service_messages)
print(service_response.content, end="\n")

#
print("=" * 100)
#

customer_review = """\
This leaf blower is pretty amazing.  It has four settings:\
candle blower, gentle breeze, windy city, and tornado. \
It arrived in two days, just in time for my wife's \
anniversary present. \
I think my wife liked it so much she was speechless. \
So far I've been the only one using it, and I've been \
using it every other morning to clear the leaves on our lawn. \
It's slightly more expensive than the other leaf blowers \
out there, but I think it's worth it for the extra features.
"""

review_template = """\
For the following text, extract the following information:

gift: Was the item purchased as a gift for someone else? \
Answer True if yes, False if not or unknown.

delivery_days: How many days did it take for the product \
to arrive? If this information is not found, output -1.

price_value: Extract any sentences about the value or price,\
and output them as a comma separated Python list.

Format the output as JSON with the following keys:
gift
delivery_days
price_value

text: {text}
"""
prompt_template = ChatPromptTemplate.from_template(review_template)
print(prompt_template, end="\n\n")

messages = prompt_template.format_messages(text=customer_review)

response = chat.invoke(messages, temperature=0.0)

print(response.content, end="\n\n")

#
print("=" * 100)
#


gift_schema = ResponseSchema(
    name="gift",
    description="Was the item purchased\
                             as a gift for someone else? \
                             Answer True if yes,\
                             False if not or unknown.",
)
delivery_days_schema = ResponseSchema(
    name="delivery_days",
    description="How many days\
                                      did it take for the product\
                                      to arrive? If this \
                                      information is not found,\
                                      output -1.",
)
price_value_schema = ResponseSchema(
    name="price_value",
    description="Extract any\
                                   sentences about the value or \
                                   price, and output them as a \
                                   comma separated Python list.",
)

response_schemas = [gift_schema, delivery_days_schema, price_value_schema]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

format_instructions = output_parser.get_format_instructions()

print(format_instructions, end="\n\n")

review_template_2 = """\
For the following text, extract the following information:

gift: Was the item purchased as a gift for \
someone else? Answer True if yes, False if not or unknown.

delivery_days: How many days did it take for the product\
to arrive? If this information is not found, output -1.

price_value: Extract any sentences about the value or \
price, and output them as a comma separated Python list.

text: {text}

{format_instructions}
"""

prompt_template = ChatPromptTemplate.from_template(review_template_2)
print(prompt_template, end="\n\n")

messages = prompt_template.format_messages(
    text=customer_review, format_instructions=format_instructions
)
print(messages[0].content, end="\n\n")

response = chat.invoke(messages, temperature=0.0)

print(response.content, end="\n\n")

output_dict = output_parser.parse(response.content)
print(output_dict, end="\n\n")
print(type(output_dict))
print(output_dict.get("delivery_days"))
