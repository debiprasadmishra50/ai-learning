import asyncio
import os
import sys
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.base import Handoff
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from enums.ai_models import OpenAIModels  # type: ignore
from utils.get_env import get_env_variables  # type: ignore

os.system("clear")
envs = get_env_variables()

model_client = OpenAIChatCompletionClient(
    base_url="https://router.requesty.ai/v1",
    api_key=envs["REQUESTY_API_KEY"],
    model=OpenAIModels.gpt5_nano,
    model_info={
        "vision": False,
        "family": "gpt-5",
        "function_calling": True,
        "json_output": True,
        "multiple_system_messages": True,
        "structured_output": True,
    },
)


async def user_proxy() -> None:
    # Create the agents.
    assistant = AssistantAgent("assistant", model_client=model_client)
    user_proxy = UserProxyAgent(
        "user_proxy", input_func=input
    )  # Use input() to get user input from console.

    # Create the termination condition which will end the conversation when the user says "APPROVE".
    termination = TextMentionTermination("APPROVE")

    # Create the team setting a maximum number of turns to 1.
    team = RoundRobinGroupChat(
        [assistant, user_proxy], termination_condition=termination
    )

    # task = "Write a 4-line poem about the ocean."
    task = "Tell me a joke."

    while True:
        # Run the conversation and stream to the console.
        stream = team.run_stream(task=task)
        # Use asyncio.run(...) when running in a script.
        await Console(stream)
        # Get the user response.
        task = input("Enter your feedback (type 'exit' to leave): ")
        if task.lower().strip() == "exit":
            break
    await model_client.close()


async def max_turns() -> None:
    assistant = AssistantAgent("assistant", model_client=model_client)

    # Create the team setting a maximum number of turns to 1.
    team = RoundRobinGroupChat([assistant], max_turns=1)
    # team = RoundRobinGroupChat([assistant], max_turns=2) # Assistant will reply twice

    # task = "Write a 4-line poem about the ocean."
    task = "Tell me joke."
    while True:
        # Run the conversation and stream to the console.
        stream = team.run_stream(task=task)
        # Use asyncio.run(...) when running in a script.
        await Console(stream)
        # Get the user response.
        task = input("Enter your feedback (type 'exit' to leave): ")
        if task.lower().strip() == "exit":
            break
    await model_client.close()


async def with_termination_condition() -> None:
    # Create a lazy assistant agent that always hands off to the user.
    lazy_agent = AssistantAgent(
        "lazy_assistant",
        model_client=model_client,
        handoffs=[Handoff(target="user", message="Transfer to user.")],
        system_message="If you cannot complete the task, transfer to user. Otherwise, when finished, respond with 'TERMINATE'.",
    )

    # Define a termination condition that checks for handoff messages.
    handoff_termination = HandoffTermination(target="user")
    # Define a termination condition that checks for a specific text mention.
    text_termination = TextMentionTermination("TERMINATE")

    # Create a single-agent team with the lazy assistant and both termination conditions.
    lazy_agent_team = RoundRobinGroupChat(
        [lazy_agent], termination_condition=handoff_termination | text_termination
    )

    task = "Tell me weather in delhi."  # Won't Work
    task = "The weather in New York is sunny."  # Will Work

    while True:
        # Run the conversation and stream to the console.
        stream = lazy_agent_team.run_stream(task=task)

        # Use asyncio.run(...) when running in a script.
        await Console(stream)

        # Get the user response.
        task = input("Enter your feedback (type 'exit' to leave): ")
        if task.lower().strip() == "exit":
            break
    await model_client.close()


if __name__ == "__main__":
    asyncio.run(user_proxy())
    # asyncio.run(max_turns())
    # asyncio.run(with_termination_condition())
