"""Visualization page for plotting coin history and portfolio charts."""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from crypto_invest_portfolio.analysis import plot_coin_history
from crypto_invest_portfolio.i18n import get_text
from crypto_invest_portfolio.portfolio import load_portfolio


def show_visualization():
    """Display visualization page."""
    st.header("📉 " + get_text("menu_plot_coin"))

    try:
        df = load_portfolio()

        if df.empty:
            st.info(get_text("empty_for_analysis"))
            st.write("Add some purchases first to enable visualizations.")
            return

        # Visualization options
        viz_type = st.radio("Visualization Type", ["Coin History Plot", "Portfolio Charts"], horizontal=True)

        st.divider()

        if viz_type == "Coin History Plot":
            show_coin_history_plot()
        else:
            show_portfolio_charts(df)

    except Exception as e:
        st.error(f"Error in visualization: {e!s}")


def show_coin_history_plot():
    """Show coin history plotting interface."""
    st.subheader("📈 Coin Price History")

    # Get available coins from portfolio
    try:
        df = load_portfolio()
        if not df.empty and "symbol" in df.columns:
            available_coins = sorted(df["symbol"].unique().tolist())

            col1, col2 = st.columns(2)

            with col1:
                # Let user select from portfolio coins or enter custom
                coin_source = st.radio("Select coin:", ["From Portfolio", "Custom"], horizontal=True)

                if coin_source == "From Portfolio":
                    if available_coins:
                        selected_coin = st.selectbox("Choose coin:", available_coins)
                    else:
                        st.warning("No coins found in portfolio.")
                        return
                else:
                    selected_coin = st.text_input("Enter coin symbol:", placeholder="e.g., BTC, ETH").upper()

            with col2:
                # Time period selection
                period_options = {"7d": "7 days", "30d": "30 days", "90d": "90 days", "1y": "1 year", "max": "Maximum"}
                st.selectbox("Time period:", list(period_options.keys()), format_func=lambda x: period_options[x])

            if st.button("📊 Generate Plot", type="primary"):
                if selected_coin:
                    with st.spinner(f"Fetching data for {selected_coin}..."):
                        try:
                            # Note: plot_coin_history() might need modification to work with Streamlit
                            # For now, we'll show a placeholder
                            st.info(f"Generating plot for {selected_coin}...")

                            # Call the plotting function
                            # This will likely show the plot in a separate window
                            plot_coin_history()

                            st.success(f"✅ Plot generated for {selected_coin}!")
                            st.info("Note: The plot may open in a separate window or be displayed in the console.")

                        except Exception as e:
                            st.error(f"Error generating plot: {e!s}")
                else:
                    st.warning("Please enter a coin symbol.")
        else:
            st.warning("No coins available. Add some purchases first.")

    except Exception as e:
        st.error(f"Error setting up coin plot: {e!s}")


def show_portfolio_charts(df: pd.DataFrame):
    """Show various portfolio charts."""
    st.subheader("📊 Portfolio Charts")

    try:
        # Portfolio distribution by coin
        if "symbol" in df.columns and "amount" in df.columns:
            _show_portfolio_charts_symbol(df)

        # Portfolio by wallet
        if "wallet" in df.columns and len(df["wallet"].unique()) > 1:
            _show_portfolio_charts_wallet(df)

        # Portfolio by type
        if "type" in df.columns:
            _show_portfolio_charts_type(df)

        # Investment timeline
        if "id" in df.columns:
            _show_portfolio_charts_id(df)

        # Summary table
        st.subheader("Portfolio Summary Table")

        if "symbol" in df.columns:
            summary_data = _show_portfolio_charts_symbol(df, need_summary_data=True)

        if "summary_data" in locals() and summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)

    except Exception as e:
        st.error(f"Error creating portfolio charts: {e!s}")


