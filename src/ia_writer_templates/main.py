"""iA Writer template bundle generator.

Thin entry point that delegates to the TemplateBuilder.

Typical usage example:
    python -m ia_writer_templates.main
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from ia_writer_templates.builder import TemplateBuilder


# Constants for directory paths relative to the project root
FRAGMENTS_DIR_RELATIVE = Path("src/fragments")
TEMPLATES_DIR_RELATIVE = Path("templates")
OUTPUT_DIR_RELATIVE = Path("dist/templates")


def get_project_root() -> Path:
    """Get the project root directory.

    Returns:
        Path to the project root (where pyproject.toml is located).
    """
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()


# Resolved absolute paths used throughout the module
PROJECT_ROOT = get_project_root()
FRAGMENTS_DIR = PROJECT_ROOT / FRAGMENTS_DIR_RELATIVE
TEMPLATES_DIR = PROJECT_ROOT / TEMPLATES_DIR_RELATIVE
OUTPUT_DIR = PROJECT_ROOT / OUTPUT_DIR_RELATIVE


# ---------------------------------------------------------------------------
# Backwards-compatible shims used by existing tests (monkeypatched via
# ``monkeypatch.setattr(main_module, "OUTPUT_DIR", ...)``).
# The builder reads OUTPUT_DIR from this module at call-time so the
# monkeypatch takes effect.
# ---------------------------------------------------------------------------


def build_bundle(template_dir: Path) -> None:
    """Build a single iA Writer template bundle (backwards-compatible API).

    Args:
        template_dir: Path to the source template directory.
    """
    builder = TemplateBuilder(
        project_root=PROJECT_ROOT,
        output_dir=OUTPUT_DIR,
        fragments_dir=FRAGMENTS_DIR,
    )
    builder.build_one(template_dir)


def main() -> None:
    """Build all template bundles found in the templates directory.

    Raises:
        RuntimeError: If no templates directory exists or no templates found.
        SystemExit: On any build errors.
    """
    # Clean and recreate output directory
    if OUTPUT_DIR.parent.exists():
        shutil.rmtree(OUTPUT_DIR.parent)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    builder = TemplateBuilder(
        project_root=PROJECT_ROOT,
        output_dir=OUTPUT_DIR,
        fragments_dir=FRAGMENTS_DIR,
    )

    try:
        builder.build_all(TEMPLATES_DIR)
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"Error: {e}")
        raise SystemExit(1) from e

    print("\nTemplates generated successfully in dist/templates/")
    print("To install, double-click the .iatemplate bundle")


if __name__ == "__main__":
    main()
