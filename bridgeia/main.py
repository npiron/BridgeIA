from __future__ import annotations

from pathlib import Path

import pygame

from bridgeia.core.bridge import BridgeDesign, calculate_cost, edge_exists, edge_length
from bridgeia.core.level import Level
from bridgeia.ui.renderer import LevelRenderer

WINDOW_SIZE = (1000, 600)
LEVEL_PATH = Path(__file__).resolve().parents[1] / "levels" / "level_01.json"
COST_PER_UNIT = 3.0
MAX_EDGE_LENGTH = 220.0
ANCHOR_SNAP_RADIUS = 18


def run() -> None:
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("BridgeIA")
    clock = pygame.time.Clock()

    level = Level.from_json(LEVEL_PATH)
    renderer = LevelRenderer(screen)
    bridge = BridgeDesign(edges=[])
    selected_anchor: str | None = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                anchor_id = find_anchor_id_at(level, event.pos)
                if anchor_id is None:
                    continue
                if selected_anchor is None:
                    selected_anchor = anchor_id
                elif selected_anchor != anchor_id:
                    try_add_edge(level, bridge, selected_anchor, anchor_id)
                    selected_anchor = None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                removed = remove_edge_at(level, bridge, event.pos)
                if removed:
                    selected_anchor = None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                selected_anchor = None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE:
                hovered_edge_id = find_edge_at(level, bridge, pygame.mouse.get_pos())
                if hovered_edge_id is not None:
                    bridge.remove_edge(hovered_edge_id)

        hovered_edge_id = find_edge_at(level, bridge, pygame.mouse.get_pos())
        preview = build_preview(level, bridge, selected_anchor, pygame.mouse.get_pos())

        renderer.draw(level, bridge, preview, selected_anchor, hovered_edge_id)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def find_anchor_id_at(level: Level, position: tuple[int, int]) -> str | None:
    x, y = position
    radius_sq = ANCHOR_SNAP_RADIUS * ANCHOR_SNAP_RADIUS
    for anchor in level.anchors:
        dx = anchor.x - x
        dy = anchor.y - y
        if dx * dx + dy * dy <= radius_sq:
            return anchor.anchor_id
    return None


def try_add_edge(level: Level, bridge: BridgeDesign, a_id: str, b_id: str) -> None:
    is_valid, cost = validate_edge(level, bridge, a_id, b_id)
    if not is_valid or cost is None:
        return
    bridge.add_edge(a_id, b_id, material="wood", cost=cost)


def remove_edge_at(level: Level, bridge: BridgeDesign, position: tuple[int, int]) -> bool:
    edge_id = find_edge_at(level, bridge, position)
    if edge_id is not None:
        bridge.remove_edge(edge_id)
        return True
    return False


def point_to_segment_distance(point: tuple[int, int], start: tuple[float, float], end: tuple[float, float]) -> float:
    px, py = point
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    return ((px - closest_x) ** 2 + (py - closest_y) ** 2) ** 0.5


def build_preview(
    level: Level,
    bridge: BridgeDesign,
    selected_anchor: str | None,
    mouse_pos: tuple[int, int],
) -> tuple[tuple[int, int], tuple[int, int], bool] | None:
    if selected_anchor is None:
        return None
    anchors = anchor_positions(level)
    start = anchors.get(selected_anchor)
    if start is None:
        return None
    end_anchor_id = find_anchor_id_at(level, mouse_pos)
    if end_anchor_id is not None and end_anchor_id in anchors:
        end = anchors[end_anchor_id]
    else:
        end = mouse_pos
    is_valid, _ = validate_edge(level, bridge, selected_anchor, end_anchor_id) if end_anchor_id else (False, None)
    return (int(start[0]), int(start[1])), (int(end[0]), int(end[1])), is_valid


def anchor_positions(level: Level) -> dict[str, tuple[float, float]]:
    return {anchor.anchor_id: (anchor.x, anchor.y) for anchor in level.anchors}


def validate_edge(
    level: Level,
    bridge: BridgeDesign,
    a_id: str,
    b_id: str | None,
) -> tuple[bool, int | None]:
    if b_id is None:
        return False, None
    if a_id == b_id:
        return False, None
    if edge_exists(bridge.edges, a_id, b_id):
        return False, None
    anchors = anchor_positions(level)
    if a_id not in anchors or b_id not in anchors:
        return False, None
    length = edge_length(anchors[a_id], anchors[b_id])
    if length > MAX_EDGE_LENGTH:
        return False, None
    cost = calculate_cost(length, COST_PER_UNIT)
    if bridge.total_cost() + cost > level.budget:
        return False, None
    return True, cost


def find_edge_at(level: Level, bridge: BridgeDesign, position: tuple[int, int]) -> int | None:
    anchors = anchor_positions(level)
    x, y = position
    for edge in bridge.edges:
        start = anchors.get(edge.a)
        end = anchors.get(edge.b)
        if not start or not end:
            continue
        if point_to_segment_distance((x, y), start, end) <= 8:
            return edge.edge_id
    return None


if __name__ == "__main__":
    run()
