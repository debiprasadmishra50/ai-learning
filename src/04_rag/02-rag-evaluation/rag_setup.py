#!/usr/bin/env python3
"""
RAG Setup - Shared Module
=========================

This module contains shared components used across all evaluation tasks:
- Policy documents (single source of truth)
- RAG pipeline setup function
- Document retrieval function

Import this module in your task files to avoid code duplication.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ============================================================================
# POLICY DOCUMENTS - Single Source of Truth
# ============================================================================

POLICY_DOCUMENTS = [
    {
        "id": "policy_001",
        "title": "Home Office Equipment Reimbursement",
        "content": "Employees working from home may claim up to $500 per year for office equipment including desks, chairs, monitors, and computer accessories. Receipts must be submitted within 30 days of purchase. This policy applies to full-time remote workers only. The equipment must be used primarily for work purposes and should be ergonomic and suitable for a professional home office environment.",
        "category": "reimbursement"
    },
    {
        "id": "policy_002", 
        "title": "Travel Expense Guidelines",
        "content": "Business travel expenses are reimbursable when pre-approved by your manager. Meals are covered up to $50 per day, hotel stays up to $200 per night. All receipts must be submitted within 14 days of return. International travel requires additional approval from the department head. Travel insurance is mandatory for all business trips exceeding 7 days.",
        "category": "travel"
    },
    {
        "id": "policy_003",
        "title": "Remote Work Furniture Policy", 
        "content": "Remote employees may purchase ergonomic furniture for their home office setup. This includes standing desks, ergonomic chairs, and monitor arms. Maximum reimbursement is $300 per item with manager approval required. All furniture must meet ergonomic standards and be purchased from approved vendors. Receipts must be submitted within 45 days of purchase.",
        "category": "reimbursement"
    },
    {
        "id": "policy_004",
        "title": "Equipment and Supplies Reimbursement",
        "content": "Work-related equipment and supplies purchased for home office use are eligible for reimbursement. This covers laptops, monitors, keyboards, mice, and other computer peripherals. Submit expense reports with receipts for approval. Equipment must be used for work purposes and should be compatible with company systems. Annual limit is $1000 per employee.",
        "category": "reimbursement"
    },
    {
        "id": "policy_005",
        "title": "Vacation and PTO Policy",
        "content": "Full-time employees accrue 15 days of paid time off per year. Vacation requests must be submitted at least 2 weeks in advance. Unused PTO does not roll over to the next year. Emergency leave can be taken with manager approval. Sick leave is separate from vacation time and does not count against PTO balance.",
        "category": "benefits"
    }
]

# ============================================================================
# CONFIGURATION
# ============================================================================

CHUNK_SIZE = 200
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'


# ============================================================================
# RAG PIPELINE SETUP
# ============================================================================

def setup_rag_pipeline(collection_name="rag_eval_collection"):
    """
    Set up the complete RAG pipeline.
    
    Returns:
        tuple: (model, collection, chunks) - embedding model, ChromaDB collection, and chunks list
    """
    print("Setting up RAG Pipeline...")
    
    # Step 1: Load embedding model FIRST
    print("  Loading embedding model...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print(f"  [OK] Loaded embedding model: {EMBEDDING_MODEL}")
    
    # Step 2: Chunk documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    all_chunks = []
    for doc in POLICY_DOCUMENTS:
        chunks = text_splitter.split_text(doc["content"])
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "id": f"{doc['id']}_chunk_{i}",
                "title": doc["title"],
                "content": chunk,
                "category": doc["category"],
                "source_doc": doc["id"]
            })
    
    print(f"  [OK] Created {len(all_chunks)} chunks from {len(POLICY_DOCUMENTS)} documents")
    
    # Step 3: Set up vector database
    client = chromadb.Client()
    try:
        collection = client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    except:
        client.delete_collection(collection_name)
        collection = client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    # Step 4: Store chunks with embeddings
    ids = [chunk["id"] for chunk in all_chunks]
    documents = [chunk["content"] for chunk in all_chunks]
    metadatas = [{"title": chunk["title"], "category": chunk["category"], "source": chunk["source_doc"]} for chunk in all_chunks]
    
    # Generate embeddings
    embeddings = model.encode(documents).tolist()
    
    collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    print(f"  [OK] Stored {len(all_chunks)} chunks in vector database")
    
    print("  [OK] RAG Pipeline ready!\n")
    
    return model, collection, all_chunks


# ============================================================================
# DOCUMENT RETRIEVAL
# ============================================================================

def retrieve_documents(query, model, collection, k=5):
    """
    Retrieve top-K documents for a query.
    
    Args:
        query: Search query string
        model: SentenceTransformer model
        collection: ChromaDB collection
        k: Number of results to return
    
    Returns:
        list: List of source document IDs (deduplicated, in order)
    """
    query_embedding = model.encode(query.lower().strip())
    
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=k
    )
    
    # Extract unique source document IDs in order of retrieval
    retrieved_sources = []
    seen = set()
    for metadata in results['metadatas'][0]:
        source = metadata['source']
        if source not in seen:
            retrieved_sources.append(source)
            seen.add(source)
    
    return retrieved_sources


# ============================================================================
# DEMO / TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("RAG Setup Module - Test")
    print("=" * 60)
    
    # Test setup
    model, collection, chunks = setup_rag_pipeline("test_collection")
    
    # Test retrieval
    test_query = "home office equipment reimbursement"
    results = retrieve_documents(test_query, model, collection, k=3)
    
    print(f"Test Query: \"{test_query}\"")
    print(f"Retrieved: {results}")
    print("\n[OK] RAG Setup module working correctly!")
