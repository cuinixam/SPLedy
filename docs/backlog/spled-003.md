---
status: In Progress
priority: Medium
---

# [SPLED-003] Publish the SPL overview of develop to GitHub Pages

## Summary

As a reader of SPLed, I want every push to `develop` to publish the SPL overview and the reports it links to a public GitHub Pages site, so that I can see what the product line builds without cloning and building it myself.

## Description

`test/test_spl.py` builds 7 variant and platform pairs with the `report` target, runs `spl_pypeline.yaml` and checks the overview at `.yanga/build/index.html`. A failed build or a wrong overview stops the test. The result exists only on the machine that ran it: CI does not run it, and nothing publishes it.

This item runs that test on CI for every push to `develop` and publishes the overview with the reports below it from a GitHub Actions workflow in SPLed itself. It started as part of the epic SB-007 with pypeline-semantic-release; that epic is Superseded (2026-11-21), and the design is in the planning vault's architecture review of 2026-11-21.

## Scope decisions

- **The test is the gate.** The set of builds is `test/test_spl.py`. The site is published only after the test passes, so a failed run leaves the previous site in place.
- **A separate publish pipeline.** A new pypeline file runs the test and then the publish step. The publish step is not added to `spl_pypeline.yaml`, because the test runs that file before its own checks.
- **Publish inside the CI workflow (2026-11-21).** The `build` and `deploy` jobs are in `test.yml`, not in a workflow of their own: a separate workflow started at the same time as CI on a push to `develop` and could deploy while CI was red. `build` needs every test job (`test-windows`, `test-unix`) and runs only for a push to `develop` (`if: github.event_name == 'push' && github.ref == 'refs/heads/develop'`); a pull request runs only the tests.
- **The workflow is plumbing.** It sets up Python, creates the project venv with pypeline, and runs the publish pipeline with the venv's pypeline. All logic is in the pipeline.
- **Only the needed files.** The site holds the overview, the SPL documentation report and the variant reports, not the whole build folder.
- **Only the latest state.** The site keeps no history.
- **GitHub Pages from Actions (2026-11-21).** The site is `https://yanga-project.dev/SPLedY/` (the repository moved to `yanga-project` on 2026-11-21: a project site of a personal account is served under the user site's custom domain, and the organisation's domain is `yanga-project.dev`), with the Pages source "GitHub Actions", set once by hand in SPLedy's settings. No organisation `spledy`, no repository `spledy.github.io`, no deploy key and no `PAGES_DEPLOY_KEY` secret. GitHub runs no Jekyll for this source, so no `.nojekyll` is needed.
- **The pipeline builds a site folder (2026-11-21).** `publish_pypeline.yaml` runs `CreateVEnv`, the SPL test, then `CollectSite`; no `CheckCIContext` and no psr publish step. `CollectSite` is a step class in SPLed, `pipeline/collect_site.py`, loaded with `file:`, written as a generic copy step (`source`, `target`, `include`, `exclude`, no SPL words). It empties `target`, then copies each matching file with its relative path: from `.yanga/build` to `.yanga/build/site`, including `index.html`, `spl/reports/**/*`, `variants/**/reports/**/*`, excluding `**/.doctrees/**` and `**/.buildinfo*`. It moves to pypeline when a second repository needs it.
- **Two jobs (2026-11-21).** `build` runs the pipeline and uploads `.yanga/build/site` with `actions/upload-pages-artifact@v5` and `include-hidden-files: true` (v4 always leaves out dot-prefixed entries, which would drop the pages under `reports/.yanga/`); `deploy` needs `build`, has `pages: write` and `id-token: write`, the environment `github-pages`, and runs `actions/deploy-pages@v4`. `deploy` has the same `if:`. The workflow has `contents: read`; the concurrency group `pages` with `cancel-in-progress: false`, as GitHub's Pages starter workflow, is on the `deploy` job only, so test runs are not held back.
- **Only Sphinx build state is left out (2026-11-21).** `reports/.yanga/` is not build state: a local run found 263 rendered report pages there (autoconf, targets data, sources, test and clang-tidy reports) that the report index links to. Excluding `**/.yanga/**` broke 845 relative links; without it the site has 0 broken relative links and no `.doctrees` or `.buildinfo` files.
- **No psr change (2026-11-21).** The psr floor stays as it was; `poetry.lock` matches.
- Out of scope: releases from `stable`, artifacts in the overview, reports from other jobs, a versioned site.

## Acceptance criteria

- [x] SPLedy's Pages source is set to GitHub Actions
- [ ] A push to `develop` runs the SPL test on CI and, when it passes, deploys the site
- [x] A failed SPL test deploys nothing and leaves the previous site in place
- [x] A pull request and a local run deploy nothing
- [x] A local run of the publish pipeline writes `.yanga/build/site` with `index.html` listing the 7 builds of the SPL test, every relative link resolves inside that folder, and it holds no `.doctrees` or `.buildinfo` files
- [ ] The deployed site lists the 7 builds, and its links work
- [x] A how-to page in `doc/how-to/` explains how the site is published and the one setting

## Handoff

- Intent: every push to `develop` runs the SPL test on CI and deploys `.yanga/build/site` to `https://yanga-project.dev/SPLedY/` through GitHub Pages from Actions (`publish_pypeline.yaml`, `pipeline/collect_site.py`, the `build` and `deploy` jobs of `.github/workflows/test.yml`).
- Verified locally (macOS):
  - AC 5: `.venv/bin/pypeline run --config-file publish_pypeline.yaml` exit 0, SPL test passed, `CollectSite` copied the site. `index.html` links the 7 builds; 0 broken relative links in all html pages of the folder; 0 `.doctrees` or `.buildinfo` files; the 263 report pages under `reports/.yanga/` are present; a stale file put into the folder beforehand is gone. Checked again with the final `CollectSite`.
  - AC 3: the same pipeline with the test step failing stops with exit 1 and writes no site folder; in the workflow, `deploy` needs `build` and `build` needs every test job, so a failed test deploys nothing.
  - AC 4: `build` and `deploy` run only for a push to `develop` (`if:`), so a pull request runs only the tests; the pipeline has no deploy step, so a local run deploys nothing.
  - AC 7: `doc/how-to/publish-the-spl-overview.md`.
  - `.venv/bin/python -m pytest`: 21 passed, 5 skipped.
- AC 1: `gh api repos/yanga-project/SPLedY/pages` reports `build_type: workflow` after the move (2026-11-21).
- State: AC 1, 3, 4, 5 and 7 ticked. AC 2 (push deploys) and 6 (deployed site and links) need a push to `develop`.
- Next: merge the branch to `develop`; check the first CI run's `build` and `deploy` jobs and the site.
- Known problems: no CI job has built the `zephyr_esp32h2`, `pc_terminal` or `pc_gui` builds of the SPL test on `ubuntu-latest` yet; the first run shows it. The `.yanga` folders reach the artifact only through `include-hidden-files: true` of `upload-pages-artifact@v5`, not checked on GitHub yet: check a `reports/.yanga/` page on the deployed site. `test_collect_site.py` runs only in a plain local pytest, not in `test.yml`. `test.yml` keeps an unquoted `pip install pypeline-runner>=1.23`.
