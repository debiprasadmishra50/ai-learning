#!/usr/bin/env python3
"""
Task 4: Normalized Discounted Cumulative Gain (NDCG)
====================================================

NDCG measures: How good is the overall ranking quality?

It rewards:
  - Relevant documents appearing earlier
  - Penalizes relevant documents appearing later

Formula:
    DCG@K = Σ (relevance_i / log2(i + 1)) for i = 1 to K
    IDCG@K = DCG of ideal ranking (all relevant docs first)
    NDCG@K = DCG@K / IDCG@K
"""

import math
from rag_setup import setup_rag_pipeline, retrieve_documents
from ground_truth import get_relevant_docs

print("=" * 60)
print("Task 4: Normalized Discounted Cumulative Gain (NDCG)")
print("=" * 60)

# ============================================================================
# SECTION 1: SETUP RAG PIPELINE
# ============================================================================

model, collection, chunks = setup_rag_pipeline("ndcg_eval")

# ============================================================================
# SECTION 3: IMPLEMENT NDCG
# ============================================================================

def ndcg_at_k(retrieved_docs: list, relevant_docs: list, k: int) -> float:
    """
    Calculate NDCG@K (Normalized Discounted Cumulative Gain).
    
    Args:
        retrieved_docs: List of retrieved document IDs (in order)
        relevant_docs: List of relevant document IDs (ground truth)
        k: Number of top results to consider
    
    Returns:
        NDCG score between 0.0 and 1.0
    """
    if k <= 0 or not relevant_docs:
        return 0.0
    
    # Get top-K retrieved documents
    top_k = retrieved_docs[:k]
    relevant_set = set(relevant_docs)
    
    # TODO 1: Calculate DCG (Discounted Cumulative Gain)
    # Hint: For each relevant doc at position i, add 1/log2(i+2)
    dcg = sum(1/math.log2(i+2) for i, doc in enumerate(top_k) if doc in relevant_set)
    if dcg is None:
        raise ValueError("[X] TODO 1: Replace None with the DCG calculation")
    
    # TODO 2: Calculate IDCG (Ideal DCG) - best possible DCG
    # Hint: Imagine all relevant docs are at the top positions
    idcg = sum(1/math.log2(i+2) for i in range(min(len(relevant_docs), k)))
    if idcg is None:
        raise ValueError("[X] TODO 2: Replace None with the IDCG calculation")
    
    # Avoid division by zero
    if idcg == 0:
        return 0.0
    
    # NDCG = DCG / IDCG
    return dcg / idcg


# ============================================================================
# SECTION 4: REAL RAG EVALUATION
# ============================================================================

print("\n" + "=" * 60)
print("Evaluating Real RAG Queries")
print("=" * 60)

test_queries = [
    "Can I get money back for buying a desk?",
    "What's the travel expense policy?",
]

K = 3

for query in test_queries:
    print(f"\nQuery: \"{query}\"")
    
    retrieved = retrieve_documents(query, model, collection, k=5)
    relevant = get_relevant_docs(query)
    
    print(f"   Retrieved: {retrieved[:K]}")
    print(f"   Relevant:  {relevant}")
    
    ndcg = ndcg_at_k(retrieved, relevant, K)
    print(f"   NDCG@{K} = {ndcg:.3f}")

# ============================================================================
# COMPLETION
# ============================================================================

print("\n" + "=" * 60)
print("[OK] Task 4 Complete: NDCG")
print("=" * 60)

with open("/tmp/rag_eval_ndcg_complete.txt", "w") as f:
    f.write("NDCG_COMPLETE")

print("\nKey Takeaway:")
print("   NDCG measures OVERALL RANKING QUALITY.")
print("   NDCG = 1.0 → Perfect ranking (all relevant docs at top)")
print("   NDCG < 1.0 → Some relevant docs are ranked too low")
print("   Best for: When the ORDER of results matters")
