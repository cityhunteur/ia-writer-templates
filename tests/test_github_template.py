"""Integration tests for GitHub template generation.

This module tests that the generated GitHub template matches
the original template from iA Writer Templates repository.
"""

import filecmp
import shutil
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest
from pytest import MonkeyPatch

import ia_writer_templates.main as main_module
from ia_writer_templates.main import build_bundle, get_project_root


Environment = dict[str, Path]


def get_github_template_fixture(test_file_path: str) -> Path:
    """Get the GitHub template from fixtures directory or download if needed."""
    # Get the test directory
    test_dir = Path(test_file_path).parent
    fixtures_dir = test_dir / "fixtures"
    fixture_template = fixtures_dir / "GitHub.iatemplate" / "Contents"

    # Check if fixture exists
    if fixture_template.exists():
        return fixture_template

    # If fixture doesn't exist, try to download from GitHub
    repo_url = "https://github.com/iainc/iA-Writer-Templates.git"
    temp_dir = fixtures_dir / "temp_clone"

    if not temp_dir.exists():
        print(f"Fixture not found at {fixture_template}")
        print("Downloading from GitHub...")
        git_executable = shutil.which("git")
        if git_executable is None:
            msg = "Git executable not found on PATH"
            raise RuntimeError(msg)

        subprocess.run(
            [git_executable, "clone", "--depth", "1", repo_url, str(temp_dir)],
            check=True,
            capture_output=True,
            text=True,
        )

        # Copy the GitHub template to fixtures
        source = temp_dir / "GitHub.iatemplate"
        destination = fixtures_dir / "GitHub.iatemplate"
        shutil.copytree(source, destination)

        # Clean up temp directory
        shutil.rmtree(temp_dir)

    return fixture_template


@pytest.fixture
def setup_test_env(tmp_path: Path) -> Environment:
    """Set up test environment with clean output directory."""
    # Get project root
    root = get_project_root()

    # Create temporary output directory
    output_dir = tmp_path / "dist" / "templates"
    output_dir.mkdir(parents=True)

    # Get original template from fixtures
    original_template = get_github_template_fixture(__file__)

    # Return paths
    return {
        "root": root,
        "output_dir": output_dir,
        "template_dir": root / "templates" / "github",
        "original_template": original_template,
    }


def normalize_file(file_path: Path) -> str | bytes:
    """Read file and normalize whitespace for comparison."""
    try:
        with file_path.open(encoding="utf-8") as handle:
            content = handle.read()
            # Strip trailing whitespace from each line and file
            lines = [line.rstrip() for line in content.splitlines()]
            return "\n".join(lines).strip()
    except Exception:
        # For binary files, just read as bytes
        with file_path.open("rb") as handle:
            return handle.read()


def compare_files(file1: Path, file2: Path) -> bool:
    """Compare two files, ignoring trailing whitespace."""
    # For CSS and other binary files, do exact comparison
    if file1.suffix in [".css", ".txt", ".pdf", ".jpg", ".png"]:
        return filecmp.cmp(file1, file2, shallow=False)

    # For text files, normalize and compare
    return normalize_file(file1) == normalize_file(file2)


def compare_directories(dir1: Path, dir2: Path) -> tuple[bool, str]:
    """Recursively compare two directories."""
    dir1 = Path(dir1)
    dir2 = Path(dir2)

    # Get all files in both directories
    files1 = {
        path.relative_to(dir1) for path in dir1.rglob("*") if path.is_file()
    }
    files2 = {
        path.relative_to(dir2) for path in dir2.rglob("*") if path.is_file()
    }

    # Check if same files exist
    if files1 != files2:
        missing_in_generated = files1 - files2
        extra_in_generated = files2 - files1

        error_msg = []
        if missing_in_generated:
            error_msg.append(
                f"Missing files in generated template: {missing_in_generated}"
            )
        if extra_in_generated:
            error_msg.append(
                f"Extra files in generated template: {extra_in_generated}"
            )

        return False, "\n".join(error_msg)

    # Compare each file
    differences = []
    for file_path in files1:
        file1_full = dir1 / file_path
        file2_full = dir2 / file_path

        if not compare_files(file1_full, file2_full):
            differences.append(str(file_path))

    if differences:
        return False, f"Files differ: {differences}"

    return True, "All files match"


