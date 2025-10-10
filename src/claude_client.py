from typing import Any
from functools import lru_cache
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock
from src.logging_setup import get_logger

logger = get_logger(__name__)


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
def chat_completion_memoized(prompt: str, system_text: str) -> str:
    logger.info(f"Claude API call - prompt_len={len(prompt)} system_len={len(system_text)}")

    async def _query() -> str:
        options = ClaudeAgentOptions(max_turns=1)
        if system_text:
            options.system_prompt = system_text

        result_text = ""
        async for message in query(prompt=prompt, options=options):
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
    return chat_completion_memoized(prompt, system_text)


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
