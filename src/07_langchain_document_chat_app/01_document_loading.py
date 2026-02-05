"""

## Retrieval augmented generation
- In retrieval augmented generation (RAG), an LLM retrieves contextual documents from an external dataset as part of its execution.
- This is useful if we want to ask question about specific documents (e.g., our PDFs, a set of videos, etc).
"""

import os
import sys
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import (
    PyPDFLoader,
    WebBaseLoader,
    NotionDirectoryLoader,
)
from langchain_community.document_loaders.blob_loaders.youtube_audio import (
    YoutubeAudioLoader,
)
from langchain_community.document_loaders.blob_loaders.file_system import (
    FileSystemBlobLoader,
)
from langchain_community.document_loaders.parsers import OpenAIWhisperParser
from langchain_community.document_loaders.generic import GenericLoader

from pydantic import SecretStr

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from enums.ai_models import OpenAIModels
from utils.separator import separator

# Load environment variables
load_dotenv()
os.system("clear")

# Safely load your API key from environment
api_key = os.getenv("REQUESTY_API_KEY")
if not api_key:
    raise ValueError("REQUESTY_API_KEY not found in environment variables.")
requesty_api_key: SecretStr = SecretStr(api_key)
chat: ChatOpenAI | None = None


##########################################################################
# Load Documents with PyPDFLoader
##########################################################################
def load_pdf_document():
    filepath = os.path.join(
        os.path.dirname(__file__),
        "docs",
        "cs229_lectures",
        "MachineLearning-Lecture01.pdf",
    )
    loader = PyPDFLoader(filepath)
    pages = loader.load()
    print(f"[=] Number of pages: {len(pages)} in {filepath}")
    print(separator(80))
    print("[+] First page content:")
    print(f"{pages[0].page_content[:300]}...")
    print(separator(80))
    print("[+] First page metadata:")
    print(pages[0].metadata)
    print(separator(80))


##########################################################################
# Document Loader, load Youtube Videos
##########################################################################
def load_youtube_video():
    video_url = "https://www.youtube.com/shorts/G8nQJ4R0KwA"
    # video_url = "https://www.youtube.com/watch?v=wx2Ml3vWHys"
    save_dir = os.path.join(os.path.dirname(__file__), "docs", "youtube")
    loader = GenericLoader(
        YoutubeAudioLoader([video_url], save_dir),
        # FileSystemBlobLoader(save_dir, glob="*.m4a"),  # fetch locally
        OpenAIWhisperParser(
            api_key=requesty_api_key.get_secret_value(),
            base_url="https://router.requesty.ai/v1",
            # model="openai/whisper-1",
            model=OpenAIModels.stt_gpt_4o_mini_transcribe,
        ),
    )
    docs = loader.load()
    print(f"[+] Number of documents: {len(docs)}")
    print(separator(80))
    if docs:
        print("[+] First document content:")
        print(f"{docs[0].page_content[:300]}...")
    else:
        print("[-] No documents were loaded.")
    print(separator(80))


##########################################################################
# Web URL Loader
##########################################################################
def load_web_url():
    url = "https://lilianweng.github.io/posts/2023-06-23-agent/"
    loader = WebBaseLoader(url)
    docs = loader.load()
    print(f"[+] Number of documents: {len(docs)}")
    print(separator(80))
    if docs:
        print("[+] First document content:")
        print(f"{docs[0].page_content[:300]}...")
    else:
        print("[-] No documents were loaded.")
    print(separator(80))


##########################################################################
# Notion Loader
##########################################################################
def notion_loader():
    filepath = os.path.join(os.path.dirname(__file__), "docs", "Notion_DB")
    loader = NotionDirectoryLoader(filepath)
    docs = loader.load()
    print(f"[+] Number of documents: {len(docs)}")
    print(separator(80))
    if docs:
        print("[+] First document content:")
        print(f"{docs[0].page_content[:300]}...")
        print(separator(80))
        print("[+] First document metadata:")
        print(docs[0].metadata)
    else:
        print("[-] No documents were loaded.")
    print(separator(80))


if __name__ == "__main__":
    # load_pdf_document()
    # load_youtube_video()
    # load_web_url()
    notion_loader()
