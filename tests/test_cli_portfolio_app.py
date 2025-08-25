"""Tests for CLI portfolio application handlers."""

from unittest.mock import patch

import pandas as pd

from crypto_invest_portfolio.CLI_portfolio_app import (
    _handle_add,
    _handle_add_staking,
    _handle_analyze_once,
    _handle_auto_update,
    _handle_delete,
    _handle_edit,
    _handle_language_selection,
    _handle_plot,
    _handle_quit,
    _handle_settings,
    _handle_view_portfolio_all,
)
from crypto_invest_portfolio.constants.enums import Language
from crypto_invest_portfolio.ui import UserCancel


class TestSimpleHandlers:
    """Test simple handler functions that delegate to other modules."""

    @patch("crypto_invest_portfolio.CLI_portfolio_app.add_purchase")
    def test_handle_add(self, mock_add_purchase):
        """Test _handle_add calls add_purchase and returns True."""
        result = _handle_add()
        mock_add_purchase.assert_called_once()
        assert result is True

    @patch("crypto_invest_portfolio.CLI_portfolio_app.edit_purchase")
    def test_handle_edit(self, mock_edit_purchase):
        """Test _handle_edit calls edit_purchase and returns True."""
        result = _handle_edit()
        mock_edit_purchase.assert_called_once()
        assert result is True

    @patch("crypto_invest_portfolio.CLI_portfolio_app.add_staking_gain")
    def test_handle_add_staking(self, mock_add_staking_gain):
        """Test _handle_add_staking calls add_staking_gain and returns True."""
        result = _handle_add_staking()
        mock_add_staking_gain.assert_called_once()
        assert result is True

    @patch("crypto_invest_portfolio.CLI_portfolio_app.delete_purchase")
    def test_handle_delete(self, mock_delete_purchase):
        """Test _handle_delete calls delete_purchase and returns True."""
        result = _handle_delete()
        mock_delete_purchase.assert_called_once()
        assert result is True

    @patch("crypto_invest_portfolio.CLI_portfolio_app.plot_coin_history")
    def test_handle_plot(self, mock_plot_coin_history):
        """Test _handle_plot calls plot_coin_history and returns True."""
        result = _handle_plot()
        mock_plot_coin_history.assert_called_once()
        assert result is True

    @patch("builtins.print")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_text")
    def test_handle_quit(self, mock_get_text, mock_print):
        """Test _handle_quit prints goodbye message and returns False."""
        mock_get_text.return_value = "Goodbye!"

        result = _handle_quit()

        mock_get_text.assert_called_once_with("goodbye")
        mock_print.assert_called_once_with("Goodbye!")
        assert result is False


class TestHandlersWithLogic:
    """Test handler functions with business logic."""

    @patch("crypto_invest_portfolio.CLI_portfolio_app.analyze_portfolio")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.load_portfolio")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_text")
    @patch("builtins.print")
    def test_handle_analyze_once_with_empty_portfolio(
        self, mock_print, mock_get_text, mock_load_portfolio, mock_analyze_portfolio
    ):
        """Test _handle_analyze_once with empty portfolio."""
        # Setup empty dataframe
        empty_df = pd.DataFrame()
        mock_load_portfolio.return_value = empty_df
        mock_get_text.return_value = "Portfolio is empty"

        result = _handle_analyze_once()

        mock_load_portfolio.assert_called_once()
        mock_get_text.assert_called_once_with("empty_for_analysis")
        mock_print.assert_called_once_with("Portfolio is empty")
        mock_analyze_portfolio.assert_not_called()
        assert result is True

    @patch("crypto_invest_portfolio.CLI_portfolio_app.analyze_portfolio")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.load_portfolio")
    @patch("builtins.print")
    def test_handle_analyze_once_with_data(self, mock_print, mock_load_portfolio, mock_analyze_portfolio):
        """Test _handle_analyze_once with portfolio data."""
        # Setup non-empty dataframe
        test_df = pd.DataFrame({"symbol": ["BTC"], "amount": [1.0]})
        mock_load_portfolio.return_value = test_df

        result = _handle_analyze_once()

        mock_load_portfolio.assert_called_once()
        mock_analyze_portfolio.assert_called_once_with(test_df)
        mock_print.assert_not_called()
        assert result is True

    @patch("crypto_invest_portfolio.CLI_portfolio_app._view_portfolio")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.load_portfolio")
    def test_handle_view_portfolio_all(self, mock_load_portfolio, mock_view_portfolio):
        """Test _handle_view_portfolio_all loads and displays portfolio."""
        test_df = pd.DataFrame({"symbol": ["BTC"], "amount": [1.0]})
        mock_load_portfolio.return_value = test_df

        result = _handle_view_portfolio_all()

        mock_load_portfolio.assert_called_once()
        mock_view_portfolio.assert_called_once_with(test_df)
        assert result is True


