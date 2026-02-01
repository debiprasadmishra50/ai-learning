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
from dotenv import load_dotenv
import json

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import SecretStr
from pydantic import BaseModel, Field
from typing import Literal, cast

from utils.separator import separator
from enums.ai_models import OpenAIModels

load_dotenv()
os.system("clear")

# Safely load your API key from environment
api_key = os.getenv("REQUESTY_API_KEY")
if not api_key:
    raise ValueError("REQUESTY_API_KEY not found in environment variables.")
requesty_api_key: SecretStr = SecretStr(api_key)
llm: ChatOpenAI | None = None

try:
    # Initialize OpenAI client for chat-based LLM
    llm = ChatOpenAI(
        api_key=requesty_api_key,
        base_url="https://router.requesty.ai/v1",
        model=OpenAIModels.gpt5_nano,
        temperature=0,
    )
except Exception as e:
    print(f"Warning: Could not initialize OpenAI client: {e}")
    llm = None

# ✅ ASSERTION
assert llm is not None, "Chat model not initialized"

PRODUCT = "Queen Size Sheet Set"


# ==============================================================================
# SECTION: LLMChain
# ==============================================================================

# Create a prompt template for the LLMChain
prompt = ChatPromptTemplate.from_template(
    "What is the best name to describe a company that makes {product}? Give only one name which seem the best."
)


def llmchain_demo():
    # Chain the prompt and the chat LLM together
    chains = prompt | llm  # type: ignore

    # Invoke the chain with a sample product
    response = chains.invoke({"product": PRODUCT})

    # Print the LLM's response
    print("[+] === LLMChain === \n")
    print("Bot: ", response.content)
    print("=" * 60)


# ==============================================================================
# SECTION: SimpleSequentialChain
# ==============================================================================


def simplesequentialchain_demo():
    # Chain 1
    chain1 = prompt | llm  # type: ignore

    # Step 2: Write a catchphrase for that company
    prompt2 = ChatPromptTemplate.from_template(
        "Write a 20 words description for the following company:{company_name}"
    )

    # Chain 2
    chain2 = prompt2 | llm  # type: ignore

    ##########################################################################
    # CHAIN INVOCATION USING LCEL
    ##########################################################################
    # Create SimpleSequentialChain
    # # use LLMChain Objects, not LCEL
    # overall_simple_chain = SimpleSequentialChain(chains=[chain1, chain2], verbose=True)
    overall_simple_chain_LCEL = (
        chain1 | StrOutputParser() | (lambda cn: {"company_name": cn}) | chain2
    )
    # NOTE: Always ensure the dict key ("company_name") matches the prompt variable name the next chain expects, and add parsing/validation if the LLM output is expected to be noisy.

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


