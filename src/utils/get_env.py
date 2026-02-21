import os
import sys
from dotenv import load_dotenv
from typing import TypedDict
from pprint import pprint

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class EnvVariables(TypedDict):
    REQUESTY_API_KEY: str
    OPENAI_MODEL: str
    STT_MODEL: str
    LIVEKIT_URL: str
    LIVEKIT_API_KEY: str
    LIVEKIT_API_SECRET: str
    ELEVEN_API_KEY: str
    CLAUDE_KEY: str


def get_env_variables() -> EnvVariables:
    load_dotenv()

    return {
        "REQUESTY_API_KEY": os.environ["REQUESTY_API_KEY"],
        "OPENAI_MODEL": os.environ["OPENAI_MODEL"],
        "STT_MODEL": os.environ["STT_MODEL"],
        "LIVEKIT_URL": os.environ["LIVEKIT_URL"],
        "LIVEKIT_API_KEY": os.environ["LIVEKIT_API_KEY"],
        "LIVEKIT_API_SECRET": os.environ["LIVEKIT_API_SECRET"],
        "ELEVEN_API_KEY": os.environ["ELEVEN_API_KEY"],
        "CLAUDE_KEY": os.environ["CLAUDE_KEY"],
    }


if __name__ == "__main__":
    get_env_variables()
