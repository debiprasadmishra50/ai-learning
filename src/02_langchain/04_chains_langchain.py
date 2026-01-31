"""
This script demonstrates various types of chains available in LangChain for building complex LLM workflows:

- LLMChain: Basic chain for single prompt-response interactions with an LLM.

- Sequential Chains:
    -The idea of sequential chains is to combine multiple chains where output of one chain is input to another chain, like piping in Unix.
    - SimpleSequentialChain: Executes a sequence of chains where each output is passed as input to the next. Single input/output
    - SequentialChain: Supports more complex sequential workflows with multiple inputs and outputs. Multiple input/output

- Router Chain: Dynamically routes inputs to different chains based on conditions or logic.

Use this script to explore and compare different chaining strategies for language model applications.
"""

import os
import sys

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.chains.sequential import SimpleSequentialChain, SequentialChain

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from enums.ai_models import OpenAIModels

# Load environment variables from .env file
load_dotenv()

# Safely load your API key from environment
requesty_api_key = os.getenv("REQUESTY_API_KEY")

if not requesty_api_key:
    raise ValueError("REQUESTY_API_KEY not found in environment variables.")

try:
    # Initialize OpenAI client for chat-based LLM
    llm = ChatOpenAI(
        api_key=requesty_api_key,
        base_url="https://router.requesty.ai/v1",
        model=OpenAIModels.gpt4o,
        temperature=0,
    )

except Exception as e:
    print(f"Warning: Could not initialize OpenAI client: {e}")
    llm = None

PRODUCT = "Queen Size Sheet Set"

# Create a prompt template for the LLMChain
prompt = ChatPromptTemplate.from_template(
    "What is the best name to describe a company that makes {product}? Give only one name which seem the best."
)


# ==============================================================================
# SECTION: LLMChain
# ==============================================================================


# Chain the prompt and the chat LLM together
chains = prompt | llm

# Invoke the chain with a sample product
response = chains.invoke({"product": PRODUCT})

# Print the LLM's response
print("[+] === LLMChain === \n")
print("Bot: ", response.content)
print("=" * 60)


# ==============================================================================
# SECTION: SimpleSequentialChain
# ==============================================================================


# Chain 1
chain1 = prompt | llm

# Step 2: Write a catchphrase for that company
prompt2 = ChatPromptTemplate.from_template(
    "Write a 20 words description for the following company:{company_name}"
)

# Chain 2
chain2 = prompt2 | llm

# Create SimpleSequentialChain
# # use LLMChain Objects, not LCEL
# overall_simple_chain = SimpleSequentialChain(chains=[chain1, chain2], verbose=True)
overall_simple_chain_LCEL = (
    chain1
    | StrOutputParser()
    | (lambda company_name: {"company_name": company_name})
    | chain2
)

# Run the chain
# result = overall_simple_chain.invoke({"product": PRODUCT})
result = overall_simple_chain_LCEL.invoke({"product": PRODUCT})

print("\n=== SimpleSequentialChain === \n")
# print(type(result))
print(result.content)

print("=" * 60)


# ==============================================================================
# SECTION: SequentialChain
# ==============================================================================

# prompt template 1: translate to english
first_prompt = ChatPromptTemplate.from_template(
    "Translate the following review to english:"
    "\n\n{Review}"  # pylint: disable=implicit-str-concat
)

chain1 = first_prompt | llm

second_prompt = ChatPromptTemplate.from_template(
    "Can you summarize the following review in 1 sentence:"
    "\n\n{English_Review}"  # pylint: disable=implicit-str-concat
)
chain2 = second_prompt | llm

third_prompt = ChatPromptTemplate.from_template(
    "What language is the following review:\n\n{Review}"  # pylint: disable=implicit-str-concat
)
chain3 = third_prompt | llm

fourth_prompt = ChatPromptTemplate.from_template(
    "Write a follow up response to the following "
    "summary in the specified language:"
    "\n\nSummary: {summary}\n\nLanguage: {language}"  # pylint: disable=implicit-str-concat
)
chain4 = fourth_prompt | llm

fifth_prompt = ChatPromptTemplate.from_template(
    "Write a meaning of follow up response in English "
    "\n\nfollow up: {follow_up}"  # pylint: disable=implicit-str-concat
)
chain5 = fifth_prompt | llm


# overall_chain: input= Review
# and output= English_Review,summary, followup_message
# overall_chain = SequentialChain(
#     chains=[chain_one, chain_two, chain_three, chain_four],
#     input_variables=["Review"],
#     output_variables=["English_Review", "summary", "followup_message"],
#     verbose=True,
# )

SAMPLE_REVIEW = "Este juego de sábanas tamaño queen superó mis expectativas. La tela es suave y fresca, y los colores se mantienen vibrantes después de varios lavados. El ajuste es perfecto para mi colchón y no se deslizan durante la noche. ¡Muy recomendable para quienes buscan comodidad y calidad!"

print("\n=== SequentialChain === \n")


# Most reliable approach - execute each step clearly
def execute_sequential_chain(review):
    """
    Executes a multi-step sequential chain for product review analysis:
    1. Translates the review to English.
    2. Summarizes the English review in one sentence.
    3. Detects the original language of the review.
    4. Generates a follow-up response in the detected language.
    5. Generates meaning of follow-up response in English.

    Args:
        review (str): The product review text (in any language).

    Returns:
        dict: A dictionary containing the English review, summary, detected language, and follow-up response.
    """
    print("\nStep 1: Translating to English...")
    english_review = (chain1 | StrOutputParser()).invoke({"Review": review})
    print(f"English Review: {english_review}")

    print("\nStep 2: Summarizing...")
    summary = (chain2 | StrOutputParser()).invoke({"English_Review": english_review})
    print(f"Summary: {summary}")

    print("\nStep 3: Detecting language...")
    language = (chain3 | StrOutputParser()).invoke({"Review": review})
    print(f"Language: {language}")

    print("\nStep 4: Generating follow-up...")
    follow_up = (chain4 | StrOutputParser()).invoke(
        {"summary": summary, "language": language}
    )
    print(f"Follow-up: {follow_up}")

    print("\nStep 5: Generating Meaning of follow-up...")
    follow_up_meaning = (chain5 | StrOutputParser()).invoke({"follow_up": follow_up})
    print(f"Follow-up Meaning: {follow_up_meaning}")

    return {
        "English_Review": english_review,
        "summary": summary,
        "language": language,
        "follow_up": follow_up,
        "follow_up_meaning": follow_up_meaning,
    }


# Test
result = execute_sequential_chain(SAMPLE_REVIEW)

# print(type(result))
# print(result)

print("=" * 60)
