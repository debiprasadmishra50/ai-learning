"""Tool use"""

import os
import sys
import asyncio
from autogen_core import CancellationToken
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.tools import AgentTool
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import TextMessage

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


def get_weather(city: str) -> str:  # Async tool is possible too.
    return f"The weather in {city} is 72 degree and sunny."  # can be a API call to openweather or similar service to fetch the actual data


async def tool_use() -> None:
    """Tool use example"""
    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant. You can call tools to help user.",
        model_client=model_client,
        tools=[get_weather],
        reflect_on_tool_use=True,  # Set to True to have the model reflect on the tool use, set to False to return the tool call result directly.
    )
    while True:
        user_input = input("User: ")
        if user_input == "exit":
            break
        response = await assistant.on_messages(
            [TextMessage(content=user_input, source="user")], CancellationToken()
        )
        print("Assistant:", response.chat_message.to_text())
    await model_client.close()


async def agent_as_tool() -> None:
    """Agent as tool example"""

    math_agent = AssistantAgent(
        "math_expert",
        model_client=model_client,
        system_message="You are a math expert.",
        description="A math expert assistant.",
        model_client_stream=True,
    )
    math_agent_tool = AgentTool(math_agent, return_value_as_last_message=True)

    chemistry_agent = AssistantAgent(
        "chemistry_expert",
        model_client=model_client,
        system_message="You are a chemistry expert.",
        description="A chemistry expert assistant.",
        model_client_stream=True,
    )
    chemistry_agent_tool = AgentTool(chemistry_agent, return_value_as_last_message=True)

    agent = AssistantAgent(
        "assistant",
        system_message="You are a general assistant. Use expert tools when needed.",
        model_client=model_client,
        model_client_stream=True,
        tools=[math_agent_tool, chemistry_agent_tool],
        max_tool_iterations=10,
    )

    await Console(agent.run_stream(task="What is the integral of x^2?"))
    # await Console(agent.run_stream(task="What is the molecular weight of water?"))
    await Console(agent.run_stream(task="How 1 liter of water is 1 kilogram?"))

    await model_client.close()


if __name__ == "__main__":
    asyncio.run(tool_use())
    # asyncio.run(agent_as_tool())
