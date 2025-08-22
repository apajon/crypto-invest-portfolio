import datetime
import sqlite3
import time
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
import requests

DB_FILE = "data/db/crypto_portfolio.db"


# --- Helpers UI ---
def _is_cancel(s: str) -> bool:
    """Retourne True si la saisie demande une annulation."""
    return str(s).strip().lower() in {"q", "quit", "cancel", "annuler", "exit"}


class UserCancel(Exception):
    """Exception utilisée pour une annulation utilisateur."""


def _input_with_cancel(prompt: str) -> str:
    """Lit une saisie et lève UserCancel si l'utilisateur annule."""
    s = input(prompt).strip()
    if _is_cancel(s):
        raise UserCancel()
    return s


def _input_with_default(prompt: str, default, caster):
    """Lit une saisie avec valeur par défaut et annulation.

    - 'q'/"quit"/etc. annule (UserCancel).
    - Entrée vide garde la valeur par défaut.
    - Sinon applique 'caster' sur la saisie.
    """
    s = input(prompt).strip()
    if _is_cancel(s):
        raise UserCancel()
    if s == "":
        return default
    return caster(s)


# --- Création des tables ---
def init_db():
    """Initialise la base SQLite et crée les tables si nécessaire.

    Crée les tables ``portfolio`` et ``history`` dans ``crypto_portfolio.db``
    si elles n'existent pas déjà.

    Args:
        None

    Returns:
        None

    Effets de bord:
        - Création/écriture dans le fichier SQLite ``crypto_portfolio.db``.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY,
            coin TEXT,
            symbol TEXT,
            amount REAL,
            buy_price_cad REAL,
            fee_buy_percent REAL DEFAULT 0,
            fee_sell_percent REAL DEFAULT 0,
            type TEXT,
            wallet TEXT
        )
    """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            coin TEXT,
            symbol TEXT,
            wallet TEXT,
            current_price_cad REAL,
            current_value_net_cad REAL,
            pct_change_net REAL
        )
    """
    )
    # Migration légère: s'assurer que les colonnes existent

    def _ensure_column(table: str, column: str, ddl: str):
        c.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in c.fetchall()]
        if column not in cols:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")

    _ensure_column("portfolio", "wallet", "wallet TEXT")
    _ensure_column("portfolio", "entry_kind", "entry_kind TEXT DEFAULT 'buy'")
    _ensure_column("history", "wallet", "wallet TEXT")
    conn.commit()
    conn.close()


# --- Ajouter un achat ---
def add_purchase():
    """Ajoute un achat au portefeuille via des saisies utilisateur.

    Demande les informations de l'achat (coin id, symbole, quantité, prix, frais,
    type), puis insère une ligne dans la table ``portfolio``.

    Args:
        None

    Returns:
        None

    Effets de bord:
        - Écrit dans la table ``portfolio``.
        - Affiche un message de confirmation en console.
        - Saisies bloquantes via ``input()``.
    """
    print("(tapez 'q' pour annuler à tout moment)")
    try:
        coin = input("Nom du coin (CoinGecko ID) : ").strip()
        if _is_cancel(coin):
            print("Annulé.")
            return
        symbol = input("Symbole : ").strip()
        if _is_cancel(symbol):
            print("Annulé.")
            return
        amount_s = input("Quantité : ").strip()
        if _is_cancel(amount_s):
            print("Annulé.")
            return
        amount = float(amount_s)
        buy_price_s = input("Prix d'achat CAD : ").strip()
        if _is_cancel(buy_price_s):
            print("Annulé.")
            return
        buy_price_cad = float(buy_price_s)
        fee_buy_s = input("Frais d'achat (%) : ").strip()
        if _is_cancel(fee_buy_s):
            print("Annulé.")
            return
        fee_buy_percent = float(fee_buy_s)
        fee_sell_s = input("Frais de vente (%) : ").strip()
        if _is_cancel(fee_sell_s):
            print("Annulé.")
            return
        fee_sell_percent = float(fee_sell_s)
        type_ = input("Type (classic/risk/stable) : ").strip().lower()
        if _is_cancel(type_):
            print("Annulé.")
            return
        wallet = input("Wallet (ex: kraken, n26, exodus) : ").strip()
        if _is_cancel(wallet):
            print("Annulé.")
            return
    except KeyboardInterrupt:
        print("\nAnnulé.")
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
    print(f"✅ Achat ajouté : {symbol} ({amount} @ {buy_price_cad} CAD)")


# --- Ajouter un gain (staking) ---
def add_staking_gain():
    """Ajoute un gain de staking (quantité gratuite, sans coût investi).

    Saisit le coin, le symbole, la quantité gagnée, le *type* (classic/risk/stable)
    et le wallet. Enregistre une ligne avec ``entry_kind='staking'`` et des
    valeurs de prix/frais à 0.
    """
    print("(tapez 'q' pour annuler à tout moment)")
    try:
        coin = input("Nom du coin (CoinGecko ID) : ").strip()
        if _is_cancel(coin):
            print("Annulé.")
            return
        symbol = input("Symbole : ").strip()
        if _is_cancel(symbol):
            print("Annulé.")
            return
        amount_s = input("Quantité gagnée (staking) : ").strip()
        if _is_cancel(amount_s):
            print("Annulé.")
            return
        amount = float(amount_s)
        type_ = input("Type (classic/risk/stable) : ").strip().lower()
        if _is_cancel(type_):
            print("Annulé.")
            return
        wallet = input("Wallet (ex: kraken, n26, exodus) : ").strip()
        if _is_cancel(wallet):
            print("Annulé.")
            return
    except KeyboardInterrupt:
        print("\nAnnulé.")
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
    print(f"✅ Gain staking ajouté : {symbol} (+{amount})")


# --- Modifier un achat ---
def edit_purchase():
    """Modifie un achat existant après sélection par ID.

    Affiche les achats, demande l'ID à modifier, puis permet de mettre à jour
    chaque champ. Entrée vide conserve la valeur actuelle; 'q' annule.

    Effets de bord:
        - Lecture et mise à jour de lignes dans la table portfolio.
        - Utilise input() pour les saisies.
    """
    df = load_portfolio()
    if df.empty:
        print("Portfolio vide. Aucun achat à modifier.")
        return
    print("(tapez 'q' pour annuler)")
    print(df[["id", "symbol", "amount", "buy_price_cad", "wallet"]])
    try:
        purchase_id = int(_input_with_cancel("ID de l'achat à modifier : "))
    except (UserCancel, ValueError, KeyboardInterrupt):
        print("Annulation ou ID invalide.")
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM portfolio WHERE id=?", (purchase_id,))
    row = c.fetchone()
    if not row:
        print("ID invalide.")
        conn.close()
        return

    print("Laissez vide pour ne pas modifier. (ou 'q' pour annuler)")
    try:
        coin = _input_with_default(f"Nom du coin [{row[1]}] : ", row[1], lambda s: s)
        symbol = _input_with_default(f"Symbole [{row[2]}] : ", row[2], lambda s: s)
        amount = _input_with_default(f"Quantité [{row[3]}] : ", row[3], float)
        buy_price_cad = _input_with_default(f"Prix d'achat CAD [{row[4]}] : ", row[4], float)
        fee_buy_percent = _input_with_default(f"Frais d'achat (%) [{row[5]}] : ", row[5], float)
        fee_sell_percent = _input_with_default(f"Frais de vente (%) [{row[6]}] : ", row[6], float)
        type_ = _input_with_default(f"Type (classic/risk/stable) [{row[7]}] : ", row[7], lambda s: s.lower())
        current_wallet = row[8] if len(row) > 8 else ""
        wallet = _input_with_default(f"Wallet [{current_wallet}] : ", current_wallet, lambda s: s)
    except (UserCancel, ValueError, KeyboardInterrupt):
        print("Annulé ou valeur invalide.")
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
    print("✅ Achat modifié avec succès.")


# --- Supprimer un achat ---
def delete_purchase():
    """Supprime un achat existant après sélection par ID.

    Affiche les achats, demande l'ID à supprimer, puis supprime la ligne
    correspondante dans ``portfolio``.

    Args:
        None

    Returns:
        None

    Effets de bord:
        - Supprime une ligne dans ``portfolio``.
        - Affiche un message en console et utilise ``input()``.
    """
    df = load_portfolio()
    if df.empty:
        print("Portfolio vide. Aucun achat à supprimer.")
        return
    print("(tapez 'q' pour annuler)")
    print(df[["id", "symbol", "amount", "buy_price_cad", "wallet"]])
    try:
        s = input("ID de l'achat à supprimer : ").strip()
        if _is_cancel(s):
            print("Annulé.")
            return
        purchase_id = int(s)
    except (ValueError, KeyboardInterrupt):
        print("Annulé ou ID invalide.")
        return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM portfolio WHERE id=?", (purchase_id,))
    conn.commit()
    conn.close()
    print("✅ Achat supprimé.")


# --- Charger le portfolio ---
def load_portfolio():
    """Charge le portefeuille depuis la base SQLite.

    Args:
        None

    Returns:
        pandas.DataFrame: Un DataFrame contenant toutes les colonnes de la table
        ``portfolio``. Peut être vide si aucun achat n'est présent.
    """
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM portfolio", conn)
    conn.close()
    return df


# --- Récupérer prix CAD ---
def get_prices_cad(coins):
    """Récupère les prix en CAD pour une liste de coins depuis CoinGecko.

    Args:
        coins (list[str]): Liste d'identifiants CoinGecko (ex: "bitcoin").

    Returns:
        dict: Mapping ``coin_id -> { 'cad': float }``. Les clés absentes
        signifieront qu'aucun prix n'a été trouvé.

    Notes:
        - Effectue un appel réseau HTTP.
        - Aucune gestion de retry n'est implémentée ici.
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    ids = ",".join(coins)
    params = {"ids": ids, "vs_currencies": "cad"}
    response = requests.get(url, params=params, timeout=10)
    return response.json()


