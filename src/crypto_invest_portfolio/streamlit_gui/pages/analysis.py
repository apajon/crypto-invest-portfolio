"""Portfolio analysis page for performance metrics and insights."""

import time

import pandas as pd
import streamlit as st

from crypto_invest_portfolio.analysis.operations import _aggregate_by_coin
from crypto_invest_portfolio.i18n import get_text
from crypto_invest_portfolio.portfolio import load_portfolio


def show_analysis():
    """Display portfolio analysis page."""
    st.header("📈 " + get_text("menu_analyze_once"))

    try:
        df = load_portfolio()

        # Show interface even when portfolio is empty, but with warning
        if df.empty:
            st.warning(get_text("empty_for_analysis"))
            st.info(get_text("add_first_purchase"))
            st.write("---")
            st.write("**Preview of Analysis Options** (requires portfolio data):")

        # Analysis options
        analysis_mode = st.radio("Analysis Mode", ["Portfolio Analysis", "Wallet Analysis"], horizontal=True)

        if analysis_mode == "Portfolio Analysis":
            # Original portfolio analysis
            col1, col2 = st.columns([3, 1])

            with col1:
                analysis_type = st.radio("Analysis Type", ["Single Analysis", "Auto-Update Analysis"], horizontal=True)

            with col2:
                by_wallet = st.checkbox("Group by Wallet", value=False)
        else:
            # Wallet analysis options
            st.subheader("🏦 Wallet Analysis Options")
            wallet_analysis_type = st.selectbox(
                "Choose Analysis Type:",
                [
                    "All Wallets (Single Analysis)",
                    "All Wallets (Auto-Update)",
                    "Single Wallet (Single Analysis)",
                    "Single Wallet (Auto-Update)",
                ],
            )

        st.divider()

        if df.empty:
            st.info("Add some purchases to enable analysis functionality.")
            return

        if analysis_mode == "Portfolio Analysis":
            if analysis_type == "Single Analysis":
                show_single_analysis(df, by_wallet)
            else:
                show_auto_update_analysis(df, by_wallet)
        else:
            # Handle wallet analysis
            show_wallet_analysis(df, wallet_analysis_type)

    except Exception as e:
        st.error(f"Error in analysis: {e!s}")


def show_single_analysis(df: pd.DataFrame, by_wallet: bool = False):
    """Show single portfolio analysis."""
    if st.button("🔄 " + get_text("menu_analyze_once"), type="primary"):
        with st.spinner("Analyzing portfolio..."):
            try:
                # Use the same analysis logic as CLI
                df_analysis = _aggregate_by_coin(df, include_wallet=by_wallet)

                if df_analysis.empty:
                    st.warning(get_text("empty_for_analysis"))
                    return

                st.success("✅ Analysis completed! Check the console for detailed results.")

                # Show portfolio analysis table
                show_portfolio_analysis_table(df_analysis, by_wallet)

            except Exception as e:
                st.error(f"Error during analysis: {e!s}")


def show_auto_update_analysis(df: pd.DataFrame, by_wallet: bool = False):
    """Show auto-update portfolio analysis."""
    st.subheader("🔄 Auto-Update Analysis")

    # Auto-update configuration
    col1, col2 = st.columns(2)

    with col1:
        interval_minutes = st.number_input(
            get_text("interval_minutes"),
            min_value=1,
            max_value=1440,
            value=15,
            step=1,  # 24 hours
        )

    with col2:
        max_updates = st.number_input(
            "Maximum number of updates",
            min_value=1,
            max_value=100,
            value=10,
            step=1,
            help="Limit the number of updates to prevent infinite loop",
        )

    # Control buttons
    col1, col2 = st.columns(2)

    with col1:
        start_auto = st.button("▶️ Start Auto-Update", type="primary")

    with col2:
        if st.button("⏹️ Stop Auto-Update"):
            if "auto_update_running" in st.session_state:
                st.session_state.auto_update_running = False
            st.success("Auto-update stopped.")

    if start_auto:
        st.session_state.auto_update_running = True
        st.session_state.update_count = 0

        # Create placeholders for dynamic content
        status_placeholder = st.empty()
        progress_placeholder = st.empty()
        results_placeholder = st.empty()

        try:
            while (
                st.session_state.get("auto_update_running", False)
                and st.session_state.get("update_count", 0) < max_updates
            ):
                current_update = st.session_state.get("update_count", 0) + 1

                with status_placeholder.container():
                    st.info(f"🔄 Running analysis #{current_update}/{max_updates}")

                with progress_placeholder.container():
                    st.progress(current_update / max_updates)

                with results_placeholder.container():
                    st.write(f"**Update #{current_update}** - {time.strftime('%H:%M:%S')}")

                    # Run analysis
                    df_analysis = _aggregate_by_coin(df, include_wallet=by_wallet)
                    if not df_analysis.empty:
                        show_portfolio_analysis_table(df_analysis, by_wallet)

                    st.write(f"Next update in {interval_minutes} minutes...")

                st.session_state.update_count = current_update

                # Wait for the specified interval
                if current_update < max_updates and st.session_state.get("auto_update_running", False):
                    time.sleep(interval_minutes * 60)

        except Exception as e:
            st.error(f"Error during auto-update: {e!s}")
        finally:
            st.session_state.auto_update_running = False
            status_placeholder.success("✅ Auto-update completed.")


