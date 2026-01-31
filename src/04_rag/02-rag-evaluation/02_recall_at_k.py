#!/usr/bin/env python3
"""
Task 2: Recall@K
================

Recall@K measures: Of all relevant documents, how many did we find in top-K?

Formula:
    Recall@K = (Number of relevant docs in top-K) / (Total relevant docs)

Example:
    - Retrieved top-3: [doc1, doc2, doc3]
    - All relevant docs: [doc1, doc3, doc5] (3 total)
    - Found in top-3: doc1 [x], doc3 [x] = 2
    - Recall@3 = 2/3 = 0.667
"""

from rag_setup import setup_rag_pipeline, retrieve_documents
from ground_truth import get_relevant_docs

print("=" * 60)
print("Task 2: Recall@K")
print("=" * 60)

# ============================================================================
# SECTION 1: SETUP RAG PIPELINE
# ============================================================================

model, collection, chunks = setup_rag_pipeline("recall_eval")

# ============================================================================
# SECTION 3: IMPLEMENT RECALL@K
# ============================================================================

def recall_at_k(retrieved_docs: list, relevant_docs: list, k: int) -> float:
    """
    Calculate Recall@K.
    
    Args:
        retrieved_docs: List of retrieved document IDs (in order)
        relevant_docs: List of relevant document IDs (ground truth)
        k: Number of top results to consider
    
    Returns:
        Recall score between 0.0 and 1.0
    """
    if not relevant_docs:
        return 0.0
    
    # Get top-K retrieved documents
    top_k = retrieved_docs[:k]
    
    # Convert relevant docs to set for fast lookup
    relevant_set = set(relevant_docs)
    
    # TODO 1: Count how many relevant docs were found in top-K
    # Hint: Loop through top_k and count docs that are in relevant_set
    found_count = sum(1 for doc in top_k if doc in relevant_set)  # <-- Replace None with: sum(1 for doc in top_k if doc in relevant_set)
    if found_count is None:
        raise ValueError("[X] TODO 1: Replace None with the count of relevant docs found in top_k")
    
    # TODO 2: Calculate recall (found_count divided by total relevant docs)
    # Hint: Recall = found_count / total_relevant_docs
    recall = found_count / len(relevant_docs)  # <-- Replace None with: found_count / len(relevant_docs)
    if recall is None:
        raise ValueError("[X] TODO 2: Replace None with found_count / len(relevant_docs)")
    
    return recall


# ============================================================================
# SECTION 4: REAL RAG EVALUATION
# ============================================================================

print("\n" + "=" * 60)
print("Evaluating Real RAG Queries")
print("=" * 60)

test_queries = [
    "What's the reimbursement policy for home office equipment?",
    "Can I get money back for buying a desk?",
]

K = 2

for query in test_queries:
    print(f"\nQuery: \"{query}\"")
    
    retrieved = retrieve_documents(query, model, collection, k=5)
    relevant = get_relevant_docs(query)
    
    print(f"   Retrieved: {retrieved[:K]}")
    print(f"   Relevant:  {relevant} ({len(relevant)} total)")
    
    recall = recall_at_k(retrieved, relevant, K)
    print(f"   Recall@{K} = {recall:.3f}")

# ============================================================================
# COMPLETION
# ============================================================================

print("\n" + "=" * 60)
print("[OK] Task 2 Complete: Recall@K")
print("=" * 60)

with open("/tmp/rag_eval_recall_at_k_complete.txt", "w") as f:
    f.write("RECALL_AT_K_COMPLETE")

print("\nKey Takeaway:")
print("   Recall@K tells you how much COVERAGE you have.")
print("   High recall = Found most relevant documents")
print("   Low recall = Missed important documents")
