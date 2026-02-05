import os
import sys
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
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
assert embeddings is not None, "OpenAI Embeddings not initialized"

persist_directory = os.path.join(os.path.dirname(__file__), "docs", "chroma")

vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
print(f"[+] Total documents in vector store: {vectordb._collection.count()}")

##########################################################################
# Vector Retrieval
# MMR: Maximum Marginal Relevance
# MMR is a way of selecting documents that are similar to the query, but also diverse from each other.
#
# LLM Aided Retrueval
# LLM can help to determine the relevance of the document to the query.
##########################################################################


def mmr_search():

    texts = [
        """The Amanita phalloides has a large and imposing epigeous (aboveground) fruiting body (basidiocarp).""",
        """A mushroom with a large fruiting body is the Amanita phalloides. Some varieties are all-white.""",
        """A. phalloides, a.k.a Death Cap, is one of the most poisonous of all known mushrooms.""",
    ]

    smalldb = Chroma.from_texts(texts, embedding=embeddings)

    question = "Tell me about all-white mushrooms with large fruiting bodies"
    print(f"Question: {question}\n")

    print(smalldb.similarity_search(question, k=2))
    print(separator(80))

    print(smalldb.max_marginal_relevance_search(question, k=2, fetch_k=3))
    print(separator(80))

    question = "what did they say about matlab?"
    print(f"Question: {question}\n")

    docs_ss = vectordb.similarity_search(question, k=3)
    print(f"[+] Similarity Search: Found {len(docs_ss)} similar documents\n")
    print(docs_ss[0].page_content[:100])
    print(separator(80))
    print(docs_ss[1].page_content[:100])
    print(separator(80))

    docs_mmr = vectordb.max_marginal_relevance_search(question, k=3)
    print(f"[+] MMR: Found {len(docs_mmr)} similar documents\n")
    print(docs_mmr[0].page_content[:100])
    print(separator(80))
    print(docs_mmr[1].page_content[:100])
    print(separator(80))

    # SELF QUERY
    print("[+] Self Query\n")
    question = "what did they say about regression in the third lecture?"
    print(f"Question: {question}\n")

    docs = vectordb.similarity_search(
        question,
        k=3,
        filter={
            "source": "./ai-learning/src/07_langchain_document_chat_app/docs/cs229_lectures/MachineLearning-Lecture03.pdf"
        },
    )
    print(f"[+] Similarity Search: Found {len(docs)} similar documents\n")
    # print(docs[0].page_content[:100])
    # print(separator(80))
    for d in docs:
        print(d.metadata)
    print(separator(80))


if __name__ == "__main__":
    mmr_search()
