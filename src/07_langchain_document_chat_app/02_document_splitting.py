"""
## Document Splitting
- Once we have loaded our documents, we need to split them into smaller chunks.
- This is because LLMs have a context limit (e.g., 8k tokens for GPT-5 nano).
- The size of the chunks depends on the LLM that we are using.
- The overlap between chunks helps to ensure that there are no missing links in the information.

"""

import os
import sys
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    TokenTextSplitter,
    MarkdownHeaderTextSplitter,
)
from langchain_community.document_loaders import PyPDFLoader

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

""" 
## Character Text Splitter
- This splitter splits the text into chunks of a specified size.
- It does not care about the separators or the structure of the text.

## Recursive Character Text Splitter
- This splitter recursively tries to split the text by a list of separators (new line, period, space, etc.).
- It will start with the first separator, and if the chunk is too large, it will try the next separator, and so on.
- This is a very flexible splitter that works well for many documents.
"""

chunk_size = 26
chunk_overlap = 4


def chunking():
    print(f"[+] Chunk size: {chunk_size}, Chunk overlap: {chunk_overlap}")

    print(separator(80))

    # Initialize the splitters
    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    c_splitter = CharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    # Test the splitters
    text1 = "abcdefghijklmnopqrstuvwxyz"
    text2 = "abcdefghijklmnopqrstuvwxyzabcdefg"

    print(f"[+] Text 1: |{text1}|")
    print(f"[+] Text 2: |{text2}|")
    print(separator(80))
    print(f"[+] Recursive Splitter: {r_splitter.split_text(text1)}")
    print(f"[+] Recursive Splitter: {r_splitter.split_text(text2)}")

    print(separator(80))

    text3 = "a b c d e f g h i j k l m n o p q r s t u v w x y z"
    print(f"[+] Text 3: |{text3}|")
    print(f"[+] Recursive Splitter: {r_splitter.split_text(text3)}")
    print(f"[+] Character Splitter: {c_splitter.split_text(text3)}")

    print(separator(80))

    c_splitter = CharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, separator=" "
    )
    print(f'[+] Character Splitter with " " separator: {c_splitter.split_text(text3)}')
    print(c_splitter.split_text(text3))

    print(separator(80))


##########################################################################
# Real World Examples
##########################################################################


def sentence_chunking():
    print("[+] Real World Examples\n")
    some_text = """When writing documents, writers will use document structure to group content. \
    This can convey to the reader, which idea's are related. For example, closely related ideas \
    are in sentances. Similar ideas are in paragraphs. Paragraphs form a document. \n\n  \
    Paragraphs are often delimited with a carriage return or two carriage returns. \
    Carriage returns are the "backslash n" you see embedded in this string. \
    Sentences have a period at the end, but also, have a space.\
    and words are separated by space."""

    print(len(some_text))

    c_splitter = CharacterTextSplitter(chunk_size=450, chunk_overlap=0, separator=" ")
    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=450, chunk_overlap=0, separators=["\n\n", "\n", " ", ""]
    )

    print(c_splitter.split_text(some_text))
    print(separator(80))
    print(r_splitter.split_text(some_text))
    print(separator(80))

    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=150, chunk_overlap=0, separators=["\n\n", "\n", ". ", " ", ""]
    )
    print(r_splitter.split_text(some_text))
    print(separator(80))

    r_splitter = RecursiveCharacterTextSplitter(
        chunk_size=150, chunk_overlap=0, separators=["\n\n", "\n", "?<=. ", " ", ""]
    )
    print(r_splitter.split_text(some_text))
    print(separator(80))


##########################################################################
# PDF Splitter
##########################################################################
filepath = os.path.join(
    os.path.dirname(__file__),
    "docs",
    "cs229_lectures",
    "MachineLearning-Lecture01.pdf",
)
loader = PyPDFLoader(filepath)
pages = loader.load()


def pdf_chunking():
    print("[+] PDF Splitter\n")
    text_splitter = CharacterTextSplitter(
        chunk_size=1000, chunk_overlap=150, separator="\n", length_function=len
    )
    docs = text_splitter.split_documents(pages)
    print(f"[+] Number of documents: {len(docs)}")
    print(f"[+] Total Document Pages: {len(pages)}")
    print("[+] First document content:")
    print(f"{docs[0].page_content[:2000]}...")
    print(separator(80))


##########################################################################
# TokenTextSplitter
# We can also split on token count explicity, if we want.
# This can be useful because LLMs often have context windows designated in tokens.
# Tokens are often ~4 characters.
##########################################################################
print("[+] TokenTextSplitter\n")


def tokentext_splitting():
    text_splitter = TokenTextSplitter(chunk_size=1, chunk_overlap=0)
    text1 = "foo bar bazzyfoo"
    print(text_splitter.split_text(text1))
    print(separator(80))

    text_splitter = TokenTextSplitter(chunk_size=10, chunk_overlap=0)
    docs = text_splitter.split_documents(pages)
    print(f"[+] Number of documents: {len(docs)}")
    print(docs[0])
    print(separator(80))
    print(docs[0].metadata)


##########################################################################
# MarkdownHeaderTextSplitter
##########################################################################
print("[+] MarkdownHeaderTextSplitter\n")


def markdown_header_splitting():
    markdown_document = """# Title\n\n \
## Chapter 1\n\n \
Hi this is Jim\n\n Hi this is Joe\n\n \
### Section \n\n \
Hi this is Lance \n\n 
## Chapter 2\n\n \
Hi this is Molly"""

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )
    md_header_splits = markdown_splitter.split_text(markdown_document)
    print(md_header_splits[0])
    print(separator(80))
    print(md_header_splits[1])
    print(separator(80))


if __name__ == "__main__":
    # chunking()
    # sentence_chunking()
    # pdf_chunking()
    # tokentext_splitting()
    markdown_header_splitting()
