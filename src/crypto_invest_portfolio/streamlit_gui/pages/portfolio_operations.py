"""Portfolio operations page for adding, editing, and viewing portfolio data."""

import sqlite3

import streamlit as st
from streamlit_tags import st_tags

from crypto_invest_portfolio.constants.config import DB_FILE
from crypto_invest_portfolio.constants.enums import CoinType
from crypto_invest_portfolio.i18n import get_text
from crypto_invest_portfolio.portfolio import load_portfolio


def get_symbol_suggestions():
    """Get existing symbols from the portfolio database for autocomplete."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        # Get unique symbols and coin names
        c.execute("SELECT DISTINCT symbol FROM portfolio WHERE symbol IS NOT NULL AND symbol != ''")
        symbols = [row[0] for row in c.fetchall()]

        conn.close()
        return sorted(symbols)
    except Exception:
        return []


def get_coin_suggestions():
    """Get existing coin names from the portfolio database for autocomplete."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        c.execute("SELECT DISTINCT coin FROM portfolio WHERE coin IS NOT NULL AND coin != ''")
        coins = [row[0] for row in c.fetchall()]

        conn.close()
        return sorted(coins)
    except Exception:
        return []


def get_wallet_suggestions():
    """Get existing wallet names from the portfolio database for autocomplete."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        c.execute("SELECT DISTINCT wallet FROM portfolio WHERE wallet IS NOT NULL AND wallet != ''")
        wallets = [row[0] for row in c.fetchall()]

        conn.close()
        return sorted(wallets)
    except Exception:
        return []


def show_portfolio_view():
    """Display the portfolio overview."""
    st.header("📊 " + get_text("menu_view_portfolio"))

    try:
        df = load_portfolio()

        if df.empty:
            st.info(get_text("empty_for_analysis"))
            st.write(get_text("add_first_purchase"))
        else:
            # Display portfolio statistics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Coins", len(df))

            with col2:
                total_amount = df["amount"].sum() if "amount" in df.columns else 0
                st.metric("Total Amount", f"{total_amount:.2f}")

            with col3:
                unique_coins = df["coin"].nunique() if "coin" in df.columns else 0
                st.metric("Unique Coins", unique_coins)

            with col4:
                if "wallet" in df.columns:
                    unique_wallets = df["wallet"].nunique()
                    st.metric("Wallets", unique_wallets)

            st.divider()

            # Display the dataframe
            st.subheader("Portfolio Details")
            st.dataframe(df, use_container_width=True)

            # Filter by wallet if wallets exist
            if "wallet" in df.columns and len(df["wallet"].unique()) > 1:
                st.subheader("Filter by Wallet")
                wallets = ["All", *sorted(df["wallet"].unique().tolist())]
                selected_wallet = st.selectbox("Select Wallet", wallets)

                if selected_wallet != "All":
                    filtered_df = df[df["wallet"] == selected_wallet]
                    st.dataframe(filtered_df, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading portfolio: {e!s}")


def show_add_purchase():
    """Display the add purchase form."""
    st.header("➕ " + get_text("menu_add_purchase"))  # noqa: RUF001

    # Get separate autocomplete suggestions
    symbol_suggestions = get_symbol_suggestions()
    coin_suggestions = get_coin_suggestions()
    wallet_suggestions = get_wallet_suggestions()

    with st.form("add_purchase_form"):
        col1, col2 = st.columns(2)

        with col1:
            # Symbol field first (before Coin Name) with streamlit-tags
            symbol_tags = st_tags(
                label=get_text("coin_symbol"),
                text="Enter symbol (e.g., BTC)",
                value=[],
                suggestions=symbol_suggestions,
                maxtags=1,  # Single tag selection
                key="symbol_input",
            )
            symbol = symbol_tags[0].upper() if symbol_tags else ""

            # Coin Name field with streamlit-tags
            coin_tags = st_tags(
                label=get_text("coin_name"),
                text="Enter coin name (e.g., Bitcoin)",
                value=[],
                suggestions=coin_suggestions,
                maxtags=1,  # Single tag selection
                key="coin_input",
            )
            coin = coin_tags[0] if coin_tags else ""

            amount = st.number_input(get_text("amount"), min_value=0.0, step=0.0001, format="%.8f")
            buy_price_cad = st.number_input(get_text("buy_price_cad"), min_value=0.0, step=0.01, format="%.2f")

        with col2:
            fee_buy_percent = st.number_input(
                get_text("buy_fee_percent"), min_value=0.0, max_value=100.0, step=0.01, format="%.2f"
            )
            fee_sell_percent = st.number_input(
                get_text("sell_fee_percent"), min_value=0.0, max_value=100.0, step=0.01, format="%.2f"
            )
            type_options = [t.value for t in CoinType]
            type_ = st.selectbox(get_text("coin_type"), type_options, index=0)
            
            # Wallet field with streamlit-tags
            wallet_tags = st_tags(
                label=get_text("wallet"),
                text="Enter wallet (e.g., kraken, binance)",
                value=[],
                suggestions=wallet_suggestions,
                maxtags=1,  # Single tag selection
                key="wallet_input",
            )
            wallet = wallet_tags[0] if wallet_tags else ""

        submitted = st.form_submit_button("💾 " + get_text("add_purchase"))

        if submitted:
            if not all([coin, symbol, amount > 0, buy_price_cad > 0, wallet]):
                st.error("Please fill in all required fields.")
            else:
                try:
                    # Add to database
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute(
                        """
                        INSERT INTO portfolio (coin, symbol, amount, buy_price_cad, fee_buy_percent, fee_sell_percent, type, wallet)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (coin, symbol, amount, buy_price_cad, fee_buy_percent, fee_sell_percent, type_, wallet),
                    )
                    conn.commit()
                    conn.close()

                    st.success(get_text("success_purchase_added", symbol, amount, buy_price_cad))
                    st.balloons()

                except Exception as e:
                    st.error(f"Error adding purchase: {e!s}")


