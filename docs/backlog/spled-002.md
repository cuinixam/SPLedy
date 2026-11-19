---
status: Done (2026-11-20)
priority: Medium
blocked_by: [YCORE-002, YANGA-004, YANGA-005]
---

# [SPLED-002] Components and the Disco variant use the testing blocks per framework

## Summary

As a developer of SPLed, I want the components to declare their tests in the new per-framework testing blocks and the Disco variant to have a test of its own, so that SPLed keeps building and reporting with the new yanga and shows a variant test as the example.

## Description

YCORE-002 makes `testing` a list with one block per test framework and drops the old single-block form; YANGA-004 and YANGA-005 build gtest blocks and a variant test from them. SPLed still uses the old form, so it stops parsing with the new yanga-core. This is the last part of a change across yanga-core, yanga and SPLed; the design and the scope decisions are in the planning vault's epic SB-006.

## Scope decisions

- **Block form.** Every component's `testing` becomes a list with one `gtest` block, with the same sources as today.
- **One variant test.** Disco gets a `gtest` block with one test that drives the whole variant through its selected components (holding the power button turns the light green). Disco selects the integration component `test_integrations_spled` on gtest, so its variant test also checks that an integration component does not break the variant test.
- **Floor bump.** The yanga floor goes up to the release that carries YANGA-005, and the lock file is refreshed, once that release exists. Until then the item is checked with yanga-core and yanga installed as editable from the epic's worktrees.
- Out of scope: variant tests for Sleep and Spa, other test frameworks, test sources per platform on a variant.

## Acceptance criteria

- [x] SPLed's components use the block form, and their unit tests and reports on the gtest platform are as before
- [x] In SPLed, the Disco variant's `gtest` block runs its variant test on the gtest platform and shows its result and its coverage in the variant report
- [x] The yanga floor is at the release with YANGA-005, and `pytest test` passes with the released packages
