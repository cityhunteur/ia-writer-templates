"""Fragment loading and placeholder rendering.

Handles loading HTML/Plist fragments from template or global directories
and rendering placeholder substitutions.
"""

from __future__ import annotations

from pathlib import Path


def load_fragment(
    name: str,
    template_dir: Path,
    fragments_dir: Path,
) -> str:
    """Load an HTML/Plist fragment with optional template overrides.

    Searches for fragments in the following order:
    1. Template directory root
    2. Template's fragments subdirectory
    3. Global fragments directory

    Args:
        name: Name of the fragment file to load.
        template_dir: Path to the template directory.
        fragments_dir: Path to the global fragments directory.

    Returns:
        Content of the fragment file as a string.

    Raises:
        FileNotFoundError: If fragment not found in any location.
    """
    candidate_paths = [
        template_dir / name,
        template_dir / "fragments" / name,
        fragments_dir / name,
    ]

    for path in candidate_paths:
        if path.exists():
            return path.read_text(encoding="utf-8")

    msg = f"Fragment '{name}' not found for template {template_dir.name}"
    raise FileNotFoundError(msg)


def render_placeholders(
    text: str,
    replacements: dict[str, str],
) -> str:
    """Replace placeholders in a template with provided values.

    Placeholders in the template should be wrapped in curly braces,
    e.g., {name}, {identifier}, etc.

    Args:
        text: The template string containing placeholders.
        replacements: Dictionary mapping placeholder names to values.

    Returns:
        The template string with all placeholders replaced.

    Examples:
        >>> render_placeholders("Hello {name}!", {"name": "World"})
        'Hello World!'
    """
    result = text
    for key, value in replacements.items():
        placeholder = f"{{{key}}}"
        if placeholder in result:
            result = result.replace(placeholder, str(value))
    return result
