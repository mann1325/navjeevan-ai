import json
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.services.data_service import load_data
from backend.services.chat_service import process_chat_query
from backend.services.market_service import handle_market


class TestMarketFallback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_data()
        cls.market_path = Path(__file__).resolve().parents[2] / "data" / "markets.json"

    def setUp(self):
        self.markets = json.loads(self.market_path.read_text(encoding="utf-8"))
        self.entities = {"crop": "amla", "location": "vadodara", "query_type": "price"}

    def test_cache_contains_exactly_the_ten_supplied_records(self):
        self.assertEqual(len(self.markets), 10)
        self.assertEqual({record["commodity"] for record in self.markets}, {"Amla(Nelli Kai)"})
        self.assertEqual({record["market"] for record in self.markets}, {"Vadodara(Sayajipura)"})

        mandi_path = Path(__file__).resolve().parents[2] / "data" / "mandis.json"
        self.assertEqual(json.loads(mandi_path.read_text(encoding="utf-8")), [])

    def test_amla_vadodara_lookup_uses_latest_exact_record(self):
        with patch("backend.services.market_service.fetch_realtime_market_price", return_value=None):
            response = handle_market("Amla price in Vadodara", self.markets, self.entities)

        self.assertIn("Amla(Nelli Kai)", response)
        self.assertIn("Vadodara(Sayajipura)", response)
        self.assertIn("Modal Price: Rs. 4300/qtl", response)
        self.assertIn("Min Price: Rs. 4000/qtl", response)
        self.assertIn("Max Price: Rs. 4500/qtl", response)
        self.assertIn("Cached / Historical Data", response)
        self.assertIn("Source: data.gov.in", response)
        self.assertIn("Last available record: 19/10/2025", response)

    def test_all_dates_and_prices_match_exactly(self):
        expected = [
            ("02/08/2025", 4500, 4000, 4300),
            ("07/08/2025", 4500, 4000, 4300),
            ("10/08/2025", 4500, 4000, 4300),
            ("19/08/2025", 4500, 4000, 4300),
            ("30/09/2025", 7000, 6000, 6500),
            ("07/10/2025", 5000, 4500, 4800),
            ("08/10/2025", 5000, 4500, 4800),
            ("11/10/2025", 5000, 4500, 4800),
            ("13/10/2025", 5000, 4500, 4800),
            ("19/10/2025", 4500, 4000, 4300),
        ]
        actual = [
            (record["arrival_date"], record["max_price"], record["min_price"], record["modal_price"])
            for record in self.markets
        ]
        self.assertEqual(actual, expected)

    @patch("backend.services.market_service.fetch_realtime_market_price", return_value=None)
    def test_missing_api_key_uses_cache(self, _live_lookup):
        response = handle_market("Amla price in Vadodara", self.markets, self.entities)
        self.assertIn("Cached / Historical Data", response)

    @patch("backend.services.market_service.fetch_realtime_market_price", side_effect=RuntimeError("API down"))
    def test_live_api_failure_uses_cache(self, _live_lookup):
        response = handle_market("Amla price in Vadodara", self.markets, self.entities)
        self.assertIn("Cached / Historical Data", response)

    @patch("backend.services.market_service.fetch_realtime_market_price", return_value=None)
    def test_unavailable_commodity_does_not_return_fabricated_data(self, _live_lookup):
        entities = {"crop": "wheat", "location": "surat", "query_type": "price"}
        response = handle_market("Wheat price in Surat", self.markets, entities)
        self.assertEqual(response, "Market data unavailable")

    @patch("backend.services.market_service.fetch_realtime_market_price", return_value=None)
    def test_chat_api_path_returns_cached_label(self, _live_lookup):
        response = process_chat_query("Amla price in Vadodara")
        self.assertEqual(response["status"], "success")
        self.assertIn("Cached / Historical Data", response["response"])

    @patch(
        "backend.services.market_service.fetch_realtime_market_price",
        return_value={
            "market_name": "Vadodara(Sayajipura)",
            "location": "Vadodara(Baroda)",
            "price_per_qtl": 9999,
            "date": "20/10/2025",
        },
    )
    def test_live_data_remains_primary(self, _live_lookup):
        response = handle_market("Amla price in Vadodara", self.markets, self.entities)
        self.assertIn("Data status: Live", response)
        self.assertIn("Price: Rs. 9999/qtl", response)
        self.assertNotIn("Cached / Historical Data", response)