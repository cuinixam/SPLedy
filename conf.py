# -*- coding: utf-8 -*-
"""Configuration"""

import datetime
from typing import Any

from yanga_core.docs.sphinx import SphinxConfig

day = datetime.date.today()

# meta data #################################################################

project = "SPLed"
copyright = f"{day.year}, RMT and Friends"
release = f"{day}"

# file handling #############################################################
# @see https://www.sphinx-doc.org/en/master/usage/configuration.html

templates_path = [
    "doc/_tmpl",
]

exclude_patterns = [
    "README.md",
    "build/modules",
    "build/deps",
    ".venv",
    ".git",
    "**/test_results.rst",  # We renamed this file, but nobody deletes it.
]

html_context: dict[str, Any] = {
    "env": {
        # Add current execution time in UTC
        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    },
    # TODO: the feature configuration is not yet implemented
    "config": {},
}

include_patterns = ["index.md", "doc/**"]

report_config = SphinxConfig()
html_context.update(report_config.html_context)
include_patterns.extend(report_config.include_patterns)

# Print all include patterns
print("Include patterns:")
for pattern in include_patterns:
    print(f" - {pattern}")

project = report_config.project

# configuration of built-in stuff ###########################################
# @see https://www.sphinx-doc.org/en/master/usage/configuration.html

numfig = True

# html config ###############################################################
# @see https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Omit "documentation" in title
html_title = f"{project} {release}"

html_theme = "sphinx_rtd_theme"

# Show hyper link which leeds to the source of page displayed
html_show_sourcelink = True

html_theme_options = {
    "canonical_url": "",
    "analytics_id": "",  # Provided by Google in your dashboard
    "prev_next_buttons_location": "bottom",
    "style_external_links": True,
    "logo_only": False,
    "style_nav_header_background": "white",
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 6,
    "includehidden": True,
    "titles_only": False,
}


html_logo = "doc/_figures/SPLED_logo.png"

# Copy the standalone CI pipeline page into the report output as-is.
# It is referenced from the toctree as `CI Pipeline <./ci_pipeline.html#http://>`
# and the fix_html_links step rewrites the link to the correct relative path.
html_extra_path = ["doc/ci_pipeline.html"]

# extensions and their configuration #########################################
extensions = []

extensions.append("sphinx_rtd_size")
sphinx_rtd_size_width = "90%"

extensions.append("sphinxcontrib.mermaid")

# Parse markdown files
extensions.append("myst_parser")
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_admonition",
    "html_image",
]

# Traceability extension
extensions.append("sphinx_needs")
extensions.append("sphinx_test_reports")

# needs_types - this option allows the setup of own need types like bugs, user_stories and more.
needs_types = [
    dict(directive="req", title="Requirement", prefix="R_", color="#BFD8D2", style="node"),
    dict(
        directive="spec",
        title="Specification",
        prefix="S_",
        color="#FEDCD2",
        style="node",
    ),
    dict(
        directive="impl",
        title="Implementation",
        prefix="I_",
        color="#DF744A",
        style="node",
    ),
    dict(directive="test", title="Test Case", prefix="T_", color="#DCB239", style="node"),
]

# Define own link types
needs_links = {
    # SWE.3 BP.5: link from Implementation (Software unit) to Specification (Software detailed design)
    # AND
    # SWE.2 BP.7: link from Requirements (Software Requirement) to Architecture (Software Architecture)
    "implements": {"incoming": "is implemented by", "outgoing": "implements"},
    # SWE.4 BP.5: link from Test Case (Unit test specification) to Specification (Software detailed design)
    "tests": {"incoming": "is tested by", "outgoing": "tests"},
    # SWE.4 BP.5: link from Test Case (Unit test specification) to Test Result (Unit test result).
    # A test spec titled `Suite.Case` (clanguru's `{{ gtest.test }}`) links every gtest result of that test.
    # The rule drops the `Prefix/` of a parametrized suite and the `/N` of each instance, so a TEST_P spec needs no pattern.
    "results": {
        "incoming": "is resulted from",
        "outgoing": "results",
        "default": (
            "[[links_from_filter(\"type == 'testcase'"
            " and current_need['title'].split('.')[0] in classname.split('/')"
            " and case.split('/')[0] == current_need['title'].split('.')[1]\")]]"
        ),
    },
}

# Every test spec must have a result: a typo in the title or a test that did not run fails the build.
needs_schema_definitions = {
    "schemas": [
        {
            "id": "test-results-required",
            "select": {"properties": {"type": {"const": "test"}}},
            "validate": {"local": {"properties": {"results": {"minItems": 1}}, "required": ["results"]}},
        }
    ]
}

# The suffix of source filenames.
source_suffix = [
    ".md",
    ".rst",
]


def setup(app):  # type: ignore
    app.connect("source-read", report_config.render_with_jinja)
