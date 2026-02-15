"""Bundle configuration loading, validation, and utilities.

Handles reading, parsing, and validating bundle.json files for iA Writer
templates.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Maximum header/footer height per iA docs (400 CSS px).
_MAX_HEIGHT = 400

# Fragment filenames that must not appear in the ``assets`` list.
RESERVED_FRAGMENT_NAMES: frozenset[str] = frozenset(
    {
        "Info.plist",
        "document.html",
        "title.html",
        "header.html",
        "footer.html",
    }
)


def slugify(name: str) -> str:
    """Convert display names into filesystem-friendly slugs.

    Args:
        name: The display name to convert.

    Returns:
        A lowercase slug with spaces and hyphens replaced by underscores.

    Examples:
        >>> slugify("Neon Flux")
        'neon_flux'
        >>> slugify("My-Template Name")
        'my_template_name'
    """
    return name.lower().replace(" ", "_").replace("-", "_")


def read_json(path: Path) -> dict[str, Any]:
    """Read and parse a JSON file.

    Args:
        path: Path to the JSON file to read.

    Returns:
        Parsed JSON content as a dictionary.

    Raises:
        FileNotFoundError: If the JSON file doesn't exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


@dataclass
class BundleConfig:
    """Validated representation of a bundle.json file."""

    name: str
    identifier: str
    description: str = ""
    author: str = ""
    author_url: str = ""
    version: str = "1.0.0"
    bundle_version: str = "1"
    development_region: str = "en"
    bundle_dir: str = ""
    slug: str = ""
    header_height: int = 90
    footer_height: int = 90
    assets: list[str] = field(default_factory=list)
    skip_fragments: list[str] = field(default_factory=list)
    placeholders: dict[str, str] = field(default_factory=dict)

    # Optional iA Writer feature flags
    supports_smart_tables: bool = False
    supports_math: bool = False
    title_uses_header_footer_height: bool = True


def load_bundle_config(
    config_path: Path,
    template_dir: Path | None = None,
) -> BundleConfig:
    """Load a bundle.json file and return a validated BundleConfig.

    Args:
        config_path: Path to the bundle.json file.
        template_dir: Path to the template directory (for asset validation).

    Returns:
        A validated BundleConfig instance.

    Raises:
        FileNotFoundError: If bundle.json doesn't exist.
        json.JSONDecodeError: If the file contains invalid JSON.
        ValueError: If validation fails.
    """
    if not config_path.exists():
        msg = f"bundle.json missing: {config_path}"
        raise FileNotFoundError(msg)

    raw = read_json(config_path)
    cfg = _parse_config(raw)
    validate_bundle_config(cfg, template_dir)
    return cfg


def _parse_config(raw: dict[str, Any]) -> BundleConfig:
    """Parse a raw JSON dict into a BundleConfig.

    Args:
        raw: Parsed JSON dictionary.

    Returns:
        A BundleConfig instance (not yet validated).

    Raises:
        ValueError: If required keys are missing.
    """
    missing = [k for k in ("name", "identifier") if k not in raw]
    if missing:
        msg = f"bundle.json missing required keys: {', '.join(missing)}"
        raise ValueError(msg)

    name = raw["name"]
    return BundleConfig(
        name=name,
        identifier=raw["identifier"],
        description=raw.get("description", ""),
        author=raw.get("author", ""),
        author_url=raw.get("author_url", ""),
        version=raw.get("version", "1.0.0"),
        bundle_version=raw.get("bundle_version", "1"),
        development_region=raw.get("development_region", "en"),
        bundle_dir=raw.get("bundle_dir", f"{name}.iatemplate"),
        slug=raw.get("slug", slugify(name)),
        header_height=raw.get("header_height", 90),
        footer_height=raw.get("footer_height", 90),
        assets=raw.get("assets", []),
        skip_fragments=raw.get("skip_fragments", []),
        placeholders=raw.get("placeholders", {}),
        supports_smart_tables=raw.get("supports_smart_tables", False),
        supports_math=raw.get("supports_math", False),
        title_uses_header_footer_height=raw.get(
            "title_uses_header_footer_height",
            True,
        ),
    )


def validate_bundle_config(
    cfg: BundleConfig,
    template_dir: Path | None = None,
) -> None:
    """Validate a BundleConfig, raising ValueError on problems.

    Checks:
    - ``bundle_dir`` ends with ``.iatemplate``
    - ``header_height`` and ``footer_height`` are ints <= 400
    - ``assets`` do not include reserved fragment filenames
    - All asset paths exist on disk (when *template_dir* is provided)

    Args:
        cfg: The configuration to validate.
        template_dir: Optional template directory for file-existence checks.

    Raises:
        ValueError: On any validation failure.
    """
    errors: list[str] = []

    # bundle_dir suffix
    if not cfg.bundle_dir.endswith(".iatemplate"):
        errors.append(
            f"bundle_dir must end with '.iatemplate', got '{cfg.bundle_dir}'"
        )

    # Height constraints
    for field_name in ("header_height", "footer_height"):
        value = getattr(cfg, field_name)
        if not isinstance(value, int):
            errors.append(
                f"{field_name} must be an integer, got {type(value).__name__}"
            )
        elif value > _MAX_HEIGHT:
            errors.append(f"{field_name} must be <= {_MAX_HEIGHT}, got {value}")

    # Reserved fragment names in assets
    bad_assets = {
        a for a in cfg.assets if Path(a).name in RESERVED_FRAGMENT_NAMES
    }
    if bad_assets:
        errors.append(
            f"assets must not include reserved fragment files: "
            f"{sorted(bad_assets)}. Fragments are rendered by the build "
            f"pipeline and must not be listed in assets."
        )

    # Asset existence
    if template_dir is not None:
        for asset in cfg.assets:
            if not (template_dir / asset).exists():
                errors.append(f"Asset '{asset}' not found in {template_dir}")

    if errors:
        msg = f"Invalid bundle config for '{cfg.name}':\n  " + "\n  ".join(
            errors,
        )
        raise ValueError(msg)


def build_replacements(config: BundleConfig) -> dict[str, str]:
    """Build the placeholder replacement dictionary from config.

    Args:
        config: Validated BundleConfig.

    Returns:
        Dictionary mapping placeholder names to their replacement values.
    """
    replacements = {
        "name": config.name,
        "identifier": config.identifier,
        "description": config.description,
        "title_name": config.name,
        "subtitle": "",
        "slug": config.slug,
        "author": config.author,
        "author_url": config.author_url,
        "version": config.version,
        "bundle_version": config.bundle_version,
        "development_region": config.development_region,
        "header_height": str(config.header_height),
        "footer_height": str(config.footer_height),
    }

    if config.placeholders:
        replacements.update(config.placeholders)

    return replacements