def show_add_staking():
    """Display the add staking gain form."""
    st.header("🎯 " + get_text("menu_add_staking"))

    # Get separate autocomplete suggestions
    symbol_suggestions = get_symbol_suggestions()
    coin_suggestions = get_coin_suggestions()
    wallet_suggestions = get_wallet_suggestions()

    with st.form("add_staking_form"):
        col1, col2 = st.columns(2)

        with col1:
            # Symbol field first (before Coin Name) with streamlit-tags
            symbol_tags = st_tags(
                label=get_text("coin_symbol"),
                text="Enter symbol (e.g., ETH)",
                value=[],
                suggestions=symbol_suggestions,
                maxtags=1,  # Single tag selection
                key="staking_symbol_input",
            )
            symbol = symbol_tags[0].upper() if symbol_tags else ""

            # Coin Name field with streamlit-tags
            coin_tags = st_tags(
                label=get_text("coin_name"),
                text="Enter coin name (e.g., Ethereum)",
                value=[],
                suggestions=coin_suggestions,
                maxtags=1,  # Single tag selection
                key="staking_coin_input",
            )
            coin = coin_tags[0] if coin_tags else ""

            amount = st.number_input(get_text("amount"), min_value=0.0, step=0.0001, format="%.8f")

        with col2:
            type_options = [t.value for t in CoinType]
            type_ = st.selectbox(get_text("coin_type"), type_options, index=0)
            
            # Wallet field with streamlit-tags
            wallet_tags = st_tags(
                label=get_text("wallet"),
                text="Enter wallet (e.g., kraken, binance)",
                value=[],
                suggestions=wallet_suggestions,
                maxtags=1,  # Single tag selection
                key="staking_wallet_input",
            )
            wallet = wallet_tags[0] if wallet_tags else ""

        submitted = st.form_submit_button("💰 " + "Add Staking Gain")

        if submitted:
            if not all([coin, symbol, amount > 0, wallet]):
                st.error("Please fill in all required fields.")
            else:
                try:
                    # Add staking gain to database
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute(
                        """
                        INSERT INTO portfolio (coin, symbol, amount, buy_price_cad, fee_buy_percent, fee_sell_percent, type, wallet, entry_kind)
                        VALUES (?, ?, ?, 0, 0, 0, ?, ?, 'staking')
                        """,
                        (coin, symbol, amount, type_, wallet),
                    )
                    conn.commit()
                    conn.close()

                    st.success(get_text("success_staking_added", symbol, amount))
                    st.balloons()

                except Exception as e:
                    st.error(f"Error adding staking gain: {e!s}")