def show_wallet_analysis(df: pd.DataFrame, wallet_analysis_type: str):
    """Show wallet-specific analysis options."""
    if df.empty:
        st.warning(get_text("empty_for_analysis"))
        return

    if "wallet" not in df.columns or df["wallet"].isna().all():
        st.warning("No wallet information available in the portfolio.")
        return

    available_wallets = sorted(df["wallet"].dropna().unique().tolist())

    if wallet_analysis_type == "All Wallets (Single Analysis)":
        show_all_wallets_single_analysis(df)
    elif wallet_analysis_type == "All Wallets (Auto-Update)":
        show_all_wallets_auto_update(df)
    elif wallet_analysis_type == "Single Wallet (Single Analysis)":
        show_single_wallet_analysis(df, available_wallets)
    elif wallet_analysis_type == "Single Wallet (Auto-Update)":
        show_single_wallet_auto_update(df, available_wallets)


def show_all_wallets_single_analysis(df: pd.DataFrame):
    """Show analysis for all wallets."""
    if st.button("🔄 Analyze All Wallets", type="primary"):
        with st.spinner("Analyzing all wallets..."):
            try:
                # Group by wallet and analyze
                df_analysis = _aggregate_by_coin(df, include_wallet=True)

                if df_analysis.empty:
                    st.warning(get_text("empty_for_analysis"))
                    return

                st.success("✅ Analysis completed for all wallets!")
                show_portfolio_analysis_table(df_analysis, by_wallet=True)

            except Exception as e:
                st.error(f"Error during wallet analysis: {e!s}")


def show_all_wallets_auto_update(df: pd.DataFrame):
    """Show auto-update analysis for all wallets."""
    st.subheader("🔄 Auto-Update All Wallets")

    interval_minutes = st.number_input("Interval in minutes:", min_value=1, max_value=1440, value=15, step=1)

    max_updates = st.number_input("Maximum number of updates:", min_value=1, max_value=100, value=10, step=1)

    col1, col2 = st.columns(2)

    with col1:
        start_auto = st.button("▶️ Start Auto-Update All Wallets", type="primary")

    with col2:
        if st.button("⏹️ Stop Auto-Update"):
            if "wallet_auto_update_running" in st.session_state:
                st.session_state.wallet_auto_update_running = False
            st.success("Auto-update stopped.")

    if start_auto:
        st.session_state.wallet_auto_update_running = True
        st.session_state.wallet_update_count = 0

        status_placeholder = st.empty()
        progress_placeholder = st.empty()
        results_placeholder = st.empty()

        try:
            while (
                st.session_state.get("wallet_auto_update_running", False)
                and st.session_state.get("wallet_update_count", 0) < max_updates
            ):
                current_update = st.session_state.get("wallet_update_count", 0) + 1

                with status_placeholder.container():
                    st.info(f"🔄 Running wallet analysis #{current_update}/{max_updates}")

                with progress_placeholder.container():
                    st.progress(current_update / max_updates)

                with results_placeholder.container():
                    st.write(f"**Wallet Analysis Update #{current_update}** - {time.strftime('%H:%M:%S')}")

                    df_analysis = _aggregate_by_coin(df, include_wallet=True)
                    if not df_analysis.empty:
                        show_portfolio_analysis_table(df_analysis, by_wallet=True)

                    st.write(f"Next update in {interval_minutes} minutes...")

                st.session_state.wallet_update_count = current_update

                if current_update < max_updates and st.session_state.get("wallet_auto_update_running", False):
                    time.sleep(interval_minutes * 60)

        except Exception as e:
            st.error(f"Error during auto-update: {e!s}")
        finally:
            st.session_state.wallet_auto_update_running = False
            status_placeholder.success("✅ Auto-update completed.")


