---
name: building-rag-systems
description: Build Retrieval Augmented Generation (RAG) systems for AI applications. Use when creating document Q&A systems, knowledge bases, semantic search, or any application combining retrieval with LLM generation. Triggers include "RAG", "vector database", "embeddings", "document chunking", "semantic search", or "knowledge base".
---

# Building RAG Systems Skill

Build production-ready Retrieval Augmented Generation (RAG) pipelines.

## RAG Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG Pipeline                              │
├─────────────────────────────────────────────────────────────┤
│  1. INGESTION                                                │
│     Documents → Chunking → Embeddings → Vector Store         │
├─────────────────────────────────────────────────────────────┤
│  2. RETRIEVAL                                                │
│     Query → Embed Query → Similarity Search → Top-K Chunks   │
├─────────────────────────────────────────────────────────────┤
│  3. GENERATION                                               │
│     Query + Retrieved Context → LLM → Response               │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
pip install openai chromadb langchain tiktoken
# For PDF processing:
pip install pypdf
# For web scraping:
pip install beautifulsoup4 requests
```

### Minimal RAG Implementation

```python
import os
from openai import OpenAI
import chromadb

client = OpenAI()
chroma = chromadb.Client()
collection = chroma.create_collection("docs")

# 1. Ingest documents
def add_document(text: str, doc_id: str):
    # Get embedding
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    embedding = response.data[0].embedding

    # Store in vector DB
    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[doc_id]
    )

# 2. Query
def query_rag(question: str, top_k: int = 3) -> str:
    # Embed query
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=question
    )
    query_embedding = response.data[0].embedding

    # Retrieve similar chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # Build context
    context = "\n\n".join(results["documents"][0])

    # Generate response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Answer based on this context:\n\n{context}"},
            {"role": "user", "content": question}
        ]
    )

    return response.choices[0].message.content
```

## Document Chunking Strategies

### Fixed Size Chunking

```python
def chunk_fixed_size(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into fixed-size chunks with overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks
```

### Semantic Chunking (Recommended)

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_semantic(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """Split text semantically at sentence/paragraph boundaries."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_text(text)
```

### Markdown/Code Aware Chunking

```python
from langchain.text_splitter import MarkdownTextSplitter, Language, RecursiveCharacterTextSplitter

# For Markdown
md_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = md_splitter.split_text(markdown_text)

# For Python code
code_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1000,
    chunk_overlap=200
)
chunks = code_splitter.split_text(python_code)
```

## Embedding Models

### OpenAI Embeddings

```python
from openai import OpenAI

client = OpenAI()

def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """Get embedding for text using OpenAI."""
    response = client.embeddings.create(
        model=model,  # or "text-embedding-3-large" for better quality
        input=text
    )
    return response.data[0].embedding

# Batch embeddings (more efficient)
def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]
```

### Local Embeddings (sentence-transformers)

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_local_embedding(text: str) -> list[float]:
    return model.encode(text).tolist()

def get_local_embeddings_batch(texts: list[str]) -> list[list[float]]:
    return model.encode(texts).tolist()
```

## Vector Databases

### ChromaDB (Local/Simple)

```python
import chromadb

# Persistent storage
client = chromadb.PersistentClient(path="./chroma_db")

# Create collection
collection = client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}  # or "l2", "ip"
)

# Add documents
collection.add(
    documents=["doc1 text", "doc2 text"],
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    metadatas=[{"source": "file1.pdf"}, {"source": "file2.pdf"}],
    ids=["id1", "id2"]
)

# Query
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    where={"source": "file1.pdf"},  # Optional filter
    include=["documents", "metadatas", "distances"]
)
```

### Pinecone (Cloud/Production)

```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Create index
pc.create_index(
    name="documents",
    dimension=1536,  # Match your embedding model
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)

index = pc.Index("documents")

# Upsert vectors
index.upsert(vectors=[
    {"id": "id1", "values": embedding1, "metadata": {"source": "doc1"}},
    {"id": "id2", "values": embedding2, "metadata": {"source": "doc2"}},
])

# Query
results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True,
    filter={"source": {"$eq": "doc1"}}
)
```

### Weaviate (Hybrid Search)

```python
import weaviate

client = weaviate.Client("http://localhost:8080")

# Create class
client.schema.create_class({
    "class": "Document",
    "vectorizer": "none",  # We provide our own embeddings
    "properties": [
        {"name": "content", "dataType": ["text"]},
        {"name": "source", "dataType": ["string"]}
    ]
})

# Add documents
client.data_object.create(
    data_object={"content": "text", "source": "file.pdf"},
    class_name="Document",
    vector=embedding
)

# Hybrid search (vector + keyword)
results = client.query.get("Document", ["content", "source"]) \
    .with_hybrid(query="search term", alpha=0.5) \
    .with_limit(5) \
    .do()
