"""Main Streamlit application for crypto portfolio management."""

import streamlit as st

from crypto_invest_portfolio.constants.enums import Language
from crypto_invest_portfolio.database import init_db
from crypto_invest_portfolio.i18n import get_current_language, get_supported_languages, get_text, set_language
from crypto_invest_portfolio.streamlit_gui.pages import analysis, portfolio_operations, settings, visualization


def setup_page_config():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Crypto Portfolio Tracker",
        page_icon="💰",
        layout="wide",
    )


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "language" not in st.session_state:
        st.session_state.language = get_current_language()


def create_language_selector():
    """Create language selector in sidebar."""
    with st.sidebar:
        st.title("🚀 " + get_text("menu_title"))

        # Language selector
        languages = get_supported_languages()
        language_codes = [lang.value for lang in languages]
        language_names = {"en": "🇺🇸 English", "fr": "🇫🇷 Français"}

        current_lang = st.selectbox(
            "🌐 Language",
            options=language_codes,
            format_func=lambda x: language_names.get(x, x),
            index=(
                language_codes.index(st.session_state.language) if st.session_state.language in language_codes else 0
            ),
            key="language_selector",
        )

        if current_lang != st.session_state.language:
            set_language(Language(current_lang))
            st.session_state.language = current_lang
            st.rerun()


def portfolio_page():
    """Portfolio overview page."""
    portfolio_operations.show_portfolio_view()


def add_purchase_page():
    """Add purchase page."""
    portfolio_operations.show_add_purchase()


def add_staking_page():
    """Add staking page."""
    portfolio_operations.show_add_staking()


def edit_delete_page():
    """Edit/Delete operations page."""
    portfolio_operations.show_edit_delete()


def analysis_page():
    """Analysis page."""
    analysis.show_analysis()


def visualization_page():
    """Visualization page."""
    visualization.show_visualization()


def settings_page():
    """Settings page."""
    settings.show_settings()


def main():
    """Main entry point for the Streamlit application."""
    setup_page_config()
    initialize_session_state()

    # Initialize database
    init_db()

    # Create language selector in sidebar
    create_language_selector()

    # Define pages using st.Page
    pages = {
        get_text("streamlit_menu_portfolio"): [
            st.Page(portfolio_page, title="📊 " + get_text("menu_view_portfolio"), default=True),
        ],
        get_text("streamlit_menu_add_edit"): [
            st.Page(add_purchase_page, title="➕ " + get_text("menu_add_purchase")),  # noqa: RUF001
            st.Page(add_staking_page, title="🎯 " + get_text("menu_add_staking")),
            st.Page(
                edit_delete_page,
                title="✏️ " + get_text("menu_edit_purchase") + " / " + get_text("menu_delete_purchase"),
            ),
        ],
        get_text("streamlit_menu_analysis"): [
            st.Page(analysis_page, title="📈 " + get_text("menu_analyze_once")),
        ],
        get_text("streamlit_menu_visualization"): [
            st.Page(visualization_page, title="📉 " + get_text("menu_plot_coin")),
        ],
        get_text("streamlit_menu_settings"): [
            st.Page(settings_page, title="⚙️ " + get_text("menu_settings")),
        ],
    }

    # Create navigation
    pg = st.navigation(pages, position="top")
    pg.run()


if __name__ == "__main__":
    main()
