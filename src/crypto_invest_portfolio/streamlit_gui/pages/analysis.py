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


def show_portfolio_analysis_table(df_analysis: pd.DataFrame, by_wallet: bool = False):
    """Display the portfolio analysis table with color coding like CLI."""
    try:
        st.subheader("📊 Portfolio Analysis Results")

        # Prepare the table columns based on by_wallet flag
        if by_wallet:
            columns_to_show = [
                "Wallet",
                "Coin", 
                "Amount",
                "Avg Buy Price CAD",
                "Current Price CAD", 
                "Invested Value CAD (incl. frais)",
                "Current Value CAD (net)",
                "% Change Net"
            ]
        else:
            columns_to_show = [
                "Coin",
                "Amount", 
                "Avg Buy Price CAD",
                "Current Price CAD",
                "Invested Value CAD (incl. frais)",
                "Current Value CAD (net)", 
                "% Change Net"
            ]

        # Filter to available columns
        available_cols = [c for c in columns_to_show if c in df_analysis.columns]
        
        if not available_cols:
            st.warning("No data columns available for display.")
            return

        # Create a styled dataframe for display
        df_display = df_analysis[available_cols].copy()
        
        # Format numeric columns
        numeric_format_cols = {
            "Amount": "{:.8f}",
            "Avg Buy Price CAD": "{:.6f}", 
            "Current Price CAD": "{:.2f}",
            "Invested Value CAD (incl. frais)": "{:.2f}",
            "Current Value CAD (net)": "{:.2f}",
            "% Change Net": "{:.2f}%"
        }
        
        for col, fmt in numeric_format_cols.items():
            if col in df_display.columns:
                if col == "% Change Net":
                    df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}%")
                else:
                    df_display[col] = df_display[col].apply(lambda x: fmt.format(x))

        # Apply color styling to % Change Net column using Streamlit's style API
        def color_pct_change(val):
            """Color the percentage change column."""
            if pd.isna(val):
                return ""
            # Extract numeric value from formatted string
            try:
                numeric_val = float(val.replace('%', ''))
                if numeric_val > 0:
                    return "color: green"
                elif numeric_val < 0:
                    return "color: red"
                else:
                    return "color: black"
            except:
                return ""

        # Style the dataframe
        if "% Change Net" in df_display.columns:
            styled_df = df_display.style.applymap(
                color_pct_change, 
                subset=["% Change Net"]
            )
        else:
            styled_df = df_display

        # Display the table
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # Show portfolio summary metrics
        show_portfolio_metrics(df_analysis)

    except Exception as e:
        st.error(f"Error creating analysis table: {e!s}")


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
            color = "normal" if total_pct_change >= 0 else "inverse"
            st.metric("Total % Change", f"{total_pct_change:.2f}%")

        # Show breakdown by type if available
        if "Type" in df_analysis.columns:
            st.subheader("📊 Portfolio by Type")
            type_summary = df_analysis.groupby("Type").agg({
                "Invested Value CAD (incl. frais)": "sum",
                "Current Value CAD (net)": "sum"
            }).round(2)
            
            type_summary["P&L"] = type_summary["Current Value CAD (net)"] - type_summary["Invested Value CAD (incl. frais)"]
            type_summary["% Change"] = (type_summary["P&L"] / type_summary["Invested Value CAD (incl. frais)"] * 100).round(2)
            
            st.dataframe(type_summary, use_container_width=True)

    except Exception as e:
        st.error(f"Error creating portfolio metrics: {e!s}")
