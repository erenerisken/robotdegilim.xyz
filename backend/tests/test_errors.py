from __future__ import annotations

import pytest

from src.errors import AppError, AbortScrapingError


def test_app_error_stores_metadata():
    err = AppError("oops", code="E_TEST", details={"a": 1})
    assert err.message == "oops"
    assert err.code == "E_TEST"
    assert err.details == {"a": 1}
    assert str(err) == "oops"


def test_abort_scraping_error_inherits_metadata():
    err = AbortScrapingError("fail", code="SCRAPE", details=[1, 2])
    assert err.message == "fail"
    assert err.code == "SCRAPE"
    assert err.details == [1, 2]
    with pytest.raises(AbortScrapingError):
        raise err