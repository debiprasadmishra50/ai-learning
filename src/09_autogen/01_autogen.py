import os
import sys
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from enums.ai_models import OpenAIModels  # type: ignore
from utils.get_env import get_env_variables  # type: ignore

os.system("clear")

envs = get_env_variables()


async def main() -> None:
    model_client = OpenAIChatCompletionClient(
        base_url="https://router.requesty.ai/v1",
        api_key=envs["REQUESTY_API_KEY"],
        model=OpenAIModels.gpt5_nano,
        model_info={
            "vision": False,
            "family": "gpt-5",
            "function_calling": False,
            "json_output": False,
            "multiple_system_messages": True,
            "structured_output": True,
        },
    )
    agent = AssistantAgent("assistant", model_client=model_client)
    print(await agent.run(task="Say 'Hello World!'"))
    await model_client.close()


asyncio.run(main())
