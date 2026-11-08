# Build the SPL overview

The SPL overview is one page for the whole product line: per variant and platform, what was
built, from which commit, with a link to the variant report, and a link to the SPL documentation
report. It is built locally from what is on the disk.

## Build the variants you want to see

Each variant build ends with `WritePublishManifest` (see [yanga.yaml](../../yanga.yaml)), which
writes `publish_manifest.json` into the variant build folder. Build the `report` target, because
the overview links only reports for now:

```bash
yanga run --variant Disco --platform gtest --target report
yanga run --variant Disco --platform pc_terminal --build-type Debug --target report
```

A variant that was not built is not listed. Builds of removed variants stay listed until you
delete their folders under `.yanga/build/variants/`.

## Build the overview

```bash
pypeline run --config-file spl_pypeline.yaml
```

This builds the SPL documentation report (the SPL branch of [index.md](../../index.md)) into
`.yanga/build/spl/reports/`, then renders [spl_overview.html.jinja](../../spl_overview.html.jinja)
to `.yanga/build/index.html`. Open that file. The overview links to the reports where the builds
left them; nothing is copied. A build made from a different commit than the overview is marked
`other commit`, so old builds left on the disk are visible.

To change the look, edit `spl_overview.html.jinja`. The data it gets is described under
`RenderSplOverview` in the yanga-core step reference.

## Build and check a sample overview

```bash
pytest test/test_spl.py
```

This deletes the manifests of earlier builds, builds the variant and platform pairs listed in
[test_spl.py](../../test/test_spl.py), which work on Windows, Linux and macOS, then builds the
overview. The test checks that the overview lists exactly these builds, all from the current
commit, and that every relative link points to a file.