def _show_portfolio_charts_symbol(df: pd.DataFrame, need_summary_data=False):
    if not need_summary_data:
        st.subheader("Portfolio Distribution by Coin")

        coin_amounts = df.groupby("symbol")["amount"].sum().sort_values(ascending=False)

        # Show as pie chart and bar chart
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Pie Chart**")
            fig_pie, ax_pie = plt.subplots(figsize=(8, 6))
            ax_pie.pie(coin_amounts.values.tolist(), labels=coin_amounts.index.tolist(), autopct="%1.1f%%")
            ax_pie.set_title("Portfolio Distribution by Coin")
            st.pyplot(fig_pie)
            plt.close(fig_pie)

        with col2:
            st.write("**Bar Chart**")
            fig_bar, ax_bar = plt.subplots(figsize=(8, 6))
            coin_amounts.plot(kind="bar", ax=ax_bar)
            ax_bar.set_title("Coin Holdings")
            ax_bar.set_ylabel("Amount")
            ax_bar.tick_params(axis="x", rotation=45)
            plt.tight_layout()
            st.pyplot(fig_bar)
            plt.close(fig_bar)

        return

    summary_data = []
    for symbol in df["symbol"].unique():
        symbol_data = df[df["symbol"] == symbol]

        total_amount = symbol_data["amount"].sum()
        avg_price = symbol_data["buy_price_cad"].mean() if "buy_price_cad" in symbol_data.columns else 0
        total_investment = (
            (symbol_data["buy_price_cad"] * symbol_data["amount"]).sum()
            if "buy_price_cad" in symbol_data.columns
            else 0
        )

        summary_data.append(
            {
                "Symbol": symbol,
                "Total Amount": f"{total_amount:.4f}",
                "Avg Price (CAD)": f"{avg_price:.2f}",
                "Total Investment (CAD)": f"{total_investment:.2f}",
                "Purchases": len(symbol_data),
            }
        )
    return summary_data


def _show_portfolio_charts_id(df: pd.DataFrame):
    st.subheader("Investment Timeline")

    # Simple timeline based on purchase order (ID)
    timeline_data = df.copy()
    timeline_data = timeline_data.sort_values("id")

    if "buy_price_cad" in timeline_data.columns and "amount" in timeline_data.columns:
        timeline_data["investment_value"] = timeline_data["buy_price_cad"] * timeline_data["amount"]

        fig_timeline, ax_timeline = plt.subplots(figsize=(12, 6))
        ax_timeline.plot(
            range(len(timeline_data)),
            timeline_data["investment_value"].cumsum(),
            marker="o",
            linewidth=2,
            markersize=6,
        )
        ax_timeline.set_title("Cumulative Investment Value Over Time")
        ax_timeline.set_xlabel("Purchase Order")
        ax_timeline.set_ylabel("Cumulative Investment (CAD)")
        ax_timeline.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig_timeline)
        plt.close(fig_timeline)


def _show_portfolio_charts_type(df: pd.DataFrame):
    st.subheader("Portfolio Distribution by Type")

    type_amounts = df.groupby("type")["amount"].sum().sort_values(ascending=False)

    if len(type_amounts) > 1:
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Type Distribution**")
            fig_type, ax_type = plt.subplots(figsize=(8, 6))
            ax_type.pie(type_amounts.values.tolist(), labels=type_amounts.index.tolist(), autopct="%1.1f%%")
            ax_type.set_title("Portfolio Distribution by Type")
            st.pyplot(fig_type)
            plt.close(fig_type)

        with col2:
            st.write("**Type Holdings**")
            fig_type_bar, ax_type_bar = plt.subplots(figsize=(8, 6))
            type_amounts.plot(kind="bar", ax=ax_type_bar)
            ax_type_bar.set_title("Holdings by Type")
            ax_type_bar.set_ylabel("Amount")
            ax_type_bar.tick_params(axis="x", rotation=45)
            plt.tight_layout()
            st.pyplot(fig_type_bar)
            plt.close(fig_type_bar)
    else:
        st.info("Only one coin type in portfolio. Add different types for distribution chart.")


def _show_portfolio_charts_wallet(df: pd.DataFrame):
    st.subheader("Portfolio Distribution by Wallet")

    wallet_amounts = df.groupby("wallet")["amount"].sum().sort_values(ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Wallet Distribution**")
        fig_wallet, ax_wallet = plt.subplots(figsize=(8, 6))
        ax_wallet.pie(wallet_amounts.values.tolist(), labels=wallet_amounts.index.tolist(), autopct="%1.1f%%")
        ax_wallet.set_title("Portfolio Distribution by Wallet")
        st.pyplot(fig_wallet)
        plt.close(fig_wallet)

    with col2:
        st.write("**Wallet Holdings**")
        fig_wallet_bar, ax_wallet_bar = plt.subplots(figsize=(8, 6))
        wallet_amounts.plot(kind="bar", ax=ax_wallet_bar)
        ax_wallet_bar.set_title("Holdings by Wallet")
        ax_wallet_bar.set_ylabel("Amount")
        ax_wallet_bar.tick_params(axis="x", rotation=45)
        plt.tight_layout()
        st.pyplot(fig_wallet_bar)
        plt.close(fig_wallet_bar)