def sequentialchain_demo():
    # prompt template 1: translate to english
    first_prompt = ChatPromptTemplate.from_template(
        "Translate the following review to english:\n\n{Review}"
    )

    chain1 = first_prompt | llm  # type: ignore

    second_prompt = ChatPromptTemplate.from_template(
        "Can you summarize the following review in 1 sentence:\n\n{English_Review}"
    )
    chain2 = second_prompt | llm  # type: ignore

    third_prompt = ChatPromptTemplate.from_template(
        "What language is the following review:\n\n{Review}"
    )
    chain3 = third_prompt | llm  # type: ignore

    fourth_prompt = ChatPromptTemplate.from_template(
        "Write a follow up response to the following "
        "summary in the specified language:"
        "\n\nSummary: {summary}\n\nLanguage: {language}"
    )
    chain4 = fourth_prompt | llm  # type: ignore

    fifth_prompt = ChatPromptTemplate.from_template(
        "Write a meaning of follow up response in English \n\nfollow up: {follow_up}"
    )
    chain5 = fifth_prompt | llm  # type: ignore

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
        print("\n[+] Step 1: Translating to English...")
        english_review = (chain1 | StrOutputParser()).invoke({"Review": review})
        print(f"[+] English Review: {english_review}")

        print("\n[+] Step 2: Summarizing...")
        summary = (chain2 | StrOutputParser()).invoke(
            {"English_Review": english_review}
        )
        print(f"[+] Summary: {summary}")

        print("\n[+] Step 3: Detecting language...")
        language = (chain3 | StrOutputParser()).invoke({"Review": review})
        print(f"[+] Language: {language}")

        print("\n[+] Step 4: Generating follow-up...")
        follow_up = (chain4 | StrOutputParser()).invoke(
            {"summary": summary, "language": language}
        )
        print(f"[+] Follow-up: {follow_up}")

        print("\n[+] Step 5: Generating Meaning of follow-up...")
        follow_up_meaning = (chain5 | StrOutputParser()).invoke(
            {"follow_up": follow_up}
        )
        print(f"[+] Follow-up Meaning: {follow_up_meaning}")

        return {
            "English_Review": english_review,
            "summary": summary,
            "language": language,
            "follow_up": follow_up,
            "follow_up_meaning": follow_up_meaning,
        }

    # Test
    result = execute_sequential_chain(SAMPLE_REVIEW)

    print(separator(60))

    print(type(result), end="\n")
    print(result)
    print(separator(60))

    print("JSON result:")
    print(json.dumps(result, indent=2))

    print(separator(60))


##########################################################################
# SECTION: Router Chain
##########################################################################