# --- Sauvegarder historique ---
def save_history(df_analysis):
    """Enregistre un snapshot d'analyse dans la table ``history``.

    Args:
        df_analysis (pandas.DataFrame): Résultats agrégés par coin, contenant
            les colonnes "Coin", "Current Price CAD",
            "Current Value CAD (net)" et "% Change Net".

    Returns:
        None

    Effets de bord:
        - Insère une ligne par coin dans la table ``history`` avec un timestamp.
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


# --- Helpers d'analyse ---
def _aggregate_by_coin(df: pd.DataFrame, include_wallet: bool = False) -> pd.DataFrame:
    """Agrège le portefeuille par coin/symbole et calcule les métriques.

    Args:
        df (pandas.DataFrame): Table ``portfolio`` non vide.

    Returns:
        pandas.DataFrame: Lignes agrégées par coin avec colonnes calculées.
    """
    unique_coin_ids = df["coin"].dropna().unique().tolist()
    prices = get_prices_cad(unique_coin_ids)

    group_cols = ["coin", "symbol"] + (["wallet"] if include_wallet and "wallet" in df.columns else [])
    grouped = df.groupby(group_cols, dropna=False)
    rows = []
    for keys, g in grouped:
        # déstructure les clés
        coin_id = keys[0]
        symbol = keys[1]
        wallet = keys[2] if len(keys) > 2 else None
        total_amount = g["amount"].sum()
        # Exclure les gains staking des coûts et des frais moyens
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
    """Retourne une copie de df avec couleur ANSI sur % Change Net pour l'affichage."""

    def _colorize_pct(pct: float) -> str:
        if pct > 0:
            return f"\033[92m{pct:.2f}%\033[0m"  # vert
        if pct < 0:
            return f"\033[91m{pct:.2f}%\033[0m"  # rouge
        return f"{pct:.2f}%"

    df_display = df_analysis.copy()
    if not df_display.empty and "% Change Net" in df_display.columns:
        df_display["% Change Net"] = df_display["% Change Net"].apply(_colorize_pct)

    # Colorer le symbole du coin selon le type (couleurs distinctes de rouge/vert)
    def _colorize_symbol(symbol: str, type_label: str) -> str:
        t = (type_label or "").lower()
        if t == "risk":
            code = "35"  # magenta
        elif t == "stable":
            code = "33"  # jaune
        else:
            code = "36"  # cyan pour classic/other
        return f"\033[{code}m{symbol}\033[0m"

    if "Coin" in df_display.columns and "Type" in df_display.columns:
        df_display["Coin"] = df_display.apply(lambda r: _colorize_symbol(r["Coin"], r.get("Type", "")), axis=1)
    return df_display


