def get_adjacency_list(node_names: list[str], edges: list[tuple[str, str]]) -> dict[str, list]:
    adj: dict[str, list[str]] = {node: [] for node in node_names}
    for edge in edges:
        adj[edge[0]].append(edge[1])
    return adj


def get_reverse_adjacency_list(node_names: list[str], edges: list[tuple[str, str]]) -> dict[str, list[str]]:
    adj: dict[str, list[str]] = {node: [] for node in node_names}
    for edge in edges:
        adj[edge[1]].append(edge[0])
    return adj


def detect_cycles(node_names: list[str], edges: list[tuple[str, str]]) -> bool:
    visited: set[str] = set()
    stack: set[str] = set()
    adj: dict[str, list] = get_adjacency_list(node_names, edges)

    def dfs(u: str) -> bool:
        visited.add(u)
        stack.add(u)
        for v in adj.get(u, []):
            if v not in visited:
                if dfs(v):
                    return True
            elif v in stack:
                return True
        stack.remove(u)
        return False

    for node in node_names:
        if node not in visited:
            if dfs(node):
                return True
    return False
