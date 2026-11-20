---
status: Ready
priority: Medium
blocked_by: [PSR-001]
---

# [SPLED-003] Publish the SPL overview of develop to GitHub Pages

## Summary

As a reader of SPLed, I want every push to `develop` to publish the SPL overview and the reports it links to a public GitHub Pages site, so that I can see what the product line builds without cloning and building it myself.

## Description

`test/test_spl.py` builds 7 variant and platform pairs with the `report` target, runs `spl_pypeline.yaml` and checks the overview at `.yanga/build/index.html`. A failed build or a wrong overview stops the test. The result exists only on the machine that ran it: CI does not run it, and nothing publishes it.

This item runs that test on CI for every push to `develop` and publishes the overview with the reports below it, using the `PublishToRepository` step of pypeline-semantic-release. It is part of a change across pypeline-semantic-release and SPLed; the design is in the planning vault's epic.

## Scope decisions

- **The test is the gate.** The set of builds is `test/test_spl.py`. The site is published only after the test passes, so a failed run leaves the previous site in place.
- **A separate publish pipeline.** A new pypeline file runs the test and then the publish step. The publish step is not added to `spl_pypeline.yaml`, because the test runs that file before its own checks.
- **A separate workflow.** It runs on push to `develop` only, on one Ubuntu runner, with a concurrency group so that an older run cannot overwrite a newer site. It does not wait for the jobs of the existing test workflow.
- **The workflow is plumbing.** It sets up Python, creates the project venv with pypeline, and runs the publish pipeline with the venv's pypeline, with the deploy key in the environment. All logic is in the pipeline.
- **Only the needed files.** The site holds the overview, the SPL documentation report and the variant reports, not the whole build folder.
- **Only the latest state.** The site keeps no history.
- **Tested locally first.** The target repository can be set for one run, so the whole publish can run against a local bare repository with CI simulated, before anything goes to GitHub.
- **The target is set up by hand, as the first task.** The organisation `spledy` and the repository `spledy.github.io`, served by GitHub Pages from the root of `main`, a deploy key with write access there, and its private key as a secret in SPLed. If the name `spledy` is taken, a repository under `cuinixam` works, with a sub-path in the URL.
- **SPLed adds `.nojekyll`.** The psr step knows nothing about GitHub Pages, so the publish pipeline writes `.nojekyll` into the published folder; without it, Pages drops Sphinx folders that start with `_`.
- Out of scope: releases from `stable`, artifacts in the overview, reports from other jobs, a versioned site.

## Acceptance criteria

- [ ] The organisation, the Pages repository, its deploy key and the secret in SPLed exist
- [ ] A push to `develop` runs the SPL test on CI and, when it passes, publishes the site
- [ ] A failed SPL test publishes nothing and leaves the previous site in place
- [ ] A pull request and a local run of the publish pipeline publish nothing
- [ ] A local run of the publish pipeline, with CI simulated and a local bare repository as the target, pushes the site there; a clone of it lists the 7 builds of the SPL test, and its links work
- [ ] The published site lists the 7 builds of the SPL test, and its links to the variant reports and the SPL documentation report work
- [ ] The deploy key does not appear in the CI log
- [ ] A how-to page in `doc/how-to/` explains how the site is published and how to set up the target
