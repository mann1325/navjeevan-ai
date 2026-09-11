import unittest
import time
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import _rate_limit_state, app, settings, startup_event

class TestAPIIntegration(unittest.TestCase):
    def setUp(self):
        startup_event()
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_cors_allows_configured_local_origin_and_blocks_unknown_origin(self):
        allowed = self.client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        blocked = self.client.options(
            "/health",
            headers={
                "Origin": "https://unknown.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(allowed.headers.get("access-control-allow-origin"), "http://localhost:5173")
        self.assertIsNone(blocked.headers.get("access-control-allow-origin"))

    def test_chat_rate_limit_returns_429(self):
        key = ("chat", "testclient")
        _rate_limit_state[key] = [time.monotonic()] * settings.chat_rate_limit_requests
        try:
            response = self.client.post("/chat", json={"query": "hello"})
            self.assertEqual(response.status_code, 429)
            self.assertIn("Retry-After", response.headers)
        finally:
            _rate_limit_state.pop(key, None)

    def test_chat_success_matches_react_contract(self):
        response = self.client.post("/chat", json={"query": "Amla price in Vadodara"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("status", payload)
        self.assertIn("intent", payload)
        self.assertIn("response", payload)
        self.assertIn("Cached / Historical Data", payload["response"])

    def test_chat_validation_error_is_non_success(self):
        response = self.client.post("/chat", json={"query": ""})
        self.assertEqual(response.status_code, 422)

    def test_root_serves_canonical_frontend(self):
        response = self.client.get("/")
        index_file = Path(__file__).resolve().parents[3] / "frontend" / "dist" / "index.html"
        if index_file.is_file():
            self.assertEqual(response.status_code, 200)
            self.assertIn("text/html", response.headers["content-type"])
        else:
            self.assertEqual(response.status_code, 503)

    def test_advisory_endpoint(self):
        payload = {
            "crop": "wheat",
            "location": "Pune",
            "sowing_date": "2024-01-01"
        }
        # This will test the entire stack: Route -> Engine -> Providers (Open-Meteo) -> AI Formatter (Groq/Mocked)
        response = self.client.post("/api/v1/advisory", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("data", data)
        
        payload_data = data["data"]
        self.assertIn("ai_advice", payload_data)
        self.assertIn("decision_data", payload_data)
        
        decision_data = payload_data["decision_data"]
        self.assertIn("confidence", decision_data)
        self.assertIn("metadata", decision_data)
        
        # Verify provider integration successfully pulled data
        self.assertGreaterEqual(decision_data["confidence"]["score"], 0)
