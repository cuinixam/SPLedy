"""
Pipeline step that copies selected files of one folder into another, keeping their relative paths.

Loaded with `file:` from publish_pypeline.yaml. It moves to pypeline once a second repository needs it.
"""

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from py_app_dev.core.config import BaseConfigJSONMixin
from py_app_dev.core.exceptions import UserNotificationException
from py_app_dev.core.logging import logger
from pypeline.domain.execution_context import ExecutionContext
from pypeline.domain.pipeline import PipelineStep


@dataclass
class CollectSiteConfig(BaseConfigJSONMixin):
    #: Folder to copy from, relative to the project root
    source: str
    #: Folder to copy into, relative to the project root. It is emptied first.
    target: str
    #: Glob patterns relative to `source` that select the files
    include: list[str]
    #: Patterns relative to `source` (`PurePath.full_match`) of files to leave out
    exclude: list[str] = field(default_factory=list)


class CollectSite(PipelineStep[ExecutionContext]):
    def __init__(self, execution_context: ExecutionContext, group_name: str | None, config: dict[str, Any] | None = None) -> None:
        super().__init__(execution_context, group_name, config)
        self.user_config = CollectSiteConfig.from_dict(config or {})
        self.source_dir = self.project_root_dir / self.user_config.source
        self.target_dir = self.project_root_dir / self.user_config.target

    def get_name(self) -> str:
        return self.__class__.__name__

    def get_needs_dependency_management(self) -> bool:
        # Always runs: the source changes with every build, and the target is rebuilt from scratch.
        return False

    def run(self) -> int:
        # Emptied first, so no file of an older run stays in the target.
        if self.target_dir.exists():
            shutil.rmtree(self.target_dir)
        files = sorted(
            {
                path.relative_to(self.source_dir)
                for pattern in self.user_config.include
                for path in self.source_dir.glob(pattern)
                if path.is_file()
            }
        )
        files = [file for file in files if not any(file.full_match(pattern) for pattern in self.user_config.exclude)]
        if not files:
            raise UserNotificationException(f"No files in '{self.user_config.source}' match {self.user_config.include}. Nothing to collect.")
        for file in files:
            (self.target_dir / file).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.source_dir / file, self.target_dir / file)
        logger.info(f"Copied {len(files)} files from '{self.user_config.source}' to '{self.user_config.target}'.")
        return 0

    def get_inputs(self) -> list[Path]:
        return []

    def get_outputs(self) -> list[Path]:
        return []

    def update_execution_context(self) -> None:
        pass
