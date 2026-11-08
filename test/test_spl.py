"""
Builds a set of variants that works on every OS, then the SPL overview from them.

Run it with `pytest test/test_spl.py`, then open `.yanga/build/index.html`.
"""

import re
import subprocess  # nosec
import sys
from pathlib import Path

import pytest

from yanga_core.commands.run import RunCommand, RunCommandConfig

BUILDS = [
    ("Disco", "gtest"),
    ("Disco", "pc_terminal"),
    ("Disco", "zephyr_esp32h2"),
    ("Sleep", "gtest"),
    ("Sleep", "pc_terminal"),
    ("Spa", "gtest"),
    ("Spa", "pc_gui"),
]


@pytest.fixture(scope="module")
def overview_file() -> Path:
    """Build in a fixture, so that selecting the test with `-k` still builds first."""
    project_dir = Path.cwd()
    build_dir = project_dir / ".yanga" / "build"
    # The overview lists every manifest on the disk; this run must list only its own builds.
    for manifest in (build_dir / "variants").rglob("publish_manifest.json"):
        manifest.unlink()

    for variant, platform in BUILDS:
        config = RunCommandConfig(
            project_dir=project_dir,
            platform=platform,
            variant_name=variant,
            not_interactive=True,
            target="report",
        )
        assert RunCommand().do_run(config) == 0, f"Building {variant} on {platform} failed"

    # This interpreter, because a pypeline outside the project venv cannot load the steps.
    subprocess.run([sys.executable, "-m", "pypeline.main", "run", "--config-file", "spl_pypeline.yaml"], cwd=project_dir, check=True)  # nosec
    return build_dir / "index.html"


def test_overview_links_every_build(overview_file: Path) -> None:
    # Arrange
    html = overview_file.read_text(encoding="utf-8")

    # Act
    relative_links = [href for href in re.findall(r'href="([^"]+)"', html) if "://" not in href]
    variant_links = [link for link in relative_links if link.startswith("variants/")]

    # Assert
    assert [link for link in relative_links if not (overview_file.parent / link).is_file()] == []
    assert len(variant_links) == len(BUILDS), variant_links
    for variant, platform in BUILDS:
        assert any(link.startswith(f"variants/{variant}/{platform}/") for link in variant_links), f"No link for {variant} on {platform}"
    assert 'class="commit-mismatch"' not in html, "Every build in this run must come from the current commit"
