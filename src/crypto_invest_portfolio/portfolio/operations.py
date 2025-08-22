"""Portfolio operations: add, edit, delete purchases and load portfolio data."""

import sqlite3

import pandas as pd

from ..constants.config import DB_FILE
from ..constants.enums import CoinType
from ..i18n import get_text
from ..ui import input_with_cancel, input_with_default, is_cancel, UserCancel


def add_purchase():
    """Add a purchase to the portfolio via user input.

    Asks for purchase information (coin id, symbol, amount, price, fees,
    type), then inserts a row into the ``portfolio`` table.

    Args:
        None

    Returns:
        None

    Side effects:
        - Writes to the ``portfolio`` table.
        - Displays confirmation message in console.
        - Blocking input via ``input()``.
    """
    print(get_text("cancel_anytime"))
    try:
        coin = input(get_text("coin_name")).strip()
        if is_cancel(coin):
            print(get_text("cancelled"))
            return
        symbol = input(get_text("coin_symbol")).strip()
        if is_cancel(symbol):
            print(get_text("cancelled"))
            return
        amount_s = input(get_text("amount")).strip()
        if is_cancel(amount_s):
            print(get_text("cancelled"))
            return
        amount = float(amount_s)
        buy_price_s = input(get_text("buy_price_cad")).strip()
        if is_cancel(buy_price_s):
            print(get_text("cancelled"))
            return
        buy_price_cad = float(buy_price_s)
        fee_buy_s = input(get_text("buy_fee_percent")).strip()
        if is_cancel(fee_buy_s):
            print(get_text("cancelled"))
            return
        fee_buy_percent = float(fee_buy_s)
        fee_sell_s = input(get_text("sell_fee_percent")).strip()
        if is_cancel(fee_sell_s):
            print(get_text("cancelled"))
            return
        fee_sell_percent = float(fee_sell_s)
        type_ = input(get_text("coin_type")).strip().lower()
        if is_cancel(type_):
            print(get_text("cancelled"))
            return
        # Validate coin type
        if type_ not in [t.value for t in CoinType]:
            type_ = CoinType.CLASSIC.value  # Default fallback
        wallet = input(get_text("wallet")).strip()
        if is_cancel(wallet):
            print(get_text("cancelled"))
            return
    except KeyboardInterrupt:
        print(get_text("cancelled_newline"))
        return
    
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
    print(get_text("success_purchase_added", symbol, amount, buy_price_cad))


def add_staking_gain():
    """Add a staking gain (free amount, no investment cost).

    Enters the coin, symbol, amount gained, *type* (classic/risk/stable)
    and wallet. Records a row with ``entry_kind='staking'`` and price/fee
    values at 0.
    """
    print(get_text("cancel_anytime"))
    try:
        coin = input(get_text("coin_name")).strip()
        if is_cancel(coin):
            print(get_text("cancelled"))
            return
        symbol = input(get_text("coin_symbol")).strip()
        if is_cancel(symbol):
            print(get_text("cancelled"))
            return
        amount_s = input(get_text("amount")).strip()
        if is_cancel(amount_s):
            print(get_text("cancelled"))
            return
        amount = float(amount_s)
        type_ = input(get_text("coin_type")).strip().lower()
        if is_cancel(type_):
            print(get_text("cancelled"))
            return
        # Validate coin type
        if type_ not in [t.value for t in CoinType]:
            type_ = CoinType.CLASSIC.value  # Default fallback
        wallet = input(get_text("wallet")).strip()
        if is_cancel(wallet):
            print(get_text("cancelled"))
            return
    except KeyboardInterrupt:
        print(get_text("cancelled_newline"))
        return

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
    print(get_text("success_staking_added", symbol, amount))


def edit_purchase():
    """Modify an existing purchase after selection by ID.

    Displays purchases, asks for ID to modify, then allows updating
    each field. Empty input preserves current value; 'q' cancels.

    Side effects:
        - Reads and updates rows in the portfolio table.
        - Uses input() for user input.
    """
    df = load_portfolio()
    if df.empty:
        print(get_text("empty_portfolio"))
        return
    print(get_text("cancel_anytime"))
    print(df[["id", "symbol", "amount", "buy_price_cad", "wallet"]])
    try:
        purchase_id = int(input_with_cancel(get_text("purchase_id")))
    except (UserCancel, ValueError, KeyboardInterrupt):
        print(get_text("cancelled_invalid"))
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM portfolio WHERE id=?", (purchase_id,))
    row = c.fetchone()
    if not row:
        print(get_text("invalid_id"))
        conn.close()
        return

    print(get_text("empty_modify"))
    try:
        coin = input_with_default(get_text("edit_coin_name", row[1]), row[1], lambda s: s)
        symbol = input_with_default(get_text("edit_symbol", row[2]), row[2], lambda s: s)
        amount = input_with_default(get_text("edit_amount", row[3]), row[3], float)
        buy_price_cad = input_with_default(get_text("edit_buy_price", row[4]), row[4], float)
        fee_buy_percent = input_with_default(get_text("edit_buy_fee", row[5]), row[5], float)
        fee_sell_percent = input_with_default(get_text("edit_sell_fee", row[6]), row[6], float)
        type_ = input_with_default(get_text("edit_type", row[7]), row[7], lambda s: s.lower())
        # Validate coin type
        if type_ not in [t.value for t in CoinType]:
            type_ = row[7]  # Keep original if invalid
        current_wallet = row[8] if len(row) > 8 else ""
        wallet = input_with_default(get_text("edit_wallet", current_wallet), current_wallet, lambda s: s)
    except (UserCancel, ValueError, KeyboardInterrupt):
        print(get_text("cancelled_invalid"))
        conn.close()
        return

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
            purchase_id,
        ),
    )
    conn.commit()
    conn.close()
    print(get_text("success_purchase_modified"))


def delete_purchase():
    """Delete an existing purchase after selection by ID.

    Displays purchases, asks for ID to delete, then deletes the
    corresponding row in ``portfolio``.

    Args:
        None

    Returns:
        None

    Side effects:
        - Deletes a row in ``portfolio``.
        - Displays message in console and uses ``input()``.
    """
    df = load_portfolio()
    if df.empty:
        print(get_text("empty_portfolio"))
        return
    print(get_text("cancel_anytime"))
    print(df[["id", "symbol", "amount", "buy_price_cad", "wallet"]])
    try:
        s = input(get_text("delete_id")).strip()
        if is_cancel(s):
            print(get_text("cancelled"))
            return
        purchase_id = int(s)
    except (ValueError, KeyboardInterrupt):
        print(get_text("cancelled_invalid"))
        return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM portfolio WHERE id=?", (purchase_id,))
    conn.commit()
    conn.close()
    print(get_text("success_purchase_deleted"))


def load_portfolio():
    """Load the portfolio from SQLite database.

    Args:
        None

    Returns:
        pandas.DataFrame: A DataFrame containing all columns from the
        ``portfolio`` table. Can be empty if no purchases are present.
    """
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM portfolio", conn)
    conn.close()
    return df