def show_edit_delete():
    """Display the edit/delete interface."""
    st.header("✏️ " + get_text("menu_edit_purchase") + " / " + get_text("menu_delete_purchase"))

    try:
        df = load_portfolio()

        if df.empty:
            st.info(get_text("empty_for_analysis"))
            return

        # Select purchase to edit/delete
        st.subheader("Select Purchase")

        # Create a readable display of purchases
        display_df = df.copy()
        if "id" in display_df.columns:
            display_df["Display"] = display_df.apply(
                lambda row: f"ID {row['id']}: {row.get('symbol', 'N/A')} - {row.get('amount', 0):.4f} @ {row.get('buy_price_cad', 0):.2f} CAD ({row.get('wallet', 'N/A')})",
                axis=1,
            )

            selected_row = st.selectbox(
                "Choose purchase to edit/delete:",
                options=range(len(display_df)),
                format_func=lambda i: display_df.iloc[i]["Display"],
            )

            if selected_row is not None:
                row = display_df.iloc[selected_row]

                col1, col2 = st.columns(2)

                # Edit form
                with col1:
                    st.subheader("✏️ Edit Purchase")

                    # Get separate autocomplete suggestions for edit form
                    symbol_suggestions = get_symbol_suggestions()
                    coin_suggestions = get_coin_suggestions()
                    wallet_suggestions = get_wallet_suggestions()

                    with st.form("edit_purchase_form"):
                        # Symbol field first (before Coin Name) with streamlit-tags
                        symbol_tags = st_tags(
                            label="Symbol",
                            text="Enter symbol",
                            value=[row.get("symbol", "")] if row.get("symbol") else [],
                            suggestions=symbol_suggestions,
                            maxtags=1,  # Single tag selection
                            key="edit_symbol_input",
                        )
                        symbol = symbol_tags[0].upper() if symbol_tags else ""

                        # Coin Name field with streamlit-tags
                        coin_tags = st_tags(
                            label="Coin Name",
                            text="Enter coin name",
                            value=[row.get("coin", "")] if row.get("coin") else [],
                            suggestions=coin_suggestions,
                            maxtags=1,  # Single tag selection
                            key="edit_coin_input",
                        )
                        coin = coin_tags[0] if coin_tags else ""

                        amount = st.number_input(
                            "Amount", value=float(row.get("amount", 0)), min_value=0.0, step=0.0001, format="%.8f"
                        )
                        buy_price_cad = st.number_input(
                            "Buy Price (CAD)",
                            value=float(row.get("buy_price_cad", 0)),
                            min_value=0.0,
                            step=0.01,
                            format="%.2f",
                        )
                        fee_buy_percent = st.number_input(
                            "Buy Fee (%)",
                            value=float(row.get("fee_buy_percent", 0)),
                            min_value=0.0,
                            max_value=100.0,
                            step=0.01,
                            format="%.2f",
                        )
                        fee_sell_percent = st.number_input(
                            "Sell Fee (%)",
                            value=float(row.get("fee_sell_percent", 0)),
                            min_value=0.0,
                            max_value=100.0,
                            step=0.01,
                            format="%.2f",
                        )

                        type_options = [t.value for t in CoinType]
                        current_type = row.get("type", CoinType.CLASSIC.value)
                        type_index = type_options.index(current_type) if current_type in type_options else 0
                        type_ = st.selectbox("Type", type_options, index=type_index)

                        # Wallet field with streamlit-tags
                        wallet_tags = st_tags(
                            label="Wallet",
                            text="Enter wallet",
                            value=[row.get("wallet", "")] if row.get("wallet") else [],
                            suggestions=wallet_suggestions,
                            maxtags=1,  # Single tag selection
                            key="edit_wallet_input",
                        )
                        wallet = wallet_tags[0] if wallet_tags else ""

                        edit_submitted = st.form_submit_button("💾 Update Purchase")

                        if edit_submitted:
                            try:
                                conn = sqlite3.connect(DB_FILE)
                                c = conn.cursor()
                                c.execute(
                                    """
                                    UPDATE portfolio
                                    SET coin=?, symbol=?, amount=?, buy_price_cad=?, fee_buy_percent=?, fee_sell_percent=?, type=?, wallet=?
                                    WHERE id=?
                                    """,
                                    (
                                        coin,
                                        symbol,
                                        amount,
                                        buy_price_cad,
                                        fee_buy_percent,
                                        fee_sell_percent,
                                        type_,
                                        wallet,
                                        row["id"],
                                    ),
                                )
                                conn.commit()
                                conn.close()

                                st.success(get_text("success_purchase_modified"))
                                st.rerun()

                            except Exception as e:
                                st.error(f"Error updating purchase: {e!s}")

                # Delete form
                with col2:
                    st.subheader("🗑️ Delete Purchase")

                    st.warning("⚠️ This action cannot be undone!")
                    st.write(f"**Coin:** {row.get('coin', 'N/A')}")
                    st.write(f"**Symbol:** {row.get('symbol', 'N/A')}")
                    st.write(f"**Amount:** {row.get('amount', 0):.4f}")
                    st.write(f"**Wallet:** {row.get('wallet', 'N/A')}")

                    if st.button("🗑️ Delete Purchase", type="secondary"):
                        try:
                            conn = sqlite3.connect(DB_FILE)
                            c = conn.cursor()
                            c.execute("DELETE FROM portfolio WHERE id=?", (row["id"],))
                            conn.commit()
                            conn.close()

                            st.success(get_text("success_purchase_deleted"))
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error deleting purchase: {e!s}")
        else:
            st.error("Portfolio data missing ID column. Cannot edit or delete.")

    except Exception as e:
        st.error(f"Error loading portfolio: {e!s}")
