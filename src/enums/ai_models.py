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

    gpt5_nano = "openai/gpt-5-nano"
    """
    GPT-5-Nano model identifier for OpenAI API.
    """

    text_embedding_3_small = "openai/text-embedding-3-small"
    """
    Text Embedding 3 Small model identifier for OpenAI API.
    """

    stt_gpt_4o_mini_transcribe = "openai/gpt-4o-mini-transcribe"
    """
    GPT-4o-Mini-Transcribe model identifier for OpenAI API.
    """

    def __str__(self):
        return self.value
