from src import models


# ##################################################################
# test get models
# verifies that get models returns a valid hardwired list
def test_get_models():
    result = models.get_models()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["name"] == "claude"
    assert result[0]["model"] == "claude"
    assert "details" in result[0]


# ##################################################################
# test map model name
# verifies model name mapping returns claude model identifier
def test_map_model_name():
    result = models.map_model_name("claude")
    assert result == models.CLAUDE_MODEL
    assert isinstance(result, str)
    assert len(result) > 0
