from random import choice
from string import ascii_letters, digits

from django.conf import settings


def get_random_url_code(
    size: int | None = None,
    available_chars: str | None = None,
    exlude_chars: str | None = None,
) -> str:
    size = size or getattr(settings, "MAXIMUM_URL_CHARS", 5)
    exlude_chars = exlude_chars or getattr(settings, "EXCLUDE_URL_CHARS", "Ii1")
    available_chars = available_chars or (ascii_letters + digits)
    chars = available_chars.translate({ord(char): None for char in exlude_chars})
    return "".join([choice(chars) for _ in range(size)])
