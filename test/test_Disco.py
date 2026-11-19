import re
import sys
from pathlib import Path
from xml.etree import ElementTree

import pytest
from pypeline_semantic_release.check_ci_context import CISystem

from spled_lib import POWER_BUTTON_KEY, Variant, build_dir, find_library
from yanga_core.commands.run import RunCommand, RunCommandConfig

VARIANT_NAME = "Disco"
# POWER_BUTTON_PRESS_DEBOUNCE, from components/power_button/src/power_button.h.
PRESS_DEBOUNCE_STEPS = 10
LIGHT_OFF = "#000000"
# CONFIG_COLOR_GREEN at the default brightness of 128.
LIGHT_GREEN = "#008000"
# A resolved `source:` link to a coverage page: href, fragment line, link text path and line.
COVERAGE_LINK = re.compile(r'<a\b[^>]*\bhref="([^"#]*coverage/[^"#]*\.html)#l(\d+)"[^>]*>([^<]*):(\d+)</a>')
VSCODE_LINK = re.compile(r'href="vscode://file/([^"]*):(\d+)"')
# The source docs pages of light_controller, relative to a report directory.
LIGHT_CONTROLLER_PAGES = Path(".yanga/build/variants", VARIANT_NAME, "gtest/light_controller")
# The build picks the resolver profile with CheckCIContext; detect CI the same way.
IS_CI = any(detector.detect() for system in CISystem if (detector := system.get_detector()))
# The variant report's link to the variant test coverage page, as sphinx renders the toctree entry.
VARIANT_TEST_COVERAGE_LINK = re.compile(r'<a\b[^>]*\bhref="variant_test_coverage/index\.html"[^>]*>Variant Test Coverage</a>')


@pytest.fixture(scope="module")
def variant() -> Variant:
    """
    Build the variant as a shared library and bind to it.

    Requesting this fixture is what orders the build before the test that drives the
    library; declaration order in the file would not survive `-k` or a single node id.
    """
    config = RunCommandConfig(
        project_dir=Path.cwd(),
        platform="pc_gui",
        variant_name=VARIANT_NAME,
        not_interactive=True,
        target="build",
    )
    assert RunCommand().do_run(config) == 0, "Building the shared library failed"

    return Variant(find_library(build_dir(Path.cwd(), VARIANT_NAME), VARIANT_NAME))


@pytest.fixture(scope="module")
def gtest_build_dir() -> Path:
    """Build the variant report and the light_controller component report on gtest."""
    for target in ("report", "light_controller_report"):
        config = RunCommandConfig(
            project_dir=Path.cwd(),
            platform="gtest",
            variant_name=VARIANT_NAME,
            not_interactive=True,
            target=target,
        )
        assert RunCommand().do_run(config) == 0, f"Building {target} failed"

    return Path.cwd() / ".yanga/build/variants" / VARIANT_NAME / "gtest"