@pytest.mark.integration
class TestGitHubTemplate:
    """Test GitHub template generation."""

    def test_github_template_exists(self, setup_test_env: Environment) -> None:
        """Test that GitHub template source files exist."""
        env = setup_test_env
        template_dir = env["template_dir"]

        assert template_dir.exists(), (
            f"Template directory not found: {template_dir}"
        )
        assert (template_dir / "bundle.json").exists(), "bundle.json not found"
        assert (template_dir / "document.html").exists(), (
            "document.html not found"
        )
        assert (template_dir / "github.css").exists(), "github.css not found"
        assert (template_dir / "LICENSE.txt").exists(), "LICENSE.txt not found"

    def test_original_template_exists(
        self,
        setup_test_env: Environment,
    ) -> None:
        """Test that original GitHub template exists for comparison."""
        env = setup_test_env
        original = env["original_template"]

        assert original.exists(), f"Original template not found at {original}"
        assert (original / "Info.plist").exists(), (
            "Original Info.plist not found"
        )
        assert (original / "Resources").exists(), (
            "Original Resources directory not found"
        )

    def test_build_github_template(
        self,
        setup_test_env: Environment,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test building the GitHub template."""
        env = setup_test_env

        monkeypatch.setattr(main_module, "OUTPUT_DIR", env["output_dir"])

        # Build the template
        build_bundle(env["template_dir"])

        # Check output exists
        output_bundle = env["output_dir"] / "GitHub.iatemplate"
        assert output_bundle.exists(), "Generated bundle not found"
        assert (output_bundle / "Contents").exists(), (
            "Contents directory not found"
        )
        assert (output_bundle / "Contents" / "Info.plist").exists(), (
            "Info.plist not found"
        )
        assert (output_bundle / "Contents" / "Resources").exists(), (
            "Resources not found"
        )

    def test_generated_matches_original(
        self,
        setup_test_env: Environment,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test that generated GitHub template matches the original."""
        env = setup_test_env

        monkeypatch.setattr(main_module, "OUTPUT_DIR", env["output_dir"])

        # Build the template
        build_bundle(env["template_dir"])

        # Compare with original
        generated = env["output_dir"] / "GitHub.iatemplate" / "Contents"
        original = env["original_template"]

        matches, message = compare_directories(original, generated)
        assert matches, f"Generated template does not match original: {message}"

    def test_info_plist_content(
        self,
        setup_test_env: Environment,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test that Info.plist contains correct values."""
        env = setup_test_env

        monkeypatch.setattr(main_module, "OUTPUT_DIR", env["output_dir"])

        # Build the template
        build_bundle(env["template_dir"])

        # Read generated Info.plist
        info_plist = (
            env["output_dir"] / "GitHub.iatemplate" / "Contents" / "Info.plist"
        )
        content = info_plist.read_text()

        # Check expected values
        assert "net.ia.writer.template.github" in content, (
            "Bundle identifier not found"
        )
        assert "<string>GitHub</string>" in content, "Bundle name not found"
        assert "<string>1.0.1</string>" in content, "Version not found"
        assert "<string>iA</string>" in content, "Author not found"
        assert "https://github.com/" in content, "Author URL not found"
        assert "<integer>90</integer>" in content, "Height values not found"

    def test_css_files_copied(
        self,
        setup_test_env: Environment,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test that all CSS files are copied correctly."""
        env = setup_test_env

        monkeypatch.setattr(main_module, "OUTPUT_DIR", env["output_dir"])

        # Build the template
        build_bundle(env["template_dir"])

        resources = (
            env["output_dir"] / "GitHub.iatemplate" / "Contents" / "Resources"
        )

        # Check CSS files exist
        css_files = [
            "github.css",
            "github-markdown-light.css",
            "github-markdown-dark.css",
        ]

        for css_file in css_files:
            assert (resources / css_file).exists(), f"{css_file} not found"

            # Compare with original
            original_css = env["original_template"] / "Resources" / css_file
            generated_css = resources / css_file

            assert filecmp.cmp(original_css, generated_css, shallow=False), (
                f"{css_file} content differs from original"
            )

    def test_no_extra_html_files(
        self,
        setup_test_env: Environment,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Test that no extra HTML files are generated for GitHub template."""
        env = setup_test_env

        monkeypatch.setattr(main_module, "OUTPUT_DIR", env["output_dir"])

        # Build the template
        build_bundle(env["template_dir"])

        resources = (
            env["output_dir"] / "GitHub.iatemplate" / "Contents" / "Resources"
        )

        # Check that only document.html exists
        html_files = list(resources.glob("*.html"))
        assert len(html_files) == 1, (
            f"Expected only document.html, found {[f.name for f in html_files]}"
        )
        assert html_files[0].name == "document.html", "document.html not found"

        # These files should NOT exist
        assert not (resources / "title.html").exists(), (
            "title.html should not exist"
        )
        assert not (resources / "header.html").exists(), (
            "header.html should not exist"
        )
        assert not (resources / "footer.html").exists(), (
            "footer.html should not exist"
        )


@pytest.fixture(autouse=True)
def cleanup_dist() -> Iterator[None]:
    """Clean up dist directory after each test."""
    yield
    # Cleanup happens after test
    dist_dir = get_project_root() / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