class TestLanguageSelection:
    """Test language selection functionality."""

    @patch("builtins.input")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.set_language")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_supported_languages")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_current_language")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_text")
    @patch("builtins.print")
    def test_handle_language_selection_valid_choice(
        self,
        mock_print,
        mock_get_text,
        mock_get_current_language,
        mock_get_supported_languages,
        mock_set_language,
        mock_input,
    ):
        """Test language selection with valid choice."""
        # Setup
        mock_get_supported_languages.return_value = [Language.FR, Language.EN]
        mock_get_current_language.return_value = Language.FR
        mock_input.return_value = "2"  # Select English (second option)
        mock_get_text.side_effect = [
            "Select language:",  # language_selection
            "Choice: ",  # menu_choice
            "Language changed to English",  # language_changed
        ]

        _handle_language_selection()

        mock_set_language.assert_called_once_with(Language.EN)
        mock_get_text.assert_any_call("language_changed", "English")

    @patch("builtins.input")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_supported_languages")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_current_language")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_text")
    @patch("builtins.print")
    def test_handle_language_selection_invalid_choice(
        self,
        mock_print,
        mock_get_text,
        mock_get_current_language,
        mock_get_supported_languages,
        mock_input,
    ):
        """Test language selection with invalid choice."""
        # Setup
        mock_get_supported_languages.return_value = [Language.FR, Language.EN]
        mock_get_current_language.return_value = Language.FR
        mock_input.return_value = "99"  # Invalid choice
        mock_get_text.side_effect = [
            "Select language:",  # language_selection
            "Choice: ",  # menu_choice
            "Invalid choice",  # menu_invalid
        ]

        _handle_language_selection()

        mock_get_text.assert_any_call("menu_invalid")

    @patch("builtins.input")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_supported_languages")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_current_language")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_text")
    @patch("builtins.print")
    def test_handle_language_selection_value_error(
        self,
        mock_print,
        mock_get_text,
        mock_get_current_language,
        mock_get_supported_languages,
        mock_input,
    ):
        """Test language selection with non-numeric input."""
        # Setup
        mock_get_supported_languages.return_value = [Language.FR, Language.EN]
        mock_get_current_language.return_value = Language.FR
        mock_input.return_value = "invalid"  # Non-numeric input
        mock_get_text.side_effect = [
            "Select language:",  # language_selection
            "Choice: ",  # menu_choice
            "Cancelled",  # cancelled
        ]

        _handle_language_selection()

        mock_get_text.assert_any_call("cancelled")

    @patch("builtins.input")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_supported_languages")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_current_language")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_text")
    @patch("builtins.print")
    def test_handle_language_selection_user_cancel(
        self,
        mock_print,
        mock_get_text,
        mock_get_current_language,
        mock_get_supported_languages,
        mock_input,
    ):
        """Test language selection with UserCancel exception."""
        # Setup
        mock_get_supported_languages.return_value = [Language.FR, Language.EN]
        mock_get_current_language.return_value = Language.FR
        mock_input.side_effect = UserCancel()  # User cancels
        mock_get_text.side_effect = [
            "Select language:",  # language_selection
            "Choice: ",  # menu_choice
            "Cancelled",  # cancelled
        ]

        _handle_language_selection()

        mock_get_text.assert_any_call("cancelled")