def _trigger_alerts(df_analysis: pd.DataFrame) -> None:
    """Affiche les alertes Take Profit / Stop Loss pour les coins 'risk'."""
    for _, row in df_analysis.iterrows():
        if str(row.get("Type", "")).lower() == "risk":
            pct = float(row["% Change Net"])
            colored = (
                f"\033[92m{pct:.2f}%\033[0m"
                if pct > 0
                else (f"\033[91m{pct:.2f}%\033[0m" if pct < 0 else f"{pct:.2f}%")
            )
            if pct >= 50:
                print(f"⚡ Take Profit Alert: {row['Coin']} up {colored} (net après frais)")
            elif pct <= -30:
                print(f"💀 Stop Loss Alert: {row['Coin']} down {colored} (net après frais)")


def _strip_ansi(text: str) -> str:
    """Supprime les séquences ANSI pour le calcul des largeurs d'affichage."""
    import re

    ansi_re = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_re.sub("", text)


def _print_table(df: pd.DataFrame, columns: list[str]) -> None:
    """Affiche un DataFrame avec alignement correct en présence de couleurs ANSI.

    Args:
        df: DataFrame à afficher (peut contenir des valeurs colorées par ANSI).
        columns: Ordre et sous-ensemble de colonnes à afficher.
    """
    if df.empty:
        print("(vide)")
        return

    # Build string values and compute widths based on visible length (ANSI-stripped)
    values = [["" if pd.isna(v) else str(v) for v in df[col]] for col in columns]
    headers = [str(col) for col in columns]

    def visible_len(s: str) -> int:
        return len(_strip_ansi(s))

    widths = [
        max(len(h), max(visible_len(v) for v in col_vals) if col_vals else len(h))
        for h, col_vals in zip(headers, values, strict=True)
    ]

    # Print header
    header_row = " | ".join(h.ljust(w) for h, w in zip(headers, widths, strict=True))
    sep_row = "-+-".join("-" * w for w in widths)
    print(header_row)
    print(sep_row)

    # Print rows
    for row_idx in range(len(df)):
        cells = []
        for col_idx, col in enumerate(columns):
            raw = "" if pd.isna(df.iloc[row_idx][col]) else str(df.iloc[row_idx][col])
            pad = widths[col_idx] - len(_strip_ansi(raw))
            cells.append(raw + (" " * max(0, pad)))
        print(" | ".join(cells))


