"""Unit tests for the summarisation prompt builder (T026, U2)."""

from __future__ import annotations

import pytest

from meetinglens.prompt import build_summarisation_prompt

pytestmark = pytest.mark.unit


def test_includes_count_and_interval():
    prompt = build_summarisation_prompt(18, 45)
    assert "18" in prompt
    assert "45" in prompt


def test_requests_required_content():
    prompt = build_summarisation_prompt(5, 30).lower()
    for phrase in [
        "in order",
        "visible text",
        "bullet points",
        "chart",
        "names",
        "dates",
        "action items",
        "owners",
    ]:
        assert phrase in prompt


def test_uses_plural_for_many():
    assert "18 screenshots" in build_summarisation_prompt(18, 45)


def test_uses_singular_for_one():
    prompt = build_summarisation_prompt(1, 45)
    assert "1 screenshot " in prompt
    assert "1 screenshots" not in prompt
