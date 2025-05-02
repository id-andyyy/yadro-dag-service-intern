def detect_cycles(names: list[str], edges: list[tuple[str, str]]) -> bool:
    adj = {name: [] for name in names}
    for s, t in edges:
        adj[s].append(t)

    visited = set()
    on_stack = set()

    def dfs(u: str) -> bool:
        visited.add(u)
        on_stack.add(u)
        for v in adj.get(u, []):
            if v not in visited:
                if dfs(v):
                    return True
            elif v in on_stack:
                return True
        on_stack.remove(u)
        return False

    for n in names:
        if n not in visited:
            if dfs(n):
                return True
    return False
