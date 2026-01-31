# AI & LLM Workshop

This project contains the code and docs for the AI & LLM workshop.

## Documentation

- [01-ai-intro.md](docs/01-ai-intro.md) — Introduction to AI
- [02-llm.md](docs/02-llm.md) — Large Language Models overview
- [03-vector-database.md](docs/03-vector-database.md) — Vector database concepts
- [04-RAG.md](docs/04-RAG.md) — Retrieval-Augmented Generation
- [05-gen-ai-RNN.md](docs/05-gen-ai-RNN.md) — Generative AI with RNNs
- [06-transformer.md](docs/06-transformer.md) — Transformer architecture
- [07-autonomous-ai-agents.md](docs/07-autonomous-ai-agents.md) — Autonomous agents
- [08-mcp-ai-integration.md](docs/08-mcp-ai-integration.md) — MCP & AI integration
- [09-agentic-ai.md](docs/09-agentic-ai.md) — Agentic AI concepts
- [10-llm-learning.md](docs/10-llm-learning.md) — LLM learning resources
- [langchain-in-memory.md](docs/langchain-in-memory.md) — LangChain in-memory patterns
- [langchain-window-memory-migration.md](docs/langchain-window-memory-migration.md) — Memory migration guide
- [python-servers-guide.md](docs/python-servers-guide.md) — Python servers guide

## Project Structure

```
.
├── README.md                    # Project README
├── docs/                        # Markdown docs and guides
├── src/                         # Example code & demos
│   └── ...
├── .env                         # Environment variables (not in git)
├── .gitignore
├── .pylintrc
└── .vscode/                     # VS Code settings
    └── settings.json
```

## Setup Instructions

### 1. Environment Setup

To make the project ready to run, first create a virtual environment. To activate it:

```bash
python -m venv venv
```

```bash
source .venv/bin/activate
```

### 2. Install Dependencies

Dependencies are already installed, but if you need to reinstall:

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Update the `.env` file with your actual API key:

```
REQUESTY_API_KEY=your_actual_api_key_here
```

### 4. Run the Demo

```bash
python <python_script.py>
```

## Code Quality

The code follows Python best practices:

- Snake_case naming convention
- Comprehensive docstrings
- Specific exception handling
- Environment variable validation
- Main function pattern

## Security Notes

- The `.env` file is excluded from version control
- API keys are never hardcoded in the source code
- Virtual environment isolates project dependencies
