import pytest

from app.utils.graph import detect_cycles, get_adjacency_list


@pytest.mark.parametrize(
    "names, edges, expected",
    [
        (["a", "b", "c"], [("a", "b"), ("b", "c")], False),
        (["a", "b", "c"], [("a", "b"), ("b", "a")], True),
        (["a", "b", "c"], [("a", "a")], True),
        (["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")], True),
        (["a"], [], False),
        (["a", "b", "c", "d", "e", "f"], [], False),
    ],
    ids=[
        "simple-acyclic",
        "two-node-cycle",
        "self-loop",
        "three-node-cycle",
        "single-node",
        "multiple-no-edges",
    ],
)
def test_detect_cycles(names, edges, expected):
    assert detect_cycles(names, edges) is expected


@pytest.mark.parametrize(
    "names, edges, expected_adj",
    [
        (["a", "b", "c", "d"], [("a", "c"), ("b", "c"), ("c", "d")],
         {"a": ["c"], "b": ["c"], "c": ["d"], "d": []}),
        (["a", "b", "c"], [], {"a": [], "b": [], "c": []}),
        (["a", "b", "c", "d"], [("a", "b"), ("a", "c"), ("a", "d")],
         {"a": ["b", "c", "d"], "b": [], "c": [], "d": []}),
        (["a"], [], {"a": []}),
    ],
    ids=[
        "branching-tree",
        "no-edges",
        "star-shape",
        "singleton",
    ],
)
def test_get_adjacency_list(names, edges, expected_adj):
    assert get_adjacency_list(names, edges) == expected_adj
