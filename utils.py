"""
=========================================================
AI SQL Analytics Assistant
File: utils.py
=========================================================

Purpose
-------
Shared utility functions used throughout the application.

Includes:
- Question normalization
- Synonym handling
- Typo correction
- SQL formatting
- Formatting helpers
"""

from __future__ import annotations

import re
import unicodedata
from typing import Dict, List

import sqlparse

# =========================================================
# Common Typo Corrections
# =========================================================

TYPO_MAP: Dict[str, str] = {

    "custmer": "customer",
    "custmers": "customers",

    "ordr": "order",
    "ordrs": "orders",

    "paymnt": "payment",
    "paymnts": "payments",

    "prodct": "product",
    "prodcts": "products",

    "categry": "category",
    "catgory": "category",

    "reveneu": "revenue",
    "revnue": "revenue",

    "retun": "return",
    "retrun": "return",

    "amunt": "amount",
    "totl": "total",

    "quanity": "quantity",
    "quanitity": "quantity"

}

# =========================================================
# Domain Synonyms
# =========================================================

SYNONYM_MAP: Dict[str, str] = {

    # Selling

    "best": "highest",

    "top": "highest",

    "most": "highest",

    "maximum": "highest",

    "selling": "sales",

    "sold": "sales",

    "sale": "sales",

    "sales": "sales",

    "item": "product",

    "items": "products",

    # Customer

    "buyer": "customer",

    "buyers": "customers",

    "client": "customer",

    "clients": "customers",

    # Orders

    "purchase": "order",

    "purchases": "orders",

    # Revenue

    "income": "revenue",

    "earnings": "revenue",

    "profit": "revenue",

    # Returns

    "refund": "return",

    "refunded": "return",

    # Payments

    "payment": "payments",

    "paid": "payments"

}

# =========================================================
# Stop Words
# =========================================================

STOP_WORDS = {

    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "of",
    "for",
    "to",
    "in",
    "on",
    "from",
    "please",
    "show",
    "give",
    "display",
    "tell",
    "me"

}

# =========================================================
# Remove Unicode Noise
# =========================================================

def normalize_unicode(text: str) -> str:

    return unicodedata.normalize("NFKC", text)

# =========================================================
# Remove Punctuation
# =========================================================

def remove_punctuation(text: str) -> str:

    return re.sub(r"[^\w\s]", " ", text)

# =========================================================
# Remove Extra Spaces
# =========================================================

def remove_extra_spaces(text: str) -> str:

    return " ".join(text.split())

# =========================================================
# Typo Correction
# =========================================================

def correct_typos(text: str) -> str:

    words = []

    for word in text.split():

        words.append(

            TYPO_MAP.get(
                word,
                word
            )

        )

    return " ".join(words)

# =========================================================
# Synonym Replacement
# =========================================================

def replace_synonyms(text: str) -> str:

    words = []

    for word in text.split():

        words.append(

            SYNONYM_MAP.get(
                word,
                word
            )

        )

    return " ".join(words)

# =========================================================
# Remove Stop Words
# =========================================================

def remove_stop_words(text: str) -> str:

    words = [

        word

        for word in text.split()

        if word not in STOP_WORDS

    ]

    return " ".join(words)

# =========================================================
# Singular / Plural Normalization
# =========================================================

def normalize_plural(word: str) -> str:

    if len(word) > 3 and word.endswith("s"):

        return word[:-1]

    return word

def normalize_tokens(text: str) -> str:

    words = [

        normalize_plural(word)

        for word in text.split()

    ]

    return " ".join(words)

# =========================================================
# Main Question Normalization
# =========================================================

def normalize_question(question: str) -> str:
    """
    Produces a canonical representation of a user question
    for RapidFuzz matching.
    """

    question = normalize_unicode(question)

    question = question.lower()

    question = remove_punctuation(question)

    question = remove_extra_spaces(question)

    question = correct_typos(question)

    question = replace_synonyms(question)

    question = remove_stop_words(question)

    question = normalize_tokens(question)

    question = remove_extra_spaces(question)

    return question
    # =========================================================
# SQL Formatting
# =========================================================

def format_sql(sql: str) -> str:
    """
    Beautify SQL for display.
    """

    return sqlparse.format(
        sql,
        reindent=True,
        keyword_case="upper",
        identifier_case=None,
        strip_comments=False
    )


# =========================================================
# Compact SQL
# =========================================================

def compact_sql(sql: str) -> str:
    """
    Convert SQL into a single line.
    """

    return " ".join(sql.split())


# =========================================================
# Execution Time Formatting
# =========================================================

def format_execution_time(seconds: float) -> str:

    if seconds < 1:
        return f"{seconds * 1000:.2f} ms"

    return f"{seconds:.3f} sec"


# =========================================================
# Number Formatting
# =========================================================

def format_number(value) -> str:

    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)


# =========================================================
# Decimal Formatting
# =========================================================

def format_decimal(value, digits: int = 2) -> str:

    try:
        return f"{float(value):,.{digits}f}"
    except Exception:
        return str(value)


# =========================================================
# Currency Formatting
# =========================================================

def format_currency(
    value,
    symbol: str = "₹"
) -> str:

    try:
        return f"{symbol}{float(value):,.2f}"
    except Exception:
        return str(value)


