from __future__ import annotations

import pygame

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
    ) -> None:
        self.screen.fill((18, 18, 24))
        self._draw_banks(level)
        self._draw_edges(level, bridge)
        self._draw_preview(preview_line)
        self._draw_anchors(level, selected_anchor)
        self._draw_hud(level, bridge)

    def _draw_banks(self, level: Level) -> None:
        for bank in level.banks:
            pygame.draw.line(
                self.screen,
                (120, 120, 120),
                (bank.x1, bank.y1),
                (bank.x2, bank.y2),
                8,
            )

    def _draw_anchors(self, level: Level, selected_anchor: str | None) -> None:
        for anchor in level.anchors:
            color = (80, 200, 120) if anchor.fixed else (200, 200, 80)
            pygame.draw.circle(self.screen, color, (anchor.x, anchor.y), 8)
            if anchor.anchor_id == selected_anchor:
                pygame.draw.circle(self.screen, (240, 240, 240), (anchor.x, anchor.y), 12, 2)

    def _draw_edges(self, level: Level, bridge: BridgeDesign) -> None:
        anchors = {anchor.anchor_id: (anchor.x, anchor.y) for anchor in level.anchors}
        for edge in bridge.edges:
            start = anchors.get(edge.a)
            end = anchors.get(edge.b)
            if start and end:
                pygame.draw.line(self.screen, (200, 170, 80), start, end, 4)

    def _draw_preview(self, preview_line: tuple[tuple[int, int], tuple[int, int]] | None) -> None:
        if preview_line is None:
            return
        pygame.draw.line(self.screen, (80, 160, 220), preview_line[0], preview_line[1], 2)

    def _draw_hud(self, level: Level, bridge: BridgeDesign) -> None:
        budget_text = self.font.render(f"Budget: {level.budget}", True, (220, 220, 220))
        cost_text = self.font.render(f"Cost: {bridge.total_cost()}", True, (220, 220, 220))
        remaining = level.budget - bridge.total_cost()
        remaining_text = self.font.render(f"Remaining: {remaining}", True, (220, 220, 220))
        edges_text = self.font.render(f"Edges: {len(bridge.edges)}", True, (220, 220, 220))
        self.screen.blit(budget_text, (20, 20))
        self.screen.blit(cost_text, (20, 44))
        self.screen.blit(remaining_text, (20, 68))
        self.screen.blit(edges_text, (20, 92))

        controls = [
            "Left click: select anchors / add edge",
            "Right click: remove edge",
            "Esc: cancel selection",
        ]
        for index, line in enumerate(controls):
            text = self.font.render(line, True, (180, 180, 180))
            self.screen.blit(text, (20, 540 + index * 22))
