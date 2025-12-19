from __future__ import annotations

import argparse
import os
from pathlib import Path

import pygame

from bridgeia.core.bridge import BridgeDesign, calculate_cost, edge_exists, edge_length
from bridgeia.core.level import AnchorPoint, Level
from bridgeia.ui.renderer import LevelRenderer

WINDOW_SIZE = (1000, 600)
LEVEL_PATH = Path(__file__).resolve().parents[1] / "levels" / "level_01.json"
COST_PER_UNIT = 3.0
MAX_EDGE_LENGTH = 220.0
ANCHOR_SNAP_RADIUS = 18


def run() -> None:
    args = parse_args()
    if args.screenshot:
        render_screenshot(Path(args.screenshot))
        return

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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                selected_anchor = None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                anchor = find_anchor_at(level, event.pos)
                if anchor is None:
                    continue
                if selected_anchor is None:
                    selected_anchor = anchor.anchor_id
                elif selected_anchor != anchor.anchor_id:
                    try_add_edge(level, bridge, selected_anchor, anchor.anchor_id)
                    selected_anchor = None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                removed = remove_edge_at(level, bridge, event.pos)
                if removed:
                    selected_anchor = None

        preview_line = build_preview_line(level, selected_anchor)

        renderer.draw(level, bridge, preview_line, selected_anchor)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BridgeIA prototype")
    parser.add_argument(
        "--screenshot",
        type=str,
        help="Render a static frame to an image file and exit.",
    )
    return parser.parse_args()


def render_screenshot(output_path: Path) -> None:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("BridgeIA")

    level = Level.from_json(LEVEL_PATH)
    renderer = LevelRenderer(screen)
    bridge = BridgeDesign(edges=[])
    anchor_ids = [anchor.anchor_id for anchor in level.anchors]
    if len(anchor_ids) >= 2:
        try_add_edge(level, bridge, anchor_ids[0], anchor_ids[1])
    if len(anchor_ids) >= 3:
        try_add_edge(level, bridge, anchor_ids[1], anchor_ids[2])

    renderer.draw(level, bridge, preview_line=None, selected_anchor=None)
    pygame.display.flip()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(screen, str(output_path))
    pygame.quit()


def find_anchor_at(level: Level, position: tuple[int, int]) -> AnchorPoint | None:
    x, y = position
    for anchor in level.anchors:
        dx = anchor.x - x
        dy = anchor.y - y
        if (dx * dx + dy * dy) ** 0.5 <= ANCHOR_SNAP_RADIUS:
            return anchor
    return None


def try_add_edge(level: Level, bridge: BridgeDesign, a_id: str, b_id: str) -> None:
    if edge_exists(bridge.edges, a_id, b_id):
        return
    anchors = {anchor.anchor_id: (anchor.x, anchor.y) for anchor in level.anchors}
    if a_id not in anchors or b_id not in anchors:
        return
    length = edge_length(anchors[a_id], anchors[b_id])
    if length > MAX_EDGE_LENGTH:
        return
    cost = calculate_cost(length, COST_PER_UNIT)
    if bridge.total_cost() + cost > level.budget:
        return
    bridge.add_edge(a_id, b_id, material="wood", cost=cost)


def remove_edge_at(level: Level, bridge: BridgeDesign, position: tuple[int, int]) -> bool:
    anchors = {anchor.anchor_id: (anchor.x, anchor.y) for anchor in level.anchors}
    x, y = position
    for edge in list(bridge.edges):
        start = anchors.get(edge.a)
        end = anchors.get(edge.b)
        if not start or not end:
            continue
        if point_to_segment_distance((x, y), start, end) <= 8:
            bridge.remove_edge(edge.edge_id)
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


def build_preview_line(level: Level, selected_anchor: str | None) -> tuple[tuple[int, int], tuple[int, int]] | None:
    if selected_anchor is None:
        return None
    anchors = {anchor.anchor_id: (anchor.x, anchor.y) for anchor in level.anchors}
    start = anchors.get(selected_anchor)
    if start is None:
        return None
    mouse_pos = pygame.mouse.get_pos()
    return (int(start[0]), int(start[1])), mouse_pos


if __name__ == "__main__":
    run()
