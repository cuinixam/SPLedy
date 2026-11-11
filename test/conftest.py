import os
from pathlib import Path

# VS Code starts pytest in `k:\spledy`, but CMake writes the drive as `K:`, and ninja treats the two as different files.
os.chdir(Path.cwd().resolve())