# --- Visualisation simple du portefeuille (sans analyse) ---
def _format_portfolio_display(df: pd.DataFrame) -> pd.DataFrame:
    """Formate le DataFrame du portefeuille pour affichage simple.

    - Renomme les colonnes techniques en libellés lisibles.
    - Colore le symbole (colonne Coin) selon le type.
    """
    if df.empty:
        return df

    disp = df.copy().rename(
        columns={
            "id": "ID",
            "symbol": "Coin",
            "buy_price_cad": "Buy Price CAD",
            "fee_buy_percent": "Fee Buy %",
            "fee_sell_percent": "Fee Sell %",
            "wallet": "Wallet",
        }
    )
    if "entry_kind" in df.columns:
        disp = disp.rename(columns={"entry_kind": "Entry"})

    # Colorer la colonne Coin selon le type
    def _colorize_symbol(symbol: str, type_label: str) -> str:
        t = (type_label or "").lower()
        if t == "risk":
            code = "35"  # magenta
        elif t == "stable":
            code = "33"  # jaune
        else:
            code = "36"  # cyan
        return f"\033[{code}m{symbol}\033[0m"

    if "Coin" in disp.columns and "type" in df.columns:
        disp["Coin"] = [_colorize_symbol(sym, typ) for sym, typ in zip(disp["Coin"], df["type"], strict=True)]
    return disp


def _view_portfolio(df: pd.DataFrame) -> None:
    if df.empty:
        print("Portfolio vide.")
        return
    disp = _format_portfolio_display(df)
    cols = ["ID", "Coin", "amount", "Buy Price CAD", "Fee Buy %", "Fee Sell %", "Wallet", "Entry"]
    # Renommer amount en Amount pour l'affichage sans dupliquer les données
    if "amount" in disp.columns:
        disp = disp.rename(columns={"amount": "Amount"})
    cols = ["ID", "Coin", "Amount", "Buy Price CAD", "Fee Buy %", "Fee Sell %", "Wallet", "Entry"]
    cols = [c for c in cols if c in disp.columns]
    _print_table(disp[cols], cols)


