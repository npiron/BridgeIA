from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import pygame

from bridgeia.core.bridge import BridgeDesign, calculate_cost, edge_exists, edge_length
from bridgeia.core.level import AnchorPoint, Level
from bridgeia.ui.renderer import LevelRenderer
from bridgeia.sim.simulation import PhysicsSimulation

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
    bridge = BridgeDesign(edges=[], joints={})
    
    # State
    selected_anchor: str | None = None
    simulation: PhysicsSimulation | None = None
    
    # Grid State
    grid_enabled: bool = True
    grid_size: int = 40
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if simulation:
                        simulation = None # Stop simulation
                    else:
                        selected_anchor = None # Cancel selection
                elif event.key == pygame.K_SPACE:
                    if simulation:
                        simulation = None
                    else:
                        simulation = PhysicsSimulation(level, bridge)
                        selected_anchor = None
                elif event.key == pygame.K_g:
                    grid_enabled = not grid_enabled
                elif event.key == pygame.K_LEFTBRACKET: # [
                    grid_size = max(10, grid_size - 10)
                elif event.key == pygame.K_RIGHTBRACKET: # ]
                    grid_size = min(100, grid_size + 10)

            # Mouse interaction only in BUILD mode
            if not simulation:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left Click
                        # Use SNAPPED position for actions
                        mouse_pos = event.pos
                        snapped_pos = get_snapped_position(mouse_pos, grid_size, grid_enabled)
                        
                        # Logic:
                        # 1. Check entity at Mouse (Raw)
                        target_id = find_point_at(level, bridge, mouse_pos)
                        
                        if target_id:
                            # Clicked on existing point
                            if selected_anchor:
                                if selected_anchor != target_id:
                                    try_add_edge(level, bridge, selected_anchor, target_id)
                                    selected_anchor = target_id
                                else:
                                    selected_anchor = target_id 
                            else:
                                selected_anchor = target_id
                        else:
                            # Clicked on empty space -> Create joint at Snapped Pos
                            if selected_anchor:
                                # Create new joint at snapped position
                                # Ensure we don't accidentally create a joint ON TOP of an existing one (duplicate)
                                # Check if snapped pos is on top of an existing point
                                existing_at_snap = find_point_at(level, bridge, snapped_pos)
                                if existing_at_snap:
                                    # We snapped to an existing point! Connect to it.
                                    try_add_edge(level, bridge, selected_anchor, existing_at_snap)
                                    selected_anchor = existing_at_snap
                                else:
                                    # Real new point
                                    create_new_joint(level, bridge, selected_anchor, snapped_pos)
                                    # Auto-select the new joint? usually yes.
                                    # create_new_joint needs to return the id, but we can assume it works for now?
                                    # Use a helper that returns ID
                                    new_id = create_new_joint_and_return_id(level, bridge, selected_anchor, snapped_pos)
                                    if new_id:
                                        selected_anchor = new_id
                                    
                    elif event.button == 3: # Right Click
                        remove_element_at(level, bridge, event.pos)
                        selected_anchor = None

        if simulation:
            simulation.step(dt)

        if not simulation and selected_anchor:
            mouse_pos = pygame.mouse.get_pos()
            snapped_pos = get_snapped_position(mouse_pos, grid_size, grid_enabled)
            preview_line = build_preview_line(level, bridge, selected_anchor, snapped_pos)
        else:
            preview_line = None

        renderer.draw(level, bridge, preview_line, selected_anchor, simulation, grid_enabled, grid_size)
        pygame.display.flip()

    pygame.quit()


def get_snapped_position(pos: tuple[int, int], grid_size: int, enabled: bool) -> tuple[int, int]:
    if not enabled:
        return pos
    x, y = pos
    snapped_x = round(x / grid_size) * grid_size
    snapped_y = round(y / grid_size) * grid_size
    return snapped_x, snapped_y


