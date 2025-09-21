"""iA Writer template bundle generator.

This module provides functionality to generate iA Writer template bundles
from source templates with support for multiple CSS variants and custom
fragment overrides.

Typical usage example:
    python src/main.py
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


# Constants for directory paths relative to the project root
FRAGMENTS_DIR_RELATIVE = Path("src/fragments")
TEMPLATES_DIR_RELATIVE = Path("templates")
OUTPUT_DIR_RELATIVE = Path("dist/templates")


def get_project_root() -> Path:
    """Get the project root directory.

    Returns:
        Path to the project root (where pyproject.toml is located).
    """
    # Start from current file and go up to find project root
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback to current working directory
    return Path.cwd()


# Resolved absolute paths used throughout the module
PROJECT_ROOT = get_project_root()
FRAGMENTS_DIR = PROJECT_ROOT / FRAGMENTS_DIR_RELATIVE
TEMPLATES_DIR = PROJECT_ROOT / TEMPLATES_DIR_RELATIVE
OUTPUT_DIR = PROJECT_ROOT / OUTPUT_DIR_RELATIVE


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


def process_template(
    template_content: str,
    replacements: dict[str, str],
) -> str:
    """Replace placeholders in a template with provided values.

    Placeholders in the template should be wrapped in curly braces,
    e.g., {name}, {identifier}, etc.

    Args:
        template_content: The template string containing placeholders.
        replacements: Dictionary mapping placeholder names to values.

    Returns:
        The template string with all placeholders replaced.

    Examples:
        >>> process_template("Hello {name}!", {"name": "World"})
        'Hello World!'
    """
    result = template_content
    for key, value in replacements.items():
        placeholder = f"{{{key}}}"
        if placeholder in result:
            result = result.replace(placeholder, str(value))
    return result


def load_fragment(name: str, template_dir: Path) -> str:
    """Load an HTML/Plist fragment with optional template overrides.

    Searches for fragments in the following order:
    1. Template directory root
    2. Template's fragments subdirectory
    3. Global fragments directory

    Args:
        name: Name of the fragment file to load.
        template_dir: Path to the template directory.

    Returns:
        Content of the fragment file as a string.

    Raises:
        FileNotFoundError: If fragment not found in any location.
    """
    candidate_paths = [
        template_dir / name,
        template_dir / "fragments" / name,
        FRAGMENTS_DIR / name,
    ]

    for path in candidate_paths:
        if path.exists():
            return path.read_text(encoding="utf-8")

    msg = f"Fragment '{name}' not found for template {template_dir.name}"
    raise FileNotFoundError(msg)


def copy_file(source: Path, destination: Path) -> None:
    """Copy a file or directory to the destination.

    Creates parent directories as needed. If copying a directory and
    the destination exists, it will be removed first.

    Args:
        source: Path to the source file or directory.
        destination: Path to the destination.

    Raises:
        FileNotFoundError: If the source doesn't exist.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)

    if source.is_dir():
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
    else:
        shutil.copy2(source, destination)


def copy_assets(
    asset_list: list[str],
    template_dir: Path,
    resources_dir: Path,
) -> None:
    """Copy asset files from template to resources directory.

    Args:
        asset_list: List of relative paths to asset files.
        template_dir: Source template directory.
        resources_dir: Destination resources directory.

    Raises:
        FileNotFoundError: If any asset file is missing.
    """
    for relative_path in asset_list:
        source_path = template_dir / relative_path
        if not source_path.exists():
            msg = (
                f"Expected asset '{relative_path}' missing in "
                f"template directory {template_dir}"
            )
            raise FileNotFoundError(msg)

        destination_path = resources_dir / Path(relative_path).name
        copy_file(source_path, destination_path)