# --- Analyse du portefeuille ---
def analyze_portfolio(df, *, by_wallet: bool = False):
    """Analyse le portefeuille agrégé par coin.

    Agrège toutes les lignes d'achats par ``coin``/``symbol`` pour calculer des
    métriques consolidées: quantité totale, prix d'achat moyen pondéré, frais
    moyens pondérés, valeur investie totale, valeur actuelle nette, et variation
    nette en pourcentage. Affiche le tableau d'analyse et déclenche des alertes
    sur les coins de type "risk".

    Args:
        df (pandas.DataFrame): DataFrame de la table ``portfolio``.

    Returns:
        None

    Effets de bord:
        - Appels réseau à CoinGecko.
        - Affiche le tableau d'analyse en console (avec couleur pour % Change Net).
        - Écrit l'historique dans ``history`` via :func:`save_history`.
    """
    # Agrégation par coin/symbole pour regrouper plusieurs achats du même coin
    if df.empty:
        print("Portfolio vide. Ajoutez des achats.")
        return

    df_analysis = _aggregate_by_coin(df, include_wallet=by_wallet)
    pd.set_option("display.float_format", "{:.6f}".format)

    df_display = _format_analysis_display(df_analysis)
    title = "Portfolio Analysis (par coin)" if not by_wallet else "Portfolio Analysis (par coin et par wallet)"
    print(f"\n--- {title} ---")
    # Colonnes à afficher (sans frais moyens et sans colonne Type)
    cols = [
        "Coin",
        "Amount",
        "Avg Buy Price CAD",
        "Current Price CAD",
        "Invested Value CAD (incl. frais)",
        "Current Value CAD (net)",
        "% Change Net",
    ]
    if by_wallet and "Wallet" in df_display.columns:
        cols.append("Wallet")
    # Restreindre à l'ensemble de colonnes disponibles pour éviter KeyError
    cols = [c for c in cols if c in df_display.columns]
    _print_table(df_display[cols], cols)
    print("\n---------------------------\n")

    save_history(df_analysis)
    _trigger_alerts(df_analysis)


# --- Graphique historique ---
def plot_coin_history():
    """Affiche l'évolution de la valeur nette d'un coin depuis l'historique.

    Lit la table ``history``, propose la liste des coins disponibles, puis trace
    la série temporelle de ``current_value_net_cad`` pour le coin choisi.

    Args:
        None

    Returns:
        None

    Effets de bord:
        - Ouvre une fenêtre Matplotlib avec la courbe.
        - Saisies via ``input()``.
    """
    df = pd.read_sql_query("SELECT * FROM history", sqlite3.connect(DB_FILE))
    if df.empty:
        print("Aucun historique disponible.")
        return
    coins = df["symbol"].unique()
    print("Coins disponibles :", ", ".join(coins))
    coin = input("Choisissez un coin à visualiser : ").strip()
    df_coin = df[df["symbol"] == coin]
    if df_coin.empty:
        print("Aucune donnée pour ce coin.")
        return
    df_coin["timestamp"] = pd.to_datetime(df_coin["timestamp"])
    df_coin = df_coin.sort_values("timestamp")

    plt.figure(figsize=(10, 5))
    plt.plot(df_coin["timestamp"], df_coin["current_value_net_cad"], marker="o")
    plt.title(f"Évolution de {coin} (valeur nette CAD)")
    plt.xlabel("Date")
    plt.ylabel("Valeur nette CAD")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# --- Handlers de menu (réduisent la complexité de main_menu) ---
def _handle_add():
    add_purchase()
    return True


def _handle_edit():
    edit_purchase()
    return True


def _handle_add_staking():
    add_staking_gain()
    return True


def _handle_wallet_menu():
    """Sous-menu pour les analyses par wallet."""
    while True:
        print("\n=== Analyses par wallet ===")
        print("1. Tous les wallets (une fois)")
        print("2. Auto-update de tous les wallets (X minutes)")
        print("3. Un wallet (une fois)")
        print("4. Auto-update d'un wallet (X minutes)")
        print("5. Retour")
        print("6. Quitter")
        choice = input("Choix : ").strip()
        if choice == "1":
            _handle_analyze_all_wallets_once()
        elif choice == "2":
            _handle_analyze_all_wallets_periodic()
        elif choice == "3":
            _handle_analyze_one_wallet_once()
        elif choice == "4":
            _handle_analyze_one_wallet_periodic()
        elif choice == "5":
            return True
        elif choice == "6":
            return _handle_quit()
        else:
            print("Choix invalide, réessayez.")