def router_chain_demo():
    print("\n=== RouterChain Demo === \n")

    # ✅ Define Templates
    physics_template = """You are a very smart physics professor. \
    You are great at answering questions about physics in a concise\
    and easy to understand manner. \
    When you don't know the answer to a question you admit\
    that you don't know.

    Here is a question:
    {input}"""

    math_template = """You are a very good mathematician. \
    You are great at answering math questions. \
    You are so good because you are able to break down \
    hard problems into their component parts, 
    answer the component parts, and then put them together\
    to answer the broader question.

    Here is a question:
    {input}"""

    history_template = """You are a very good historian. \
    You have an excellent knowledge of and understanding of people,\
    events and contexts from a range of historical periods. \
    You have the ability to think, reflect, debate, discuss and \
    evaluate the past. You have a respect for historical evidence\
    and the ability to make use of it to support your explanations \
    and judgements.

    Here is a question:
    {input}"""

    computerscience_template = """ You are a successful computer scientist.\
    You have a passion for creativity, collaboration,\
    forward-thinking, confidence, strong problem-solving capabilities,\
    understanding of theories and algorithms, and excellent communication \
    skills. You are great at answering coding questions. \
    You are so good because you know how to solve a problem by \
    describing the solution in imperative steps \
    that a machine can easily interpret and you know how to \
    choose a solution that has a good balance between \
    time complexity and space complexity. 

    Here is a question:
    {input}"""

    # ✅ Create prompt info
    prompt_infos = [
        {
            "name": "physics",
            "description": "Good for answering questions about physics",
            "prompt_template": physics_template,
        },
        {
            "name": "math",
            "description": "Good for answering math questions",
            "prompt_template": math_template,
        },
        {
            "name": "history",
            "description": "Good for answering history questions",
            "prompt_template": history_template,
        },
        {
            "name": "computer science",
            "description": "Good for answering computer science questions",
            "prompt_template": computerscience_template,
        },
    ]

    # Define routing schema
    class Route(BaseModel):
        """Route to the appropriate expert"""

        destination: Literal[
            "physics", "math", "history", "computer science", "DEFAULT"
        ] = Field(description="The expert domain to route to")

        next_inputs: str = Field(
            description="A potentially modified version of the original input"
        )

    assert llm is not None, "LLM not initialized"
    # ✅ Create router with structured output
    router_llm = llm.with_structured_output(Route)

    # ✅ Build destination chains
    destination_chains = {}
    for p_info in prompt_infos:
        name = p_info["name"]
        prompt_template = p_info["prompt_template"]
        prompt = ChatPromptTemplate.from_template(template=prompt_template)
        # ✅ Use pipe operator instead of LLMChain
        destination_chains[name] = prompt | llm

    print("[+] Destination Chains:")
    print(destination_chains)

    # Default chain
    default_prompt = ChatPromptTemplate.from_template("{input}")
    default_chain = default_prompt | llm

    # ✅ Router function - no LLMRouterChain
    def route_input(user_input: str) -> Route:
        """Route the input to the appropriate expert"""

        destinations = [f"{p['name']}: {p['description']}" for p in prompt_infos]
        destinations_str = "\n".join(destinations)

        router_instructions = f"""Given a raw text input to a language model, select the model prompt best suited for the input. \
    You will be given the names of the available prompts and a description of what the prompt is best suited for. \
    You may also revise the original input if you think that revising it will ultimately lead to a better response from the language model.

    CANDIDATE PROMPTS:
    {destinations_str}

    If the input doesn't fit any of the specified prompts, set destination to "DEFAULT."
    """

        # ✅ Use proper message format (list of messages, not dict)
        messages = [
            SystemMessage(content=router_instructions),
            HumanMessage(content=user_input),
        ]

        # ✅ Invoke with messages, ensure result is Route type
        result = router_llm.invoke(messages)
        decision: Route = cast(Route, result)

        return decision

    # ✅ Main router chain function - no MultiPromptChain

    def router_chain(user_input: str) -> str:
        """
        Main router that classifies input and routes to appropriate expert.
        Returns the final answer.
        """

        # Step 1: Route the input
        print(f"\n🔀 Routing input: {user_input}\n")
        route_decision = route_input(user_input)
        print(f"✓ Routed to: {route_decision.destination}")
        print(f"✓ Modified input: {route_decision.next_inputs}\n")

        # Step 2: Get the appropriate chain
        destination = route_decision.destination
        modified_input = route_decision.next_inputs

        if destination in destination_chains:
            # Use the expert chain
            chain = destination_chains[destination]
            print(f"🤖 Invoking {destination.upper()} expert...")
            result = chain.invoke({"input": modified_input})
            answer: str = result.content if hasattr(result, "content") else str(result)
        else:
            # Use default chain
            print("🤖 Invoking DEFAULT chain...")
            result = default_chain.invoke({"input": modified_input})
            answer: str = result.content if hasattr(result, "content") else str(result)  # type: ignore

        return answer

    ##########################################################################
    # Testing
    ##########################################################################
    # Test 1: Physics question
    print("=" * 80)
    print("TEST 1: PHYSICS QUESTION")
    print("=" * 80)
    answer = router_chain("What is black body radiation?")
    print(f"\n📝 Answer:\n{answer}\n")

    # Test 2: Math question
    print("=" * 80)
    print("TEST 2: MATH QUESTION")
    print("=" * 80)
    answer = router_chain("What is the quadratic formula?")
    print(f"\n📝 Answer:\n{answer}\n")

    # Test 3: History question
    print("=" * 80)
    print("TEST 3: HISTORY QUESTION")
    print("=" * 80)
    answer = router_chain("Who was Napoleon Bonaparte?")
    print(f"\n📝 Answer:\n{answer}\n")

    # Test 4: Computer Science question
    print("=" * 80)
    print("TEST 4: COMPUTER SCIENCE QUESTION")
    print("=" * 80)
    answer = router_chain("Explain what a binary search tree is")
    print(f"\n📝 Answer:\n{answer}\n")

    # Test 5: General question (goes to DEFAULT)
    print("=" * 80)
    print("TEST 5: GENERAL QUESTION")
    print("=" * 80)
    answer = router_chain("What's your favorite color?")
    print(f"\n📝 Answer:\n{answer}\n")


if __name__ == "__main__":
    # llmchain_demo()
    # simplesequentialchain_demo()
    # sequentialchain_demo()
    router_chain_demo()
