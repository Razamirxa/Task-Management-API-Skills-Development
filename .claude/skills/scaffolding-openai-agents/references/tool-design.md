# Tool Design Best Practices for OpenAI Agents

## Tool Naming

### Good Names
- `search_web` - Clear, verb + noun
- `get_user_profile` - Specific action
- `calculate_total` - Describes output

### Bad Names
- `process` - Too vague
- `doThing` - Not descriptive
- `helper` - Meaningless

## Description Writing

The description is crucial - it's how the LLM decides when to use the tool.

### Good Description
```python
{
    "name": "search_database",
    "description": "Search the product database for items matching the query. Returns product names, prices, and availability. Use this when the user asks about products, inventory, or prices.",
}
```

### Bad Description
```python
{
    "name": "search_database",
    "description": "Searches the database",  # Too vague
}
```

## Parameter Design

### Include Defaults
```python
"parameters": {
    "type": "object",
    "properties": {
        "limit": {
            "type": "integer",
            "description": "Maximum results to return",
            "default": 10
        }
    }
}
```

### Use Enums for Limited Options
```python
"sort_order": {
    "type": "string",
    "enum": ["asc", "desc"],
    "description": "Sort order: ascending or descending"
}
```

### Provide Examples in Description
```python
"date": {
    "type": "string",
    "description": "Date in ISO format, e.g., '2024-01-15'"
}
```

## Tool Categories

### 1. Information Retrieval
```python
# Search, query, get, fetch, lookup
{
    "name": "search_knowledge_base",
    "description": "Search internal documentation for answers",
}
```

### 2. Actions/Mutations
```python
# Create, update, delete, send, execute
{
    "name": "send_notification",
    "description": "Send a notification to a user. Requires confirmation for bulk sends.",
}
```

### 3. Calculations
```python
# Calculate, compute, analyze
{
    "name": "calculate_shipping",
    "description": "Calculate shipping cost based on destination and weight",
}
```

### 4. External APIs
```python
# Wrap external service calls
{
    "name": "get_weather",
    "description": "Get current weather from OpenWeatherMap API",
}
```

## Safety Patterns

### Confirmation for Destructive Actions
```python
def delete_user(user_id: str, confirm: bool = False) -> str:
    if not confirm:
        return "Please confirm deletion by calling again with confirm=True"
    # Proceed with deletion
```

### Rate Limiting
```python
from functools import wraps
import time

def rate_limit(calls_per_minute: int):
    min_interval = 60.0 / calls_per_minute
    last_call = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            last_call[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(calls_per_minute=10)
def search_api(query: str) -> str:
    # API call
    pass
```

### Input Validation
```python
def query_database(sql: str) -> str:
    # Only allow SELECT queries
    if not sql.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed"

    # Additional validation
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]
    if any(word in sql.upper() for word in forbidden):
        return "Error: Query contains forbidden keywords"

    # Execute query
    pass
```

## Tool Composition

### Wrapper Tools
```python
def comprehensive_search(query: str) -> str:
    """Combines multiple search sources."""
    results = []

    # Search multiple sources
    web_results = search_web(query)
    db_results = search_database(query)
    doc_results = search_docs(query)

    return json.dumps({
        "web": web_results,
        "database": db_results,
        "documentation": doc_results
    })
```

### Tool Chains
```python
def analyze_and_summarize(document_id: str) -> str:
    """Fetch document, analyze it, and provide summary."""
    # Step 1: Fetch
    document = fetch_document(document_id)

    # Step 2: Analyze
    analysis = analyze_sentiment(document)

    # Step 3: Summarize
    summary = generate_summary(document)

    return json.dumps({
        "summary": summary,
        "sentiment": analysis,
        "word_count": len(document.split())
    })
```

## Testing Tools

```python
import pytest

def test_search_tool_returns_results():
    result = search_database("test query")
    assert isinstance(result, str)
    data = json.loads(result)
    assert "results" in data

def test_search_tool_handles_empty_query():
    result = search_database("")
    data = json.loads(result)
    assert "error" in data or len(data.get("results", [])) == 0

def test_delete_tool_requires_confirmation():
    result = delete_item("item_123")
    assert "confirm" in result.lower()

def test_delete_tool_works_with_confirmation():
    result = delete_item("item_123", confirm=True)
    assert "deleted" in result.lower() or "success" in result.lower()
```

## Monitoring and Logging

```python
import logging
from functools import wraps

logger = logging.getLogger("agent_tools")

def log_tool_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Tool called: {func.__name__}, args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Tool result: {func.__name__} -> {result[:200]}...")
            return result
        except Exception as e:
            logger.error(f"Tool error: {func.__name__} -> {str(e)}")
            raise
    return wrapper

@log_tool_call
def search_database(query: str) -> str:
    # Implementation
    pass
```
