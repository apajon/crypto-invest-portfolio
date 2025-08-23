"""Portfolio analysis page for performance metrics and insights."""

import time

import pandas as pd
import streamlit as st

from ...analysis import analyze_portfolio
from ...i18n import get_text
from ...portfolio import load_portfolio


def show_analysis():
    """Display portfolio analysis page."""
    st.header("📈 " + get_text("menu_analyze_once"))

    try:
        df = load_portfolio()

        if df.empty:
            st.info(get_text("empty_for_analysis"))
            st.write(get_text("add_first_purchase"))
            return

        # Analysis options
        col1, col2 = st.columns([3, 1])

        with col1:
            analysis_type = st.radio(
                "Analysis Type",
                ["Single Analysis", "Auto-Update Analysis"],
                horizontal=True
            )

        with col2:
            by_wallet = st.checkbox("Group by Wallet", value=False)

        st.divider()

        if analysis_type == "Single Analysis":
            show_single_analysis(df, by_wallet)
        else:
            show_auto_update_analysis(df, by_wallet)

    except Exception as e:
        st.error(f"Error in analysis: {e!s}")


def show_single_analysis(df: pd.DataFrame, by_wallet: bool = False):
    """Show single portfolio analysis."""
    if st.button("🔄 " + get_text("menu_analyze_once"), type="primary"):
        with st.spinner("Analyzing portfolio..."):
            try:
                # Create containers for output capture
                analysis_container = st.container()

                with analysis_container:
                    st.subheader("Portfolio Analysis Results")

                    # Note: The analyze_portfolio function prints to console
                    # In a real implementation, we'd need to modify it to return data
                    # For now, we'll show a placeholder and the user will see output in console
                    st.info("Analysis running... Check the console/terminal for detailed output.")

                    # Call the analysis function
                    analyze_portfolio(df, by_wallet=by_wallet)

                    st.success("✅ Analysis completed! Check the console for detailed results.")

                    # Show basic portfolio info in Streamlit
                    show_portfolio_summary(df, by_wallet)

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
            max_value=1440,  # 24 hours
            value=15,
            step=1
        )

    with col2:
        max_updates = st.number_input(
            "Maximum number of updates",
            min_value=1,
            max_value=100,
            value=10,
            step=1,
            help="Limit the number of updates to prevent infinite loop"
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
            while (st.session_state.get("auto_update_running", False) and
                   st.session_state.get("update_count", 0) < max_updates):

                current_update = st.session_state.get("update_count", 0) + 1

                with status_placeholder.container():
                    st.info(f"🔄 Running analysis #{current_update}/{max_updates}")

                with progress_placeholder.container():
                    st.progress(current_update / max_updates)

                with results_placeholder.container():
                    st.write(f"**Update #{current_update}** - {time.strftime('%H:%M:%S')}")

                    # Run analysis
                    analyze_portfolio(df, by_wallet=by_wallet)
                    show_portfolio_summary(df, by_wallet)

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


def show_portfolio_summary(df: pd.DataFrame, by_wallet: bool = False):
    """Show a summary of the portfolio in Streamlit."""
    try:
        st.subheader("📊 Portfolio Summary")

        if by_wallet and 'wallet' in df.columns:
            # Group by wallet
            wallet_summary = df.groupby('wallet').agg({
                'amount': 'sum',
                'coin': 'count',
                'symbol': lambda x: ', '.join(x.unique())
            }).round(4)

            wallet_summary.columns = ['Total Amount', 'Number of Purchases', 'Coins']
            st.dataframe(wallet_summary, use_container_width=True)

        else:
            # Overall summary
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                total_purchases = len(df)
                st.metric("Total Purchases", total_purchases)

            with col2:
                unique_coins = df['symbol'].nunique() if 'symbol' in df.columns else 0
                st.metric("Unique Coins", unique_coins)

            with col3:
                if 'wallet' in df.columns:
                    unique_wallets = df['wallet'].nunique()
                    st.metric("Wallets", unique_wallets)

            with col4:
                if 'amount' in df.columns:
                    total_amount = df['amount'].sum()
                    st.metric("Total Amount", f"{total_amount:.4f}")

            # Top coins by amount
            if 'symbol' in df.columns and 'amount' in df.columns:
                st.subheader("Top Coins by Amount")
                top_coins = df.groupby('symbol')['amount'].sum().sort_values(ascending=False).head(10)
                st.bar_chart(top_coins)

            # Portfolio composition
            if 'type' in df.columns:
                st.subheader("Portfolio by Type")
                type_composition = df.groupby('type')['amount'].sum()
                st.pie_chart(type_composition)

    except Exception as e:
        st.error(f"Error creating portfolio summary: {e!s}")
