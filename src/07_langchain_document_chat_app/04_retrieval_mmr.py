import os
import sys
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma

from pydantic import SecretStr
import numpy as np

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
embeddings: OpenAIEmbeddings | None = None
embeddings = OpenAIEmbeddings(
    api_key=requesty_api_key,
    base_url="https://router.requesty.ai/v1",
    model=OpenAIModels.text_embedding_3_small,
)


filepath = os.path.join(os.path.dirname(__file__), "docs", "cs229_lectures")
files = [
    "MachineLearning-Lecture01.pdf",
    "MachineLearning-Lecture02.pdf",
    "MachineLearning-Lecture03.pdf",
]

loaders = [PyPDFLoader(os.path.join(filepath, file)) for file in files]
docs = []
for loader in loaders:
    docs.extend(loader.load())

print(f"[+] Number of documents: {len(docs)}")
print(separator(80))

# Split
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
splits = text_splitter.split_documents(docs)
print(f"[+] Number of splits: {len(splits)}")
print(separator(80))


##########################################################################
# Embeddings
##########################################################################
def embeddings_openai():
    print("[+] Embeddings\n")
    assert embeddings is not None, "OpenAI Embeddings not initialized"

    sentence1 = "i like dogs"
    sentence2 = "i like canines"
    sentence3 = "the weather is ugly outside"

    embedding1 = embeddings.embed_query(sentence1)
    embedding2 = embeddings.embed_query(sentence2)
    embedding3 = embeddings.embed_query(sentence3)

    print(np.dot(embedding1, embedding2))
    print(separator(80))
    print(np.dot(embedding1, embedding3))
    print(separator(80))
    print(np.dot(embedding2, embedding3))
    print(separator(80))


##########################################################################
# Vector Embeddings
##########################################################################
def vector_embeddings():
    print("[+] Vector Embeddings\n")
    assert embeddings is not None, "OpenAI Embeddings not initialized"

    # Remove the collection if it exists
    # rm -r ./src/07_langchain_chat_app/docs/chroma
    persist_directory = os.path.join(os.path.dirname(__file__), "docs", "chroma")

    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=persist_directory,
    )

    print(f"[+] Total documents in vector store: {vectordb._collection.count()}")

    ##########################################################################
    # Similarity Search
    ##########################################################################
    question = "is there an email i can ask for help"
    docs = vectordb.similarity_search(question, k=3)
    print(f"[+] Found {len(docs)} similar documents\n")
    for doc in docs:
        print(doc.page_content)

    print(separator(80))

    # Failure Case
    question = "what did they say about matlab?"
    docs = vectordb.similarity_search(question, k=3)
    print(f"[+] Found {len(docs)} documents for matlab query\n")
    for doc in docs:
        print(doc.metadata)

    print(separator(80))

    question = "what did they say about regression in the third lecture?"
    docs = vectordb.similarity_search(question, k=3)
    print(f"[+] Found {len(docs)} documents for regression query\n")
    for doc in docs:
        print(doc.metadata)

    print(separator(80))

    return vectordb


if __name__ == "__main__":
    # embeddings_openai()
    vector_embeddings()