class TestAutoUpdateHandler:
    """Test auto-update functionality."""

    @patch("crypto_invest_portfolio.CLI_portfolio_app.load_portfolio")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_text")
    @patch("builtins.print")
    def test_handle_auto_update_empty_portfolio(self, mock_print, mock_get_text, mock_load_portfolio):
        """Test _handle_auto_update with empty portfolio."""
        empty_df = pd.DataFrame()
        mock_load_portfolio.return_value = empty_df
        mock_get_text.return_value = "Portfolio is empty"

        result = _handle_auto_update()

        mock_load_portfolio.assert_called_once()
        mock_get_text.assert_called_once_with("empty_before_auto")
        mock_print.assert_called_once_with("Portfolio is empty")
        assert result is True

    @patch("builtins.input")
    @patch("time.sleep")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.analyze_portfolio")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.load_portfolio")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_text")
    @patch("builtins.print")
    def test_handle_auto_update_keyboard_interrupt(
        self,
        mock_print,
        mock_get_text,
        mock_load_portfolio,
        mock_analyze_portfolio,
        mock_sleep,
        mock_input,
    ):
        """Test _handle_auto_update with KeyboardInterrupt."""
        test_df = pd.DataFrame({"symbol": ["BTC"], "amount": [1.0]})
        mock_load_portfolio.return_value = test_df
        mock_input.return_value = "1"  # 1 minute interval
        mock_get_text.side_effect = [
            "Enter interval in minutes:",  # interval_minutes
            "Press Ctrl+C to stop auto-update.",  # auto_update_stop
            "Auto-update stopped.",  # auto_update_stopped
        ]
        # Simulate KeyboardInterrupt after first analysis
        mock_sleep.side_effect = KeyboardInterrupt()

        result = _handle_auto_update()

        mock_load_portfolio.assert_called_once()
        mock_analyze_portfolio.assert_called_once_with(test_df)
        mock_input.assert_called_once()
        mock_get_text.assert_any_call("auto_update_stopped")
        assert result is True


class TestSettingsHandler:
    """Test settings menu functionality."""

    @patch("builtins.input")
    @patch("crypto_invest_portfolio.CLI_portfolio_app._handle_language_selection")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_text")
    @patch("builtins.print")
    def test_handle_settings_language_choice(
        self, mock_print, mock_get_text, mock_handle_language_selection, mock_input
    ):
        """Test _handle_settings with language selection choice."""
        # First call returns "1" (language), second call returns "2" (back)
        mock_input.side_effect = ["1", "2"]
        mock_get_text.side_effect = [
            "\nSettings",  # settings_title
            "Language",  # settings_language
            "Back",  # settings_back
            "Choice: ",  # menu_choice
            "\nSettings",  # settings_title (second iteration)
            "Language",  # settings_language
            "Back",  # settings_back
            "Choice: ",  # menu_choice (second iteration)
        ]

        result = _handle_settings()

        mock_handle_language_selection.assert_called_once()
        assert result is True

    @patch("builtins.input")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_text")
    @patch("builtins.print")
    def test_handle_settings_back_choice(self, mock_print, mock_get_text, mock_input):
        """Test _handle_settings with back choice."""
        mock_input.return_value = "2"  # Back
        mock_get_text.side_effect = [
            "\nSettings",  # settings_title
            "Language",  # settings_language
            "Back",  # settings_back
            "Choice: ",  # menu_choice
        ]

        result = _handle_settings()

        assert result is True

    @patch("builtins.input")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_text")
    @patch("builtins.print")
    def test_handle_settings_invalid_choice(self, mock_print, mock_get_text, mock_input):
        """Test _handle_settings with invalid choice then back."""
        # First invalid choice, then back
        mock_input.side_effect = ["99", "2"]
        mock_get_text.side_effect = [
            "\nSettings",  # settings_title
            "Language",  # settings_language
            "Back",  # settings_back
            "Choice: ",  # menu_choice
            "Invalid choice",  # menu_invalid
            "\nSettings",  # settings_title (second iteration)
            "Language",  # settings_language
            "Back",  # settings_back
            "Choice: ",  # menu_choice (second iteration)
        ]

        result = _handle_settings()

        mock_get_text.assert_any_call("menu_invalid")
        assert result is True


