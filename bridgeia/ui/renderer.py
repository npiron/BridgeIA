from __future__ import annotations

import pygame
from typing import Any

from bridgeia.core.bridge import BridgeDesign
from bridgeia.core.level import Level


class LevelRenderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.Font(None, 24)

    def draw(
        self,
        level: Level,
        bridge: BridgeDesign,
        preview_line: tuple[tuple[int, int], tuple[int, int]] | None,
        selected_anchor: str | None,
        simulation: Any | None = None,
        grid_enabled: bool = False,
        grid_size: int = 40,
    ) -> None:
        self.screen.fill((28, 28, 36))  # Slightly better background color
        
        if grid_enabled:
            self._draw_grid(grid_size)

        # Build a lookup for all point positions
        # Start with level anchors
        points: dict[str, tuple[float, float]] = {
            a.anchor_id: (a.x, a.y) for a in level.anchors
        }
        
        # Add bridge joints (design or simulation)
        if simulation:
            # Update points from simulation bodies
            for j_id in bridge.joints:
                pos = simulation.get_joint_position(j_id)
                if pos:
                    points[j_id] = pos
            # Also update level anchors if they moved (unlikely but consistent)
            for a in level.anchors:
                pos = simulation.get_joint_position(a.anchor_id)
                if pos:
                    points[a.anchor_id] = pos
        else:
            # Use design positions
            points.update(bridge.joints)

        self._draw_banks(level)
        self._draw_edges(bridge, points)
        self._draw_preview(preview_line)
        self._draw_anchors(level, bridge, points, selected_anchor)
        self._draw_hud(level, bridge, simulation_active=simulation is not None, grid_enabled=grid_enabled, grid_size=grid_size)

    def _draw_grid(self, grid_size: int) -> None:
        width, height = self.screen.get_size()
        color = (40, 40, 50)
        
        for x in range(0, width, grid_size):
            pygame.draw.line(self.screen, color, (x, 0), (x, height), 1)
        for y in range(0, height, grid_size):
            pygame.draw.line(self.screen, color, (0, y), (width, y), 1)

    def _draw_banks(self, level: Level) -> None:
        for bank in level.banks:
            pygame.draw.line(
                self.screen,
                (120, 120, 120),
                (bank.x1, bank.y1),
                (bank.x2, bank.y2),
                8,
            )

    def _draw_anchors(
        self, 
        level: Level, 
        bridge: BridgeDesign, 
        points: dict[str, tuple[float, float]], 
        selected_anchor: str | None
    ) -> None:
        # Draw level anchors (fixed vs non-fixed)
        for anchor in level.anchors:
            pos = points.get(anchor.anchor_id)
            if not pos:
                continue
            color = (80, 200, 120) if anchor.fixed else (200, 200, 80)
            pygame.draw.circle(self.screen, color, (int(pos[0]), int(pos[1])), 6)
            
            if anchor.anchor_id == selected_anchor:
                pygame.draw.circle(self.screen, (240, 240, 240), (int(pos[0]), int(pos[1])), 10, 2)

        # Draw bridge joints
        for j_id in bridge.joints:
            pos = points.get(j_id)
            if not pos:
                continue
            color = (200, 200, 200)
            pygame.draw.circle(self.screen, color, (int(pos[0]), int(pos[1])), 4)
             
            if j_id == selected_anchor:
                pygame.draw.circle(self.screen, (240, 240, 240), (int(pos[0]), int(pos[1])), 8, 2)


    def _draw_edges(self, bridge: BridgeDesign, points: dict[str, tuple[float, float]]) -> None:
        for edge in bridge.edges:
            start = points.get(edge.a)
            end = points.get(edge.b)
            if start and end:
                pygame.draw.line(self.screen, (200, 170, 80), start, end, 4)

    def _draw_preview(self, preview_line: tuple[tuple[int, int], tuple[int, int]] | None) -> None:
        if preview_line is None:
            return
        pygame.draw.line(self.screen, (80, 160, 220), preview_line[0], preview_line[1], 2)

    def _draw_hud(
        self, 
        level: Level, 
        bridge: BridgeDesign, 
        simulation_active: bool,
        grid_enabled: bool,
        grid_size: int
    ) -> None:
        budget_text = self.font.render(f"Budget: {level.budget}", True, (220, 220, 220))
        cost_text = self.font.render(f"Cost: {bridge.total_cost()}", True, (220, 220, 220))
        remaining = level.budget - bridge.total_cost()
        remaining_text = self.font.render(f"Remaining: {remaining}", True, (220, 220, 220))
        edges_text = self.font.render(f"Edges: {len(bridge.edges)}", True, (220, 220, 220))
        
        mode_str = "SIMULATION" if simulation_active else "BUILD"
        mode_color = (255, 100, 100) if simulation_active else (100, 255, 100)
        mode_text = self.font.render(f"Mode: {mode_str}", True, mode_color)

        grid_str = f"On ({grid_size}px)" if grid_enabled else "Off"
        grid_text = self.font.render(f"Grid: {grid_str}", True, (150, 150, 180))

        self.screen.blit(budget_text, (20, 20))
        self.screen.blit(cost_text, (20, 44))
        self.screen.blit(remaining_text, (20, 68))
        self.screen.blit(edges_text, (20, 92))
        self.screen.blit(mode_text, (20, 120))
        self.screen.blit(grid_text, (20, 144))

        controls = [
            "Left click: select anchors / add edge",
            "Right click: remove edge",
            "Esc: cancel selection",
            "Space: toggle simulation",
            "G: toggle grid",
            "[ / ]: change grid size"
        ]
        
        # Get width safely
        width, height = self.screen.get_size()
        for index, line in enumerate(controls):
            text = self.font.render(line, True, (180, 180, 180))
            # Align right
            self.screen.blit(text, (width - 320, 20 + index * 20))