def show_single_wallet_analysis(df: pd.DataFrame, available_wallets: list):
    """Show analysis for a single selected wallet."""
    st.subheader("🏦 Single Wallet Analysis")

    if not available_wallets:
        st.warning("No wallets available for analysis.")
        return

    st.write("**Available wallets:**", ", ".join(available_wallets))

    selected_wallet = st.selectbox("Choose a wallet:", available_wallets, key="single_wallet_selector")

    if st.button(f"🔄 Analyze Wallet: {selected_wallet}", type="primary"):
        with st.spinner(f"Analyzing wallet {selected_wallet}..."):
            try:
                # Filter by selected wallet
                df_wallet = df[df["wallet"] == selected_wallet]

                if df_wallet.empty:
                    st.warning(f"No purchases found for wallet '{selected_wallet}'.")
                    return

                df_analysis = _aggregate_by_coin(df_wallet, include_wallet=True)

                if df_analysis.empty:
                    st.warning(f"No analysis data for wallet '{selected_wallet}'.")
                    return

                st.success(f"✅ Analysis completed for wallet '{selected_wallet}'!")
                show_portfolio_analysis_table(df_analysis, by_wallet=True)

            except Exception as e:
                st.error(f"Error during wallet analysis: {e!s}")


def show_single_wallet_auto_update(df: pd.DataFrame, available_wallets: list):
    """Show auto-update analysis for a single selected wallet."""
    st.subheader("🔄 Auto-Update Single Wallet")

    if not available_wallets:
        st.warning("No wallets available for analysis.")
        return

    col1, col2 = st.columns(2)

    with col1:
        selected_wallet = st.selectbox("Choose a wallet:", available_wallets, key="auto_wallet_selector")

    with col2:
        interval_minutes = st.number_input(
            "Interval (minutes):", min_value=1, max_value=1440, value=15, step=1, key="wallet_interval"
        )

    max_updates = st.number_input(
        "Maximum updates:", min_value=1, max_value=100, value=10, step=1, key="wallet_max_updates"
    )

    col1, col2 = st.columns(2)

    with col1:
        start_auto = st.button(f"▶️ Start Auto-Update: {selected_wallet}", type="primary")

    with col2:
        if st.button("⏹️ Stop Auto-Update", key="stop_wallet_auto"):
            if "single_wallet_auto_running" in st.session_state:
                st.session_state.single_wallet_auto_running = False
            st.success("Auto-update stopped.")

    if start_auto:
        # Filter by selected wallet
        df_wallet = df[df["wallet"] == selected_wallet]

        if df_wallet.empty:
            st.warning(f"No purchases found for wallet '{selected_wallet}'.")
            return

        st.session_state.single_wallet_auto_running = True
        st.session_state.single_wallet_update_count = 0

        status_placeholder = st.empty()
        progress_placeholder = st.empty()
        results_placeholder = st.empty()

        try:
            while (
                st.session_state.get("single_wallet_auto_running", False)
                and st.session_state.get("single_wallet_update_count", 0) < max_updates
            ):
                current_update = st.session_state.get("single_wallet_update_count", 0) + 1

                with status_placeholder.container():
                    st.info(f"🔄 Running analysis for {selected_wallet} #{current_update}/{max_updates}")

                with progress_placeholder.container():
                    st.progress(current_update / max_updates)

                with results_placeholder.container():
                    st.write(f"**{selected_wallet} Analysis Update #{current_update}** - {time.strftime('%H:%M:%S')}")

                    df_analysis = _aggregate_by_coin(df_wallet, include_wallet=True)
                    if not df_analysis.empty:
                        show_portfolio_analysis_table(df_analysis, by_wallet=True)

                    st.write(f"Next update in {interval_minutes} minutes...")

                st.session_state.single_wallet_update_count = current_update

                if current_update < max_updates and st.session_state.get("single_wallet_auto_running", False):
                    time.sleep(interval_minutes * 60)

        except Exception as e:
            st.error(f"Error during auto-update: {e!s}")
        finally:
            st.session_state.single_wallet_auto_running = False
            status_placeholder.success("✅ Auto-update completed.")


