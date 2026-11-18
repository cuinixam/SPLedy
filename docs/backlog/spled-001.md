---
status: In Progress
priority: Medium
blocked_by: [YANGA-001]
---

# [SPLED-001] Source links in the gtest reports

## Summary

As a reader of an SPLed report on the gtest platform, I want each declaration in a source docs page to link to its line in the coverage report, so that I can go from a function's documentation to its coverage in one click.

## Description

With CLG-016 and YANGA-001, clanguru writes `source:` links and yanga resolves them, but only for a project that turns the feature on and lets MyST keep the links. SPLed does neither today. This is the last part of a change across clanguru, yanga and SPLed; the design and the checks against a built report are in the planning vault's epic SB-004.

## Scope decisions

- **MyST.** MyST drops a link whose scheme it does not know, so SPLed's `conf.py` adds `source` to `myst_url_schemes`.
- **Config.** In the gtest platform: `source_links: true` and `resolvers: {default: [gcovr], local: [gcovr, vscode]}` in `ReportCMakeGenerator`'s `config:`. On CI (`ci` falls back to `default`) test sources show plain text; locally they open in VS Code.
- **CI check in the build.** `CheckCIContext` runs only in the SPL overview pipeline today. This item adds it to the `yanga.yaml` build pipeline before `GenerateBuildSystemFiles`; without it a CI build always uses `local`.
- Out of scope: the SPL overview report (it copies the variant reports after their links are resolved, and the links are relative).

## Acceptance criteria

- [ ] In a component report and a variant report built from SPLed on the gtest platform, each declaration in a production source docs page links to the coverage page of its file, scrolled to the declaration's first line
- [ ] A test builds the Disco variant on gtest and checks that a declaration in a source docs page links to its coverage page with the right `#l<line>`
- [ ] Under the `local` profile, a declaration in a test source docs page links to `vscode://file/<absolute path>:<line>`
- [ ] `CheckCIContext` runs in the build pipeline before `GenerateBuildSystemFiles`
