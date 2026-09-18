# Build in a container

The [devcontainer](../../.devcontainer/devcontainer.json) image `cuinixam/yanga-dev` carries every
dependency a build needs. Two platforms only build there: `tc375` (no free tricore-elf GCC for
macOS) and, on a Mac, anything that needs a Linux toolchain from poks.

In VS Code, "Reopen in Container" and `yanga run` is all there is to it. This page is for driving
the same image from the terminal, for example on macOS with podman.

## Start the container runtime

```bash
podman machine start                  # macOS only; the VM is not started automatically
export DOCKER_HOST='unix:///var/folders/.../podman/podman-machine-default-api.sock'
```

`podman machine start` prints the socket path to export. The image is `linux/arm64`, so it runs
natively on Apple Silicon.

## Copy the work tree in, do not mount it

`.venv/` and `.yanga/` hold absolute paths and host binaries, and the first pipeline step
(`CreateVEnv`) rebuilds `.venv` wherever it runs. Bind-mounting the repository read-write therefore
destroys the venv you use on the host. Pack the sources instead:

```bash
tar --exclude=.venv --exclude=.yanga --exclude=build --exclude=.git \
    -czf /tmp/spled.tgz -C /path/to/spled .
```

Keep the poks cache in a container volume rather than a host mount: poks moves directories into
place while installing, which fails on a macOS bind mount.

```bash
podman volume create spled-poks
```

## Run a build

```bash
podman run --rm \
  -v /tmp:/host:ro \
  -v "$PWD/ctr-work:/work" \
  -v spled-poks:/home/ubuntu/.poks \
  cuinixam/yanga-dev:1.1.0 bash -lc '
    tar -xzf /host/spled.tgz -C /work
    cd /work
    pipx runpip yanga install -q -U poks
    yanga run --variant Disco --platform zephyr_esp32h2
  '
```

The work directory is a host path, so the build output, `.config` and the generated headers can be
inspected afterwards without entering the container.

A first run downloads the west workspace (Zephyr, `hal_espressif`, the ESP32-H2 blobs) and the
toolchains. With both cached, `Disco` for `zephyr_esp32h2` takes about two minutes.

## Testing a local yanga or yanga-core

The image ships whatever yanga version it was built with, which is older than the repository
expects. Mount the checkouts read-only and install them into the pipx environment yanga runs from:

```bash
podman run --rm \
  -v ~/ateliere/yanga-core:/pkgs/yanga-core:ro \
  -v ~/ateliere/yanga:/pkgs/yanga:ro \
  ... \
  cuinixam/yanga-dev:1.1.0 bash -lc '
    pipx runpip yanga install -q -U /pkgs/yanga-core /pkgs/yanga
    cd /work && yanga run --variant Disco --platform zephyr_esp32h2
  '
```

## Known wrinkles

- **poks must be upgraded in the image.** The version it ships nests the extracted toolchain and
  aborts with `Destination path '.../riscv64-zephyr-elf/riscv64-zephyr-elf' already exists`. The
  `postCreateCommand` upgrades pypeline-runner and yanga, not poks, so a fresh devcontainer needs
  `pipx runpip yanga install -U poks` as well.
- **`CreateVEnv` reinstalls yanga from PyPI**, dropping any local install. Reinstall after a run
  that includes that step.
- **Interactive editors need a terminal.** `yanga features` opens `guiconfig` (needs a display) or
  `menuconfig` (needs a TTY), so run those on the host, or with `podman run -it` and an X display.
