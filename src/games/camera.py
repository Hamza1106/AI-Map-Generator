"""
camera.py - Camera System
"""

from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT
)


class Camera:
    def __init__(self, world_width: int, world_height: int):
        """
        Initial camera position 
        world_width, world_height = In tiles
        """
        
        # Camera position ( in pixels) 
        
        self.x = 0.0
        self.y = 0.0

        
        self.world_pixel_w = world_width  * TILE_SIZE
        self.world_pixel_h = world_height * TILE_SIZE

       
        self.smoothness = 0.12

    def update(self, player_x: float, player_y: float):
        """
        Move the camera at the center of the player smoothly.
        player_x, player_y = pixel position of player
        """

        target_x = player_x - SCREEN_WIDTH  // 2
        target_y = player_y - SCREEN_HEIGHT // 2

       
        self.x += (target_x - self.x) * self.smoothness
        self.y += (target_y - self.y) * self.smoothness

       
        self._clamp()

    def _clamp(self):
        """
        World bound (Do not go beyond world edges)
        """
        # Left/Top boundary
        self.x = max(0, self.x)
        self.y = max(0, self.y)

        # Right/Bottom boundary
        max_x = self.world_pixel_w - SCREEN_WIDTH
        max_y = self.world_pixel_h - SCREEN_HEIGHT

        self.x = min(self.x, max(0, max_x))
        self.y = min(self.y, max(0, max_y))

    def apply(self, world_x: float, world_y: float) -> tuple:
        """
       Convert world coordinates (in pixels) to screen coordinates
        
        Example:
            tile (5, 3) In world
            camera (100, 80) pe hai
            screen position = (5*32 - 100, 3*32 - 80) = (60, 16)
        """
        return (
            int(world_x - self.x),
            int(world_y - self.y)
        )

    def apply_tile(self, tile_x: int, tile_y: int) -> tuple:
        """
        Convert tile coordinates (in tiles) to screen coordinates.
        """
        world_x = tile_x * TILE_SIZE
        world_y = tile_y * TILE_SIZE
        return self.apply(world_x, world_y)

    def is_visible(self, world_x: float, world_y: float,
                   width: int = TILE_SIZE, height: int = TILE_SIZE) -> bool:
       
        screen_x, screen_y = self.apply(world_x, world_y)

        return (
            screen_x + width  > 0 and
            screen_x          < SCREEN_WIDTH and
            screen_y + height > 0 and
            screen_y          < SCREEN_HEIGHT
        )

    def get_visible_tile_range(self) -> tuple:
        """
        Only visible tiles on screen(Optimization)
        """
        start_x = max(0, int(self.x // TILE_SIZE))
        start_y = max(0, int(self.y // TILE_SIZE))

        end_x = min(WORLD_WIDTH,  start_x + (SCREEN_WIDTH  // TILE_SIZE) + 2)
        end_y = min(WORLD_HEIGHT, start_y + (SCREEN_HEIGHT // TILE_SIZE) + 2)

        return (start_x, start_y, end_x, end_y)

    def snap_to(self, player_x: float, player_y: float):
       
        self.x = player_x - SCREEN_WIDTH  // 2
        self.y = player_y - SCREEN_HEIGHT // 2
        self._clamp()

    @property
    def offset_x(self) -> int:
        return int(self.x)

    @property
    def offset_y(self) -> int:
        return int(self.y)