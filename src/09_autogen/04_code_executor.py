import asyncio
import os
import sys
from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
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
    seed=42,
    temperature=0.0,
)


async def coding_assistant() -> None:

    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant. Write all code in python. Reply only 'TERMINATE' if the task is done.",
        model_client=model_client,
    )

    code_executor = CodeExecutorAgent(
        name="code_executor",
        code_executor=LocalCommandLineCodeExecutor(work_dir="coding"),
    )

    # The termination condition is a combination of text termination and max message termination, either of which will cause the chat to terminate.
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)

    # The group chat will alternate between the assistant and the code executor.
    group_chat = RoundRobinGroupChat(
        [assistant, code_executor], termination_condition=termination
    )

    # `run_stream` returns an async generator to stream the intermediate messages.
    stream = group_chat.run_stream(
        task="Write a python script to print 'Hello, world!'"
    )
    # `Console` is a simple UI to display the stream.
    await Console(stream)

    # Close the connection to the model client.
    await model_client.close()


async def coding_assistant_with_human_in_the_loop() -> None:
    """Coding assistant with human in the loop example"""
    assistant = AssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant. Write all code in python.",
        model_client=model_client,
    )

    code_executor = CodeExecutorAgent(
        name="code_executor",
        code_executor=LocalCommandLineCodeExecutor(work_dir="coding"),
    )

    user_proxy = UserProxyAgent(
        "user_proxy", input_func=input
    )  # Use input() to get user input from console.

    # The termination condition is a combination of text termination and max message termination, either of which will cause the chat to terminate.
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)

    # The group chat will alternate between the assistant and the code executor.
    coding_agent = RoundRobinGroupChat(
        [user_proxy, assistant, code_executor],
        termination_condition=termination,
    )

    while True:
        print("=" * 100)
        print("Enter your task (type 'TERMINATE' to leave): ")
        # Run the conversation and stream to the console.
        stream = coding_agent.run_stream()
        # Use asyncio.run(...) when running in a script.
        await Console(stream)
        # Get the user response.
        task = input("Enter your feedback (type 'exit' to leave): ")
        if task.lower().strip() == "exit":
            break
    await model_client.close()


if __name__ == "__main__":
    # asyncio.run(coding_assistant())
    asyncio.run(coding_assistant_with_human_in_the_loop())