# =========================================================
# Percentage Formatting
# =========================================================

def format_percentage(
    value,
    digits: int = 2
) -> str:

    try:
        return f"{float(value):.{digits}f}%"
    except Exception:
        return str(value)


# =========================================================
# Row Count Formatting
# =========================================================

def format_rows(rows: int) -> str:

    try:
        return f"{rows:,} rows"
    except Exception:
        return str(rows)


# =========================================================
# Timestamp Helpers
# =========================================================

from datetime import datetime


def current_timestamp() -> str:

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def current_date() -> str:

    return datetime.now().strftime(
        "%Y-%m-%d"
    )


def current_time() -> str:

    return datetime.now().strftime(
        "%H:%M:%S"
    )


# =========================================================
# Safe Filename
# =========================================================

def safe_filename(filename: str) -> str:
    """
    Remove invalid filename characters.
    """

    filename = re.sub(
        r'[<>:"/\\\\|?*]',
        "_",
        filename
    )

    filename = filename.strip()

    if not filename:
        filename = "output"

    return filename


# =========================================================
# File Name with Timestamp
# =========================================================

def timestamped_filename(
    prefix: str,
    extension: str
) -> str:

    ts = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return f"{safe_filename(prefix)}_{ts}.{extension}"


# =========================================================
# DataFrame Empty Check
# =========================================================

def is_dataframe_empty(df) -> bool:

    if df is None:
        return True

    return df.empty


# =========================================================
# Limit DataFrame Rows
# =========================================================

def limit_dataframe(df, limit: int = 1000):

    if df is None:
        return df

    if len(df) <= limit:
        return df

    return df.head(limit)
    # =========================================================
# Data Export Helpers
# =========================================================

import hashlib
import json
from io import BytesIO
from typing import Any

import pandas as pd


def dataframe_to_csv(df: pd.DataFrame) -> bytes:
    """
    Convert DataFrame to CSV bytes.
    Suitable for Streamlit download_button.
    """
    return df.to_csv(index=False).encode("utf-8")


def dataframe_to_excel(df: pd.DataFrame) -> bytes:
    """
    Convert DataFrame to Excel bytes.
    """

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Results",
            index=False
        )

    output.seek(0)

    return output.read()


# =========================================================
# JSON Helpers
# =========================================================

def to_json(data: Any) -> str:
    """
    Convert object to formatted JSON string.
    """

    return json.dumps(
        data,
        indent=4,
        default=str,
        ensure_ascii=False
    )


# =========================================================
# Query Hash
# =========================================================

def query_hash(query: str) -> str:
    """
    Stable hash for caching/history.
    """

    return hashlib.sha256(
        query.strip().encode("utf-8")
    ).hexdigest()


# =========================================================
# Markdown Table
# =========================================================

def dataframe_to_markdown(
    df: pd.DataFrame,
    max_rows: int = 20
) -> str:
    """
    Convert DataFrame to markdown.
    """

    if df.empty:
        return "No records found."

    return (
        df.head(max_rows)
          .to_markdown(index=False)
    )


# =========================================================
# Result Summary
# =========================================================

def summarize_dataframe(
    df: pd.DataFrame
) -> dict:
    """
    Lightweight summary of query results.
    """

    if df is None or df.empty:

        return {

            "rows": 0,
            "columns": 0,
            "column_names": []

        }

    return {

        "rows": len(df),

        "columns": len(df.columns),

        "column_names": list(df.columns)

    }


# =========================================================
# Remove Duplicate Spaces
# =========================================================

def clean_text(text: str) -> str:

    return " ".join(
        str(text).split()
    )


# =========================================================
# Convert Anything to String
# =========================================================

def safe_str(value) -> str:

    if value is None:
        return ""

    return str(value)


# =========================================================
# Truncate Text
# =========================================================

def truncate_text(
    text: str,
    length: int = 150
) -> str:

    text = safe_str(text)

    if len(text) <= length:
        return text

    return text[:length] + "..."


# =========================================================
# Success / Error Helpers
# =========================================================

def success(message: str) -> dict:

    return {

        "status": "success",

        "message": message

    }


def failure(message: str) -> dict:

    return {

        "status": "error",

        "message": message

    }


# =========================================================
# Module Exports
# =========================================================

__all__ = [

    # Question Normalization
    "normalize_question",
    "normalize_unicode",
    "correct_typos",
    "replace_synonyms",
    "remove_stop_words",
    "normalize_tokens",

    # SQL
    "format_sql",
    "compact_sql",

    # Formatting
    "format_number",
    "format_decimal",
    "format_currency",
    "format_percentage",
    "format_execution_time",
    "format_rows",

    # Time
    "current_timestamp",
    "current_date",
    "current_time",

    # Files
    "safe_filename",
    "timestamped_filename",

    # DataFrame
    "is_dataframe_empty",
    "limit_dataframe",
    "dataframe_to_csv",
    "dataframe_to_excel",
    "dataframe_to_markdown",
    "summarize_dataframe",

    # JSON
    "to_json",

    # Utilities
    "query_hash",
    "clean_text",
    "safe_str",
    "truncate_text",

    # Status
    "success",
    "failure"
]