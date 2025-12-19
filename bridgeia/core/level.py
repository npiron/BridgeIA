from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class AnchorPoint:
    anchor_id: str
    x: float
    y: float
    fixed: bool


@dataclass(frozen=True)
class BankSegment:
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True)
class Goal:
    goal_type: str
    x: float


@dataclass(frozen=True)
class Level:
    name: str
    budget: int
    anchors: tuple[AnchorPoint, ...]
    banks: tuple[BankSegment, ...]
    goal: Goal

    @classmethod
    def from_json(cls, path: Path) -> "Level":
        data = json.loads(path.read_text(encoding="utf-8"))
        anchors = tuple(
            AnchorPoint(
                anchor_id=anchor["id"],
                x=anchor["x"],
                y=anchor["y"],
                fixed=anchor["fixed"],
            )
            for anchor in data.get("anchors", [])
        )
        banks = tuple(
            BankSegment(
                x1=bank["x1"],
                y1=bank["y1"],
                x2=bank["x2"],
                y2=bank["y2"],
            )
            for bank in data.get("banks", [])
        )
        goal_data: dict[str, Any] = data.get("goal", {})
        goal = Goal(goal_type=goal_data.get("type", "reach_x"), x=goal_data.get("x", 0))
        return cls(
            name=data.get("name", path.stem),
            budget=data.get("budget", 0),
            anchors=anchors,
            banks=banks,
            goal=goal,
        )
