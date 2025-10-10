from src import server


# ##################################################################
# test app exists
# verifies flask app is created
def test_app_exists():
    assert server.app is not None
    assert hasattr(server.app, "route")


# ##################################################################
# test routes registered
# verifies all required routes are registered
def test_routes_registered():
    rules = [rule.rule for rule in server.app.url_map.iter_rules()]
    assert "/api/tags" in rules
    assert "/api/chat" in rules
    assert "/api/generate" in rules
