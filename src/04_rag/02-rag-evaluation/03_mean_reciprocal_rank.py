#!/usr/bin/env python3
"""
Task 3: Mean Reciprocal Rank (MRR)
==================================

MRR measures: How high does the first relevant document appear in the ranking?

Formula:
    MRR = 1 / (position of first relevant document)

Example:
    - Retrieved: [doc2, doc1, doc3, doc4, doc5]
    - Relevant: [doc1, doc3]
    - First relevant (doc1) is at position 2
    - MRR = 1/2 = 0.500
"""

from rag_setup import setup_rag_pipeline, retrieve_documents
from ground_truth import get_relevant_docs

print("=" * 60)
print("Task 3: Mean Reciprocal Rank (MRR)")
print("=" * 60)

# ============================================================================
# SECTION 1: SETUP RAG PIPELINE
# ============================================================================

model, collection, chunks = setup_rag_pipeline("mrr_eval")

# ============================================================================
# SECTION 3: IMPLEMENT MRR
# ============================================================================

def mean_reciprocal_rank(retrieved_docs: list, relevant_docs: list) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR).
    
    Args:
        retrieved_docs: List of retrieved document IDs (in order)
        relevant_docs: List of relevant document IDs (ground truth)
    
    Returns:
        MRR score between 0.0 and 1.0
    """
    # Convert relevant docs to set for fast lookup
    relevant_set = set(relevant_docs)
    
    # Find the position of the first relevant document
    for idx, doc in enumerate(retrieved_docs):
        if doc in relevant_set:
            position = idx + 1  # Position is 1-indexed
            break
    else:
        return 0.0  # No relevant document found
    
    # TODO 1: Store the first relevant position
    # Hint: Use the position variable from the loop above
    first_relevant_position = position  # <-- Replace None with: position
    if first_relevant_position is None:
        raise ValueError("[X] TODO 1: Replace None with position")
    
    # TODO 2: Calculate MRR (1 divided by position)
    # Hint: MRR = 1 / position
    mrr = 1 / first_relevant_position  # <-- Replace None with: 1 / first_relevant_position
    if mrr is None:
        raise ValueError("[X] TODO 2: Replace None with 1 / first_relevant_position")
    
    return mrr


# ============================================================================
# SECTION 4: REAL RAG EVALUATION
# ============================================================================

print("\n" + "=" * 60)
print("Evaluating Real RAG Queries")
print("=" * 60)

test_queries = [
    "What's the travel expense policy?",
    "How many vacation days do I get?",
]

for query in test_queries:
    print(f"\nQuery: \"{query}\"")
    
    retrieved = retrieve_documents(query, model, collection, k=5)
    relevant = get_relevant_docs(query)
    
    print(f"   Retrieved: {retrieved}")
    print(f"   Relevant:  {relevant}")
    
    mrr = mean_reciprocal_rank(retrieved, relevant)
    for i, doc in enumerate(retrieved):
        if doc in relevant:
            print(f"   First relevant at position: {i+1}")
            break
    print(f"   MRR = {mrr:.3f}")

# ============================================================================
# COMPLETION
# ============================================================================

print("\n" + "=" * 60)
print("[OK] Task 3 Complete: Mean Reciprocal Rank (MRR)")
print("=" * 60)

with open("/tmp/rag_eval_mrr_complete.txt", "w") as f:
    f.write("MRR_COMPLETE")

print("\nKey Takeaway:")
print("   MRR tells you how QUICKLY you find the first relevant result.")
print("   High MRR = First relevant doc is near the top")
print("   Low MRR = First relevant doc is buried deep")
print("   Best for: Q&A systems where only one answer is needed")
