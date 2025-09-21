"""Test GitHub template fixture availability."""

import shutil
import subprocess
from pathlib import Path


def test_github_template_fixture_exists() -> None:
    """Test that GitHub template exists in fixtures directory."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    template_path = fixtures_dir / "GitHub.iatemplate" / "Contents"

    # Check that fixture exists
    assert fixtures_dir.exists(), (
        f"Fixtures directory not found at {fixtures_dir}"
    )
    assert template_path.exists(), (
        f"GitHub template fixture not found at {template_path}"
    )

    # Verify essential files
    assert (template_path / "Info.plist").exists(), (
        "Info.plist not found in fixture"
    )
    assert (template_path / "Resources").exists(), (
        "Resources directory not found in fixture"
    )
    assert (template_path / "Resources" / "document.html").exists(), (
        "document.html not found in fixture"
    )
    assert (template_path / "Resources" / "github.css").exists(), (
        "github.css not found in fixture"
    )

    print(f"GitHub template fixture found at: {template_path}")


def test_download_github_template_if_missing(tmp_path: Path) -> None:
    """Download the GitHub template from the upstream repository when absent."""
    repo_url = "https://github.com/iainc/iA-Writer-Templates.git"
    repo_dir = tmp_path / "iA-Writer-Templates"

    git_executable = shutil.which("git")
    if git_executable is None:
        msg = "Git executable not found on PATH"
        raise RuntimeError(msg)

    # Clone from GitHub
    subprocess.run(
        [git_executable, "clone", "--depth", "1", repo_url, str(repo_dir)],
        check=True,
        capture_output=True,
        text=True,
    )

    # Check that clone was successful
    assert repo_dir.exists(), "Repository was not cloned"
    template_path = repo_dir / "GitHub.iatemplate" / "Contents"
    assert template_path.exists(), (
        "GitHub template not found in cloned repository"
    )

    # Verify essential files
    assert (template_path / "Info.plist").exists(), "Info.plist not found"
    assert (template_path / "Resources").exists(), (
        "Resources directory not found"
    )
    assert (template_path / "Resources" / "document.html").exists(), (
        "document.html not found"
    )
    assert (template_path / "Resources" / "github.css").exists(), (
        "github.css not found"
    )

    print(f"Successfully cloned template to: {template_path}")


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        test_download_github_template_if_missing(Path(tmpdir))
