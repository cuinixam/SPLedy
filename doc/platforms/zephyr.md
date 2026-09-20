# Zephyr platforms

Three platforms build the same variants on Zephyr: `zephyr_sim` runs on the host as
Zephyr's `native_sim` board (Linux only), `zephyr_esp32h2` targets the ESP32-H2 DevKitM,
`zephyr_esp32h2_waveshare` a board defined in this repository (see "A board of our own").
Zephyr drives the build; yanga contributes the variant as a generated CMake fragment
that `platforms/zephyr` includes. Everything below runs through `yanga run`, which
provisions west, the toolchains from poks and the Zephyr workspace under
`.yanga/zephyr` on first use. That workspace is separate from the shared `.yanga/ext`
the other platforms clone into: a west workspace holds one manifest, and Zephyr keeps
reading it after the clone for its `west build`/`west flash`/`west blobs` commands and
its module discovery, so it must not be overwritten by the next platform's install.

## Build

```bash
yanga run --variant Disco --platform zephyr_sim
yanga run --variant Disco --platform zephyr_esp32h2
```

The image lands in `.yanga/build/variants/<variant>/<platform>/zephyr/`. `--target report`
builds the variant report (component docs, targets, objects dependencies; the objects graph
includes Zephyr's own libraries) under `reports/`.

Zephyr's options are the platform's own feature model, separate from the product's `KConfig`.
`yanga features --variant Disco --platform zephyr_esp32h2` opens Zephyr's editor on it and writes
what changed into `variants/Disco/zephyr_esp32h2.txt`, which the build merges as an
`EXTRA_CONF_FILE`. Zephyr's `menuconfig`/`guiconfig` targets are not exposed: they edit the build's
`.config` only, and the next configure throws that away. The product's features stay in
`variants/<variant>/config.txt`, edited with `yanga features --variant Disco`.

## Run the simulator

```bash
.yanga/build/variants/Disco/zephyr_sim/zephyr/zephyr.exe
```

The shell starts in that terminal. The application boots powered off, like every other
platform. There is no keyboard, so the shell presses the buttons:

```
uart:~$ spled power     # on, and again for off
uart:~$ spled up        # faster blinking (Disco) or brighter (Sleep, Spa)
uart:~$ spled down
uart:~$ spled state     # power, light and button state
```

Each command holds the emulated pin pressed long enough to pass the debounce.
`--stop-at=<seconds>` runs the simulator for that much simulated time and exits.

### Watch the LED

The LED display gets a pseudo terminal of its own. On start the binary prints:

```
uart_1 connected to pseudotty: /dev/pts/3
```

Open it in a second terminal:

```bash
picocom /dev/pts/3        # the number changes every run; Ctrl-A Ctrl-X quits
```

That is `pc_terminal`'s display: a block whose background is the RGB value, redrawn
whenever the colour changes, with the value printed next to it. Use `picocom`
(the dev container installs it, `apt-get install picocom` elsewhere): it relays the
bytes untouched, so the 24-bit colour escape reaches the terminal. `screen` re-renders
and quantises the colour to a grey block that never appears to change, and `cat` does
not open the pseudo terminal slave reliably.

## A board of our own

Zephyr has no definition for the Waveshare ESP32-H2-DEV-KIT-N4 the demo runs on, so
`zephyr_esp32h2` builds for Espressif's DevKitM (same module, same pins) and adds what
differs in `platforms/zephyr/app/boards/esp32h2_devkitm.overlay`: the onboard WS2812 LED
and the three buttons SPLed wires to header pins.

`zephyr_esp32h2_waveshare` shows the other way: the board is defined in this repository,
under `platforms/zephyr/boards/waveshare/esp32h2_dev_kit_n4/`, with the same files a board
in Zephyr's tree has (`board.yml`, `Kconfig.<board>`, `<board>_defconfig`, `board.cmake`,
the devicetree). The LED and the buttons are part of the board's `.dts`, so the
application needs no overlay for it. One line in `platforms/zephyr/zephyr.cmake` makes Zephyr
look there: `list(APPEND BOARD_ROOT ...)` before `find_package(Zephyr)`. The platform
in `platforms/zephyr/yanga.yaml` differs from `zephyr_esp32h2` only in its `board:`.

```bash
yanga run --variant Disco --platform zephyr_esp32h2_waveshare
```

## Flash the ESP32-H2

```bash
yanga run --variant Disco --platform zephyr_esp32h2 --target flash
picocom /dev/ttyACM1 -b 115200        # Ctrl-A Ctrl-X quits
```

`flash` runs `west flash`, which uses esptool from the venv; the runner picks the port
itself, or takes `ESPTOOL_PORT` from the environment. No button press is needed: the board
drives BOOT and reset from DTR and RTS. The same `spled` commands work over the console.

Board notes:

- Serial access needs the `dialout` group: `sudo usermod -aG dialout $USER`, then log
  out and in. In a Parallels VM hand the USB device to the guest first.
- Two `/dev/ttyACM*` devices enumerate. The CH343 bridge (USB vendor `1a86`) carries the
  console; the SoC's own USB (`303a`) has nothing routed to it and opens a terminal that
  never prints. Tell them apart with
  `udevadm info -q property -n /dev/ttyACM1 | grep ID_VENDOR_ID`.
