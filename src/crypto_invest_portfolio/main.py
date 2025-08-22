"""Refactored main entry point for the crypto portfolio application."""

import time

from .constants.enums import Language
from .database import init_db
from .i18n import get_text, set_language, get_current_language, get_supported_languages
from .portfolio import add_purchase, edit_purchase, delete_purchase, add_staking_gain, load_portfolio
from .ui import input_with_cancel, UserCancel

# Import the original analysis functions for now - will refactor later
from .main_original import (
    analyze_portfolio, plot_coin_history, _handle_wallet_menu,
    _handle_view_portfolio_one_wallet, _view_portfolio
)


def _handle_add():
    add_purchase()
    return True


def _handle_edit():
    edit_purchase()
    return True


def _handle_add_staking():
    add_staking_gain()
    return True


def _handle_delete():
    delete_purchase()
    return True


def _handle_analyze_once():
    df = load_portfolio()
    if df.empty:
        print(get_text("empty_for_analysis"))
    else:
        analyze_portfolio(df)
    return True


def _handle_auto_update():
    df = load_portfolio()
    if df.empty:
        print(get_text("empty_before_auto"))
        return True
    minutes = float(input(get_text("interval_minutes")))
    print(get_text("auto_update_stop"))
    try:
        while True:
            analyze_portfolio(df)
            time.sleep(minutes * 60)
    except KeyboardInterrupt:
        print(get_text("auto_update_stopped"))
    return True


def _handle_plot():
    plot_coin_history()
    return True


def _handle_quit():
    print(get_text("goodbye"))
    return False


def _handle_view_portfolio_all():
    df = load_portfolio()
    _view_portfolio(df)
    return True


def _handle_settings():
    """Handle settings menu."""
    while True:
        print(f"\\n{get_text('settings_title')}")
        print(f"1. {get_text('settings_language')}")
        print(f"2. {get_text('settings_back')}")
        
        choice = input(get_text("menu_choice")).strip()
        
        if choice == "1":
            _handle_language_selection()
        elif choice == "2":
            break
        else:
            print(get_text("menu_invalid"))
    return True


def _handle_language_selection():
    """Handle language selection."""
    print(f"\\n{get_text('language_selection')}")
    languages = get_supported_languages()
    current = get_current_language()
    
    for i, lang in enumerate(languages, 1):
        marker = " (current)" if lang == current else ""
        lang_name = "Français" if lang == Language.FR else "English"
        print(f"{i}. {lang_name}{marker}")
    
    try:
        choice = int(input(get_text("menu_choice")))
        if 1 <= choice <= len(languages):
            selected_lang = languages[choice - 1]
            set_language(selected_lang)
            lang_name = "Français" if selected_lang == Language.FR else "English"
            print(get_text("language_changed", lang_name))
        else:
            print(get_text("menu_invalid"))
    except (ValueError, UserCancel):
        print(get_text("cancelled"))


def main_menu():
    """Main menu of the application (CLI interface).

    Presents an interactive menu to manage a crypto portfolio and orchestrates
    key actions: adding, modifying, deleting purchases, one-time or periodic
    performance analysis and visualization of coin history.

    Functionality:
        - Initializes SQLite database if necessary.
        - Starts a loop until the user chooses to quit.
        - Delegates each action to dedicated functions.

    Menu Options:
        1) Add a purchase -> :func:`add_purchase`
        2) Add a gain (staking) -> :func:`add_staking_gain`
        3) Modify an existing purchase -> :func:`edit_purchase`
        4) Delete a purchase -> :func:`delete_purchase`
        5) Analyze portfolio once -> :func:`analyze_portfolio`
        6) Auto-update (periodic analysis)
        7) View portfolio (purchases)
        8) View portfolio of a wallet
        9) View coin evolution -> :func:`plot_coin_history`
        10) Wallet analysis (opens a sub-menu)
        11) Settings
        12) Quit

    Args:
        None

    Returns:
        None: Returns nothing. Function ends when user chooses to quit the menu.

    Side effects:
        - Creates/opens SQLite file ``crypto_portfolio.db``.
        - Reads/writes to ``portfolio`` and ``history`` tables.
        - Makes HTTP requests to CoinGecko API during analysis.
        - Displays information in console; may open Matplotlib windows.
        - Requests keyboard input (blocking) via ``input()``.

    User interactions:
        - Numbered inputs to choose an action.
        - In auto-update mode (option 6), ``Ctrl+C`` cleanly interrupts
          the loop and returns to menu without quitting the application.

    Exceptions:
        - Specific exceptions are handled within sub-functions.
        - A ``KeyboardInterrupt`` is caught during auto-update and does not
          propagate above this loop.

    Notes:
        - Auto-update uses the portfolio state loaded at the time of
          launching the option; if database content changes during the
          loop, restart the option to reload data.
        - Network access is required to retrieve current prices.

    Examples:
        Run from project root with Poetry::

            poetry run python -m crypto_invest_portfolio.main

        Or directly with Python::

            python -m crypto_invest_portfolio.main

    See also:
        :func:`add_purchase`, :func:`edit_purchase`, :func:`delete_purchase`,
        :func:`analyze_portfolio`, :func:`plot_coin_history`
    """
    init_db()
    actions = {
        "1": _handle_add,
        "2": _handle_add_staking,
        "3": _handle_edit,
        "4": _handle_delete,
        "5": _handle_analyze_once,
        "6": _handle_auto_update,
        "7": _handle_view_portfolio_all,
        "8": _handle_view_portfolio_one_wallet,
        "9": _handle_plot,
        "10": _handle_wallet_menu,
        "11": _handle_settings,
        "12": _handle_quit,
    }

    while True:
        print(f"\\n{get_text('menu_title')}")
        print(f"1. {get_text('menu_add_purchase')}")
        print(f"2. {get_text('menu_add_staking')}")
        print(f"3. {get_text('menu_edit_purchase')}")
        print(f"4. {get_text('menu_delete_purchase')}")
        print(f"5. {get_text('menu_analyze_once')}")
        print(f"6. {get_text('menu_auto_update')}")
        print(f"7. {get_text('menu_view_portfolio')}")
        print(f"8. {get_text('menu_view_wallet')}")
        print(f"9. {get_text('menu_plot_coin')}")
        print(f"10. {get_text('menu_wallet_analysis')}")
        print(f"11. {get_text('menu_settings')}")
        print(f"12. {get_text('menu_quit')}")
        choice = input(get_text("menu_choice")).strip()

        handler = actions.get(choice)
        if handler is None:
            print(get_text("menu_invalid"))
            continue
        # Each handler returns True to continue, False to quit the loop
        if not handler():
            break


if __name__ == "__main__":
    main_menu()