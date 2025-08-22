"""Enums for the crypto portfolio application."""

from enum import StrEnum


class CoinType(StrEnum):
    """Types of coins for risk categorization."""

    CLASSIC = "classic"
    RISK = "risk"
    STABLE = "stable"


class CancelCommand(StrEnum):
    """Commands that trigger cancellation."""

    Q = "q"
    QUIT = "quit"
    CANCEL = "cancel"
    ANNULER = "annuler"
    EXIT = "exit"


class Language(StrEnum):
    """Supported languages."""

    FR = "fr"
    EN = "en"
