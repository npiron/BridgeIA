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
        preview: tuple[tuple[int, int], tuple[int, int], bool] | None,
        selected_anchor: str | None,
        hovered_edge_id: int | None,
    ) -> None:
        self.screen.fill((18, 18, 24))
        self._draw_banks(level)
        self._draw_edges(level, bridge, hovered_edge_id)
        self._draw_preview(preview)
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
            if selected_anchor == anchor.anchor_id:
                pygame.draw.circle(self.screen, (240, 240, 240), (anchor.x, anchor.y), 12, 2)

    def _draw_edges(self, level: Level, bridge: BridgeDesign, hovered_edge_id: int | None) -> None:
        anchors = {anchor.anchor_id: (anchor.x, anchor.y) for anchor in level.anchors}
        for edge in bridge.edges:
            start = anchors.get(edge.a)
            end = anchors.get(edge.b)
            if start and end:
                color = (240, 210, 120) if edge.edge_id == hovered_edge_id else (200, 170, 80)
                pygame.draw.line(self.screen, color, start, end, 4)

    def _draw_preview(self, preview: tuple[tuple[int, int], tuple[int, int], bool] | None) -> None:
        if preview is None:
            return
        start, end, is_valid = preview
        color = (80, 200, 120) if is_valid else (220, 100, 100)
        pygame.draw.line(self.screen, color, start, end, 2)

    def _draw_hud(self, level: Level, bridge: BridgeDesign) -> None:
        budget_text = self.font.render(f"Budget: {level.budget}", True, (220, 220, 220))
        cost_text = self.font.render(f"Cost: {bridge.total_cost()}", True, (220, 220, 220))
        remaining = level.budget - bridge.total_cost()
        remaining_text = self.font.render(f"Remaining: {remaining}", True, (220, 220, 220))
        self.screen.blit(budget_text, (20, 20))
        self.screen.blit(cost_text, (20, 44))
        self.screen.blit(remaining_text, (20, 68))
