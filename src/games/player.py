"""
player.py - Player Movement, Health & Logic
"""

import pygame
import math
from .constants import (
    TILE_SIZE, PLAYER_SPEED, PLAYER_RADIUS,
    PLAYER_COLOR, PLAYER_OUTLINE,
    WALKABLE_TILES, TILE_EVENTS,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    PLAYER_MAX_HP, ENEMY_DAMAGE_RATE, ENEMY_DAMAGE_AMOUNT,
    VILLAGE_HEAL_AMOUNT, VILLAGE_HEAL_RATE,
    TILE_ENEMY, TILE_VILLAGE
)


class Player:
    def __init__(self, tile_x: int, tile_y: int):
        self.x = float(tile_x * TILE_SIZE + TILE_SIZE // 2)
        self.y = float(tile_y * TILE_SIZE + TILE_SIZE // 2)

        self.tile_x = tile_x
        self.tile_y = tile_y

        self.speed  = PLAYER_SPEED
        self.moving = False
        self.dx     = 0.0
        self.dy     = 0.0

        
        self.hp     = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.alive  = True

        self._damage_timer   = 0
        self._heal_timer     = 0
        self._hp_flash_timer = 0
        self._hp_heal_timer  = 0

       
        self.steps_taken   = 0
        self.tiles_visited = set()
        self.tiles_visited.add((tile_x, tile_y))

        
        self.current_event  = ""
        self.event_timer    = 0
        self.EVENT_DURATION = 180

        
        self.radius    = PLAYER_RADIUS
        self.color     = PLAYER_COLOR
        self.outline   = PLAYER_OUTLINE
        self.bob_timer = 0


    def handle_input(self, keys, tile_map):
        self.dx = 0.0
        self.dy = 0.0

        if keys[pygame.K_w] or keys[pygame.K_UP]:    self.dy = -self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  self.dy =  self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  self.dx = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.dx =  self.speed

        if self.dx != 0 and self.dy != 0:
            self.dx *= 0.707
            self.dy *= 0.707

        self.moving = (self.dx != 0 or self.dy != 0)

        if self.moving:
            self._try_move(tile_map)


    def _try_move(self, tile_map):
        rows = len(tile_map)
        cols = len(tile_map[0])

        # X axis
        new_x  = self.x + self.dx
        ntx    = int(new_x // TILE_SIZE)
        nty    = int(self.y // TILE_SIZE)
        if 0 <= ntx < cols and 0 <= nty < rows:
            if WALKABLE_TILES.get(int(tile_map[nty][ntx]), False):
                self.x = new_x

        # Y axis
        new_y  = self.y + self.dy
        ntx    = int(self.x  // TILE_SIZE)
        nty    = int(new_y   // TILE_SIZE)
        if 0 <= ntx < cols and 0 <= nty < rows:
            if WALKABLE_TILES.get(int(tile_map[nty][ntx]), False):
                self.y = new_y

        old_tx, old_ty  = self.tile_x, self.tile_y
        self.tile_x     = int(self.x // TILE_SIZE)
        self.tile_y     = int(self.y // TILE_SIZE)

        if (self.tile_x, self.tile_y) != (old_tx, old_ty):
            self.steps_taken += 1
            self.tiles_visited.add((self.tile_x, self.tile_y))
            self._check_tile_event(tile_map)


    def _check_tile_event(self, tile_map):
        rows = len(tile_map)
        cols = len(tile_map[0])
        if 0 <= self.tile_y < rows and 0 <= self.tile_x < cols:
            tile_id = int(tile_map[self.tile_y][self.tile_x])
            if tile_id in TILE_EVENTS:
                self.current_event = TILE_EVENTS[tile_id]
                self.event_timer   = self.EVENT_DURATION


    def update_health(self, tile_map):
        
        if not self.alive:
            return

        rows = len(tile_map)
        cols = len(tile_map[0])
        if not (0 <= self.tile_y < rows and 0 <= self.tile_x < cols):
            return

        tile_id = int(tile_map[self.tile_y][self.tile_x])

        
        if tile_id == TILE_ENEMY:
            self._heal_timer = 0          #
            self._damage_timer += 1
            if self._damage_timer >= ENEMY_DAMAGE_RATE:
                self._damage_timer   = 0
                self.hp              = max(0, self.hp - ENEMY_DAMAGE_AMOUNT)
                self._hp_flash_timer = 25
                if self.hp <= 0:
                    self.alive = False


        elif tile_id == TILE_VILLAGE:
            self._damage_timer = 0       
            if self.hp < self.max_hp:    
                self._heal_timer += 1
                if self._heal_timer >= VILLAGE_HEAL_RATE:
                    self._heal_timer    = 0
                    old_hp              = self.hp
                    self.hp             = min(self.max_hp, self.hp + VILLAGE_HEAL_AMOUNT)
                    if self.hp > old_hp:
                        self._hp_heal_timer = 25

        
        else:
            self._damage_timer = 0
            self._heal_timer   = 0

        # Flash timers countdown
        if self._hp_flash_timer > 0: self._hp_flash_timer -= 1
        if self._hp_heal_timer  > 0: self._hp_heal_timer  -= 1


    def update(self):
        self.bob_timer += 0.1
        if not self.moving:
            self.bob_timer = 0

        if self.event_timer > 0:
            self.event_timer -= 1
        else:
            self.current_event = ""


    def draw(self, surface, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        bob      = int(math.sin(self.bob_timer) * 2) if self.moving else 0
        screen_y += bob

        if not (0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT):
            return

        pygame.draw.circle(surface, self.outline, (screen_x, screen_y), self.radius + 3)
        pygame.draw.circle(surface, self.color,   (screen_x, screen_y), self.radius)
        pygame.draw.circle(surface, self.outline, (screen_x, screen_y), 3)


    def get_stats(self) -> dict:
        return {
            "position":      (self.tile_x, self.tile_y),
            "steps":         self.steps_taken,
            "tiles_visited": len(self.tiles_visited),
            "event":         self.current_event,
            "event_active":  self.event_timer > 0,
            "hp":            self.hp,
            "max_hp":        self.max_hp,
            "hp_flash":      self._hp_flash_timer > 0,
            "hp_heal":       self._hp_heal_timer  > 0,
            "alive":         self.alive,
        }


    def find_spawn(tile_map) -> tuple:
        rows = len(tile_map)
        cols = len(tile_map[0])
        for y in range(rows // 4, rows * 3 // 4):
            for x in range(cols // 4, cols * 3 // 4):
                if int(tile_map[y][x]) == 2:
                    return (x, y)
        for y in range(rows):
            for x in range(cols):
                if WALKABLE_TILES.get(int(tile_map[y][x]), False):
                    return (x, y)
        return (cols // 2, rows // 2)