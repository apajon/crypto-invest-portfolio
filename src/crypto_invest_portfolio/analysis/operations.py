"""Analysis and visualization operations including price fetching, analysis, and plotting."""

import datetime
import re
import sqlite3
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
import requests

from ..constants.config import DB_FILE
from ..constants.enums import CoinType
from ..i18n import get_text


def get_prices_cad(coins):
    """Get CAD prices for a list of coins from CoinGecko.

    Args:
        coins (list[str]): List of CoinGecko identifiers (e.g. "bitcoin").

    Returns:
        dict: Mapping ``coin_id -> { 'cad': float }``. Missing keys
        mean no price was found.

    Notes:
        - Makes HTTP network call.
        - No retry logic implemented here.
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    ids = ",".join(coins)
    params = {"ids": ids, "vs_currencies": "cad"}
    response = requests.get(url, params=params, timeout=10)
    return response.json()


def save_history(df_analysis):
    """Save an analysis snapshot to the ``history`` table.

    Args:
        df_analysis (pandas.DataFrame): Results aggregated by coin, containing
            columns "Coin", "Current Price CAD",
            "Current Value CAD (net)" and "% Change Net".

    Returns:
        None

    Side effects:
        - Inserts one row per coin in the ``history`` table with a timestamp.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    for _, row in df_analysis.iterrows():
        c.execute(
            """
            INSERT INTO history (timestamp, coin, symbol, wallet, current_price_cad, current_value_net_cad, pct_change_net)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                timestamp,
                row["Coin"].lower(),
                row["Coin"],
                row.get("Wallet", None),
                row["Current Price CAD"],
                row["Current Value CAD (net)"],
                row["% Change Net"],
            ),
        )
    conn.commit()
    conn.close()


def _aggregate_by_coin(df: pd.DataFrame, include_wallet: bool = False) -> pd.DataFrame:
    """Aggregate portfolio by coin/symbol and calculate metrics.

    Args:
        df (pandas.DataFrame): Non-empty ``portfolio`` table.
        include_wallet (bool): Whether to include wallet in grouping.

    Returns:
        pandas.DataFrame: Rows aggregated by coin with calculated columns.
    """
    unique_coin_ids = df["coin"].dropna().unique().tolist()
    prices = get_prices_cad(unique_coin_ids)

    group_cols = ["coin", "symbol"] + (["wallet"] if include_wallet and "wallet" in df.columns else [])
    grouped = df.groupby(group_cols, dropna=False)
    rows = []
    for keys, g in grouped:
        # destructure keys
        coin_id = keys[0]
        symbol = keys[1]
        wallet = keys[2] if len(keys) > 2 else None
        total_amount = g["amount"].sum()
        # Exclude staking gains from costs and average fees
        if "entry_kind" in g.columns:
            purchase_mask = g["entry_kind"].fillna("buy").str.lower() != "staking"
        else:
            purchase_mask = pd.Series(True, index=g.index)
        purchases = g[purchase_mask]
        purchased_amount = purchases["amount"].sum()

        invested_value = float(
            (purchases["buy_price_cad"] * purchases["amount"] * (1 + purchases["fee_buy_percent"] / 100)).sum()
        )
        avg_buy_price = (
            float((purchases["buy_price_cad"] * purchases["amount"]).sum() / purchased_amount)
            if purchased_amount
            else 0.0
        )
        avg_fee_buy = (
            float((purchases["fee_buy_percent"] * purchases["amount"]).sum() / purchased_amount)
            if purchased_amount
            else 0.0
        )
        avg_fee_sell = (
            float((purchases["fee_sell_percent"] * purchases["amount"]).sum() / purchased_amount)
            if purchased_amount
            else 0.0
        )

        type_counts = Counter(g["type"].astype(str).str.lower())
        type_label = type_counts.most_common(1)[0][0] if type_counts else ""

        current_price = prices.get(str(coin_id), {}).get("cad", 0) or 0.0
        current_value_gross = current_price * total_amount
        current_value_net = current_value_gross * (1 - (avg_fee_sell / 100.0))
        pct_change_net = (current_value_net - invested_value) / invested_value * 100.0 if invested_value > 0 else 0.0

        row = {
            "Coin": symbol,
            "Amount": float(total_amount),
            "Avg Buy Price CAD": round(avg_buy_price, 6),
            "Avg Fee Buy %": round(avg_fee_buy, 4),
            "Avg Fee Sell %": round(avg_fee_sell, 4),
            "Current Price CAD": float(current_price),
            "Invested Value CAD (incl. frais)": round(invested_value, 2),
            "Current Value CAD (net)": round(current_value_net, 2),
            "% Change Net": round(pct_change_net, 2),
            "Type": type_label,
        }
        if include_wallet:
            row["Wallet"] = wallet
        rows.append(row)

    return pd.DataFrame(rows)


def _format_analysis_display(df_analysis: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with ANSI color on % Change Net for display."""

    def _colorize_pct(pct: float) -> str:
        if pct > 0:
            return f"\033[92m{pct:.2f}%\033[0m"  # green
        if pct < 0:
            return f"\033[91m{pct:.2f}%\033[0m"  # red
        return f"{pct:.2f}%"

    df_display = df_analysis.copy()
    if "% Change Net" in df_display.columns:
        df_display["% Change Net"] = df_display["% Change Net"].apply(_colorize_pct)

    def _colorize_symbol(symbol: str, type_label: str) -> str:
        t = str(type_label).strip().lower()
        if t == CoinType.RISK.value:
            code = "31"  # red for risk
        elif t == CoinType.STABLE.value:
            code = "33"  # yellow for stable
        else:
            code = "36"  # cyan for classic/other
        return f"\033[{code}m{symbol}\033[0m"

    if "Type" in df_display.columns:
        df_display["Coin"] = df_display.apply(lambda r: _colorize_symbol(r["Coin"], r.get("Type", "")), axis=1)
    return df_display


def _trigger_alerts(df_analysis: pd.DataFrame) -> None:
    """Display Take Profit / Stop Loss alerts for 'risk' coins."""
    print("Risk alerts:")
    for _, row in df_analysis.iterrows():
        if str(row.get("Type", "")).lower() == CoinType.RISK.value:
            pct = row["% Change Net"]
            symbol = row["Coin"]
            if pct >= 20:
                print(f"🚀 {symbol}: +{pct:.1f}% - Consider taking profit!")
            elif pct <= -15:
                print(f"🔻 {symbol}: {pct:.1f}% - Stop loss triggered!")


def _strip_ansi(text: str) -> str:
    """Remove ANSI sequences for width calculation."""
    ansi_re = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_re.sub("", text)


def _print_table(df: pd.DataFrame, columns: list[str]) -> None:
    """Print a DataFrame as a nicely formatted table with ANSI colors."""
    if df.empty:
        return

    # Filter to available columns
    available_cols = [c for c in columns if c in df.columns]
    if not available_cols:
        return

    df_subset = df[available_cols]

    # Calculate column widths considering ANSI codes
    def visible_len(s: str) -> int:
        return len(_strip_ansi(s))

    # Start with header widths
    widths = [len(col) for col in available_cols]

    # Check data widths
    for _, row in df_subset.iterrows():
        for col_idx, col in enumerate(available_cols):
            cell_value = str(row[col])
            width = visible_len(cell_value)
            widths[col_idx] = max(widths[col_idx], width)

    # Print header
    header_parts = []
    for col_idx, col in enumerate(available_cols):
        header_parts.append(col.ljust(widths[col_idx]))
    print(" | ".join(header_parts))
    print("-+-".join("-" * w for w in widths))

    # Print rows
    for _, row in df_subset.iterrows():
        row_parts = []
        for col_idx, col in enumerate(available_cols):
            raw = str(row[col])
            pad = widths[col_idx] - visible_len(raw)
            row_parts.append(raw + " " * pad)
        print(" | ".join(row_parts))


def _format_portfolio_display(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with colored symbols for portfolio display."""
    disp = df.copy()

    def _colorize_symbol(symbol: str, type_label: str) -> str:
        t = str(type_label).strip().lower()
        if t == CoinType.RISK.value:
            code = "31"  # red for risk
        elif t == CoinType.STABLE.value:
            code = "33"  # yellow for stable
        else:
            code = "36"  # cyan for classic/other
        return f"\033[{code}m{symbol}\033[0m"

    if "symbol" in disp.columns and "type" in disp.columns:
        disp["Coin"] = [_colorize_symbol(sym, typ) for sym, typ in zip(disp["symbol"], df["type"], strict=True)]
    return disp


def _view_portfolio(df: pd.DataFrame) -> None:
    """Display the portfolio in a formatted table."""
    if df.empty:
        print(get_text("empty_portfolio"))
        return

    disp = _format_portfolio_display(df)
    cols = ["id", "Coin", "amount", "buy_price_cad", "type", "wallet"]
    # Only use columns that exist
    cols = [c for c in cols if c in disp.columns]
    _print_table(disp[cols], cols)


def analyze_portfolio(df, *, by_wallet: bool = False):
    """Analyze the portfolio aggregated by coin.

    Aggregates all purchase rows by ``coin``/``symbol`` to calculate
    consolidated metrics: total amount, weighted average buy price, weighted
    average fees, total invested value, current net value, and variation
    percentage.

    This function also displays Take Profit/Stop Loss alerts specifically
    for 'risk' type coins.

    Args:
        df (pandas.DataFrame): The portfolio DataFrame returned by
            :func:`load_portfolio`.
        by_wallet (bool): If True, groups by wallet as well.

    Returns:
        None

    Side effects:
        - Network calls to CoinGecko.
        - Displays analysis table in console (with color for % Change Net).
        - Writes history to ``history`` via :func:`save_history`.
    """
    # Aggregate by coin/symbol to group multiple purchases of the same coin
    if df.empty:
        print(get_text("empty_for_analysis"))
        return

    df_analysis = _aggregate_by_coin(df, include_wallet=by_wallet)
    if df_analysis.empty:
        print(get_text("empty_for_analysis"))
        return

    df_display = _format_analysis_display(df_analysis)

    if by_wallet:
        cols = [
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
        cols = [
            "Coin",
            "Amount",
            "Avg Buy Price CAD",
            "Current Price CAD",
            "Invested Value CAD (incl. frais)",
            "Current Value CAD (net)",
            "% Change Net",
        ]

    # Restrict to available columns to avoid KeyError
    cols = [c for c in cols if c in df_display.columns]
    _print_table(df_display[cols], cols)
    print("\n---------------------------\n")

    save_history(df_analysis)
    _trigger_alerts(df_analysis)


def plot_coin_history():
    """Display the evolution of net value of a coin from history.

    Reads the ``history`` table, proposes list of available coins, then plots
    the time series of ``current_value_net_cad`` for the chosen coin.

    Args:
        None

    Returns:
        None

    Side effects:
        - Reads from SQLite ``history`` table.
        - Uses ``input()`` for user choice.
        - Opens a Matplotlib window if data is available.
    """
    conn = sqlite3.connect(DB_FILE)
    df_hist = pd.read_sql_query("SELECT * FROM history ORDER BY timestamp", conn)
    conn.close()

    if df_hist.empty:
        print("No history data available.")
        return

    available_coins = df_hist["symbol"].unique()
    print("Available coins:")
    for i, coin in enumerate(available_coins, 1):
        print(f"{i}. {coin}")

    try:
        choice = int(input("Choose a coin (number): ")) - 1
        if 0 <= choice < len(available_coins):
            chosen_coin = available_coins[choice]
            coin_data = df_hist[df_hist["symbol"] == chosen_coin].copy()
            coin_data["timestamp"] = pd.to_datetime(coin_data["timestamp"])

            plt.figure(figsize=(12, 6))
            plt.plot(coin_data["timestamp"], coin_data["current_value_net_cad"], marker="o")
            plt.title(f"Net Value Evolution - {chosen_coin}")
            plt.xlabel("Date")
            plt.ylabel("Net Value (CAD)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        else:
            print("Invalid choice.")
    except (ValueError, KeyboardInterrupt):
        print(get_text("cancelled"))