def _handle_delete():
    delete_purchase()
    return True


def _handle_analyze_once():
    df = load_portfolio()
    if df.empty:
        print("Portfolio vide. Ajoutez des achats.")
    else:
        analyze_portfolio(df)
    return True


def _handle_auto_update():
    df = load_portfolio()
    if df.empty:
        print("Portfolio vide. Ajoutez des achats avant auto-update.")
        return True
    minutes = float(input("Intervalle en minutes : "))
    print("Appuyez Ctrl+C pour arrêter l'auto-update.")
    try:
        while True:
            analyze_portfolio(df)
            time.sleep(minutes * 60)
    except KeyboardInterrupt:
        print("🔹 Auto-update arrêté. Retour au menu.")
    return True


def _handle_plot():
    plot_coin_history()
    return True


def _handle_quit():
    print("Au revoir !")
    return False


def _handle_view_portfolio_all():
    df = load_portfolio()
    _view_portfolio(df)
    return True


def _handle_view_portfolio_one_wallet():
    df = load_portfolio()
    if df.empty:
        print("Portfolio vide.")
        return True
    if "wallet" not in df.columns or df["wallet"].isna().all():
        print("Aucun wallet renseigné dans le portefeuille.")
        return True
    wallets = sorted(df["wallet"].dropna().unique().tolist())
    print("Wallets disponibles :", ", ".join(wallets))
    w = input("Choisissez un wallet : ").strip()
    df_w = df[df["wallet"] == w]
    if df_w.empty:
        print("Aucun achat pour ce wallet.")
        return True
    _view_portfolio(df_w)
    return True


def _handle_analyze_all_wallets_once():
    df = load_portfolio()
    if df.empty:
        print("Portfolio vide. Ajoutez des achats.")
    else:
        analyze_portfolio(df, by_wallet=True)
    return True


def _handle_analyze_all_wallets_periodic():
    df = load_portfolio()
    if df.empty:
        print("Portfolio vide. Ajoutez des achats avant auto-update.")
        return True
    minutes = float(input("Intervalle en minutes : "))
    print("Appuyez Ctrl+C pour arrêter l'auto-update (tous wallets).")
    try:
        while True:
            analyze_portfolio(df, by_wallet=True)
            time.sleep(minutes * 60)
    except KeyboardInterrupt:
        print("🔹 Auto-update (wallets) arrêté. Retour au menu.")
    return True


def _handle_analyze_one_wallet_once():
    df = load_portfolio()
    if df.empty:
        print("Portfolio vide. Ajoutez des achats.")
        return True
    if "wallet" not in df.columns or df["wallet"].isna().all():
        print("Aucun wallet renseigné dans le portefeuille.")
        return True
    wallets = sorted(df["wallet"].dropna().unique().tolist())
    print("Wallets disponibles :", ", ".join(wallets))
    w = input("Choisissez un wallet : ").strip()
    df_w = df[df["wallet"] == w]
    if df_w.empty:
        print("Aucun achat pour ce wallet.")
        return True
    analyze_portfolio(df_w, by_wallet=True)
    return True


def _handle_analyze_one_wallet_periodic():
    df = load_portfolio()
    if df.empty:
        print("Portfolio vide. Ajoutez des achats avant auto-update.")
        return True
    if "wallet" not in df.columns or df["wallet"].isna().all():
        print("Aucun wallet renseigné dans le portefeuille.")
        return True
    wallets = sorted(df["wallet"].dropna().unique().tolist())
    print("Wallets disponibles :", ", ".join(wallets))
    w = input("Choisissez un wallet : ").strip()
    df_w = df[df["wallet"] == w]
    if df_w.empty:
        print("Aucun achat pour ce wallet.")
        return True
    minutes = float(input("Intervalle en minutes : "))
    print("Appuyez Ctrl+C pour arrêter l'auto-update (wallet choisi).")
    try:
        while True:
            analyze_portfolio(df_w, by_wallet=True)
            time.sleep(minutes * 60)
    except KeyboardInterrupt:
        print("🔹 Auto-update (wallet choisi) arrêté. Retour au menu.")
    return True


