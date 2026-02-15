"""Template bundle builder.

Orchestrates building iA Writer .iatemplate bundles from source templates.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from ia_writer_templates.config import build_replacements, load_bundle_config
from ia_writer_templates.fragments import load_fragment, render_placeholders


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


def _copy_assets(
    asset_list: list[str],
    template_dir: Path,
    resources_dir: Path,
) -> None:
    """Copy asset files from template to resources directory.

    Preserves relative subdirectory layout and detects collisions with
    previously written files (fragments or earlier assets).

    Args:
        asset_list: List of relative paths to asset files.
        template_dir: Source template directory.
        resources_dir: Destination resources directory.

    Raises:
        FileNotFoundError: If any asset file is missing.
        ValueError: If an asset would collide with an existing file.
    """
    for relative_path in asset_list:
        source_path = template_dir / relative_path
        if not source_path.exists():
            msg = (
                f"Expected asset '{relative_path}' missing in "
                f"template directory {template_dir}"
            )
            raise FileNotFoundError(msg)

        # Preserve relative paths instead of flattening
        destination_path = resources_dir / relative_path

        # Collision detection
        if destination_path.exists():
            msg = (
                f"Asset '{relative_path}' would overwrite an existing "
                f"file at {destination_path}. Check for duplicate assets "
                f"or a collision with a rendered fragment."
            )
            raise ValueError(msg)

        copy_file(source_path, destination_path)


class TemplateBuilder:
    """Builds iA Writer template bundles from source directories.

    Args:
        project_root: Path to the project root directory.
        output_dir: Path to the output directory for built bundles.
        fragments_dir: Path to the global fragments directory.
    """

    def __init__(
        self,
        project_root: Path,
        output_dir: Path,
        fragments_dir: Path,
    ) -> None:
        """Initialize the builder with project paths."""
        self.project_root = project_root
        self.output_dir = output_dir
        self.fragments_dir = fragments_dir

    def build_one(self, template_dir: Path) -> Path:
        """Build a single iA Writer template bundle.

        Args:
            template_dir: Path to the source template directory.

        Returns:
            Path to the built bundle directory.

        Raises:
            FileNotFoundError: If bundle.json or required assets are missing.
            KeyError: If required configuration keys are missing.
            ValueError: If validation fails or collisions are detected.
        """
        config_path = template_dir / "bundle.json"
        config = load_bundle_config(config_path, template_dir)

        bundle_dir_name = config.bundle_dir

        # Create output directory structure
        bundle_dir = self.output_dir / bundle_dir_name
        contents_dir = bundle_dir / "Contents"
        resources_dir = contents_dir / "Resources"
        resources_dir.mkdir(parents=True, exist_ok=True)

        replacements = build_replacements(config)

        # Process Info.plist (required per template, no global fallback)
        info_plist_path = template_dir / "Info.plist"
        if not info_plist_path.exists():
            msg = (
                f"Info.plist required in template directory "
                f"'{template_dir.name}'. Each template must provide "
                f"its own Info.plist."
            )
            raise FileNotFoundError(msg)
        info_content = render_placeholders(
            info_plist_path.read_text(encoding="utf-8"),
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

        skip_fragments = config.skip_fragments

        for fragment_name in html_fragments:
            if fragment_name in skip_fragments:
                continue

            try:
                fragment = load_fragment(
                    fragment_name,
                    template_dir,
                    self.fragments_dir,
                )
                rendered = render_placeholders(fragment, replacements)
                (resources_dir / fragment_name).write_text(
                    rendered,
                    encoding="utf-8",
                )
            except FileNotFoundError:
                if fragment_name == "document.html":
                    raise
                continue

        # Copy assets (validated: no reserved names, paths preserved)
        if config.assets:
            _copy_assets(config.assets, template_dir, resources_dir)

        # Handle CSS variants (backwards compatibility)
        if hasattr(config, "_raw_css"):
            self._copy_css_variants(
                config._raw_css,  # noqa: SLF001
                template_dir,
                resources_dir,
            )

        print(f"Built template bundle: {bundle_dir}")
        return bundle_dir

    def _copy_css_variants(
        self,
        css_config: dict,
        template_dir: Path,
        resources_dir: Path,
    ) -> None:
        """Copy CSS variant files (backwards compatibility).

        Args:
            css_config: The ``css`` section from bundle.json.
            template_dir: Source template directory.
            resources_dir: Destination resources directory.
        """
        if "base" in css_config:
            _copy_assets(
                css_config["base"],
                template_dir,
                resources_dir,
            )

        if "variants" in css_config:
            for variant_spec in css_config["variants"].values():
                if isinstance(variant_spec, str):
                    _copy_assets(
                        [variant_spec],
                        template_dir,
                        resources_dir,
                    )
                elif (
                    isinstance(variant_spec, dict) and "source" in variant_spec
                ):
                    source = variant_spec["source"]
                    _copy_assets(
                        [source],
                        template_dir,
                        resources_dir,
                    )

                    if "targets" in variant_spec:
                        source_path = template_dir / source
                        targets = variant_spec["targets"]
                        if isinstance(targets, str):
                            targets = [targets]
                        for target in targets:
                            dest = resources_dir / target
                            copy_file(source_path, dest)

    def build_all(self, templates_dir: Path) -> list[Path]:
        """Build all template bundles found in a templates directory.

        Args:
            templates_dir: Path to the directory containing template subdirs.

        Returns:
            List of paths to built bundle directories.

        Raises:
            RuntimeError: If no templates directory or templates found.
        """
        if not templates_dir.exists():
            msg = (
                "No 'templates/' directory found. Add at least one "
                "template before building."
            )
            raise RuntimeError(msg)

        template_dirs = [
            path for path in templates_dir.iterdir() if path.is_dir()
        ]

        if not template_dirs:
            msg = "No templates found under the 'templates' directory."
            raise RuntimeError(msg)

        results = []
        for template_dir in sorted(template_dirs, key=lambda p: p.name):
            results.append(self.build_one(template_dir))

        return results
