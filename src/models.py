from datetime import datetime
from typing import Any

CLAUDE_MODEL = "claude-sonnet-4-20250514"


# ##################################################################
# get models
# returns hardwired list of available models in ollama format
def get_models() -> list[dict[str, Any]]:
    return [
        {
            "name": "claude",
            "model": "claude",
            "modified_at": datetime.now().isoformat() + "Z",
            "size": 0,
            "digest": "sha256:hardwired",
            "details": {
                "parent_model": "",
                "format": "gguf",
                "family": "claude",
                "families": ["claude"],
                "parameter_size": "0B",
                "quantization_level": "Q4_0",
            },
        }
    ]


# ##################################################################
# map model name
# converts ollama model name to actual claude model identifier
def map_model_name(ollama_name: str) -> str:
    return CLAUDE_MODEL
