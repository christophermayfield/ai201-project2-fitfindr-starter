"""Tests for the Gradio query handler in app.py."""

from unittest.mock import patch

from app import handle_query


class TestHandleQuery:
    def test_empty_query_returns_error_in_first_panel_only(self):
        listing, outfit, card = handle_query("", "Example wardrobe")

        assert listing == "Please enter a search query."
        assert outfit == ""
        assert card == ""

    def test_whitespace_query_returns_error_in_first_panel_only(self):
        listing, outfit, card = handle_query("   ", "Example wardrobe")

        assert listing == "Please enter a search query."
        assert outfit == ""
        assert card == ""

    @patch("app.run_agent")
    def test_agent_error_returns_message_in_first_panel_only(self, mock_run_agent):
        mock_run_agent.return_value = {
            "error": "No listings matched your search.",
            "selected_item": None,
            "outfit_suggestion": None,
            "fit_card": None,
        }

        listing, outfit, card = handle_query(
            "designer ballgown size XXS under $5",
            "Example wardrobe",
        )

        assert listing == "No listings matched your search."
        assert outfit == ""
        assert card == ""
        mock_run_agent.assert_called_once()

    @patch("app.run_agent")
    def test_success_maps_session_to_three_panels(self, mock_run_agent):
        mock_run_agent.return_value = {
            "error": None,
            "selected_item": {
                "title": "Vintage Band Tee",
                "description": "Faded grey band tee.",
                "price": 19.0,
                "platform": "depop",
                "size": "L",
                "condition": "fair",
                "colors": ["grey"],
                "style_tags": ["vintage", "grunge"],
                "brand": None,
            },
            "outfit_suggestion": "Pair with baggy jeans.",
            "fit_card": "thrifted this tee off depop for $19",
        }

        listing, outfit, card = handle_query(
            "vintage graphic tee under $30",
            "Empty wardrobe (new user)",
        )

        assert "Vintage Band Tee" in listing
        assert "$19.00" in listing
        assert outfit == "Pair with baggy jeans."
        assert card == "thrifted this tee off depop for $19"

    @patch("app.get_empty_wardrobe")
    @patch("app.get_example_wardrobe")
    @patch("app.run_agent")
    def test_wardrobe_choice_selects_correct_wardrobe(
        self, mock_run_agent, mock_example, mock_empty
    ):
        mock_run_agent.return_value = {
            "error": "No listings matched your search.",
            "selected_item": None,
            "outfit_suggestion": None,
            "fit_card": None,
        }
        mock_example.return_value = {"items": [{"id": "w_001"}]}
        mock_empty.return_value = {"items": []}

        handle_query("vintage tee", "Example wardrobe")
        mock_run_agent.assert_called_once_with("vintage tee", {"items": [{"id": "w_001"}]})

        mock_run_agent.reset_mock()
        handle_query("vintage tee", "Empty wardrobe (new user)")
        mock_run_agent.assert_called_once_with("vintage tee", {"items": []})
