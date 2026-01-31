#!/usr/bin/env python3
"""
Task 1: Precision@K
===================

Precision@K measures: Of the top-K documents retrieved, how many are relevant?

Formula:
    Precision@K = (Number of relevant docs in top-K) / K

"""

from rag_setup import setup_rag_pipeline, retrieve_documents
from ground_truth import get_relevant_docs

print("=" * 60)
print("Task 1: Precision@K")
print("=" * 60)

# ============================================================================
# SECTION 1: SETUP RAG PIPELINE
# ============================================================================

model, collection, chunks = setup_rag_pipeline("precision_eval")

# ============================================================================
# SECTION 3: IMPLEMENT PRECISION@K
# ============================================================================

def precision_at_k(retrieved_docs: list, relevant_docs: list, k: int) -> float:
    """
    Calculate Precision@K.
    
    Args:
        retrieved_docs: List of retrieved document IDs (in order)
        relevant_docs: List of relevant document IDs (ground truth)
        k: Number of top results to consider
    
    Returns:
        Precision score between 0.0 and 1.0
    """
    # Get top-K retrieved documents
    top_k = retrieved_docs[:k]
    
    # Convert relevant docs to set for fast lookup
    relevant_set = set(relevant_docs)
    
    # TODO 1: Count how many retrieved docs are relevant
    # Hint: Loop through top_k and count docs that are in relevant_set
    relevant_count = sum(1 for doc in top_k if doc in relevant_set)  # <-- Replace None with: sum(1 for doc in top_k if doc in relevant_set)
    if relevant_count is None:
        raise ValueError("[X] TODO 1: Replace None with the count of relevant docs in top_k")
    
    # TODO 2: Calculate precision (relevant_count divided by k)
    # Hint: Precision = relevant_count / k
    precision = relevant_count / k  # <-- Replace None with: relevant_count / k
    if precision is None:
        raise ValueError("[X] TODO 2: Replace None with relevant_count / k")
    
    return precision


# ============================================================================
# SECTION 4: REAL RAG EVALUATION
# ============================================================================

print("\n" + "=" * 60)
print("Evaluating Real RAG Queries")
print("=" * 60)

test_queries = [
    "What's the travel expense policy?",
    "Can I get money back for buying a desk?",
]

K = 3

for query in test_queries:
    print(f"\nQuery: \"{query}\"")
    
    retrieved = retrieve_documents(query, model, collection, k=5)
    relevant = get_relevant_docs(query)
    
    print(f"   Retrieved: {retrieved[:K]}")
    print(f"   Relevant:  {relevant}")
    
    precision = precision_at_k(retrieved, relevant, K)
    print(f"   Precision@{K} = {precision:.3f}")

# ============================================================================
# COMPLETION
# ============================================================================

print("\n" + "=" * 60)
print("[OK] Task 1 Complete: Precision@K")
print("=" * 60)

with open("/tmp/rag_eval_precision_at_k_complete.txt", "w") as f:
    f.write("PRECISION_AT_K_COMPLETE")

print("\nKey Takeaway:")
print("   Precision@K tells you how much NOISE is in your results.")
print("   High precision = Clean, relevant results")
print("   Low precision = Many irrelevant docs mixed in")