# --- Menu interactif ---
def main_menu():
    """Menu principal de l'application (interface CLI).

    Présente un menu interactif pour gérer un portefeuille crypto et orchestre
    les actions clés : ajout, modification, suppression d'achats, analyse
    ponctuelle ou périodique des performances et visualisation de l'historique
    d'un coin.

    Fonctionnement:
        - Initialise la base SQLite si nécessaire.
        - Démarre une boucle jusqu'à ce que l'utilisateur choisisse de quitter.
        - Délègue chaque action aux fonctions dédiées.

    Options du menu:
        1) Ajouter un achat -> :func:`add_purchase`
        2) Ajouter un gain (staking) -> :func:`add_staking_gain`
        3) Modifier un achat existant -> :func:`edit_purchase`
        4) Supprimer un achat -> :func:`delete_purchase`
        5) Analyser le portefeuille une fois -> :func:`analyze_portfolio`
        6) Auto-update (analyse périodique)
        7) Visualiser le portefeuille (achats)
        8) Visualiser le portefeuille d'un wallet
        9) Visualiser l'évolution d'un coin -> :func:`plot_coin_history`
        10) Analyses wallet (ouvre un sous-menu)
        11) Quitter

    Args:
        None

    Returns:
        None: Ne retourne rien. La fonction se termine lorsque l'utilisateur
        choisit de quitter le menu.

    Effets de bord:
        - Crée/ouvre le fichier SQLite ``crypto_portfolio.db``.
        - Lit/écrit dans les tables ``portfolio`` et ``history``.
        - Effectue des requêtes HTTP vers l'API CoinGecko lors des analyses.
        - Affiche des informations en console ; peut ouvrir des fenêtres Matplotlib.
        - Sollicite des saisies clavier (blocantes) via ``input()``.

    Interactions utilisateur:
        - Saisies numérotées pour choisir une action.
        - Dans le mode auto-update (option 5), ``Ctrl+C`` interrompt proprement
          la boucle et revient au menu sans quitter l'application.

    Exceptions:
        - Les exceptions spécifiques sont gérées au sein des sous-fonctions.
        - Un ``KeyboardInterrupt`` est capturé pendant l'auto-update et ne
          remonte pas au-dessus de cette boucle.

    Notes:
        - L'auto-update utilise l'état du portefeuille chargé au moment du
          lancement de l'option ; si le contenu de la base change pendant la
          boucle, relancez l'option pour recharger les données.
        - Un accès réseau est requis pour récupérer les prix courants.

    Examples:
        Exécuter depuis la racine du projet avec Poetry::

            poetry run python -m crypto_invest_portfolio.main

        Ou directement avec Python::

            python -m crypto_invest_portfolio.main

    Voir aussi:
        :func:`add_purchase`, :func:`edit_purchase`, :func:`delete_purchase`,
        :func:`analyze_portfolio`, :func:`plot_coin_history`
    """
    init_db()
    actions = {
        "1": _handle_add,
        "2": _handle_add_staking,
        "3": _handle_edit,
        "4": _handle_delete,
        "5": _handle_analyze_once,
        "6": _handle_auto_update,
        "7": _handle_view_portfolio_all,
        "8": _handle_view_portfolio_one_wallet,
        "9": _handle_plot,
        "10": _handle_wallet_menu,
        "11": _handle_quit,
    }

    while True:
        print("\n=== Crypto Portfolio Tracker ===")
        print("1. Ajouter un achat")
        print("2. Ajouter un gain (staking)")
        print("3. Modifier un achat existant")
        print("4. Supprimer un achat")
        print("5. Analyser le portefeuille une fois")
        print("6. Auto-update toutes les X minutes")
        print("7. Visualiser le portefeuille (achats)")
        print("8. Visualiser le portefeuille d'un wallet")
        print("9. Visualiser l'évolution d'un coin")
        print("10. Analyses wallet ➜")
        print("11. Quitter")
        choice = input("Choix : ").strip()

        handler = actions.get(choice)
        if handler is None:
            print("Choix invalide, réessayez.")
            continue
        # Chaque handler retourne True pour continuer, False pour quitter la boucle
        if not handler():
            break


if __name__ == "__main__":
    main_menu()
