# Platforms

A platform is what a variant is built for: a compiler, a scheduler and the adapters behind
the `led_interface` / `button_interface` seam. The product code under `components/` is the
same on every row. Select one with `yanga run --variant <variant> --platform <platform>`.

| Platform | What it builds |
| --- | --- |
| `gtest` | Build and run the components' GoogleTest tests |
| `pc_terminal` | PC terminal executable with clang (Windows/Linux) |
| `pc_gui` | The variant as a shared library for the Python GUI and for tests (Windows/Linux/macOS) |
| `arduino_uno_r3` | Arduino Uno R3 with avr-gcc |
| `tc375` | Infineon AURIX TC375 ShieldBuddy with tricore-elf GCC |
| `zephyr_sim` | Zephyr `native_sim`, host compiler (Linux only) |
| `zephyr_esp32h2` | Zephyr on the ESP32-H2 devkit, riscv64-zephyr-elf from poks |
| `zephyr_esp32h2_waveshare` | The same on the Waveshare ESP32-H2-DEV-KIT-N4, a board defined in this repository |

## macOS: `ld: tapi error: malformed file`

The host platforms link with Apple's `ld`, which comes from the developer directory that
`xcode-select -p` points to. When the Command Line Tools are newer than that Xcode, the SDK the
compiler picks has `.tbd` stubs the older `ld` cannot read:

```text
ld: tapi error: malformed file
.../MacOSX27.0.sdk/usr/lib/libSystem.B.tbd:4:20: error: unknown architecture
```

The project's `.env` sets `DEVELOPER_DIR=/Library/Developer/CommandLineTools`, so every
step of a pipeline run takes the linker and the SDK from the Command Line Tools, whatever
`xcode-select` says. Other platforms ignore the variable. Two consequences:

- The Command Line Tools must be installed (`xcode-select --install`); Xcode alone is not enough.
- A shell outside the pipeline gets the same setting from `.yanga/build/install/env_setup.sh`.

The `gtest` gcc does not parse the SDK 26.x headers (`mach/message.h`); it works with SDK 15.x
and 27, and prefers a 15.x SDK from the Command Line Tools when one is installed.

```{toctree}
:maxdepth: 2

pc_gui
zephyr
```
