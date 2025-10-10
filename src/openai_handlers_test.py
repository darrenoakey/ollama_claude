import json
from src import openai_handlers


# ##################################################################
# test list models
# verifies that openai format list models returns expected structure
def test_list_models():
    result = openai_handlers.handle_list_models()

    assert result["object"] == "list"
    assert "data" in result
    assert len(result["data"]) > 0
    assert result["data"][0]["object"] == "model"
    assert result["data"][0]["owned_by"] == "anthropic"


# ##################################################################
# test chat completions basic
# verifies basic chat completion without schema works
def test_chat_completions_basic():
    request_data = {
        "model": "claude",
        "messages": [{"role": "user", "content": "Say hello"}],
        "stream": False
    }

    result = openai_handlers.handle_chat_completions(request_data)

    assert result["object"] == "chat.completion"
    assert result["model"] == "claude"
    assert len(result["choices"]) == 1
    assert result["choices"][0]["message"]["role"] == "assistant"
    assert len(result["choices"][0]["message"]["content"]) > 0
    assert result["choices"][0]["finish_reason"] == "stop"


# ##################################################################
# test chat completions with simple schema
# verifies json schema with simple object structure serializes correctly
def test_chat_completions_simple_schema():
    simple_schema = {
        "name": "simple_response",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
                "confidence": {"type": "number"}
            },
            "required": ["answer", "confidence"],
            "additionalProperties": False
        }
    }

    request_data = {
        "model": "claude",
        "messages": [{"role": "user", "content": "What is 2+2? Respond with answer and confidence."}],
        "stream": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": simple_schema
        }
    }

    result = openai_handlers.handle_chat_completions(request_data)
    response_text = result["choices"][0]["message"]["content"]

    parsed = json.loads(response_text)
    assert "answer" in parsed
    assert "confidence" in parsed
    assert isinstance(parsed["answer"], str)
    assert isinstance(parsed["confidence"], (int, float))


# ##################################################################
# test chat completions with nested schema
# verifies json schema with nested objects serializes correctly
def test_chat_completions_nested_schema():
    nested_schema = {
        "name": "user_profile",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"},
                        "zip_code": {"type": "string"}
                    },
                    "required": ["street", "city", "zip_code"],
                    "additionalProperties": False
                }
            },
            "required": ["name", "age", "address"],
            "additionalProperties": False
        }
    }

    request_data = {
        "model": "claude",
        "messages": [{"role": "user", "content": "Create a user profile for John Doe, age 30, living in San Francisco."}],
        "stream": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": nested_schema
        }
    }

    result = openai_handlers.handle_chat_completions(request_data)
    response_text = result["choices"][0]["message"]["content"]

    parsed = json.loads(response_text)
    assert "name" in parsed
    assert "age" in parsed
    assert "address" in parsed
    assert isinstance(parsed["name"], str)
    assert isinstance(parsed["age"], int)
    assert "street" in parsed["address"]
    assert "city" in parsed["address"]
    assert "zip_code" in parsed["address"]


# ##################################################################
# test chat completions with array schema
# verifies json schema with array of objects serializes correctly
def test_chat_completions_array_schema():
    array_schema = {
        "name": "task_list",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "priority": {"type": "integer"},
                            "completed": {"type": "boolean"}
                        },
                        "required": ["title", "priority", "completed"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["tasks"],
            "additionalProperties": False
        }
    }

    request_data = {
        "model": "claude",
        "messages": [{"role": "user", "content": "Create a list of 3 tasks with titles, priorities, and completion status."}],
        "stream": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": array_schema
        }
    }

    result = openai_handlers.handle_chat_completions(request_data)
    response_text = result["choices"][0]["message"]["content"]

    parsed = json.loads(response_text)
    assert "tasks" in parsed
    assert isinstance(parsed["tasks"], list)
    assert len(parsed["tasks"]) > 0
    for task in parsed["tasks"]:
        assert "title" in task
        assert "priority" in task
        assert "completed" in task
        assert isinstance(task["title"], str)
        assert isinstance(task["priority"], int)
        assert isinstance(task["completed"], bool)


# ##################################################################
# test chat completions with enum schema
# verifies json schema with enum values serializes correctly
def test_chat_completions_enum_schema():
    enum_schema = {
        "name": "sentiment_analysis",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "sentiment": {
                    "type": "string",
                    "enum": ["positive", "negative", "neutral"]
                },
                "score": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                }
            },
            "required": ["text", "sentiment", "score"],
            "additionalProperties": False
        }
    }

    request_data = {
        "model": "claude",
        "messages": [{"role": "user", "content": "Analyze the sentiment of: 'This is a great day!'"}],
        "stream": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": enum_schema
        }
    }

    result = openai_handlers.handle_chat_completions(request_data)
    response_text = result["choices"][0]["message"]["content"]

    parsed = json.loads(response_text)
    assert "text" in parsed
    assert "sentiment" in parsed
    assert "score" in parsed
    assert parsed["sentiment"] in ["positive", "negative", "neutral"]
    assert 0 <= parsed["score"] <= 1


# ##################################################################
# test chat completions with complex schema
# verifies json schema with multiple nested levels and types serializes correctly
def test_chat_completions_complex_schema():
    complex_schema = {
        "name": "product_catalog",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "products": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "price": {"type": "number"},
                            "in_stock": {"type": "boolean"},
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "metadata": {
                                "type": "object",
                                "properties": {
                                    "brand": {"type": "string"},
                                    "warranty_months": {"type": "integer"}
                                },
                                "required": ["brand", "warranty_months"],
                                "additionalProperties": False
                            }
                        },
                        "required": ["id", "name", "price", "in_stock", "tags", "metadata"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["category", "products"],
            "additionalProperties": False
        }
    }

    request_data = {
        "model": "claude",
        "messages": [{"role": "user", "content": "Create a product catalog for electronics with 2 products."}],
        "stream": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": complex_schema
        }
    }

    result = openai_handlers.handle_chat_completions(request_data)
    response_text = result["choices"][0]["message"]["content"]

    parsed = json.loads(response_text)
    assert "category" in parsed
    assert "products" in parsed
    assert isinstance(parsed["products"], list)

    for product in parsed["products"]:
        assert "id" in product
        assert "name" in product
        assert "price" in product
        assert "in_stock" in product
        assert "tags" in product
        assert "metadata" in product
        assert isinstance(product["id"], int)
        assert isinstance(product["name"], str)
        assert isinstance(product["price"], (int, float))
        assert isinstance(product["in_stock"], bool)
        assert isinstance(product["tags"], list)
        assert "brand" in product["metadata"]
        assert "warranty_months" in product["metadata"]


# ##################################################################
# test chat completions schema validation failure
# verifies that invalid json raises error
def test_chat_completions_schema_validation():
    simple_schema = {
        "name": "simple_response",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "answer": {"type": "string"}
            },
            "required": ["answer"],
            "additionalProperties": False
        }
    }

    request_data = {
        "model": "claude",
        "messages": [{"role": "user", "content": "Respond with valid JSON matching the schema."}],
        "stream": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": simple_schema
        }
    }

    result = openai_handlers.handle_chat_completions(request_data)
    response_text = result["choices"][0]["message"]["content"]

    json.loads(response_text)
