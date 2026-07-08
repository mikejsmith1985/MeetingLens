"""Unit test covering the package markers (src/meetinglens and adapters __init__)."""

from __future__ import annotations

import pytest

import meetinglens
from meetinglens import adapters  # noqa: F401 - importing proves the package initialises

pytestmark = pytest.mark.unit


def test_package_exposes_version():
    assert isinstance(meetinglens.__version__, str)
    assert meetinglens.__version__


def test_adapters_package_imports():
    from meetinglens import adapters as adapters_pkg

    assert adapters_pkg is not None
