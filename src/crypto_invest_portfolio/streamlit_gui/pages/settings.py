"""Settings page for application configuration."""

import os
import sqlite3

import streamlit as st

from crypto_invest_portfolio.constants.config import DB_FILE
from crypto_invest_portfolio.i18n import get_current_language, get_supported_languages, get_text, set_language


def show_settings():
    """Display settings page."""
    st.header("⚙️ " + get_text("menu_settings"))

    # Language settings
    show_language_settings()

    st.divider()

    # Database settings
    show_database_settings()

    st.divider()

    # Application info
    show_application_info()


def show_language_settings():
    """Show language configuration."""
    st.subheader("🌐 " + get_text("settings_language"))

    languages = get_supported_languages()
    language_codes = [lang.value for lang in languages]
    current_lang = get_current_language()

    language_names = {"en": "🇺🇸 English", "fr": "🇫🇷 Français"}

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Current Language:** {language_names.get(current_lang, current_lang)}")

        new_language = st.selectbox(
            "Select Language:",
            options=language_codes,
            format_func=lambda x: language_names.get(x, x),
            index=language_codes.index(current_lang) if current_lang in language_codes else 0,
            key="settings_language_selector",
        )

        if st.button("🔄 Apply Language Change"):
            if new_language != current_lang:
                set_language(new_language)
                st.success(f"Language changed to {language_names.get(new_language, new_language)}")
                st.info("Page will reload to apply changes...")
                st.rerun()
            else:
                st.info("Language is already set to the selected option.")

    with col2:
        st.write("**Available Languages:**")
        for lang_code, lang_name in language_names.items():
            if lang_code in language_codes:
                status = "✅ Current" if lang_code == current_lang else "⚪ Available"
                st.write(f"{status} {lang_name}")


def show_database_settings():
    """Show database information and management."""
    st.subheader("🗃️ Database Settings")

    try:
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Database Information:**")

            # Check if database exists
            if os.path.exists(DB_FILE):
                st.write(f"✅ Database file: `{DB_FILE}`")

                # Get file size
                file_size = os.path.getsize(DB_FILE)
                st.write(f"📁 File size: {file_size:,} bytes")

                # Get row counts
                conn = sqlite3.connect(DB_FILE)

                # Check portfolio table
                try:
                    portfolio_count = conn.execute("SELECT COUNT(*) FROM portfolio").fetchone()[0]
                    st.write(f"📊 Portfolio entries: {portfolio_count}")
                except sqlite3.OperationalError:
                    st.write("📊 Portfolio entries: Table not found")

                # Check history table
                try:
                    history_count = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
                    st.write(f"📈 History entries: {history_count}")
                except sqlite3.OperationalError:
                    st.write("📈 History entries: Table not found")

                conn.close()

            else:
                st.write(f"❌ Database file not found: `{DB_FILE}`")
                if st.button("🔄 Initialize Database"):
                    from ...database import init_db

                    init_db()
                    st.success("Database initialized!")
                    st.rerun()

        with col2:
            st.write("**Database Actions:**")

            # Show database schema
            if st.button("📋 Show Database Schema"):
                if os.path.exists(DB_FILE):
                    show_database_schema()
                else:
                    st.error("Database file not found.")

            # Export data (basic JSON export)
            if st.button("💾 Export Portfolio Data"):
                export_portfolio_data()

            # Database maintenance
            if st.button("🧹 Vacuum Database"):
                vacuum_database()

    except Exception as e:
        st.error(f"Error accessing database: {e!s}")


def show_database_schema():
    """Display database schema information."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        st.subheader("Database Schema")

        for table in tables:
            table_name = table[0]
            st.write(f"**Table: {table_name}**")

            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            schema_data = []
            for col in columns:
                schema_data.append(
                    {
                        "Column": col[1],
                        "Type": col[2],
                        "Not Null": "Yes" if col[3] else "No",
                        "Default": col[4] if col[4] is not None else "None",
                        "Primary Key": "Yes" if col[5] else "No",
                    }
                )

            st.dataframe(schema_data, use_container_width=True)
            st.write("")

        conn.close()

    except Exception as e:
        st.error(f"Error retrieving schema: {e!s}")


def export_portfolio_data():
    """Export portfolio data as JSON."""
    try:
        from ...portfolio import load_portfolio

        df = load_portfolio()

        if df.empty:
            st.warning("No portfolio data to export.")
            return

        # Convert to JSON
        json_data = df.to_json(orient="records", indent=2)

        # Create download button
        st.download_button(
            label="📥 Download Portfolio JSON",
            data=json_data,
            file_name="portfolio_export.json",
            mime="application/json",
        )

        st.success(f"Portfolio data ready for download ({len(df)} entries)")

    except Exception as e:
        st.error(f"Error exporting data: {e!s}")


def vacuum_database():
    """Vacuum the database to optimize it."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("VACUUM;")
        conn.close()

        st.success("✅ Database vacuumed successfully!")

    except Exception as e:
        st.error(f"Error vacuuming database: {e!s}")


def show_application_info():
    """Show application information."""
    st.subheader("ℹ️ Application Information")  # noqa: RUF001

    col1, col2 = st.columns(2)

    with col1:
        st.write("**About Crypto Portfolio Tracker**")
        st.write("A comprehensive tool for managing and analyzing cryptocurrency investments.")
        st.write("")
        st.write("**Features:**")
        st.write("• Portfolio management (add/edit/delete)")
        st.write("• Real-time price analysis")
        st.write("• Interactive visualizations")
        st.write("• Multi-language support")
        st.write("• Wallet-based organization")
        st.write("• Historical tracking")

    with col2:
        st.write("**Technical Details:**")

        # Python version
        import sys

        st.write(f"🐍 Python: {sys.version.split()[0]}")

        # Streamlit version
        import streamlit as st_version

        st.write(f"🚀 Streamlit: {st_version.__version__}")

        # Pandas version
        import pandas as pd

        st.write(f"📊 Pandas: {pd.__version__}")

        # Matplotlib version
        import matplotlib

        st.write(f"📈 Matplotlib: {matplotlib.__version__}")

        st.write("")
        st.write("**Data Storage:**")
        st.write("📁 Database: SQLite")
        st.write(f"📍 Location: `{DB_FILE}`")

    # Credits and links
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**CLI Version**")
        st.write("This GUI is based on the CLI crypto portfolio application.")

    with col2:
        st.write("**Data Source**")
        st.write("Price data provided by CoinGecko API")

    with col3:
        st.write("**Open Source**")
        st.write("Built with open-source technologies")
