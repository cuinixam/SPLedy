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

- [x] In a component report and a variant report built from SPLed on the gtest platform, each declaration in a production source docs page links to the coverage page of its file, scrolled to the declaration's first line
- [x] A test builds the Disco variant on gtest and checks that a declaration in a source docs page links to its coverage page with the right `#l<line>`
- [x] Under the `local` profile, a declaration in a test source docs page links to `vscode://file/<absolute path>:<line>`
- [x] `CheckCIContext` runs in the build pipeline before `GenerateBuildSystemFiles`

## Questions

- In the Disco gtest variant report, `light_controller.c` has a row in two component coverage trees: `coverage/light_controller/` (shown name `light_controller.c`) and `coverage/test_integrations_spled/` (shown name `light_controller/src/light_controller.c`), because the integration test component covers production files of other components. YANGA-001's gcovr strategy treats two matching rows as ambiguous and returns no target, so under `local` every production declaration in the variant report links to VS Code instead of coverage, and on CI it would be plain text. AC 1 cannot be met with SPLed config alone. Both rows point to a page with the same gcovr hash (`index.light_controller.c.fe0174….html`), which means the same source file. I would pick a fix in YANGA-001: treat matching rows whose page names are equal as one file and take the component tree whose name is the first path component of the match (`light_controller`), and keep the warning only for rows with different page names. That needs the epic's scope decision on the gcovr strategy ("More than one matching row gives a warning and plain text") to be reworded.
  - Answer (2026-11-18): yes, change it. The epic SB-004 gcovr rule now treats rows with the same page name as one file, and the tree named by the source path's component wins. YANGA-001 has the fix on `feat/yanga-001-source-links` (test `test_gcovr_same_page_in_several_trees_goes_to_the_component_tree`).

## Handoff

- Intent: turn on source links in the gtest reports: `platforms/gtest/yanga.yaml` (`source_links`, `resolvers`), `conf.py` (`myst_url_schemes`), `yanga.yaml` (`CheckCIContext` before `GenerateBuildSystemFiles`).
- Verified: gate `pypeline run --config-file yanga.yaml --step CreateVEnv --single` then `.venv/bin/python -m pytest -k "Test_Disco and gtest"`, exit 0 (4 passed), on macOS, with clanguru and yanga editable from the CLG-016 and YANGA-001 worktrees (including YANGA-001's same-page fix). `jarvis floor-guard 7cec2e5` exit 0. Tests: `test/test_Disco.py`, `test_gtest_source_docs_link_to_coverage_lines` and `test_gtest_test_source_docs_link_to_vscode_locally_and_plain_text_on_ci`.
- State: every acceptance criterion ticked; branch `feat/spled-001-source-links`, local feature commit, nothing pushed.
- Next step: after CLG-016 and YANGA-001 are released, raise SPLed's yanga (and clanguru) floor in `pyproject.toml`, relock, then publish.
- Known problems: on CI with the released packages the coverage test fails until that floor bump. The CI branch of the test-source test was not run for real.
