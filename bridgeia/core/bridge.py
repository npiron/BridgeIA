from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Iterable


@dataclass(frozen=True)
class Edge:
    edge_id: int
    a: str
    b: str
    material: str
    cost: int


@dataclass
class BridgeDesign:
    edges: list[Edge]
    joints: dict[str, tuple[float, float]]  # ID -> (x, y)
    next_edge_id: int = 1
    next_joint_id: int = 1

    def add_edge(self, a: str, b: str, material: str, cost: int) -> Edge:
        edge = Edge(edge_id=self.next_edge_id, a=a, b=b, material=material, cost=cost)
        self.edges.append(edge)
        self.next_edge_id += 1
        return edge

    def add_joint(self, x: float, y: float) -> str:
        joint_id = f"j_{self.next_joint_id}"
        self.joints[joint_id] = (x, y)
        self.next_joint_id += 1
        return joint_id

    def remove_edge(self, edge_id: int) -> None:
        self.edges = [edge for edge in self.edges if edge.edge_id != edge_id]
        # Clean up orphan joints? Maybe later.

    def total_cost(self) -> int:
        return sum(edge.cost for edge in self.edges)


def edge_length(a: tuple[float, float], b: tuple[float, float]) -> float:
    return hypot(a[0] - b[0], a[1] - b[1])


def calculate_cost(length: float, cost_per_unit: float) -> int:
    return int(round(length * cost_per_unit))


def edge_exists(edges: Iterable[Edge], a: str, b: str) -> bool:
    return any(
        (edge.a == a and edge.b == b) or (edge.a == b and edge.b == a)
        for edge in edges
    )
