---
name: scaffolding-openai-agents
description: Build AI agents with OpenAI's API. Use when creating tool-calling agents, multi-step reasoning systems, function calling implementations, or autonomous AI workflows. Triggers include "OpenAI agent", "function calling", "tool use", "agent loop", "autonomous agent", or "AI assistant with tools".
---

# Scaffolding OpenAI Agents Skill

Build production-ready AI agents with OpenAI's function calling and tool use capabilities.

## Agent Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    AGENT LOOP                             │
├──────────────────────────────────────────────────────────┤
│  1. User Input → LLM                                      │
│  2. LLM decides: respond OR call tool(s)                  │
│  3. If tool call → Execute tool → Return result to LLM    │
│  4. Repeat until LLM responds without tool calls          │
│  5. Return final response to user                         │
└──────────────────────────────────────────────────────────┘
```

## Quick Start

### Installation

```bash
pip install openai
```

### Minimal Agent with Tools

```python
import json
from openai import OpenAI

client = OpenAI()

# Define tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g., 'San Francisco'"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# Tool implementation
def get_weather(location: str) -> str:
    # In real app, call weather API
    return f"Weather in {location}: 72°F, sunny"

# Map function names to implementations
tool_functions = {
    "get_weather": get_weather
}

# Agent loop
def run_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )

        message = response.choices[0].message

        # If no tool calls, return response
        if not message.tool_calls:
            return message.content

        # Process tool calls
        messages.append(message)

        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            # Execute tool
            result = tool_functions[func_name](**func_args)

            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

# Usage
print(run_agent("What's the weather in Tokyo?"))
```

## Defining Tools

### Basic Tool Schema

```python
{
    "type": "function",
    "function": {
        "name": "function_name",
        "description": "Clear description of what this function does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "What this parameter is for"
                },
                "param2": {
                    "type": "integer",
                    "description": "Another parameter"
                }
            },
            "required": ["param1"]
        }
    }
}
```

### Supported Parameter Types

```python
# String
{"type": "string", "description": "A text value"}

# Number
{"type": "number", "description": "A decimal number"}

# Integer
{"type": "integer", "description": "A whole number"}

# Boolean
{"type": "boolean", "description": "True or false"}

# Array
{
    "type": "array",
    "items": {"type": "string"},
    "description": "A list of strings"
}

# Enum
{
    "type": "string",
    "enum": ["option1", "option2", "option3"],
    "description": "One of the allowed values"
}

# Object
{
    "type": "object",
    "properties": {
        "nested_field": {"type": "string"}
    }
}
```

### Real-World Tool Examples

```python
tools = [
    # Search tool
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information. Use for current events or facts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (1-10)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    # Database query tool
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Execute a read-only SQL query on the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    }
                },
                "required": ["query"]
            }
        }
    },
    # Send email tool
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email to a recipient",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        }
    }
]
```

## Agent Patterns

### 1. Simple ReAct Agent

```python
class SimpleAgent:
    def __init__(self, tools: list, tool_functions: dict):
        self.client = OpenAI()
        self.tools = tools
        self.tool_functions = tool_functions
        self.system_prompt = """You are a helpful assistant with access to tools.
Think step by step before acting. Use tools when needed."""

    def run(self, user_input: str, max_turns: int = 10) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]

        for _ in range(max_turns):
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools
            )

            message = response.choices[0].message

            if not message.tool_calls:
                return message.content

            messages.append(message)

            for tool_call in message.tool_calls:
                result = self._execute_tool(tool_call)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

        return "Max turns reached without final response"

    def _execute_tool(self, tool_call) -> str:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)

        if func_name not in self.tool_functions:
            return f"Error: Unknown function {func_name}"

        try:
            result = self.tool_functions[func_name](**func_args)
            return str(result)
        except Exception as e:
            return f"Error executing {func_name}: {str(e)}"
```

### 2. Conversational Agent with Memory

```python
class ConversationalAgent:
    def __init__(self, tools: list, tool_functions: dict):
        self.client = OpenAI()
        self.tools = tools
        self.tool_functions = tool_functions
        self.conversation_history = []
        self.system_prompt = "You are a helpful assistant. Remember our conversation."

    def chat(self, user_input: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_input})

        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.conversation_history
        ]

        while True:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools
            )

            message = response.choices[0].message

            if not message.tool_calls:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": message.content
                })
                return message.content

            messages.append(message)

            for tool_call in message.tool_calls:
                result = self._execute_tool(tool_call)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

    def _execute_tool(self, tool_call) -> str:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        return str(self.tool_functions[func_name](**func_args))

    def clear_history(self):
        self.conversation_history = []
