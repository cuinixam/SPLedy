from pathlib import Path

from collect_site import CollectSite
from pypeline.domain.execution_context import ExecutionContext


def test_collect_site_copies_only_included_files(tmp_path: Path) -> None:
    # Arrange
    source = tmp_path / "build"
    for file in ["index.html", "a/reports/index.html", "a/reports/.doctrees/env.pickle", "a/reports/.buildinfo", "a/bin/app.exe"]:
        (source / file).parent.mkdir(parents=True, exist_ok=True)
        (source / file).write_text(file)
    stale = tmp_path / "site" / "old.html"
    stale.parent.mkdir()
    stale.write_text("old")
    config = {"source": "build", "target": "site", "include": ["index.html", "**/reports/**/*"], "exclude": ["**/.doctrees/**", "**/.buildinfo*"]}

    # Act
    CollectSite(ExecutionContext(project_root_dir=tmp_path), None, config).run()

    # Assert
    copied = sorted(path.relative_to(tmp_path / "site").as_posix() for path in (tmp_path / "site").rglob("*") if path.is_file())
    assert copied == ["a/reports/index.html", "index.html"]
    assert (tmp_path / "site" / "a/reports/index.html").read_text() == "a/reports/index.html"