class Test_Disco:
    variant_name = VARIANT_NAME

    @pytest.mark.parametrize(
        ("platform", "target"),
        [
            ("pc_terminal", "report"),
            ("pc_gui", "report"),
            ("gtest", "report"),
            # The riscv64 toolchain comes from poks on every OS; native_sim needs a Linux host.
            pytest.param("zephyr_sim", "all", marks=pytest.mark.skipif(sys.platform != "linux", reason="native_sim is Linux-only")),
            ("zephyr_esp32h2", "all"),
            # A board defined in this repository (platforms/zephyr/boards), not in Zephyr.
            ("zephyr_esp32h2_waveshare", "all"),
        ],
    )
    def test_build(self, platform: str, target: str):
        # Arrange
        config = RunCommandConfig(
            project_dir=Path.cwd(),
            platform=platform,
            variant_name=self.variant_name,
            not_interactive=True,
            target=target,
        )

        # Act
        result = RunCommand().do_run(config)

        # Assert
        assert result == 0, "Building variant failed"

    def test_holding_the_power_button_turns_the_light_green(self, variant: Variant):
        """Drives the built library the way the GUI does: button in, LED colour out."""
        # Arrange
        variant.set_button(POWER_BUTTON_KEY, True)

        # Act
        for _ in range(PRESS_DEBOUNCE_STEPS - 1):
            variant.step()

        # Assert
        assert variant.led_colour() == LIGHT_OFF, "The light must stay off until the press is debounced"
        variant.step()
        assert variant.led_colour() == LIGHT_GREEN

    @pytest.mark.parametrize("report", ["reports", "light_controller/reports"])
    def test_gtest_source_docs_link_to_coverage_lines(self, gtest_build_dir: Path, report: str):
        # Arrange
        page = gtest_build_dir / report / LIGHT_CONTROLLER_PAGES / "light_controller.c.html"

        # Act
        html = page.read_text(encoding="utf-8")
        links = COVERAGE_LINK.findall(html)

        # Assert
        assert links, f"No declaration links to its coverage page in {page}"
        source_lines = (Path.cwd() / links[0][2]).read_text(encoding="utf-8").splitlines()
        for href, fragment_line, text_path, text_line in links:
            assert fragment_line == text_line, f"{href}#l{fragment_line} does not point to line {text_line}"
            assert text_path.endswith("light_controller.c")
            assert 1 <= int(fragment_line) <= len(source_lines), f"{href}#l{fragment_line} is outside {text_path}"
            assert (page.parent / href).is_file(), f"{href} does not exist"
        declaration_line = next(i for i, line in enumerate(source_lines, 1) if "void lightController(void)" in line)
        assert str(declaration_line) in {fragment_line for _, fragment_line, _, _ in links}, f"lightController does not link to #l{declaration_line}"
        assert 'href="source:' not in html, "An unresolved source: link is left"
        assert 'href="vscode://' not in html, "A production declaration fell back to VS Code"

    def test_gtest_variant_test_runs_and_reports_its_coverage(self, gtest_build_dir: Path):
        # Arrange
        junit = gtest_build_dir / "variant_test/variant_test_junit.xml"
        coverage_page = gtest_build_dir / "reports/variant_test_coverage/index.html"

        # Act
        suites = ElementTree.parse(junit).getroot()
        report = (gtest_build_dir / "reports/index.html").read_text(encoding="utf-8")

        # Assert
        assert int(suites.get("tests", 0)) > 0, f"No variant test ran in {junit}"
        assert suites.get("failures") == "0" and suites.get("errors") == "0", f"The variant test failed, see {junit}"
        assert "spled.c" in coverage_page.read_text(encoding="utf-8"), f"spled.c is missing from {coverage_page}"
        assert VARIANT_TEST_COVERAGE_LINK.search(report), "The variant report does not link to the variant test coverage"

    def test_gtest_test_source_docs_link_to_vscode_locally_and_plain_text_on_ci(self, gtest_build_dir: Path):
        # Arrange
        page = gtest_build_dir / "reports" / LIGHT_CONTROLLER_PAGES / "test_light_controller.cc.html"

        # Act
        html = page.read_text(encoding="utf-8")
        links = VSCODE_LINK.findall(html)

        # Assert
        if IS_CI:
            # The ci profile falls back to default (gcovr only): test sources stay plain text.
            assert 'href="vscode://' not in html, "A test source links to VS Code on CI"
            assert 'href="source:' not in html, "An unresolved source: link is left"
            assert re.search(r">components/light_controller/test/test_light_controller\.cc:\d+<", html), f"No plain text source location in {page}"
            return
        assert any(
            path.endswith("test_light_controller.cc")
            and Path(path).is_absolute()
            and Path(path).is_relative_to(Path.cwd().resolve())
            and Path(path).is_file()
            and 1 <= int(line) <= len(Path(path).read_text(encoding="utf-8").splitlines())
            for path, line in links
        ), f"No declaration links to VS Code at a line of the test file in {page}"
