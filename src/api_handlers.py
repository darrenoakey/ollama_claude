import json
from typing import Any, Iterator
from flask import Response
from src import models
from src import claude_client
from src.logging_setup import get_logger

logger = get_logger(__name__)


# ##################################################################
# handle list models
# returns json response with available models
def handle_list_models() -> dict[str, Any]:
    logger.info("Request: list models")
    result = {"models": models.get_models()}
    logger.info(f"Response: {len(result['models'])} models")
    return result


# ##################################################################
# handle chat
# processes chat request and returns claude response
def handle_chat(request_data: dict[str, Any]) -> dict[str, Any] | Response:
    model_name = request_data.get("model", "claude")
    messages = request_data.get("messages", [])
    stream = request_data.get("stream", False)
    format_spec = request_data.get("format")

    logger.info(f"Request: chat - model={model_name} messages={len(messages)} stream={stream}")

    claude_model = models.map_model_name(model_name)

    if stream:
        logger.info("Response: chat streaming started")
        return handle_chat_streaming(messages, claude_model)

    response_text = claude_client.chat_completion(messages, claude_model, format_spec)
    logger.info(f"Response: chat - response_len={len(response_text)}")

    return {
        "model": model_name,
        "created_at": "",
        "message": {"role": "assistant", "content": response_text},
        "done": True,
    }


# ##################################################################
# handle chat streaming
# processes streaming chat request and yields response chunks
def handle_chat_streaming(messages: list[dict[str, Any]], claude_model: str) -> Response:
    def generate() -> Iterator[str]:
        for chunk in claude_client.chat_completion_streaming(messages, claude_model):
            response_chunk = {
                "model": "claude",
                "created_at": "",
                "message": {"role": "assistant", "content": chunk},
                "done": False,
            }
            yield json.dumps(response_chunk) + "\n"

        final_chunk = {
            "model": "claude",
            "created_at": "",
            "message": {"role": "assistant", "content": ""},
            "done": True,
        }
        yield json.dumps(final_chunk) + "\n"

    return Response(generate(), mimetype="application/x-ndjson")


# ##################################################################
# handle generate
# processes generate request and returns claude response
def handle_generate(request_data: dict[str, Any]) -> dict[str, Any] | Response:
    model_name = request_data.get("model", "claude")
    prompt = request_data.get("prompt", "")
    stream = request_data.get("stream", False)
    format_spec = request_data.get("format")

    logger.info(f"Request: generate - model={model_name} prompt_len={len(prompt)} stream={stream}")

    messages = [{"role": "user", "content": prompt}]
    claude_model = models.map_model_name(model_name)

    if stream:
        logger.info("Response: generate streaming started")
        return handle_generate_streaming(prompt, claude_model)

    response_text = claude_client.chat_completion(messages, claude_model, format_spec)
    logger.info(f"Response: generate - response_len={len(response_text)}")

    return {"model": model_name, "created_at": "", "response": response_text, "done": True}


# ##################################################################
# handle generate streaming
# processes streaming generate request and yields response chunks
def handle_generate_streaming(prompt: str, claude_model: str) -> Response:
    messages = [{"role": "user", "content": prompt}]

    def generate() -> Iterator[str]:
        for chunk in claude_client.chat_completion_streaming(messages, claude_model):
            response_chunk = {"model": "claude", "created_at": "", "response": chunk, "done": False}
            yield json.dumps(response_chunk) + "\n"

        final_chunk = {"model": "claude", "created_at": "", "response": "", "done": True}
        yield json.dumps(final_chunk) + "\n"

    return Response(generate(), mimetype="application/x-ndjson")
