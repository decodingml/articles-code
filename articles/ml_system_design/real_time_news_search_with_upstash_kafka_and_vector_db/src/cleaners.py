from unstructured.cleaners.core import (
    clean,
    clean_non_ascii_chars,
    replace_unicode_quotes,
    remove_punctuation,
    clean_ordered_bullets,
)
import re


def standardize_dates(text, placeholder="[DATE]"):
    date_pattern = (
        r"\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{2,4}[-/]\d{1,2}[-/]\d{1,2})\b"
    )
    return re.sub(date_pattern, placeholder, text)


def standardize_times(text, placeholder="[TIME]"):
    time_pattern = r"\b(?:\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM)?)\b"
    return re.sub(time_pattern, placeholder, text)


def remove_html_tags(text):
    html_tag_pattern = r"<[^>]+>"
    return re.sub(html_tag_pattern, "", text)


def normalize_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()


def clean_full(text: str) -> str:
    """
    Cleans the given text by applying the following set of operations:
    - clean (e.g whitespaces)
    - clean_ordered_bullets (eg. bullets)
    - replace_unicode_quotes (eg. quotes)
    - clean_non_ascii_chars (eg. non-ascii characters)
    - remove_punctuation (eg. punctuation)

    Args:
        text (str): The text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    text = clean(
        text=text, lowercase=True, extra_whitespace=True, dashes=True, bullets=True
    )
    text = replace_unicode_quotes(text)
    text = clean_non_ascii_chars(text)
    text = remove_punctuation(text)
    return text
