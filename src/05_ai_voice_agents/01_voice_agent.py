"""
# Voice Agent Architecture and Workflow Documentation.

This module outlines the architecture of a real-time Voice Agent system. The system is
designed to handle full-duplex conversational interactions by orchestrating a pipeline
of specialized components.

System Components
-----------------
The Voice Agent stack consists of the following key components:

1.  **VAD (Voice Activity Detection):**
    Monitors the audio stream to detect the presence of human speech. It filters out
    background noise and silence, ensuring that downstream components only process
    relevant audio data.

2.  **EOT (End of Turn / Utterance Detection):**
    Analyzes speech patterns, pauses, and semantic completeness to determine when
    the user has finished speaking. This triggers the transition from listening to
    processing.

3.  **ASR (Automatic Speech Recognition) or STT (Speech-to-Text):**
    Converts the raw audio waveform into text. This transcription is the input for
    the intelligence layer.

4.  **LLM Agent (Large Language Model):**
    The cognitive core of the system. It processes the transcribed text, manages
    conversation state/context, and generates a semantic text response.

5.  **TTS (Text-to-Speech) or Speech Synthesis:**
    Converts the text response from the LLM into synthesized audio speech to be
    played back to the user.

Data Flow
---------
The information flows sequentially through the pipeline:
    Input -> ASR -> LLM -> TTS -> Output

Latency and Real-Time Communication
-----------------------------------
To achieve low latency and a natural conversational feel, the system utilizes
real-time peer-to-peer communication protocols:

*   **WebRTC:** Used for high-speed, low-latency audio streaming between the client
    and the server.
*   **HTTP / Websockets:** Employed for control signaling, event handling, or as
    fallback transport mechanisms.

Architecture Diagram
--------------------
.. mermaid::

    graph LR
        Input([User Audio Input]) --> VAS[Voice Activity Detection]
        VAS --> EOU[End of Turn Detection]
        EOU --> ASR[ASR / STT]
        ASR --> LLM[LLM Agent]
        LLM --> TTS[TTS / Speech Synthesis]
        TTS --> Output([Audio Output])

        subgraph Transport [Real-Time Transport]
            direction TB
            WebRTC
            Websockets
        end
"""

import os
import sys
import logging
import httpx
from dotenv import load_dotenv

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# LiveKit agent imports
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai, elevenlabs, silero
from livekit.agents.metrics import LLMMetrics, STTMetrics, TTSMetrics, EOUMetrics
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dlai-agent")

# Load environment variables (LIVEKIT credentials, OPENAI API keys, etc.)
load_dotenv()
llm_model = os.getenv("OPENAI_MODEL", "openai/gpt-5-nano")
requesty_api_key = os.getenv("REQUESTY_API_KEY")
stt_model = os.getenv("STT_MODEL", "STT_MODEL=openai/gpt-4o-mini-transcribe")

os.system("clear")
logger.log(logging.INFO, "Starting AGENT")