def show_portfolio_analysis_table(df_analysis: pd.DataFrame, by_wallet: bool = False):
    """Display the portfolio analysis table with color coding like CLI."""
    try:
        st.subheader("📊 Portfolio Analysis Results")

        df_display = _prepare_display_dataframe(df_analysis, by_wallet)
        if df_display is None:
            st.warning("No data columns available for display.")
            return

        styled_df = _style_dataframe(df_display)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # Show portfolio summary metrics
        show_portfolio_metrics(df_analysis)

    except Exception as e:
        st.error(f"Error creating analysis table: {e!s}")


def _style_dataframe(df_display: pd.DataFrame) -> pd.io.formats.style.Styler | pd.DataFrame:
    """Apply color styling to the dataframe."""

    def color_pct_change(val):
        if pd.isna(val):
            return ""
        try:
            numeric_val = float(val.replace("%", ""))
            if numeric_val > 0:
                return "color: green"
            elif numeric_val < 0:
                return "color: red"
            else:
                return "color: black"
        except Exception:
            return ""

    if "% Change Net" in df_display.columns:
        return df_display.style.applymap(color_pct_change, subset=["% Change Net"])
    return df_display


def _prepare_display_dataframe(df_analysis: pd.DataFrame, by_wallet: bool) -> pd.DataFrame | None:
    """Prepare dataframe with selected columns and formatting."""
    columns_to_show = _columns_to_show(by_wallet)

    # Filter to available columns
    available_cols = [c for c in columns_to_show if c in df_analysis.columns]

    if not available_cols:
        st.warning("No data columns available for display.")
        return None

        # Create a styled dataframe for display
    df_display = df_analysis[available_cols].copy()

    # Format numeric columns
    numeric_format_cols = {
        "Amount": "{:.8f}",
        "Avg Buy Price CAD": "{:.6f}",
        "Current Price CAD": "{:.2f}",
        "Invested Value CAD (incl. frais)": "{:.2f}",
        "Current Value CAD (net)": "{:.2f}",
        "% Change Net": "{:.2f}%",
    }

    for col, fmt in numeric_format_cols.items():
        if col in df_display.columns:
            _format_numeric_column(df_display, col, fmt)
    return df_display


def _format_numeric_column(df_display, col, fmt):
    if col == "% Change Net":
        df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}%")
    else:
        df_display[col] = df_display[col].apply(lambda x, fmt=fmt: fmt.format(x))


def _columns_to_show(by_wallet):
    if by_wallet:
        columns_to_show = [
            "Wallet",
            "Coin",
            "Amount",
            "Avg Buy Price CAD",
            "Current Price CAD",
            "Invested Value CAD (incl. frais)",
            "Current Value CAD (net)",
            "% Change Net",
        ]
    else:
        columns_to_show = [
            "Coin",
            "Amount",
            "Avg Buy Price CAD",
            "Current Price CAD",
            "Invested Value CAD (incl. frais)",
            "Current Value CAD (net)",
            "% Change Net",
        ]

    return columns_to_show


def show_portfolio_metrics(df_analysis: pd.DataFrame):
    """Show key portfolio metrics."""
    try:
        if df_analysis.empty:
            return

        st.subheader("📈 Portfolio Metrics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_invested = df_analysis["Invested Value CAD (incl. frais)"].sum()
            st.metric("Total Invested", f"${total_invested:,.2f} CAD")

        with col2:
            total_current = df_analysis["Current Value CAD (net)"].sum()
            st.metric("Total Current Value", f"${total_current:,.2f} CAD")

        with col3:
            total_change = total_current - total_invested
            st.metric("Total P&L", f"${total_change:,.2f} CAD")

        with col4:
            total_pct_change = (total_change / total_invested * 100) if total_invested > 0 else 0
            st.metric("Total % Change", f"{total_pct_change:.2f}%")

        # Show breakdown by type if available
        if "Type" in df_analysis.columns:
            st.subheader("📊 Portfolio by Type")
            type_summary = (
                df_analysis.groupby("Type")
                .agg({"Invested Value CAD (incl. frais)": "sum", "Current Value CAD (net)": "sum"})
                .round(2)
            )

            type_summary["P&L"] = (
                type_summary["Current Value CAD (net)"] - type_summary["Invested Value CAD (incl. frais)"]
            )
            type_summary["% Change"] = (
                type_summary["P&L"] / type_summary["Invested Value CAD (incl. frais)"] * 100
            ).round(2)

            st.dataframe(type_summary, use_container_width=True)

    except Exception as e:
        st.error(f"Error creating portfolio metrics: {e!s}")