def build_bundle(template_dir: Path) -> None:
    """Build an iA Writer template bundle from source.

    Processes a template directory containing bundle.json and associated
    assets to create a complete .iatemplate bundle.

    Args:
        template_dir: Path to the source template directory.

    Raises:
        FileNotFoundError: If bundle.json or required assets are missing.
        KeyError: If required configuration keys are missing.
        json.JSONDecodeError: If bundle.json contains invalid JSON.
    """
    # Load configuration
    config_path = template_dir / "bundle.json"
    if not config_path.exists():
        msg = f"bundle.json missing for template {template_dir}"
        raise FileNotFoundError(msg)

    config = read_json(config_path)

    # Extract configuration values
    name = config["name"]
    bundle_dir_name = config.get("bundle_dir", f"{name}.iatemplate")

    # Create output directory structure
    bundle_dir = OUTPUT_DIR / bundle_dir_name
    contents_dir = bundle_dir / "Contents"
    resources_dir = contents_dir / "Resources"
    resources_dir.mkdir(parents=True, exist_ok=True)

    # Prepare replacements for templates
    replacements = {
        "name": name,
        "identifier": config["identifier"],
        "description": config.get("description", ""),
        "title_name": config.get("title_name", name),
        "subtitle": config.get("subtitle", ""),
        "slug": config.get("slug", slugify(name)),
        "author": config.get("author", ""),
        "author_url": config.get("author_url", ""),
        "version": config.get("version", "1.0.0"),
        "bundle_version": config.get("bundle_version", "1"),
        "development_region": config.get("development_region", "en"),
        "header_height": str(config.get("header_height", 90)),
        "footer_height": str(config.get("footer_height", 90)),
    }

    # Add any custom placeholders
    if "placeholders" in config:
        replacements.update(config["placeholders"])

    # Process Info.plist
    info_content = process_template(
        load_fragment("Info.plist", template_dir),
        replacements,
    )
    (contents_dir / "Info.plist").write_text(
        info_content,
        encoding="utf-8",
    )

    # Process HTML fragments
    html_fragments = [
        "title.html",
        "header.html",
        "footer.html",
        "document.html",
    ]

    # Check if template wants to skip certain fragments
    skip_fragments = config.get("skip_fragments", [])

    for fragment_name in html_fragments:
        # Skip if explicitly marked to skip
        if fragment_name in skip_fragments:
            continue

        try:
            fragment = load_fragment(fragment_name, template_dir)
            rendered = process_template(fragment, replacements)
            (resources_dir / fragment_name).write_text(
                rendered,
                encoding="utf-8",
            )
        except FileNotFoundError:
            # Skip missing fragments.
            # GitHub template only requires document.html.
            if fragment_name == "document.html":
                # document.html is required
                raise
            continue

    # Copy CSS and other assets
    if "assets" in config:
        copy_assets(config["assets"], template_dir, resources_dir)

    # Handle CSS variants if specified (for backwards compatibility)
    if "css" in config:
        css_config = config["css"]

        # Copy base CSS files
        if "base" in css_config:
            copy_assets(css_config["base"], template_dir, resources_dir)

        # Copy variant CSS files
        if "variants" in css_config:
            for variant_spec in css_config["variants"].values():
                if isinstance(variant_spec, str):
                    copy_assets([variant_spec], template_dir, resources_dir)
                elif (
                    isinstance(variant_spec, dict) and "source" in variant_spec
                ):
                    source = variant_spec["source"]
                    copy_assets([source], template_dir, resources_dir)

                    # Copy to additional targets if specified
                    if "targets" in variant_spec:
                        source_path = template_dir / source
                        targets = variant_spec["targets"]
                        if isinstance(targets, str):
                            targets = [targets]
                        for target in targets:
                            dest = resources_dir / target
                            copy_file(source_path, dest)

    print(f"Built template bundle: {bundle_dir}")


def main() -> None:
    """Build all template bundles found in the templates directory.

    Scans the templates directory for subdirectories containing bundle.json
    files and builds each one into a complete .iatemplate bundle.

    Raises:
        RuntimeError: If no templates directory exists or no templates found.
        SystemExit: On any build errors.
    """
    # Clean and recreate output directory
    if OUTPUT_DIR.parent.exists():
        shutil.rmtree(OUTPUT_DIR.parent)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Check for templates directory
    if not TEMPLATES_DIR.exists():
        msg = (
            "No 'templates/' directory found. Add at least one "
            "template before building."
        )
        raise RuntimeError(msg)

    # Find all template directories
    template_dirs = [path for path in TEMPLATES_DIR.iterdir() if path.is_dir()]

    if not template_dirs:
        msg = "No templates found under the 'templates' directory."
        raise RuntimeError(msg)

    # Build each template
    for template_dir in sorted(template_dirs, key=lambda p: p.name):
        try:
            build_bundle(template_dir)
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            print(f"Error building {template_dir.name}: {e}")
            raise SystemExit(1) from e

    print("\nTemplates generated successfully in dist/templates/")
    print("To install, double-click the .iatemplate bundle")


if __name__ == "__main__":
    main()
