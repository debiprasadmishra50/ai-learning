"""
Selector Group chat with agents
======================

This example demonstrates how to use AutoGen to create a group chat with multiple agents.
The group chat will alternate between the agents until a termination condition is met.
"""

import asyncio
import os
import sys
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.messages import TextMessage

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from enums.ai_models import OpenAIModels  # type: ignore
from utils.get_env import get_env_variables  # type: ignore

# os.system("clear")
envs = get_env_variables()

""" 
    Selector Group Chat
    - This is used to create a group chat with multiple agents.
    - The group chat will alternate between the agents until a termination condition is met.
    - The termination condition is a text termination, which will cause the chat to terminate when the text "APPROVE" is received.
"""
async def main() -> None:
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
        temperature=1,
        # seed=42,
        # temperature=0.0,
    )

    async def lookup_hotel(location: str) -> str:
        return f"Here are some hotels in {location}: hotel1, hotel2, hotel3.\n"

    async def lookup_flight(origin: str, destination: str) -> str:
        return f"Here are some flights from {origin} to {destination}: flight1, flight2, flight3.\n"

    async def book_trip() -> str:
        return "Your trip is booked!\n"
    
    user_proxy = UserProxyAgent(
        "user_proxy", input_func=input
    )  # Use input() to get user input from console.

    travel_advisor = AssistantAgent(
        "Travel_Advisor",
        model_client,
        tools=[book_trip],
        description="Helps with travel planning.",
    )
    hotel_agent = AssistantAgent(
        "Hotel_Agent",
        model_client,
        tools=[lookup_hotel],
        description="Helps with hotel booking.",
    )
    flight_agent = AssistantAgent(
        "Flight_Agent",
        model_client,
        tools=[lookup_flight],
        description="Helps with flight booking.",
    )

    # termination = TextMentionTermination("TERMINATE")
    # The termination condition is a combination of text termination and max message termination, either of which will cause the chat to terminate.
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(10) # | TextMentionTermination("APPROVE")
    
    # The group chat will alternate between the agents until a termination condition is met.
    booking_agent = SelectorGroupChat(
        [user_proxy, travel_advisor, hotel_agent, flight_agent],
        model_client=model_client,
        termination_condition=termination,
    )

    """
        Run the conversation and stream to the console.
        The conversation will alternate between the agents until a termination condition is met.
    """
    while True:
        print("=" * 100)
        # print("Enter your task (type 'TERMINATE' to leave): ")
        task = input("Enter your task (type 'exit' to leave): ").strip()
        if task.lower() == "exit":
            break
        
        await booking_agent.reset()
        
        # Run the conversation and stream to the console.
        stream = booking_agent.run_stream(task=task)
        
        # Use asyncio.run(...) when running in a script.
        await Console(stream)
        
        # Get the user response.
        task = input("Enter your feedback (type 'exit' to leave): ")
        if task.lower().strip() == "exit":
            break

    # Close the connection to the model client.
    print("Closing the connection to the model client.")
    await model_client.close()

    # await Console(team.run_stream(task="Book a 3-day trip to new york."))

    # Close the connection to the model client.
    # await model_client.close()



async def simple_user_agent():
    agent = UserProxyAgent("user_proxy")
    response = await asyncio.create_task(
        agent.on_messages(
            [TextMessage(content="What is your name? ", source="user")],
            cancellation_token=CancellationToken(),
        )
    )
    assert isinstance(response.chat_message, TextMessage)
    print(f"Your name is {response.chat_message.content}")

    
if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(simple_user_agent())
