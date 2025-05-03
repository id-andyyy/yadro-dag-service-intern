import pytest
from sqlalchemy.orm import Session

from app.utils.graph import detect_cycles


def test_detect_cycles(db_session: Session):
    names = ["a", "b", "c"]
    edges = [("a", "b"), ("b", "c")]
    assert not detect_cycles(names, edges)

    names = ["a", "b", "c"]
    edges = [("a", "b"), ("b", "a")]
    assert detect_cycles(names, edges)

    names = ["a", "b", "c"]
    edges = [("a", "a")]
    assert detect_cycles(names, edges)

    names = ["a", "b", "c"]
    edges = [("a", "b"), ("b", "c"), ("c", "a")]
    assert detect_cycles(names, edges)
