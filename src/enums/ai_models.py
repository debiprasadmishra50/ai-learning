"""
This module defines enums for OpenAI model names used in the API.
"""

from enum import Enum


class OpenAIModels(str, Enum):
    """
    Enum for OpenAI model names.
    """

    gpt4o = "openai/gpt-4o"
    """
    GPT-4.0 model identifier for OpenAI API.
    """

    gpt4_1 = "openai/gpt-4.1"
    """
    GPT-4.1 model identifier for OpenAI API.
    """

    def __str__(self):
        return self.value
