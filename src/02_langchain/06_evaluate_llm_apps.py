"""
LangChain: Evaluation (Updated for LangChain 1.2.7)

Outline:
* Example generation
* Manual evaluation (and debugging)
* LLM-assisted evaluation
* Chain evaluation
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_core.globals import set_debug, set_verbose

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
    print(f"[-] Warning: Could not initialize OpenAI client: {e}")
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

# ✅ Define a prompt template
qa_prompt = ChatPromptTemplate.from_template(
    """Answer the question based only on the following context:
    Context: {context}
    Question: {question}
    Provide your answer in markdown format."""
)


# ✅ Format docs function
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# ✅ Create the LCEL QA chain
qa_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | qa_prompt
    | llm
    | StrOutputParser()
)

print("[+] QA system created successfully\n")


##########################################################################
# HARD-CODED Examples
##########################################################################
print(separator(80))
print("[+] CREATING EVALUATION EXAMPLES")
print(separator(80))

examples = [
    {
        "query": "Do the Cozy Comfort Pullover Set have side pockets?",
        "answer": "Yes",
    },
    {
        "query": "What collection is the Ultra-Lofty 850 Stretch Down Hooded Jacket from?",
        "answer": "The DownTek collection",
    },
]

print(f"[+] Hard-coded examples: {len(examples)}")


##########################################################################
# LLM Generated QA testing of LLM Chain
# from langsmith import datasets, evaluate
##########################################################################

print("\n[+] Generating examples using LLM...\n")

# ✅ Create example generation chain
example_gen_prompt = ChatPromptTemplate.from_template(
    """Based on the following document, generate a question and answer pair.

Document:
{doc}

Generate a JSON object with 'query' and 'answer' fields.
Example format: {{"query": "What color is the product?", "answer": "Blue"}}
Only output valid JSON, nothing else."""
)

example_gen_chain = example_gen_prompt | llm | StrOutputParser()

# ✅ Generate examples from first 5 documents
new_examples = []
for i, doc in enumerate(docs[:5]):
    try:
        result = example_gen_chain.invoke({"doc": doc.page_content})
        # Try to parse as JSON
        import json

        # Remove any markdown formatting
        result = result.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(result)
        new_examples.append(
            {"query": parsed.get("query", ""), "answer": parsed.get("answer", "")}
        )
        print(f"[+] Generated example {i + 1}:")
        print(f"[+]   Q: {parsed.get('query', '')[:80]}...")
        print(f"[+]   A: {parsed.get('answer', '')[:80]}...")
    except Exception as e:
        print(f"[+] Failed to generate example {i + 1}: {e}")
        continue

print(f"\n[+] Generated {len(new_examples)} new examples")

# ✅ Combine examples
examples += new_examples
print(f"[+] Total examples: {len(examples)}\n")

# ============================================================================
# TEST THE QA SYSTEM
# ============================================================================

print(separator(80))
print("[+] TESTING QA SYSTEM")
print(separator(80))

if examples:
    test_query = examples[0]["query"]
    print(f"[+] Test Query: {test_query}")
    result = qa_chain.invoke(test_query)
    print(f"[+] Answer: {result}\n")

# ============================================================================
# MANUAL EVALUATION WITH DEBUG MODE
# ============================================================================

print(separator(80))
print("[+] MANUAL EVALUATION (DEBUG MODE)")
print(separator(80))

# In LangChain 1.2.7, we use set_debug instead of langchain.debug
# from langchain_core.globals import set_debug, set_verbose

print("[+] Running with debug mode ON...")
set_debug(True)
set_verbose(True)

if examples:
    result = qa_chain.invoke(examples[0]["query"])
    print(f"\n[+] Debug result: {result}\n")

# Turn off debug mode
set_debug(False)
set_verbose(False)
print("[+] Debug mode turned OFF\n")


# ============================================================================
# GENERATE PREDICTIONS FOR ALL EXAMPLES
# ============================================================================

print(separator(80))
print("[+] GENERATING PREDICTIONS FOR ALL EXAMPLES")
print(separator(80))

predictions = []
for i, example in enumerate(examples):
    try:
        result = qa_chain.invoke(example["query"])
        predictions.append(
            {"query": example["query"], "answer": example["answer"], "result": result}
        )
        print(f"[+] Prediction {i + 1}/{len(examples)} complete")
    except Exception as e:
        print(f"[+] Error generating prediction {i + 1}: {e}")
        predictions.append(
            {
                "query": example["query"],
                "answer": example["answer"],
                "result": f"Error: {str(e)}",
            }
        )

print(f"\n[+] Generated {len(predictions)} predictions\n")


# ============================================================================
# LLM-ASSISTED EVALUATION
# ============================================================================

print(separator(80))
print("[+] LLM-ASSISTED EVALUATION")
print(separator(80))


# Create evaluation chain
eval_prompt = ChatPromptTemplate.from_template("""You are a teacher grading a quiz.
You are given a question, the student's answer, and the correct answer.
Grade the student's answer as either CORRECT or INCORRECT.

Question: {query}
Student's Answer: {result}
Correct Answer: {answer}

Provide your grade (CORRECT or INCORRECT) and a brief explanation.
Format: GRADE: [CORRECT/INCORRECT] - Explanation here""")

eval_chain = eval_prompt | llm | StrOutputParser()

# Evaluate all predictions
graded_outputs = []
for i, pred in enumerate(predictions):
    try:
        grade = eval_chain.invoke(
            {"query": pred["query"], "result": pred["result"], "answer": pred["answer"]}
        )
        graded_outputs.append({"text": grade})
        print(f"[+] Graded {i + 1}/{len(predictions)}")
    except Exception as e:
        graded_outputs.append({"text": f"Error: {str(e)}"})
        print(f"[-] Error grading {i + 1}: {e}")

print(separator(80))
print("EVALUATION RESULTS")
print(separator(80))

# Display results
for i, eg in enumerate(examples[: len(predictions)]):
    print(f"[+] Example {i + 1}:")
    print(f"[+] Question: {predictions[i]['query']}")
    print(f"[+] Expected Answer: {predictions[i]['answer']}")
    print(f"[+] Predicted Answer: {predictions[i]['result']}")
    print(f"[+] Grade: {graded_outputs[i]['text']}")
    print("-" * 80)
    print()


# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print(separator(80))
print("SUMMARY STATISTICS")
print(separator(80))

correct_count = sum(
    1
    for grade in graded_outputs
    if "CORRECT" in grade["text"] and "INCORRECT" not in grade["text"]
)
total_count = len(graded_outputs)
accuracy = (correct_count / total_count * 100) if total_count > 0 else 0

print(f"[+] Total Examples: {total_count}")
print(f"[+] Correct: {correct_count}")
print(f"[+] Incorrect: {total_count - correct_count}")
print(f"[+] Accuracy: {accuracy:.1f}%")

print(separator(80))
print("[+] EVALUATION COMPLETE")
print(separator(80))
