# Document Chunking Strategies for RAG

Chunking is critical for RAG performance. This guide covers strategies for different document types.

## Chunk Size Guidelines

| Document Type | Recommended Size | Overlap |
|---------------|------------------|---------|
| General text | 500-1000 tokens | 10-20% |
| Technical docs | 800-1500 tokens | 15-25% |
| Code | 50-200 lines | 5-10 lines |
| Q&A/FAQ | Per question | None |
| Legal/contracts | By section | 20-30% |

## Strategy Selection

### 1. Fixed Size (Simple, Fast)

Best for: Homogeneous text, quick prototyping

```python
def chunk_fixed(text: str, size: int = 1000, overlap: int = 200) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
```

### 2. Recursive Character (Recommended Default)

Best for: General documents, respects natural boundaries

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function=len
)
chunks = splitter.split_text(text)
```

### 3. Semantic Chunking

Best for: Documents where meaning boundaries matter

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

chunker = SemanticChunker(
    OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=95
)
chunks = chunker.split_text(text)
```

### 4. Document-Aware Chunking

**Markdown:**
```python
from langchain.text_splitter import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]
splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
chunks = splitter.split_text(markdown_text)
```

**HTML:**
```python
from langchain.text_splitter import HTMLHeaderTextSplitter

headers_to_split_on = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
]
splitter = HTMLHeaderTextSplitter(headers_to_split_on)
chunks = splitter.split_text(html_text)
```

**Code:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language

python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1000,
    chunk_overlap=200
)

# Supports: PYTHON, JS, TS, GO, RUST, JAVA, CPP, C, CSHARP, etc.
```

### 5. Sentence-Based

Best for: When sentence integrity is critical

```python
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

def chunk_by_sentences(text: str, sentences_per_chunk: int = 5) -> list[str]:
    sentences = sent_tokenize(text)
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk = " ".join(sentences[i:i + sentences_per_chunk])
        chunks.append(chunk)
    return chunks
```

## Token Counting

Always count tokens, not characters:

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def chunk_by_tokens(text: str, max_tokens: int = 500, overlap_tokens: int = 50):
    encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    tokens = encoding.encode(text)

    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(encoding.decode(chunk_tokens))
        start = end - overlap_tokens

    return chunks
```

## Adding Context to Chunks

### Prepend Section Headers

```python
def chunk_with_context(document: dict) -> list[str]:
    """Add document context to each chunk."""
    chunks = []
    for section in document["sections"]:
        section_chunks = splitter.split_text(section["content"])
        for chunk in section_chunks:
            contextualized = f"Document: {document['title']}\nSection: {section['title']}\n\n{chunk}"
            chunks.append(contextualized)
    return chunks
```

### Summary Prefix

```python
def add_summary_to_chunks(chunks: list[str], client: OpenAI) -> list[str]:
    """Add a brief summary to each chunk for better retrieval."""
    enhanced = []
    for chunk in chunks:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Summarize this in one sentence:"},
                {"role": "user", "content": chunk}
            ]
        )
        summary = response.choices[0].message.content
        enhanced.append(f"Summary: {summary}\n\nContent: {chunk}")
    return enhanced
```

## Evaluation

Test your chunking strategy:

```python
def evaluate_chunking(chunks: list[str]) -> dict:
    lengths = [len(c) for c in chunks]
    return {
        "num_chunks": len(chunks),
        "avg_length": sum(lengths) / len(lengths),
        "min_length": min(lengths),
        "max_length": max(lengths),
        "std_dev": (sum((l - sum(lengths)/len(lengths))**2 for l in lengths) / len(lengths))**0.5
    }
```

Good chunking should have:
- Consistent chunk sizes (low std_dev)
- No extremely short chunks (< 100 chars)
- No extremely long chunks (> 2x target)
