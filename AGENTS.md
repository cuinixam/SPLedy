# AGENTS.md - SPLed Development Guide for AI Coding Agents

## Project Overview

**SPLed** is a Software Product Line (SPL) demonstration for embedded/desktop systems built with the [Yanga](https://github.com/cuinixam/yanga) build system. It showcases managing multiple **variants** (Disco, Sleep, Spa) with different features and platform targets (Arduino, Windows EXE, GTest).

## Core Architecture

### Three-Layer Structure

1. **Components** (`components/`) - Reusable C modules (e.g., `spled`, `light_controller`, `power_button`, `rte`)
2. **Variants** (`variants/`) - Product configurations combining components with feature selections
3. **Platforms** (`platforms/`) - Target-specific implementations (Arduino, GTest, Win32)

### Key Concepts

- **Feature Model**: KConfig-based variability (`KConfig` file defines features; variants select them in `config.txt`). `KConfigGen` turns that selection into `<build>/kconfig/autoconf.h` on every platform, Zephyr included
- **Platform Feature Model**: a platform may bring a second, independent model. The Zephyr platforms declare Zephyr's own tree ([platforms/zephyr/KConfig](platforms/zephyr/KConfig)); a variant selects from it in `variants/<Name>/<platform>.txt`, which the build passes to Zephyr as an `EXTRA_CONF_FILE`. The two models share no symbols and neither loads the other
- **Component Dependencies**: Declared in `components/yanga.yaml` via `required_components`
- **Runtime Environment (RTE)**: Message passing abstraction between components (`components/rte/`)
- **Platform Adapters**: Hardware/OS interfaces (e.g., `arduino_button`)

### Data Flow

```txt
Variant Config (KConfig) → Yanga → CMake → Platform Toolchain → Executables/Tests
```

## Critical Developer Workflows

### Initial Setup

#### Windows PowerShell

```powershell
.\build.ps1 -install           # Bootstrap venv, install dependencies
.\build.ps1 -startVSCode       # Launch VS Code with proper env
```

#### Linux/Unix Shell

```bash
# Install pypeline runner
pip install pipx
pipx install pypeline-runner

# Create virtual environment
pypeline run --config-file yanga.yaml --step CreateVEnv --single

# Activate the virtual environemt
source .venv/bin/activate

# Run yanga
yanga run
```

#### Devcontainer

The devcontainer has all dependencies pre-installed (including yanga). Simply run:

```bash
yanga run
```

Terminal use of the same image, and the wrinkles that come with it, are in
[doc/how-to/build-in-a-container.md](doc/how-to/build-in-a-container.md).

### Build Variants

```powershell
.\yanga.ps1 run                # Interactive variant/platform selection
.\yanga.ps1 run --variant Disco --platform pc_terminal --target report
```

### Run Tests

```bash
# Integration tests (Python-based, builds variants)
pytest test/test_Disco.py      # Test Disco variant on all platforms

# Unit tests (C++ GoogleTest, requires GTest platform build)
.\yanga.ps1 run --variant Spa --platform gtest --target all
```

### Feature Configuration

```bash
# Product features of a variant: kconfiglib's editor on variants/<Name>/config.txt
yanga features --variant Disco
yanga features --variant Disco --no-gui   # terminal editor

# Every variant's product selection side by side, read-only
yanga features

# Zephyr options for a variant on one platform: Zephyr's own editor, and the change is
# written into variants/Disco/zephyr_esp32h2.txt when it is closed
yanga features --variant Disco --platform zephyr_esp32h2
```

Each `feature_model:` block declares the pipeline that opens its editor: the product model uses
yanga's `KConfigEdit`, the Zephyr platforms use `ZephyrFeatures` from `yanga.zephyr.steps`
(installed with `yanga[zephyr]`), which runs yanga's `kconfig_frontend.py` as a Zephyr Kconfig
target. A platform's selection cannot be edited without a variant.

## Project-Specific Conventions

### Component Definition Pattern (`components/yanga.yaml`)

```yaml
- name: my_component
  path: components/my_component
  sources: [src/my_component.c]
  testing:
    sources: [test/test_my_component.cc]  # GoogleTest tests
  include_directories:
    - path: src
      scope: PUBLIC
  required_components: [rte, button_interface]
  docs_sources: [doc/index.md]  # Documentation for report generation
```

### Variant Configuration (`variants/<Name>/yanga.yaml`)

```yaml
variants:
- name: MyVariant
  components: [rte, spled, power_button]  # Core components
  feature_selection:
    file: variants/MyVariant/config.txt
  platforms:
    gtest:
      components: [test_integrations_spled]  # Platform-specific components
    arduino_uno_r3:
      components: [arduino_button, arduino_led]
```

### Platform Toolchain Setup

- **GTest**: Uses GoogleTest from West manifest, generates coverage/lint/report targets
- **Arduino**: Cross-compiles with AVR-GCC, includes Arduino Core from West
- **pc_terminal**: Native PC terminal builds with Clang (Windows/Linux)

### Test Patterns

Integration tests use `yanga.commands.run.RunCommand` directly:

```python
from yanga_core.commands.run import RunCommand, RunCommandConfig

config = RunCommandConfig(
    project_dir=Path.cwd(),
    platform="gtest",
    variant_name="Disco",
    not_interactive=True,
    target="report"
)
result = RunCommand().do_run(config)
assert result == 0
```

## Integration Points

### External Dependencies (West Manifest)

- **GoogleTest** v1.16.0 for unit tests
- **Arduino Core AVR** for embedded targets
- Configured per-platform in `platforms/<platform>/yanga.yaml`

### Build Pipeline (`yanga.yaml`)

```yaml
pipeline:
  install: [CreateVEnv, PoksInstall, WestInstall]  # Dependency setup
  gen: [KConfigGen]                                  # Generate headers from KConfig
  build: [GenerateBuildSystemFiles, ExecuteBuild]    # CMake generation + build
```

### CMake Generators (per platform)

- **GTestCMakeGenerator**: Creates test/coverage/lint targets with GoogleMock
- **CppCheckCMakeGenerator**: Static analysis integration
- **ReportCMakeGenerator**: HTML test reports (`doc/generate_overall_report.py`)

### Report Generation

Reports aggregate test results, coverage, and docs:

- Generated per variant/platform in `.yanga/build/<variant>/<platform>/reports/`
- Accessed via [index.html](doc/results/index.md) (generated by [generate_overall_report.py](doc/generate_overall_report.py))

## Key File References

- [yanga.yaml](yanga.yaml) - Project build pipeline
- [KConfig](KConfig) - Feature model definition
- [components/yanga.yaml](components/yanga.yaml) - Component declarations
- [platforms/gtest/yanga.yaml](platforms/gtest/yanga.yaml) - GTest platform config
- [variants/Disco/config.txt](variants/Disco/config.txt) - Example feature selection
- [build.ps1](build.ps1) - Bootstrap and environment script

## Common Pitfalls

- **Windows paths**: Always use `.venv\Scripts\` not `.venv/bin/` in PowerShell
- **Linux paths**: Use `.venv/bin/` for Python executables (e.g., `.venv/bin/python -m pytest`)
- **Environment (Windows)**: Must run `build.ps1 -install` or load `.yanga/build/install/env_setup.ps1` before Yanga commands
- **Environment (Linux)**: Use `pip install pypeline-runner` and `pypeline run --config-file yanga.yaml --step CreateVEnv --single`
- **CMake regeneration**: Yanga auto-regenerates on config changes; don't manually edit generated files
- **Platform components**: Must be listed in variant's platform-specific `components` list (e.g., `arduino_button` for Arduino)
- **KConfig syntax**: Use `CONFIG_<FEATURE>=y` in `config.txt`, not `FEATURE=y`
