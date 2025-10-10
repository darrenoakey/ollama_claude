from src import openai_server


# ##################################################################
# test openai server routes exist
# verifies that openai server has expected routes configured
def test_openai_server_routes_exist():
    app = openai_server.app
    rules = [rule.rule for rule in app.url_map.iter_rules()]

    assert "/v1/models" in rules
    assert "/v1/chat/completions" in rules
