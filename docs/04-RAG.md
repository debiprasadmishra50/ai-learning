# RAG (Retrieval-Augmented Generation)

Retrieval-Augmented Generation (RAG) is an advanced AI framework that combines the strengths of information retrieval and generative language models. RAG enhances the capabilities of language models by allowing them to access and utilize external knowledge sources during text generation, resulting in more accurate and contextually relevant responses.

## How RAG Works

1. **Retrieval Step**: When a query is received, the system retrieves relevant documents or passages from an external knowledge base (such as a vector database or search engine) using similarity search or keyword matching.

2. **Augmentation Step**: The retrieved information is combined with the original query and provided as context to a generative language model (like GPT or BERT-based models).

3. **Generation Step**: The language model generates a response that incorporates both the query and the retrieved knowledge, producing more informed and accurate outputs.

## Core Components of RAG

- **Knowledge Base**: An external data source (such as a vector database, document store, or search index) that provides the information used during retrieval.

- **Retriever**: Responsible for searching and fetching relevant documents or passages from a large knowledge base. Common retrievers use vector similarity search or traditional search algorithms.

- **Generator**: A generative language model(LLM) that creates responses based on the input query and the retrieved context.

RAG is widely used in applications like question answering, chatbots, and enterprise search, where up-to-date and contextually rich information is essential.

## RAG Data Flow Diagram

Below is a horizontal block diagram representing the data flow in a RAG system, from user query to final response:

```plaintext
+------------+     +------------+     +-------------------+     +---------+     +--------------+     +-----+     +----------+
| User Query | --> | Embedding  | --> | Retrieve Relevant | --> | Context | --> | Augmentation | --> | LLM | --> | Response |
|            |     | Generation |     | Data (Vector DB)  |     |         |     |              |     |     |     |          |
+------------+     +------------+     +-------------------+     +---------+     +--------------+     +-----+     +----------+
```

This diagram illustrates the step-by-step flow from receiving a user query to generating a response using Retrieval-Augmented Generation.

## Langchain

Langchain is an open-source framework designed to simplify the development of applications that use large language models (LLMs) and retrieval-augmented generation (RAG) workflows. It provides modular components and abstractions to connect LLMs with external data sources, enabling more powerful and context-aware AI applications.

### Role in RAG

Langchain acts as the orchestration layer in RAG systems, managing the flow between user queries, retrieval from knowledge bases, and language model generation. It streamlines the integration of retrievers, vector databases, and LLMs, making it easier to build robust RAG pipelines.

### What Langchain Does

- Connects LLMs to external data sources (vector databases, document stores, APIs)
- Manages the retrieval and augmentation process
- Provides tools for prompt engineering and chaining multiple operations
- Supports memory, conversation history, and context management
- Enables easy integration with various LLM providers and retrievers

### Core Components of Langchain

- **Chains**: Sequences of operations (e.g., retrieval, augmentation, generation) that define the workflow for a task.

- **Retrievers**: Interfaces to fetch relevant documents or data from external sources.

- **Prompt Templates**: Tools for constructing and managing prompts sent to LLMs.

- **Memory**: Modules for storing and recalling conversation or context history.

- **Agents**: Components that make decisions about which tools or chains to use based on user input.

- **Integrations**: Built-in support for popular vector databases, LLM APIs, and other data sources.

Langchain accelerates the development of RAG-based applications by providing reusable building blocks and best practices for connecting language models with real-world data.

## RAG Evaluation

- **Implemented Precision**@K - "Of what I retrieved, how much is useful?"

- **Implemented Recall**@K - "Of what I should find, how much did I get?"

- **Implemented MRR** - "How quickly do I find the first relevant result?"

- **Implemented NDCG** - "How good is my overall ranking?"

### When to Use Each Metric:

- Precision@K - When you want to minimize noise in results

- Recall@K - When you can't afford to miss relevant documents

- MRR - For Q&A systems where only the top result matters

- NDCG - For search engines where ranking order is important

#### Key Trade-off:
    Higher K → Better recall, but possibly lower precision

## Example: Retrieval-Augmented QA with Langchain, Wikipedia, and FAISS

Below is an improved Python code example that demonstrates how to use Langchain with OpenAI, Wikipedia, FAISS, and environment variables for the OpenAI API key. This version uses the `dotenv` package to load environment variables and ensures the API key is used by the OpenAI and embedding classes.

```python
import os
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import WikipediaLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

# Load environment variables from a .env file
load_dotenv()

# Set your OpenAI API key in a .env file as OPENAI_API_KEY=your-api-key-here
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# 1. Load documents from Wikipedia
loader = WikipediaLoader(query="artificial intelligence", lang="en", load_max_docs=3)
documents = loader.load()

# 2. Split documents into smaller chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = text_splitter.split_documents(documents)

# 3. Create embeddings for the document chunks
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
vectorstore = FAISS.from_documents(docs, embeddings)

# 4. Set up the retriever
retriever = vectorstore.as_retriever()

# 5. Set up the LLM (using OpenAI's GPT-3/4)
llm = OpenAI(temperature=0, openai_api_key=openai_api_key)

# 6. Set up the Retrieval QA chain
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# 7. Ask a question
question = "What is artificial intelligence?"
answer = qa_chain.run(question)

print(f"Q: {question}\nA: {answer}")
```

**Note:**

- Install the required packages: `langchain`, `openai`, `faiss-cpu`, `python-dotenv`.
- Create a `.env` file in your project directory with the line: `OPENAI_API_KEY=your-api-key-here`.
- This script demonstrates the full workflow: loading Wikipedia data, splitting text, creating embeddings, storing in FAISS, setting up retrieval QA, and querying the LLM.


---


## There are other techniques of RAG

1. **CAG (Corrective Augmented Generation)**:
- Evaluates the quality of retrieved documents and only uses high-confidence results
- If retrieved documents are irrelevant, it employs alternative retrieval methods
- Reformulates the query to ensure accuracy before generation

2. **Agentic RAG**:
- Implements intelligent decision-making using autonomous agents
- Dynamically decides when to retrieve information and which tools to use
- Treats retrieval as part of a broader reasoning process rather than a fixed pipeline

3. **Multi Query RAG**:
- Generates multiple variations of the user's query automatically
- Improves retrieval coverage by using different query formulations
- Reduces the risk of missing important information due to single-query limitations

4. **Hierarchical RAG**:
- Organizes documents in a hierarchical structure (summaries → sections → detailed content)
- Retrieves information at multiple levels for better efficiency
- Drills down into details as needed, improving relevance

5. **Multi Modal RAG**:
- Extends RAG to handle multiple types of data (text, images, videos, audio)
- Retrieves and processes information from diverse media types
- Integrates different media into generation for richer, more comprehensive responses