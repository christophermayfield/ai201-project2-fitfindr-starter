"""Tests for the FitFindr planning loop in agent.py."""

from unittest.mock import patch

import pytest

from agent import _parse_query, run_agent
from utils.data_loader import get_example_wardrobe


class TestParseQuery:
    def test_extracts_description_price_and_size(self):
        parsed = _parse_query("looking for a vintage graphic tee under $30")

        assert parsed["description"] == "vintage graphic tee"
        assert parsed["max_price"] == 30.0
        assert parsed["size"] is None

    def test_extracts_size_from_in_size_phrase(self):
        parsed = _parse_query("90s track jacket in size M")

        assert parsed["size"] == "M"
        assert "track jacket" in parsed["description"].lower()


class TestRunAgent:
    @patch("agent.create_fit_card", return_value="fit card caption")
    @patch("agent.suggest_outfit", return_value="outfit suggestion")
    @patch("agent.search_listings")
    def test_happy_path_stores_session_and_calls_tools_in_order(
        self, mock_search, mock_suggest, mock_fit_card
    ):
        listing = {"id": "lst_001", "title": "Vintage Tee", "price": 20.0, "platform": "depop"}
        mock_search.return_value = [listing, {"id": "lst_002"}, {"id": "lst_003"}]

        session = run_agent("vintage graphic tee under $30", get_example_wardrobe())

        assert session["error"] is None
        assert session["parsed"]["max_price"] == 30.0
        assert len(session["search_results"]) == 3
        assert session["selected_item"] == listing
        assert session["outfit_suggestion"] == "outfit suggestion"
        assert session["fit_card"] == "fit card caption"

        mock_search.assert_called_once()
        mock_suggest.assert_called_once_with(listing, session["wardrobe"])
        mock_fit_card.assert_called_once_with("outfit suggestion", listing)

    @patch("agent.create_fit_card")
    @patch("agent.suggest_outfit")
    @patch("agent.search_listings", return_value=[])
    def test_no_results_branches_early_without_calling_downstream_tools(
        self, mock_search, mock_suggest, mock_fit_card
    ):
        session = run_agent("designer ballgown size XXS under $5", get_example_wardrobe())

        assert session["error"]
        assert session["search_results"] == []
        assert session["selected_item"] is None
        assert session["outfit_suggestion"] is None
        assert session["fit_card"] is None

        mock_search.assert_called_once()
        mock_suggest.assert_not_called()
        mock_fit_card.assert_not_called()

    @patch("agent.search_listings")
    def test_stores_at_most_three_search_results(self, mock_search):
        listings = [{"id": f"lst_{i}", "title": f"Item {i}"} for i in range(5)]
        mock_search.return_value = listings

        with patch("agent.suggest_outfit", return_value="outfit"), patch(
            "agent.create_fit_card", return_value="card"
        ):
            session = run_agent("vintage tee", get_example_wardrobe())

        assert len(session["search_results"]) == 3
