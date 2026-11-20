# Publish the SPL overview

Every push to `develop` publishes the SPL overview and the reports it links to at
<https://yanga-project.dev/SPLedY/>. The site shows only the latest state of `develop`; it keeps
no history, and it is stored in no branch.

## How it works

The CI workflow [test.yml](../../.github/workflows/test.yml) has two publish jobs on Ubuntu
runners, `build` and `deploy`. They run only for a push to `develop`, and only after every test
job of the workflow has passed, so a red CI deploys nothing.

The `build` job creates the project venv and runs
[publish_pypeline.yaml](../../publish_pypeline.yaml) with the venv's pypeline. That pipeline:

1. runs `pytest test/test_spl.py`, which builds the variant and platform pairs of the SPL test and
   the overview, and checks it (see [Build the SPL overview](build-the-spl-overview.md)). When the
   test fails, the pipeline stops, nothing is uploaded, and the previous site stays in place;
2. runs `CollectSite` ([pipeline/collect_site.py](../../pipeline/collect_site.py)). It empties
   `.yanga/build/site`, then copies `index.html`, `spl/reports/` and the `reports/` folders under
   `variants/` there from `.yanga/build`, without the Sphinx build state (`.doctrees`,
   `.buildinfo`).

The job then uploads `.yanga/build/site` with `actions/upload-pages-artifact`, with hidden files
included, because each variant report keeps pages in a `.yanga` folder. The `deploy` job
publishes it with `actions/deploy-pages`. Only the `deploy` job has the permissions to publish
(`pages: write`, `id-token: write`); it uses the token GitHub issues for the run, so there is no
key or secret to manage.

A pull request runs only the tests and deploys nothing. The `deploy` job has a concurrency group:
only one deploy runs at a time, and of the deploys waiting, only the latest one is kept. The deploys
of two pushes enter the group in the order their builds finish, so when an older push finishes
last, its site goes live; the next push to `develop` replaces it. The group is on the `deploy` job
only, so test runs are not held back.

## Set up GitHub Pages

Once, by hand: in SPLedy, under *Settings > Pages > Build and deployment*, set *Source* to
*GitHub Actions*. Nothing else is needed. GitHub does not run Jekyll for this source, so the
Sphinx folders that start with `_` are served as they are.

## Check the site folder locally

```bash
.venv/bin/pypeline run --config-file publish_pypeline.yaml
```

This runs the same pipeline as the `build` job and writes `.yanga/build/site`. Open
`.yanga/build/site/index.html`: it lists the builds of the SPL test, and its links open the
variant reports and the SPL documentation report. A local run deploys nothing; only the workflow
does.