def create_new_joint_and_return_id(level: Level, bridge: BridgeDesign, origin_id: str, pos: tuple[int, int]) -> str | None:
    points = get_all_point_positions(level, bridge)
    start_pos = points[origin_id]
    dist = edge_length(start_pos, pos)
    
    if dist <= MAX_EDGE_LENGTH:
        cost = calculate_cost(dist, COST_PER_UNIT)
        if bridge.total_cost() + cost <= level.budget:
            new_id = bridge.add_joint(float(pos[0]), float(pos[1]))
            bridge.add_edge(origin_id, new_id, "wood", cost)
            return new_id
    return None

def create_new_joint(level: Level, bridge: BridgeDesign, origin_id: str, pos: tuple[int, int]) -> None:
    create_new_joint_and_return_id(level, bridge, origin_id, pos)


def get_new_selection(
    level: Level, 
    bridge: BridgeDesign, 
    pos: tuple[int, int], 
    current_selection: str | None
) -> str | None:
    # Deprecated by inline logic in main loop which handles snapping better
    return None

def build_preview_line(level: Level, bridge: BridgeDesign, selected_anchor: str | None, mouse_pos: tuple[int, int]) -> tuple[tuple[int, int], tuple[int, int]] | None:
    if selected_anchor is None:
        return None
        
    points = get_all_point_positions(level, bridge)
    start = points.get(selected_anchor)
    if start is None:
        return None
        
    return (int(start[0]), int(start[1])), mouse_pos


def get_all_point_positions(level: Level, bridge: BridgeDesign) -> dict[str, tuple[float, float]]:
    points = {a.anchor_id: (a.x, a.y) for a in level.anchors}
    points.update(bridge.joints)
    return points


def find_point_at(level: Level, bridge: BridgeDesign, position: tuple[int, int]) -> str | None:
    x, y = position
    points = get_all_point_positions(level, bridge)
    
    for p_id, (px, py) in points.items():
        dx = px - x
        dy = py - y
        if (dx * dx + dy * dy) ** 0.5 <= ANCHOR_SNAP_RADIUS:
            return p_id
    return None


def try_add_edge(level: Level, bridge: BridgeDesign, a_id: str, b_id: str) -> None:
    if edge_exists(bridge.edges, a_id, b_id):
        return
    
    points = get_all_point_positions(level, bridge)
    if a_id not in points or b_id not in points:
        return
        
    length = edge_length(points[a_id], points[b_id])
    if length > MAX_EDGE_LENGTH:
        return
        
    cost = calculate_cost(length, COST_PER_UNIT)
    if bridge.total_cost() + cost > level.budget:
        return
        
    bridge.add_edge(a_id, b_id, material="wood", cost=cost)


def remove_element_at(level: Level, bridge: BridgeDesign, position: tuple[int, int]) -> bool:
    # Priority: Remove joint (if dynamic) -> Remove edge
    points = get_all_point_positions(level, bridge)
    x, y = position
    
    # Check joints first (only dynamic ones can be removed)
    level_anchor_ids = {a.anchor_id for a in level.anchors}
    
    closest_id = find_point_at(level, bridge, position)
    if closest_id and closest_id not in level_anchor_ids:
        # It's a bridge joint. Remove it and all connected edges.
        edges_to_remove = [e.edge_id for e in bridge.edges if e.a == closest_id or e.b == closest_id]
        for e_id in edges_to_remove:
            bridge.remove_edge(e_id)
        del bridge.joints[closest_id]
        return True

    # Check edges
    for edge in list(bridge.edges):
        start = points.get(edge.a)
        end = points.get(edge.b)
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

def handle_click(level: Level, bridge: BridgeDesign, pos: tuple[int, int], selection: str | None) -> None:
    pass

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
    bridge = BridgeDesign(edges=[], joints={})
    
    renderer.draw(level, bridge, preview_line=None, selected_anchor=None)
    pygame.display.flip()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(screen, str(output_path))
    pygame.quit()


if __name__ == "__main__":
    run()
