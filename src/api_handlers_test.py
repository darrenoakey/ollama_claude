from src import api_handlers


# ##################################################################
# test handle list models
# verifies handle list models returns expected structure
def test_handle_list_models():
    result = api_handlers.handle_list_models()
    assert "models" in result
    assert isinstance(result["models"], list)
    assert len(result["models"]) > 0


# ##################################################################
# test handle chat
# verifies handle chat accepts valid request data
def test_handle_chat():
    request_data = {"model": "claude", "messages": [{"role": "user", "content": "hi"}], "stream": False}
    result = api_handlers.handle_chat(request_data)
    assert isinstance(result, dict)
    assert "message" in result
    assert "content" in result["message"]


# ##################################################################
# test handle generate
# verifies handle generate accepts valid request data
def test_handle_generate():
    request_data = {"model": "claude", "prompt": "hi", "stream": False}
    result = api_handlers.handle_generate(request_data)
    assert isinstance(result, dict)
    assert "response" in result
    assert len(result["response"]) > 0
