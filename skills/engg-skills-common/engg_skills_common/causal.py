"""Pure-Python DAG helpers for causal-inference workflows in process data.

Implements:
- Adjacency-list DAG with cycle check.
- Ancestors / descendants / parents / children queries.
- d-separation test (Geiger-Verma-Pearl moralization on ancestral subgraph).
- Backdoor adjustment set enumeration (returns the parent set of treatment
  with a verification step that it satisfies the backdoor criterion).
- DOT-language export for rendering with the Graphviz binary.

Scope is intentionally narrow per the architecture review: this skill enables
DAG construction, d-separation queries, and adjustment-set enumeration. It
does NOT estimate causal effects — that lives in downstream regression /
matching / Bayesian skills.
"""

from __future__ import annotations

from itertools import chain, combinations
from typing import Iterable


class DAG:
    def __init__(self) -> None:
        self.nodes: set[str] = set()
        self.parents: dict[str, set[str]] = {}
        self.children: dict[str, set[str]] = {}

    @classmethod
    def from_edges(cls, edges: Iterable[tuple[str, str]]) -> "DAG":
        g = cls()
        for u, v in edges:
            g.add_edge(u, v)
        if g.has_cycle():
            raise ValueError("graph contains a cycle")
        return g

    def add_edge(self, u: str, v: str) -> None:
        if u == v:
            raise ValueError("self-loops not allowed in DAG")
        self.nodes.update([u, v])
        self.parents.setdefault(v, set()).add(u)
        self.children.setdefault(u, set()).add(v)
        self.parents.setdefault(u, set())
        self.children.setdefault(v, set())

    def has_cycle(self) -> bool:
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {n: WHITE for n in self.nodes}

        def dfs(n: str) -> bool:
            color[n] = GRAY
            for ch in self.children.get(n, ()):
                if color[ch] == GRAY:
                    return True
                if color[ch] == WHITE and dfs(ch):
                    return True
            color[n] = BLACK
            return False

        return any(color[n] == WHITE and dfs(n) for n in self.nodes)

    def ancestors(self, node: str) -> set[str]:
        seen: set[str] = set()
        stack = [node]
        while stack:
            cur = stack.pop()
            for p in self.parents.get(cur, ()):
                if p not in seen:
                    seen.add(p)
                    stack.append(p)
        return seen

    def descendants(self, node: str) -> set[str]:
        seen: set[str] = set()
        stack = [node]
        while stack:
            cur = stack.pop()
            for c in self.children.get(cur, ()):
                if c not in seen:
                    seen.add(c)
                    stack.append(c)
        return seen

    def d_separated(self, x: set[str], y: set[str], z: set[str]) -> bool:
        """Test whether X is d-separated from Y given Z (Pearl).

        Implementation: build the ancestral subgraph restricted to X ∪ Y ∪ Z
        and their ancestors, moralize it, remove Z, then check connectivity.
        """

        keep = set(x) | set(y) | set(z)
        for n in list(keep):
            keep |= self.ancestors(n)
        # Build moral graph (undirected) on `keep` ancestral subgraph.
        adj: dict[str, set[str]] = {n: set() for n in keep}
        for v in keep:
            ps = [p for p in self.parents.get(v, ()) if p in keep]
            for p in ps:
                adj[p].add(v)
                adj[v].add(p)
            for a, b in combinations(ps, 2):  # marry parents
                adj[a].add(b)
                adj[b].add(a)
        # Remove Z (cannot be a path node)
        for zn in z:
            if zn in adj:
                neighbors = adj.pop(zn)
                for nb in neighbors:
                    adj[nb].discard(zn)
        # BFS from any X-node; if it reaches any Y-node, NOT d-separated.
        for s in x:
            if s in adj:
                seen = {s}
                stack = [s]
                while stack:
                    cur = stack.pop()
                    if cur in y:
                        return False
                    for nb in adj[cur]:
                        if nb not in seen:
                            seen.add(nb)
                            stack.append(nb)
        return True

    def backdoor_adjustment(self, treatment: str, outcome: str) -> dict:
        """Return the parents-of-treatment set and verify it satisfies the backdoor criterion.

        The parents-of-treatment adjustment set is always a valid backdoor set
        whenever one exists in the DAG (under standard assumptions, no latent
        common causes). Returns the candidate set and a verification flag.
        """

        if treatment not in self.nodes or outcome not in self.nodes:
            raise ValueError("treatment and outcome must be in the DAG")
        z = set(self.parents.get(treatment, set()))
        descendants_T = self.descendants(treatment) | {treatment}
        if z & descendants_T - {treatment}:
            return {"adjustment_set": sorted(z), "satisfies_backdoor": False, "reason": "parent set contains descendants of treatment"}
        # Build modified graph where outgoing edges of T are removed; check
        # whether T and Y are d-separated by Z in that graph.
        g_blocked = DAG()
        for u in self.nodes:
            for v in self.children.get(u, ()):
                if not (u == treatment):
                    g_blocked.add_edge(u, v)
            if u not in g_blocked.nodes:
                g_blocked.nodes.add(u)
        separated = g_blocked.d_separated({treatment}, {outcome}, z)
        return {
            "adjustment_set": sorted(z),
            "satisfies_backdoor": separated,
        }

    def to_dot(self, name: str = "G") -> str:
        lines = [f"digraph {name} {{", "  rankdir=LR;"]
        for u in sorted(self.nodes):
            for v in sorted(self.children.get(u, ())):
                lines.append(f'  "{u}" -> "{v}";')
        lines.append("}")
        return "\n".join(lines)
