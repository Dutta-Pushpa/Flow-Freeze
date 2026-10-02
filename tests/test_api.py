def test_api_contract_documented():
    from backend.main import app
    paths={route.path for route in app.routes if hasattr(route, "path")}
    assert "/health" in paths and "/api/v1/feedback" in paths
