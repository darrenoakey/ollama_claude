import json
import time
from typing import Any, Iterator
from flask import Response
from src import models
from src import claude_client
from src.logging_setup import get_logger

logger = get_logger(__name__)


# ##################################################################
# handle list models
# returns openai format list of available models
def handle_list_models() -> dict[str, Any]:
    logger.info("Request: OpenAI list models")
    claude_models = models.get_models()

    openai_models = []
    for model in claude_models:
        openai_models.append({
            "id": model["name"],
            "object": "model",
            "created": int(time.time()),
            "owned_by": "anthropic"
        })

    result = {"object": "list", "data": openai_models}
    logger.info(f"Response: {len(openai_models)} models")
    return result


# ##################################################################
# handle chat completions
# processes openai chat completion request and returns claude response
def handle_chat_completions(request_data: dict[str, Any]) -> dict[str, Any] | Response:
    model_name = request_data.get("model", "claude")
    messages = request_data.get("messages", [])
    stream = request_data.get("stream", False)
    response_format = request_data.get("response_format")

    logger.info(f"Request: OpenAI chat - model={model_name} messages={len(messages)} stream={stream} response_format={response_format is not None}")

    claude_model = models.map_model_name(model_name)

    json_schema = None
    if response_format and response_format.get("type") == "json_schema":
        json_schema = response_format.get("json_schema")
        logger.info(f"Using JSON schema: {json_schema.get('name') if json_schema else 'unknown'}")

    if stream:
        logger.info("Response: OpenAI chat streaming started")
        return handle_chat_completions_streaming(messages, claude_model, model_name)

    response_text = claude_client.chat_completion(messages, claude_model, json_schema)
    logger.info(f"Response: OpenAI chat - response_len={len(response_text)}")

    if json_schema:
        try:
            json.loads(response_text)
            logger.info(f"JSON schema validation successful for schema: {json_schema.get('name')}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Response is not valid JSON: {e}")

    completion_id = f"chatcmpl-{int(time.time() * 1000)}"
    return {
        "id": completion_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_name,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": response_text},
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }


# ##################################################################
# handle chat completions streaming
# processes streaming openai chat request and yields response chunks
def handle_chat_completions_streaming(messages: list[dict[str, Any]], claude_model: str, model_name: str) -> Response:
    def generate() -> Iterator[str]:
        completion_id = f"chatcmpl-{int(time.time() * 1000)}"

        for chunk in claude_client.chat_completion_streaming(messages, claude_model):
            response_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": model_name,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": chunk},
                        "finish_reason": None
                    }
                ]
            }
            yield f"data: {json.dumps(response_chunk)}\n\n"

        final_chunk = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model_name,
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }
            ]
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"

    return Response(generate(), mimetype="text/event-stream")
