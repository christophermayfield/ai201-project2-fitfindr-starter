"""Tests for FitFindr tools — at least one test per documented failure mode."""

from unittest.mock import patch

import pytest

from tools import create_fit_card, search_listings, suggest_outfit
from utils.data_loader import get_empty_wardrobe, get_example_wardrobe, load_listings


@pytest.fixture
def sample_listing() -> dict:
    """A real listing from the mock dataset."""
    return load_listings()[0]


# ── search_listings ───────────────────────────────────────────────────────────

class TestSearchListings:
    def test_no_results_returns_empty_list_without_raising(self):
        """Failure mode: no listings match the query."""
        results = search_listings(
            description="designer ballgown",
            size="XXS",
            max_price=5.0,
        )

        assert results == []
        assert isinstance(results, list)

    def test_empty_description_returns_empty_list(self):
        """No keywords means no relevance matches."""
        results = search_listings(description="")

        assert results == []

    def test_matching_query_returns_sorted_results(self):
        results = search_listings(description="vintage graphic tee", max_price=30.0)

        assert len(results) > 0
        assert all(r["price"] <= 30.0 for r in results)
        assert all("id" in r and "title" in r for r in results)


# ── suggest_outfit ────────────────────────────────────────────────────────────

class TestSuggestOutfit:
    @patch("tools._call_groq", return_value="Try wide-leg jeans and chunky sneakers.")
    def test_empty_wardrobe_returns_non_empty_general_advice(self, mock_groq, sample_listing):
        """Failure mode: wardrobe is empty — general styling advice, no exception."""
        result = suggest_outfit(sample_listing, get_empty_wardrobe())

        assert isinstance(result, str)
        assert result.strip()
        mock_groq.assert_called_once()

    @patch("tools._call_groq", side_effect=RuntimeError("API unavailable"))
    def test_empty_wardrobe_fallback_when_llm_fails(self, mock_groq, sample_listing):
        """Empty wardrobe still gets helpful advice if the LLM call fails."""
        result = suggest_outfit(sample_listing, get_empty_wardrobe())

        assert isinstance(result, str)
        assert result.strip()
        assert sample_listing["title"] in result

    @patch("tools._call_groq", return_value="Pair with your baggy jeans and chunky sneakers.")
    def test_non_empty_wardrobe_returns_suggestion(self, mock_groq, sample_listing):
        result = suggest_outfit(sample_listing, get_example_wardrobe())

        assert result.strip()
        mock_groq.assert_called_once()


# ── create_fit_card ───────────────────────────────────────────────────────────

class TestCreateFitCard:
    def test_empty_outfit_returns_error_message_without_raising(self, sample_listing):
        """Failure mode: outfit input is missing or empty."""
        result = create_fit_card("", sample_listing)

        assert isinstance(result, str)
        assert "Cannot create a fit card" in result
        assert "empty" in result.lower()

    def test_whitespace_outfit_returns_error_message(self, sample_listing):
        result = create_fit_card("   \n\t  ", sample_listing)

        assert "Cannot create a fit card" in result

    @patch("tools._call_groq", side_effect=RuntimeError("API unavailable"))
    def test_llm_failure_returns_template_caption(self, mock_groq, sample_listing):
        outfit = "Pair with baggy jeans and chunky sneakers."
        result = create_fit_card(outfit, sample_listing)

        assert isinstance(result, str)
        assert result.strip()
        assert sample_listing["platform"] in result
        assert str(int(sample_listing["price"])) in result

    @patch("tools._call_groq", return_value="thrifted this tee off depop for $19, obsessed.")
    def test_valid_outfit_returns_caption(self, mock_groq, sample_listing):
        result = create_fit_card("Pair with baggy jeans.", sample_listing)

        assert result.strip()
        mock_groq.assert_called_once()
