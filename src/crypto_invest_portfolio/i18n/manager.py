"""Internationalization manager."""

import json
import logging
from pathlib import Path

from ..constants.enums import Language
from .en import TRANSLATIONS as EN_TRANSLATIONS

# Import translation dictionaries
from .fr import TRANSLATIONS as FR_TRANSLATIONS

logger = logging.getLogger(__name__)

_TRANSLATIONS = {
    Language.FR: FR_TRANSLATIONS,
    Language.EN: EN_TRANSLATIONS,
}

_current_language = Language.FR  # Default to French
_CONFIG_FILE = Path("data/config/language.json")


def _load_language_preference():
    """Load saved language preference."""
    global _current_language
    try:
        if _CONFIG_FILE.exists():
            with open(_CONFIG_FILE) as f:
                config = json.load(f)
                lang = config.get("language", Language.FR)
                if lang in _TRANSLATIONS:
                    _current_language = Language(lang)
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        # Fallback to default if any error
        _current_language = Language.FR


def _save_language_preference():
    """Save current language preference."""
    try:
        _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_CONFIG_FILE, "w") as f:
            json.dump({"language": _current_language}, f)
    except Exception as e:
        # Log the exception instead of silently failing
        logger.warning("Failed to save language preference: %s", e)


def get_text(key: str, *args) -> str:
    """Get translated text for the given key.

    Args:
        key: Translation key
        *args: Format arguments for the text

    Returns:
        Translated and formatted text
    """
    global _current_language
    translations = _TRANSLATIONS.get(_current_language, _TRANSLATIONS[Language.FR])
    text = translations.get(key, key)  # Fallback to key if not found

    if args:
        try:
            return text.format(*args)
        except (ValueError, KeyError):
            return text
    return text


def set_language(language: Language):
    """Set the current language.

    Args:
        language: Language to set
    """
    global _current_language
    if language in _TRANSLATIONS:
        _current_language = language
        _save_language_preference()


def get_current_language() -> Language:
    """Get the current language."""
    return _current_language


def get_supported_languages() -> list[Language]:
    """Get list of supported languages."""
    return list(_TRANSLATIONS.keys())


# Load saved language preference on module import
_load_language_preference()
