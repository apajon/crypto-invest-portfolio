"""Main Streamlit application for crypto portfolio management."""

import streamlit as st

from ..database import init_db
from ..i18n import get_current_language, get_supported_languages, get_text, set_language
from .pages import analysis, portfolio_operations, settings, visualization


def setup_page_config():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Crypto Portfolio Tracker",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "language" not in st.session_state:
        st.session_state.language = get_current_language()
    if "page" not in st.session_state:
        st.session_state.page = "portfolio"


def create_sidebar_navigation():
    """Create sidebar navigation menu."""
    with st.sidebar:
        st.title("🚀 " + get_text("menu_title"))

        # Language selector
        languages = get_supported_languages()
        language_names = {
            "en": "🇺🇸 English",
            "fr": "🇫🇷 Français"
        }

        current_lang = st.selectbox(
            "🌐 Language",
            options=list(languages.keys()),
            format_func=lambda x: language_names.get(x, x),
            index=list(languages.keys()).index(st.session_state.language),
            key="language_selector"
        )

        if current_lang != st.session_state.language:
            set_language(current_lang)
            st.session_state.language = current_lang
            st.rerun()

        st.divider()

        # Navigation menu
        menu_options = {
            "portfolio": "📊 " + get_text("menu_view_portfolio"),
            "add_purchase": "➕ " + get_text("menu_add_purchase"),
            "add_staking": "🎯 " + get_text("menu_add_staking"),
            "edit_delete": "✏️ " + get_text("menu_edit_purchase") + " / " + get_text("menu_delete_purchase"),
            "analysis": "📈 " + get_text("menu_analyze_once"),
            "visualization": "📉 " + get_text("menu_plot_coin"),
            "settings": "⚙️ " + get_text("menu_settings"),
        }

        selected_page = st.radio(
            "Navigation",
            options=list(menu_options.keys()),
            format_func=lambda x: menu_options[x],
            index=list(menu_options.keys()).index(st.session_state.page) if st.session_state.page in menu_options else 0,
            label_visibility="collapsed"
        )

        if selected_page != st.session_state.page:
            st.session_state.page = selected_page
            st.rerun()


def render_main_content():
    """Render the main content area based on selected page."""
    page = st.session_state.page

    if page == "portfolio":
        portfolio_operations.show_portfolio_view()
    elif page == "add_purchase":
        portfolio_operations.show_add_purchase()
    elif page == "add_staking":
        portfolio_operations.show_add_staking()
    elif page == "edit_delete":
        portfolio_operations.show_edit_delete()
    elif page == "analysis":
        analysis.show_analysis()
    elif page == "visualization":
        visualization.show_visualization()
    elif page == "settings":
        settings.show_settings()
    else:
        st.error(f"Unknown page: {page}")


def main():
    """Main entry point for the Streamlit application."""
    setup_page_config()
    initialize_session_state()

    # Initialize database
    init_db()

    # Create layout
    create_sidebar_navigation()
    render_main_content()


if __name__ == "__main__":
    main()