```

## Retrieval Strategies

### Basic Similarity Search

```python
def retrieve_basic(query: str, top_k: int = 5):
    query_embedding = get_embedding(query)
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
```

### Hybrid Search (Vector + Keyword)

```python
from rank_bm25 import BM25Okapi

class HybridRetriever:
    def __init__(self, documents: list[str], embeddings: list[list[float]]):
        self.documents = documents
        self.embeddings = embeddings
        # BM25 for keyword search
        tokenized = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)

    def search(self, query: str, top_k: int = 5, alpha: float = 0.5):
        # Vector search scores
        query_emb = get_embedding(query)
        vector_scores = cosine_similarity([query_emb], self.embeddings)[0]

        # BM25 scores
        bm25_scores = self.bm25.get_scores(query.lower().split())

        # Normalize and combine
        vector_scores = (vector_scores - vector_scores.min()) / (vector_scores.max() - vector_scores.min())
        bm25_scores = (bm25_scores - bm25_scores.min()) / (bm25_scores.max() - bm25_scores.min() + 1e-6)

        combined = alpha * vector_scores + (1 - alpha) * bm25_scores

        # Get top-k
        top_indices = combined.argsort()[-top_k:][::-1]
        return [self.documents[i] for i in top_indices]
```

### Reranking

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def retrieve_with_rerank(query: str, initial_k: int = 20, final_k: int = 5):
    # Initial retrieval
    results = collection.query(query_embeddings=[get_embedding(query)], n_results=initial_k)
    candidates = results["documents"][0]

    # Rerank
    pairs = [(query, doc) for doc in candidates]
    scores = reranker.predict(pairs)

    # Get top after reranking
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in ranked[:final_k]]
```

## Generation with Context

### Basic RAG Prompt

```python
def generate_response(query: str, context: list[str]) -> str:
    context_str = "\n\n---\n\n".join(context)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""Answer the question based on the provided context.
If the context doesn't contain the answer, say "I don't have enough information."

Context:
{context_str}"""
            },
            {"role": "user", "content": query}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
```

### With Source Citations

```python
def generate_with_citations(query: str, chunks: list[dict]) -> str:
    # Format context with source markers
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(f"[{i+1}] {chunk['text']}\nSource: {chunk['source']}")

    context_str = "\n\n".join(context_parts)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""Answer based on the context. Cite sources using [1], [2], etc.

Context:
{context_str}"""
            },
            {"role": "user", "content": query}
        ]
    )

    return response.choices[0].message.content
```

## Complete RAG Pipeline

```python
import os
from openai import OpenAI
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter

class RAGPipeline:
    def __init__(self, collection_name: str = "documents"):
        self.client = OpenAI()
        self.chroma = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma.get_or_create_collection(collection_name)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def ingest(self, text: str, source: str):
        """Ingest a document into the RAG system."""
        chunks = self.splitter.split_text(text)

        for i, chunk in enumerate(chunks):
            embedding = self._get_embedding(chunk)
            self.collection.add(
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{"source": source, "chunk_index": i}],
                ids=[f"{source}_{i}"]
            )

    def query(self, question: str, top_k: int = 5) -> str:
        """Query the RAG system."""
        # Retrieve
        query_embedding = self._get_embedding(question)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas"]
        )

        # Generate
        context = "\n\n".join(results["documents"][0])
        sources = [m["source"] for m in results["metadatas"][0]]

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"Answer based on this context:\n\n{context}"
                },
                {"role": "user", "content": question}
            ]
        )

        answer = response.choices[0].message.content
        return f"{answer}\n\nSources: {', '.join(set(sources))}"

    def _get_embedding(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding


# Usage
rag = RAGPipeline()
rag.ingest("Your document text here...", source="document.pdf")
answer = rag.query("What is this document about?")
```

## Best Practices

1. **Chunk size matters** - 500-1000 tokens is usually optimal
2. **Overlap chunks** - 10-20% overlap prevents losing context at boundaries
3. **Metadata is key** - Store source, page number, section for citations
4. **Hybrid search** - Combine vector + keyword for better recall
5. **Reranking** - Improves precision on top results
6. **Test retrieval first** - Bad retrieval = bad RAG, regardless of LLM
7. **Evaluate** - Use metrics like recall@k, MRR, or human evaluation

## Common Pitfalls

- **Chunks too large** - Dilutes relevance, wastes context window
- **Chunks too small** - Loses context, fragments information
- **No overlap** - Important info at chunk boundaries gets lost
- **Ignoring metadata** - Can't filter or cite sources
- **Over-relying on LLM** - "I don't know" is better than hallucination

## References

- [references/chunking-strategies.md](references/chunking-strategies.md) - Detailed chunking guide
- [references/vector-databases.md](references/vector-databases.md) - Vector DB comparison
- [references/evaluation.md](references/evaluation.md) - RAG evaluation metrics
