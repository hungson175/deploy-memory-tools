"""
Collection name sanitization utilities
"""

import re


def sanitize_collection_name(name: str) -> str:
    """
    Sanitize project name for use as Qdrant collection name

    Args:
        name: Raw project name

    Returns:
        Sanitized collection name following pattern: proj-{sanitized-name}
    """
    # Convert to lowercase and replace spaces/special chars with hyphens
    sanitized = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return f"proj-{sanitized}"
