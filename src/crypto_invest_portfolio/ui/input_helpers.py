"""Input helpers and cancellation utilities."""

from ..constants.enums import CancelCommand


class UserCancel(Exception):
    """Exception used for user cancellation."""


def is_cancel(s: str) -> bool:
    """Check if input requests cancellation.

    Args:
        s: Input string to check

    Returns:
        True if the input is a cancel command
    """
    normalized = str(s).strip().lower()
    return normalized in {cmd.value for cmd in CancelCommand}


def input_with_cancel(prompt: str) -> str:
    """Read input and raise UserCancel if user cancels.

    Args:
        prompt: Prompt to display

    Returns:
        The input string

    Raises:
        UserCancel: If user enters a cancel command
    """
    s = input(prompt).strip()
    if is_cancel(s):
        raise UserCancel()
    return s


def input_with_default(prompt: str, default, caster):
    """Read input with default value and cancellation support.

    Args:
        prompt: Prompt to display
        default: Default value if input is empty
        caster: Function to cast the input value

    Returns:
        The cast value or default

    Raises:
        UserCancel: If user enters a cancel command
    """
    s = input(prompt).strip()
    if is_cancel(s):
        raise UserCancel()
    if s == "":
        return default
    return caster(s)
