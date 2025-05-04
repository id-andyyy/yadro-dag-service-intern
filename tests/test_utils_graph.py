import pytest

from app.utils.graph import detect_cycles, build_adjacency_list, build_reverse_adjacency_list


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
def test_detect_cycles(names: list[str], edges: list[tuple[str, str]], expected: bool):
    assert detect_cycles(names, edges) is expected


@pytest.mark.parametrize(
    "names, edges, expected",
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
def test_get_adjacency_list(names: list[str], edges: list[tuple[str, str]], expected: dict[str, list[str]]):
    assert build_adjacency_list(names, edges) == expected


@pytest.mark.parametrize(
    "names, edges, expected",
    [
        (["a", "b", "c", "d"], [("a", "c"), ("b", "c"), ("c", "d")],
         {"a": [], "b": [], "c": ["a", "b"], "d": ["c"]}),
        (["a", "b", "c"], [], {"a": [], "b": [], "c": []}),
        (["a", "b", "c", "d"], [("b", "a"), ("c", "a"), ("d", "a")],
         {"a": ["b", "c", "d"], "b": [], "c": [], "d": []}),
        (["a"], [], {"a": []}),
    ]
)
def test_get_reverse_adjacency_list(names: list[str], edges: list[tuple[str, str]], expected: dict[str, list[str]]):
    assert build_reverse_adjacency_list(names, edges) == expected
