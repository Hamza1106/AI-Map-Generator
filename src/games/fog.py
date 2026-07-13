"""
fog.py - Fog of War System 
3 states: Hidden, Visited, Visible
"""

import numpy as np
import pygame
from .constants import (
    TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT,
    FOG_RADIUS, FOG_REVEAL_RADIUS,
    SCREEN_WIDTH, SCREEN_HEIGHT
)

FOG_HIDDEN  = 0
FOG_VISITED = 1
FOG_VISIBLE = 2


class FogOfWar:
    def __init__(self, world_width: int, world_height: int):
        self.width  = world_width
        self.height = world_height

        self.fog_map = np.zeros((world_height, world_width), dtype=np.uint8)

    
        self._visible_mask = self._make_circle_mask(FOG_RADIUS)
        self._reveal_mask  = self._make_circle_mask(FOG_REVEAL_RADIUS)

       
        self.fog_surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        self._dirty = True   # Pehli baar full draw karna hoga

        # Last player position track karo
        self._last_px = -1
        self._last_py = -1


    def _make_circle_mask(self, radius: int) -> list:
        mask = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx*dx + dy*dy <= radius*radius:
                    mask.append((dx, dy))
        return mask


    def update(self, player_tile_x: int, player_tile_y: int):
        """
        Fog update — When player moves to a new tile:
        """
      
        if (player_tile_x == self._last_px and
                player_tile_y == self._last_py):
            return

        self._last_px = player_tile_x
        self._last_py = player_tile_y
        self._dirty   = True

      
        self.fog_map[self.fog_map == FOG_VISIBLE] = FOG_VISITED

       
        for dx, dy in self._visible_mask:
            nx = player_tile_x + dx
            ny = player_tile_y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                self.fog_map[ny][nx] = FOG_VISIBLE

        
        for dx, dy in self._reveal_mask:
            nx = player_tile_x + dx
            ny = player_tile_y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if self.fog_map[ny][nx] == FOG_HIDDEN:
                    self.fog_map[ny][nx] = FOG_VISITED


    def draw(self, surface, camera_x: int, camera_y: int):
      
        # Visible tile range
        start_x = max(0, int(camera_x // TILE_SIZE))
        start_y = max(0, int(camera_y // TILE_SIZE))
        end_x   = min(self.width,  start_x + (SCREEN_WIDTH  // TILE_SIZE) + 2)
        end_y   = min(self.height, start_y + (SCREEN_HEIGHT // TILE_SIZE) + 2)

        
        self.fog_surface.fill((0, 0, 0, 0))

        
        fog_slice = self.fog_map[start_y:end_y, start_x:end_x]

        # Hidden tiles (state == 0)
        hidden_ys, hidden_xs = np.where(fog_slice == FOG_HIDDEN)
        for i in range(len(hidden_ys)):
            tx = (hidden_xs[i] + start_x) * TILE_SIZE - int(camera_x)
            ty = (hidden_ys[i] + start_y) * TILE_SIZE - int(camera_y)
            pygame.draw.rect(self.fog_surface, (0, 0, 0, 255),
                             (tx, ty, TILE_SIZE, TILE_SIZE))

        # Visited tiles (state == 1)
        visited_ys, visited_xs = np.where(fog_slice == FOG_VISITED)
        for i in range(len(visited_ys)):
            tx = (visited_xs[i] + start_x) * TILE_SIZE - int(camera_x)
            ty = (visited_ys[i] + start_y) * TILE_SIZE - int(camera_y)
            pygame.draw.rect(self.fog_surface, (0, 0, 0, 160),
                             (tx, ty, TILE_SIZE, TILE_SIZE))

        surface.blit(self.fog_surface, (0, 0))


    def is_visible(self, tile_x: int, tile_y: int) -> bool:
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.fog_map[tile_y][tile_x] == FOG_VISIBLE
        return False

    def is_revealed(self, tile_x: int, tile_y: int) -> bool:
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            return self.fog_map[tile_y][tile_x] != FOG_HIDDEN
        return False

    def get_exploration_percent(self) -> float:
        total    = self.width * self.height
        revealed = np.sum(self.fog_map != FOG_HIDDEN)
        return round((revealed / total) * 100, 1)

    def get_stats(self) -> dict:
        total   = self.width * self.height
        hidden  = int(np.sum(self.fog_map == FOG_HIDDEN))
        visited = int(np.sum(self.fog_map == FOG_VISITED))
        visible = int(np.sum(self.fog_map == FOG_VISIBLE))
        return {
            "total":        total,
            "hidden":       hidden,
            "visited":      visited,
            "visible":      visible,
            "explored_pct": self.get_exploration_percent()
        }