class Assistant(Agent):
    """A simple LiveKit voice assistant wiring STT, LLM and TTS plugins.

    - Uses OpenAI for STT & LLM (via the LiveKit OpenAI plugin, via Requesty's OpenAI-compatible API)
    - Uses ElevenLabs for TTS
    - Uses Silero for VAD

    Configure behavior via environment variables (e.g. OPENAI_MODEL).
    """

    def __init__(self) -> None:
        # plugin factories may be None if imports failed; guard for that so module can be imported

        # Initialize LLM with Requesty's OpenAI-compatible API
        llm: openai.LLM | None = None
        if openai is not None and requesty_api_key:
            try:
                logger.info(f"Initializing LLM with model: {llm_model}")
                llm = openai.LLM(
                    model=llm_model,
                    api_key=requesty_api_key,
                    base_url="https://router.requesty.ai/v1",
                    timeout=httpx.Timeout(
                        30.0, connect=15.0, read=30.0, write=10.0, pool=5.0
                    ),
                )
                logger.info("LLM initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Requesty LLM: {e}")
                llm = None

        # Initialize STT with Requesty's OpenAI-compatible API
        stt: openai.STT | None = None
        if openai is not None and requesty_api_key:
            try:
                logger.info(f"Initializing STT with model: {stt_model}")
                stt = openai.STT(
                    model=stt_model,
                    api_key=requesty_api_key,
                    base_url="https://router.requesty.ai/v1",
                )
                logger.info("STT initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Requesty STT: {e}")
                stt = None

        # Initialize TTS with ElevenLabs
        """
        # Roger: CwhRBWXzGAHq8TQ4Fs17
        # Sarah: EXAVITQu4vr4xnSDxMaL
        # Laura: FGY2WhTYpPnrIDTdsKH5
        # George: JBFqnCBsd6RMkjVDRZzb
        """
        tts = elevenlabs.TTS() if elevenlabs is not None else None
        # Initialize VAD with Silero
        vad = silero.VAD.load() if silero is not None else None

        super().__init__(
            instructions="""
                You are a helpful assistant communicating via voice.
                Keep responses brief and conversational for a natural back-and-forth.
            """,
            stt=stt,
            llm=llm,
            tts=tts,
            vad=vad,
        )

        ##########################################################################
        # Adding Metrics to the Agent
        ##########################################################################
        assert llm is not None, "LLM not initialized"
        assert stt is not None, "STT not initialized"
        assert tts is not None, "TTS not initialized"
        assert vad is not None, "VAD not initialized"

        def llm_metrics_wrapper(metrics: LLMMetrics):
            asyncio.create_task(self.on_llm_metrics_collected(metrics))

        llm.on("metrics_collected", llm_metrics_wrapper)

        def stt_metrics_wrapper(metrics: STTMetrics):
            asyncio.create_task(self.on_stt_metrics_collected(metrics))

        stt.on("metrics_collected", stt_metrics_wrapper)

        def eou_metrics_wrapper(metrics: EOUMetrics):
            asyncio.create_task(self.on_eou_metrics_collected(metrics))

        stt.on("eou_metrics_collected", eou_metrics_wrapper)

        def tts_metrics_wrapper(metrics: TTSMetrics):
            asyncio.create_task(self.on_tts_metrics_collected(metrics))

        tts.on("metrics_collected", tts_metrics_wrapper)

    async def on_llm_metrics_collected(self, metrics: LLMMetrics) -> None:
        print("\n--- LLM Metrics ---")
        print(f"Prompt Tokens: {metrics.prompt_tokens}")
        print(f"Completion Tokens: {metrics.completion_tokens}")
        print(f"Tokens per second: {metrics.tokens_per_second:.4f}")
        print(f"TTFT: {metrics.ttft:.4f}s")
        print("------------------\n")

    async def on_stt_metrics_collected(self, metrics: STTMetrics) -> None:
        print("\n--- STT Metrics ---")
        print(f"Duration: {metrics.duration:.4f}s")
        print(f"Audio Duration: {metrics.audio_duration:.4f}s")
        print(f"Streamed: {'Yes' if metrics.streamed else 'No'}")
        print("------------------\n")

    async def on_eou_metrics_collected(self, metrics: EOUMetrics) -> None:
        print("\n--- End of Utterance Metrics ---")
        print(f"End of Utterance Delay: {metrics.end_of_utterance_delay:.4f}s")
        print(f"Transcription Delay: {metrics.transcription_delay:.4f}s")
        print("--------------------------------\n")

    async def on_tts_metrics_collected(self, metrics: TTSMetrics) -> None:
        print("\n--- TTS Metrics ---")
        print(f"TTFB: {metrics.ttfb:.4f}s")
        print(f"Duration: {metrics.duration:.4f}s")
        print(f"Audio Duration: {metrics.audio_duration:.4f}s")
        print(f"Streamed: {'Yes' if metrics.streamed else 'No'}")
        print("------------------\n")

    ## Metrics added


async def entrypoint(ctx: JobContext):
    """Entrypoint for the LiveKit worker.

    Connects and starts an AgentSession with our Assistant implementation.
    """
    await ctx.connect()

    session = AgentSession()
    await session.start(room=ctx.room, agent=Assistant())


def main():
    """Start the LiveKit Voice Agent.

    This can be run in different modes:
    - python 01_voice_agent.py console  : Test in terminal with local audio
    - python 01_voice_agent.py dev      : Development mode with hot reloading
    - python 01_voice_agent.py start    : Production mode

    Required environment variables:
    - LIVEKIT_URL: LiveKit server URL
    - LIVEKIT_API_KEY: LiveKit API key
    - LIVEKIT_API_SECRET: LiveKit API secret
    - REQUESTY_API_KEY: Requesty API key
    - OPENAI_MODEL: OpenAI model to use (e.g. gpt-5-nano)
    - ELEVEN_API_KEY: ElevenLabs API key
    """
    logger.info("Starting LiveKit Voice Agent")

    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint),
    )


if __name__ == "__main__":
    main()
