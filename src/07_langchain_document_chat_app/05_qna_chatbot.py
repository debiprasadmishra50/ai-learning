import os
import sys
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

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
llm: ChatOpenAI | None = None
embeddings: OpenAIEmbeddings | None = None
embeddings = OpenAIEmbeddings(
    api_key=requesty_api_key,
    base_url="https://router.requesty.ai/v1",
    model=OpenAIModels.text_embedding_3_small,
)
# Initialize OpenAI client
llm = ChatOpenAI(
    api_key=requesty_api_key,
    base_url="https://router.requesty.ai/v1",
    model=OpenAIModels.gpt5_nano,
    temperature=0,
)
assert embeddings is not None, "OpenAI Embeddings not initialized"
assert llm is not None, "Chat model not initialized"

persist_directory = os.path.join(os.path.dirname(__file__), "docs", "chroma")

vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
print(f"[+] Total documents in vector store: {vectordb._collection.count()}")

question = "What are major topics for this class?"
print(f"[+] Question: {question}\n")
docs = vectordb.similarity_search(question, k=3)
print(len(docs))


def qna_chatbot():
    print("[+] Q&A Chatbot\n")
    assert llm is not None, "Chat model not initialized"

    retriever = vectordb.as_retriever()

    question = "What are major topics for this class?"
    print(f"[+] Question: {question}\n")

    docs = vectordb.similarity_search(question, k=3)
    print(f"[+] Found {len(docs)} similar documents\n")

    prompt_template = ChatPromptTemplate.from_template(
        "Answer the question based only on the following context:\n\n{context}\n\nQuestion: {question}"
    )

    # Format docs function
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Create the LCEL chain
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )
    print(chain.invoke(question))
    print(separator(80))


if __name__ == "__main__":
    qna_chatbot()