```

### 3. Planning Agent

```python
class PlanningAgent:
    """Agent that creates a plan before executing."""

    def __init__(self, tools: list, tool_functions: dict):
        self.client = OpenAI()
        self.tools = tools
        self.tool_functions = tool_functions

    def run(self, task: str) -> str:
        # Step 1: Create plan
        plan = self._create_plan(task)
        print(f"Plan:\n{plan}\n")

        # Step 2: Execute plan
        return self._execute_plan(task, plan)

    def _create_plan(self, task: str) -> str:
        tool_descriptions = "\n".join(
            f"- {t['function']['name']}: {t['function']['description']}"
            for t in self.tools
        )

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""Create a step-by-step plan to accomplish the task.
Available tools:
{tool_descriptions}

Format each step as: Step N: [action]"""
                },
                {"role": "user", "content": task}
            ]
        )

        return response.choices[0].message.content

    def _execute_plan(self, task: str, plan: str) -> str:
        messages = [
            {
                "role": "system",
                "content": f"Execute this plan step by step:\n{plan}\n\nUse tools as needed."
            },
            {"role": "user", "content": task}
        ]

        while True:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools
            )

            message = response.choices[0].message

            if not message.tool_calls:
                return message.content

            messages.append(message)

            for tool_call in message.tool_calls:
                result = self._execute_tool(tool_call)
                print(f"Tool: {tool_call.function.name} → {result[:100]}...")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

    def _execute_tool(self, tool_call) -> str:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        return str(self.tool_functions[func_name](**func_args))
```

## Parallel Tool Calls

OpenAI can call multiple tools in parallel:

```python
def process_parallel_tool_calls(message, tool_functions: dict) -> list:
    """Process multiple tool calls that came in a single response."""
    results = []

    for tool_call in message.tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)

        result = tool_functions[func_name](**func_args)

        results.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(result)
        })

    return results
```

## Structured Outputs

Force specific response format:

```python
from pydantic import BaseModel

class TaskResult(BaseModel):
    success: bool
    result: str
    next_steps: list[str]

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[...],
    response_format=TaskResult
)

result = response.choices[0].message.parsed
print(result.success, result.result)
```

## Error Handling

```python
def safe_tool_execution(tool_call, tool_functions: dict) -> str:
    """Execute tool with comprehensive error handling."""
    func_name = tool_call.function.name

    # Check if function exists
    if func_name not in tool_functions:
        return json.dumps({
            "error": f"Unknown function: {func_name}",
            "available_functions": list(tool_functions.keys())
        })

    # Parse arguments
    try:
        func_args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as e:
        return json.dumps({
            "error": f"Invalid JSON arguments: {str(e)}",
            "raw_arguments": tool_call.function.arguments
        })

    # Execute function
    try:
        result = tool_functions[func_name](**func_args)
        return json.dumps({"success": True, "result": result})
    except TypeError as e:
        return json.dumps({
            "error": f"Invalid arguments for {func_name}: {str(e)}"
        })
    except Exception as e:
        return json.dumps({
            "error": f"Execution error: {str(e)}",
            "function": func_name,
            "arguments": func_args
        })
```

## Streaming Agent Responses

```python
def run_agent_streaming(user_input: str, tools: list, tool_functions: dict):
    """Run agent with streaming output."""
    messages = [{"role": "user", "content": user_input}]

    while True:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            stream=True
        )

        collected_content = ""
        collected_tool_calls = []

        for chunk in stream:
            delta = chunk.choices[0].delta

            if delta.content:
                print(delta.content, end="", flush=True)
                collected_content += delta.content

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    # Handle streaming tool calls
                    # (accumulate function name and arguments)
                    pass

        if not collected_tool_calls:
            print()  # Newline after streaming
            return collected_content

        # Process tool calls
        # ... (similar to non-streaming version)
```

## Best Practices

1. **Clear tool descriptions** - LLM needs to understand when to use each tool
2. **Validate tool inputs** - Don't trust LLM-generated arguments blindly
3. **Handle errors gracefully** - Return error messages, don't crash
4. **Set max iterations** - Prevent infinite loops
5. **Log tool calls** - For debugging and monitoring
6. **Use appropriate model** - gpt-4o for complex reasoning, gpt-4o-mini for speed
7. **Test edge cases** - What if tool fails? What if LLM hallucinates tool names?

## Common Pitfalls

- **Vague tool descriptions** - LLM won't know when to use the tool
- **No max iterations** - Agent can loop forever
- **Ignoring tool errors** - Leads to poor responses
- **Too many tools** - Confuses the model, increases latency
- **Missing required params** - LLM might not provide all required arguments

## References

- [references/tool-design.md](references/tool-design.md) - Tool design patterns
- [references/agent-patterns.md](references/agent-patterns.md) - Advanced agent architectures
- [OpenAI Function Calling Docs](https://platform.openai.com/docs/guides/function-calling)
