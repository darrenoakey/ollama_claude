from src import claude_client

TEST_PROMPT = "hi"


# ##################################################################
# test chat completion
# verifies chat completion returns valid response from claude
def test_chat_completion():
    messages = [{"role": "user", "content": TEST_PROMPT}]
    result = claude_client.chat_completion(messages, "claude-sonnet-4-20250514")

    assert isinstance(result, str)
    assert len(result) > 0


# ##################################################################
# test chat completion with system message
# verifies system messages are properly handled
def test_chat_completion_with_system():
    messages = [{"role": "system", "content": "respond briefly"}, {"role": "user", "content": TEST_PROMPT}]
    result = claude_client.chat_completion(messages, "claude-sonnet-4-20250514")

    assert isinstance(result, str)
    assert len(result) > 0


# ##################################################################
# test chat completion streaming
# verifies streaming chat returns chunks
def test_chat_completion_streaming():
    messages = [{"role": "user", "content": TEST_PROMPT}]
    chunks = list(claude_client.chat_completion_streaming(messages, "claude-sonnet-4-20250514"))

    assert len(chunks) > 0
    full_text = "".join(chunks)
    assert len(full_text) > 0
