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

```{toctree}
:maxdepth: 2

pc_gui
zephyr
```
