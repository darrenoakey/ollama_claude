from typing import Any
from functools import lru_cache
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock
from src.logging_setup import get_logger

logger = get_logger(__name__)


# ##################################################################
# extract json from delimited response
# pulls json content from triple backtick delimiters in response text
def extract_json_from_response(response_text: str) -> str:
    import re
    json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    match = re.search(json_pattern, response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response_text.strip()


# ##################################################################
# messages to prompt
# converts ollama messages format to a single prompt string
def messages_to_prompt(messages: list[dict[str, Any]]) -> tuple[str, str]:
    system_messages = [m for m in messages if m.get("role") == "system"]
    non_system_messages = [m for m in messages if m.get("role") != "system"]

    system_text = ""
    if system_messages:
        system_text = "\n".join(m.get("content", "") for m in system_messages)

    prompt_parts = []
    for msg in non_system_messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "assistant":
            prompt_parts.append(f"Assistant: {content}")
        else:
            prompt_parts.append(f"User: {content}")

    prompt = "\n".join(prompt_parts)
    return prompt, system_text


# ##################################################################
# chat completion memoized
# memoized actual api call to avoid repeated expensive llm calls in tests
@lru_cache(maxsize=256)
def chat_completion_memoized(prompt: str, system_text: str, json_schema_str: str | None = None) -> str:
    logger.info(f"Claude API call - prompt_len={len(prompt)} system_len={len(system_text)} schema={json_schema_str is not None}")

    actual_prompt = prompt
    actual_system = system_text

    if json_schema_str:
        import json
        schema_dict = json.loads(json_schema_str)
        schema_json = json.dumps(schema_dict.get("schema", schema_dict), indent=2)

        json_instruction = f"""
You must respond with valid JSON that exactly matches this schema. Wrap your JSON response in triple backticks like this:

```json
{{...your json here...}}
```

Schema:
{schema_json}

Your entire response must be the JSON wrapped in ```json and ```. Do not include any other text.
"""
        if actual_system:
            actual_system = actual_system + "\n\n" + json_instruction
        else:
            actual_system = json_instruction

    async def _query() -> str:
        options = ClaudeAgentOptions(max_turns=1)
        if actual_system:
            options.system_prompt = actual_system

        result_text = ""
        async for message in query(prompt=actual_prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        result_text += block.text

        return result_text

    result = anyio.run(_query)
    logger.info(f"Claude API response - response_len={len(result)}")
    return result


# ##################################################################
# chat completion
# calls claude agent sdk with messages and returns response content
def chat_completion(messages: list[dict[str, Any]], model: str, structured_format: dict[str, Any] | None = None) -> str:
    if not messages:
        raise ValueError("No messages provided")

    prompt, system_text = messages_to_prompt(messages)

    json_schema_str = None
    if structured_format:
        import json
        json_schema_str = json.dumps(structured_format)

    response = chat_completion_memoized(prompt, system_text, json_schema_str)

    if json_schema_str:
        response = extract_json_from_response(response)

    return response


# ##################################################################
# chat completion streaming memoized
# memoized actual streaming api call to avoid repeated expensive llm calls in tests
@lru_cache(maxsize=256)
def chat_completion_streaming_memoized(prompt: str, system_text: str) -> str:
    return chat_completion_memoized(prompt, system_text)


# ##################################################################
# chat completion streaming
# calls claude agent sdk with streaming enabled and yields response chunks
def chat_completion_streaming(messages: list[dict[str, Any]], model: str) -> Any:
    if not messages:
        raise ValueError("No messages provided")

    prompt, system_text = messages_to_prompt(messages)
    full_response = chat_completion_streaming_memoized(prompt, system_text)

    for char in full_response:
        yield char
