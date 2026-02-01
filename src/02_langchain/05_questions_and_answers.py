"""
LangChain: Q&A over Documents (Updated Version - Compatible with LangChain 1.2.7)
An example that allows you to query a product catalog for items of interest.

- LCEL Chain (Recommended for LangChain 1.2.7+)
- Step By Step Approach
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import DocArrayInMemorySearch

from pydantic import SecretStr

from utils.separator import separator
from enums.ai_models import OpenAIModels

load_dotenv()
os.system("clear")

# Safely load your API key from environment
api_key = os.getenv("REQUESTY_API_KEY")
if not api_key:
    raise ValueError("REQUESTY_API_KEY not found in environment variables.")
requesty_api_key: SecretStr = SecretStr(api_key)
llm: ChatOpenAI | None = None
embeddings: OpenAIEmbeddings | None = None

try:
    # ✅ Initialize OpenAI client for chat-based LLM
    llm = ChatOpenAI(
        api_key=requesty_api_key,
        base_url="https://router.requesty.ai/v1",
        model=OpenAIModels.gpt5_nano,
        temperature=0,
    )

    # ✅ Initialize embeddings
    embeddings = OpenAIEmbeddings(
        api_key=requesty_api_key,
        base_url="https://router.requesty.ai/v1",
        model=OpenAIModels.text_embedding_3_small,
    )
    # print(embeddings.embed_query("Hello World"), end="\n" * 2)
except Exception as e:
    print(f"Warning: Could not initialize OpenAI client: {e}")
    llm = None

# ✅ ASSERTION
assert llm is not None, "Chat model not initialized"
assert embeddings is not None, "Embeddings not initialized"

# ✅ Load data
file_path = Path(__file__).parent / "data" / "OutdoorClothingCatalog_1000.csv"
print(f"[+] Loading file: {file_path}")
loader = CSVLoader(file_path=file_path, encoding="utf-8")
docs = loader.load()
print(f"[+] Loaded {len(docs)} documents")

# ✅ Create vector database directly
vectorDB = DocArrayInMemorySearch.from_documents(docs, embeddings)

# ✅ Create retriever
retriever = vectorDB.as_retriever()


# ============================================================================
# METHOD 1: LCEL CHAIN (Recommended for LangChain 1.2.7+)
# ============================================================================
def lecl_chain():
    query = "Please list all your shirts with sun protection in a table in markdown and summarize each one."

    print(separator(60))
    print("METHOD 1: LCEL CHAIN")
    print(separator(60))

    # Define a prompt template
    lcel_prompt = ChatPromptTemplate.from_template(
        """Answer the question based only on the following context:

    Context: {context}

    Question: {question}

    Provide your answer in markdown format."""
    )

    # Format docs function
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # ✅ ASSERTION
    assert llm is not None, "Chat model not initialized"
    assert embeddings is not None, "Embeddings not initialized"

    # Create the LCEL chain
    lcel_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | lcel_prompt
        | llm
        | StrOutputParser()
    )

    # Run the chain
    response = lcel_chain.invoke(query)
    print("RESPONSE FROM LCEL CHAIN:")
    print(separator(60))
    console = Console()
    console.print(Markdown(response))
    print(separator(60))


##########################################################################
# METHOD 2: Step By Step Approach
##########################################################################
def step_by_step_approach():
    # ✅ ASSERTION
    assert llm is not None, "Chat model not initialized"
    assert embeddings is not None, "Embeddings not initialized"

    print(separator(60))
    print("METHOD 2: Step By Step Approach")
    print(separator(60))

    # ✅ Test embeddings
    print("[+] Testing embeddings...")
    embed = embeddings.embed_query("Hi my name is Harrison")
    print(f"[+] Embedding dimension: {len(embed)}")
    print(f"[+] First 5 values: {embed[:5]}\n")

    # ✅ Perform similarity search
    print(separator(60))
    print("[+] Performing similarity search...")
    query_similarity = "Please suggest a shirt with sunblocking"
    similar_docs = vectorDB.similarity_search(query_similarity)
    print(f"[+] Found {len(similar_docs)} similar documents")
    print(f"[+] Most similar document: {similar_docs[0]}\n")

    # ✅ Create retriever
    print(separator(60))
    print("[+] Creating retriever...")
    retriever = vectorDB.as_retriever()
    print(retriever.invoke(query_similarity))

    # ✅ Combine docs to a single piece of text, join all page content
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # ✅ Define a prompt template
    lcel_prompt = ChatPromptTemplate.from_template(
        """Answer the question based only on the following context:

    Context: {context}

    Question: {question}

    Provide your answer in markdown format."""
    )

    # ✅ Define the query
    query = "Please list all your shirts with sun protection in a table in markdown and summarize each one."

    # ✅ Create the LCEL chain
    lcel_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }  # RunnablePassthrough: Passes the input directly to the next step
        | lcel_prompt
        | llm
        | StrOutputParser()
    )

    # ✅ Run the chain
    response = lcel_chain.invoke(query)
    print(separator(60))
    print("RESPONSE FROM LCEL CHAIN:")
    print(separator(60))
    console = Console()
    console.print(Markdown(response))


if __name__ == "__main__":
    # lecl_chain()
    step_by_step_approach()
