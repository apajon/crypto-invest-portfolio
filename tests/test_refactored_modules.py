"""Tests for the refactored modules."""

import pytest

from crypto_invest_portfolio.constants.enums import CoinType, CancelCommand, Language
from crypto_invest_portfolio.ui.input_helpers import is_cancel
from crypto_invest_portfolio.i18n import get_text, set_language, get_current_language


def test_coin_type_enum():
    """Test CoinType enum values."""
    assert CoinType.CLASSIC == "classic"
    assert CoinType.RISK == "risk"
    assert CoinType.STABLE == "stable"


def test_cancel_command_enum():
    """Test CancelCommand enum values."""
    assert CancelCommand.Q == "q"
    assert CancelCommand.QUIT == "quit"
    assert CancelCommand.CANCEL == "cancel"


def test_is_cancel():
    """Test cancellation detection."""
    assert is_cancel("q") is True
    assert is_cancel("Q") is True
    assert is_cancel("quit") is True
    assert is_cancel("QUIT") is True
    assert is_cancel("normal_input") is False


def test_i18n_system():
    """Test internationalization system."""
    # Test French (default)
    original_lang = get_current_language()
    set_language(Language.FR)
    assert get_text("menu_quit") == "Quitter"
    
    # Test English
    set_language(Language.EN)
    assert get_text("menu_quit") == "Quit"
    
    # Test with formatting
    assert get_text("success_purchase_added", "BTC", 0.1, 50000) == "✅ Purchase added: BTC (0.1 @ 50000 CAD)"
    
    # Restore original language
    set_language(original_lang)


def test_language_persistence():
    """Test that language preference is saved."""
    original_lang = get_current_language()
    
    # Change language
    new_lang = Language.EN if original_lang == Language.FR else Language.FR
    set_language(new_lang)
    
    # Verify change took effect
    assert get_current_language() == new_lang
    
    # Restore original
    set_language(original_lang)