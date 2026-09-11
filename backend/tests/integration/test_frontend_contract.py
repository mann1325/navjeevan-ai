import unittest
from pathlib import Path


class TestFrontendContract(unittest.TestCase):
    frontend_root = Path(__file__).resolve().parents[3] / "frontend"

    def test_react_uses_configurable_api_base(self):
        source = (self.frontend_root / "src" / "components" / "AIChatModal.jsx").read_text(encoding="utf-8")
        self.assertIn("VITE_API_BASE_URL", source)
        self.assertIn("if (!res.ok)", source)

    def test_weather_component_consumes_api_envelope_and_status(self):
        source = (self.frontend_root / "src" / "components" / "WeatherWidget.jsx").read_text(encoding="utf-8")
        self.assertIn("resData.data", source)
        self.assertIn("weatherData.status", source)
        self.assertIn("weatherData.fetched_at", source)