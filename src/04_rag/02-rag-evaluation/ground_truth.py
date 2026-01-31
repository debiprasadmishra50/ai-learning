#!/usr/bin/env python3
"""
Ground Truth Dataset for RAG Evaluation
========================================

This file defines the ground truth data for evaluating RAG retrieval quality.
Each query is mapped to a list of document IDs that are considered relevant.

The policy documents used:
- policy_001: Home Office Equipment Reimbursement
- policy_002: Travel Expense Guidelines
- policy_003: Remote Work Furniture Policy
- policy_004: Equipment and Supplies Reimbursement
- policy_005: Vacation and PTO Policy
"""

# Ground truth mapping: query -> list of relevant document IDs
# These are the "correct answers" for each query
GROUND_TRUTH = {
    # Query 1: Should match home office equipment policies
    "What's the reimbursement policy for home office equipment?": [
        "policy_001",  # Home Office Equipment Reimbursement - PRIMARY
        "policy_003",  # Remote Work Furniture Policy - RELATED
        "policy_004",  # Equipment and Supplies Reimbursement - RELATED
    ],
    
    # Query 2: Should match desk/furniture policies
    "Can I get money back for buying a desk?": [
        "policy_003",  # Remote Work Furniture Policy - PRIMARY (standing desks)
        "policy_001",  # Home Office Equipment Reimbursement - RELATED (desks mentioned)
    ],
    
    # Query 3: Should match home office claim limits
    "How much can I claim for my home office?": [
        "policy_001",  # Home Office Equipment Reimbursement - $500/year
        "policy_003",  # Remote Work Furniture Policy - $300/item
        "policy_004",  # Equipment and Supplies Reimbursement - $1000/year
    ],
    
    # Query 4: Should match travel policy only
    "What's the travel expense policy?": [
        "policy_002",  # Travel Expense Guidelines - PRIMARY
    ],
    
    # Query 5: Should match vacation/PTO policy only
    "How many vacation days do I get?": [
        "policy_005",  # Vacation and PTO Policy - PRIMARY
    ],
    
    # Query 6: Should match equipment policies
    "What computer equipment can I expense?": [
        "policy_004",  # Equipment and Supplies Reimbursement - PRIMARY
        "policy_001",  # Home Office Equipment Reimbursement - RELATED
    ],
}

# Test queries list for easy iteration
TEST_QUERIES = list(GROUND_TRUTH.keys())

def get_relevant_docs(query: str) -> list:
    """
    Get the list of relevant document IDs for a given query.
    
    Args:
        query: The search query
        
    Returns:
        List of relevant document IDs, or empty list if query not found
    """
    return GROUND_TRUTH.get(query, [])

def get_all_queries() -> list:
    """
    Get all test queries.
    
    Returns:
        List of all test query strings
    """
    return TEST_QUERIES

def print_ground_truth():
    """Print the ground truth dataset in a readable format."""
    print("Ground Truth Dataset for RAG Evaluation")
    print("=" * 60)
    print()
    
    for i, (query, relevant_docs) in enumerate(GROUND_TRUTH.items(), 1):
        print(f"Query {i}: \"{query}\"")
        print(f"  Relevant Documents ({len(relevant_docs)}):")
        for doc_id in relevant_docs:
            print(f"    - {doc_id}")
        print()
    
    print("=" * 60)
    print(f"Total: {len(GROUND_TRUTH)} queries with ground truth labels")

if __name__ == "__main__":
    print_ground_truth()
