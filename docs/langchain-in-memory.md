# LangChain Resources & Usage Guide

## How to Execute Your LangChain Code

### 1. Run the Memory Demo

```bash
# From your project root directory
cd /Users/debiprasadmishra/Documents/Python-Learning/ai-learning
python src/02-langchain/02-langchain_memory.py
```

### 2. Run the Basic Demo

```bash
python src/02-langchain/01_langchain_demo.py
```

## Essential LangChain Resources

### Official Documentation

1. **LangChain Python Documentation**: https://python.langchain.com/
2. **API Reference**: https://python.langchain.com/api_reference/
3. **LangChain Expression Language (LCEL)**: https://python.langchain.com/docs/concepts/lcel/
4. **Memory & Chat History**: https://python.langchain.com/docs/how_to/chatbots_memory/

### Key Concepts to Master

#### 1. LangChain Expression Language (LCEL)

- **Chain Composition**: Use `|` operator to connect components
- **Runnable Interface**: All components implement the same interface
- **Streaming Support**: Built-in streaming capabilities

```python
# Basic LCEL pattern
chain = prompt | llm | output_parser
result = chain.invoke({"input": "Hello"})
```

#### 2. Memory Management

- **RunnableWithMessageHistory**: Modern approach for conversation memory
- **Session Management**: Use session IDs to maintain separate conversations
- **Memory Types**: Buffer, Window, Token Buffer, Summary

#### 3. Prompt Templates

- **ChatPromptTemplate**: For chat-based interactions
- **MessagesPlaceholder**: For dynamic message insertion
- **System/Human/AI Messages**: Structured conversation flow

### Modern LangChain Patterns

#### 1. Basic Chat Chain

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("human", "{input}")
])

llm = ChatOpenAI()
chain = prompt | llm

response = chain.invoke({"input": "Hello!"})
```

#### 2. Chain with Memory

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chain = prompt | llm

# Add memory
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: InMemoryChatMessageHistory(),
    input_messages_key="input",
    history_messages_key="history",
)
```

#### 3. Output Parsing

```python
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

# String output
chain = prompt | llm | StrOutputParser()

# JSON output with schema
class Person(BaseModel):
    name: str = Field(description="person's name")
    age: int = Field(description="person's age")

parser = JsonOutputParser(pydantic_object=Person)
chain = prompt | llm | parser
```

### Best Practices

#### 1. Error Handling

```python
try:
    response = chain.invoke({"input": "Hello"})
except Exception as e:
    print(f"Chain execution failed: {e}")
```

#### 2. Environment Configuration

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found")
```

#### 3. Streaming Responses

```python
for chunk in chain.stream({"input": "Tell me a story"}):
    print(chunk.content, end="", flush=True)
```

### Advanced Features

#### 1. RAG (Retrieval Augmented Generation)

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough

# Create retriever
vectorstore = FAISS.from_texts(texts, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# RAG chain
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

#### 2. Agents

```python
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_community.tools import DuckDuckGoSearchRun

tools = [DuckDuckGoSearchRun()]
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)
```

### Learning Path

#### Beginner (Week 1-2)

1. Master LCEL basics
2. Understand prompt templates
3. Practice with simple chains
4. Learn memory management

#### Intermediate (Week 3-4)

1. Output parsing and validation
2. Custom chains and runnables
3. Error handling and debugging
4. Streaming and async operations

#### Advanced (Week 5+)

1. RAG implementations
2. Agent frameworks
3. Custom tools and retrievers
4. Production deployment patterns

### Useful GitHub Repositories

1. **LangChain**: https://github.com/langchain-ai/langchain
2. **LangChain Templates**: https://github.com/langchain-ai/langchain/tree/master/templates
3. **LangServe**: https://github.com/langchain-ai/langserve (for deployment)
4. **LangSmith**: https://smith.langchain.com/ (for monitoring)

### Community Resources

1. **Discord**: LangChain Discord community
2. **Twitter**: @LangChainAI
3. **YouTube**: LangChain official channel
4. **Blog**: https://blog.langchain.dev/

### Troubleshooting Common Issues

#### 1. Import Errors

- Use specific imports: `from langchain_openai import ChatOpenAI`
- Avoid deprecated imports: `from langchain.llms import OpenAI`

#### 2. Memory Issues

- Use session IDs for conversation management
- Clear memory when needed: `store.clear()`

#### 3. API Rate Limits

- Implement retry logic
- Use async operations for better performance
- Consider using different models for different tasks

### Next Steps for Your Project

1. **Execute the updated memory demo** to see conversation history in action
2. **Experiment with different memory types** (Buffer, Window, Summary)
3. **Add output parsing** to structure responses
4. **Implement RAG** for document-based Q&A
5. **Create custom tools** for specific use cases

This guide provides a solid foundation for mastering LangChain. Start with the basics and gradually work your way up to more advanced features.