class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch("crypto_invest_portfolio.CLI_portfolio_app.load_portfolio")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_text")
    @patch("builtins.print")
    def test_handle_analyze_once_empty_dataframe_is_detected_correctly(
        self, mock_print, mock_get_text, mock_load_portfolio
    ):
        """Test that empty DataFrame detection works correctly with different empty states."""
        # Test with completely empty DataFrame
        empty_df = pd.DataFrame()
        mock_load_portfolio.return_value = empty_df
        mock_get_text.return_value = "Empty portfolio message"

        result = _handle_analyze_once()

        assert result is True
        mock_print.assert_called_once_with("Empty portfolio message")

        # Reset mocks
        mock_print.reset_mock()
        mock_get_text.reset_mock()
        mock_load_portfolio.reset_mock()

        # Test with DataFrame that has columns but no rows
        empty_with_columns_df = pd.DataFrame(columns=["symbol", "amount"])
        mock_load_portfolio.return_value = empty_with_columns_df
        mock_get_text.return_value = "Empty portfolio message"

        result = _handle_analyze_once()

        assert result is True
        mock_print.assert_called_once_with("Empty portfolio message")

    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_supported_languages")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_current_language")
    def test_handle_language_selection_edge_case_single_language(
        self, mock_get_current_language, mock_get_supported_languages
    ):
        """Test language selection when only one language is available."""
        # Test with only one language available
        mock_get_supported_languages.return_value = [Language.FR]
        mock_get_current_language.return_value = Language.FR

        with (
            patch("builtins.input", return_value="1"),
            patch("crypto_invest_portfolio.CLI_portfolio_app.set_language") as mock_set_language,
            patch("crypto_invest_portfolio.CLI_portfolio_app.get_text") as mock_get_text,
            patch("builtins.print"),
        ):
            mock_get_text.side_effect = ["Select language:", "Choice: ", "Language changed to Français"]

            _handle_language_selection()

            mock_set_language.assert_called_once_with(Language.FR)

    @patch("builtins.input")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_supported_languages")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_current_language")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_text")
    @patch("builtins.print")
    def test_handle_language_selection_boundary_values(
        self,
        mock_print,
        mock_get_text,
        mock_get_current_language,
        mock_get_supported_languages,
        mock_input,
    ):
        """Test language selection with boundary values (0, negative, etc.)."""
        mock_get_supported_languages.return_value = [Language.FR, Language.EN]
        mock_get_current_language.return_value = Language.FR

        # Test with 0 (should be invalid)
        mock_input.return_value = "0"
        mock_get_text.side_effect = ["Select language:", "Choice: ", "Invalid choice"]

        _handle_language_selection()

        mock_get_text.assert_any_call("menu_invalid")

    @patch("builtins.input")
    @patch("time.sleep")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.analyze_portfolio")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.load_portfolio")
    @patch("crypto_invest_portfolio.CLI_portfolio_app.get_text")
    @patch("builtins.print")
    def test_handle_auto_update_float_conversion_edge_cases(
        self,
        mock_print,
        mock_get_text,
        mock_load_portfolio,
        mock_analyze_portfolio,
        mock_sleep,
        mock_input,
    ):
        """Test auto-update with different float input formats."""
        test_df = pd.DataFrame({"symbol": ["BTC"], "amount": [1.0]})
        mock_load_portfolio.return_value = test_df

        # Test with decimal input
        mock_input.return_value = "0.5"  # 0.5 minutes (30 seconds)
        mock_get_text.side_effect = ["Enter interval:", "Press Ctrl+C to stop", "Auto-update stopped"]
        mock_sleep.side_effect = KeyboardInterrupt()

        result = _handle_auto_update()

        assert result is True
        # Verify that sleep was called with correct value (0.5 * 60 = 30 seconds)
        mock_sleep.assert_called_once_with(30.0)
