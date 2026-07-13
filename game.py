"""
game.py - Main Game 
"""

import pygame
import sys
import os
import math
import random
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))
sys.path.insert(0, BASE_DIR)

from noise import generate_terrain_features
from classifier   import load_model, classify_world
from placer       import place_villages, place_enemy_zones, apply_placements

from games.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    TILE_SIZE, TILE_COLORS, TILE_COLORS_DARK,
    WORLD_WIDTH, WORLD_HEIGHT, WORLD_SEED,
    COLOR_DARK, COLOR_BLACK, WALKABLE_TILES,
    TILE_VILLAGE, TILE_ENEMY,
    WATER_ANIM_FRAMES, WATER_ANIM_SPEED
)
from games.player import Player
from games.camera import Camera
from games.fog    import FogOfWar
from games.hud    import HUD

STATE_START   = "start"
STATE_LOADING = "loading"
STATE_PLAYING = "playing"
STATE_QUIT    = "quit_dialog"
STATE_WIN     = "win"
STATE_LOSS    = "loss"

TILE_SPRITE_FILES = {
    0:  "assets/tiles/water.png",
    1:  "assets/tiles/beach.png",
    2:  "assets/tiles/plains.png",
    3:  "assets/tiles/forest.png",
    4:  "assets/tiles/mountain.png",
    5:  "assets/tiles/snow.png",
    10: "assets/tiles/village.png",
    11: "assets/tiles/enemy.png",
}
PLAYER_SPRITE_FILE = "assets/player/player.png"
MUSIC_FILE         = "assets/audio/music.mp3"


class Game:
    def __init__(self, world_w=WORLD_WIDTH, world_h=WORLD_HEIGHT):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption(TITLE)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock  = pygame.time.Clock()

        self.world_w = world_w
        self.world_h = world_h
        self.seed    = WORLD_SEED  

        self.state        = STATE_START
        self.running      = True
        self.show_minimap = True

        self.tile_map  = None
        self.player    = None
        self.camera    = None
        self.fog       = None
        self.hud       = HUD()

        self.tile_surfaces      = {}
        self.tile_surfaces_dark = {}
        self.player_sprite      = None

        self.water_frames      = []
        self.water_frames_dark = []
        self.water_frame_idx   = 0
        self.water_frame_timer = 0

        self._build_tile_surfaces()
        self._build_water_animation()
        self._load_player_sprite()
        self._start_music()

        self._last_tile_id   = -1
        self._villages_list  = []
        self._found_villages = set()
        self._total_villages = 4


    def _start_music(self):
        
        music_path = os.path.join(BASE_DIR, MUSIC_FILE)
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)  


    def _load_sprite(self, path, size=TILE_SIZE):
        full = os.path.join(BASE_DIR, path)
        if os.path.exists(full):
            img = pygame.image.load(full).convert_alpha()
            return pygame.transform.scale(img, (size, size))
        return None


    def _make_fallback(self, tile_id, dark=False):
        colors = TILE_COLORS_DARK if dark else TILE_COLORS
        color  = colors.get(tile_id, (80, 80, 80))
        surf   = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill(color)
        border = tuple(max(0, c - 30) for c in color)
        pygame.draw.rect(surf, border, (0, 0, TILE_SIZE, TILE_SIZE), 1)
        return surf


    def _build_tile_surfaces(self):
        for tile_id in TILE_COLORS.keys():
            sprite = self._load_sprite(TILE_SPRITE_FILES.get(tile_id, ""))
            self.tile_surfaces[tile_id] = sprite if sprite else self._make_fallback(tile_id)
            dark = self.tile_surfaces[tile_id].copy()
            ov   = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 130))
            dark.blit(ov, (0, 0))
            self.tile_surfaces_dark[tile_id] = dark


    def _build_water_animation(self):
        base = self._load_sprite(TILE_SPRITE_FILES.get(0, ""))
        for i in range(WATER_ANIM_FRAMES):
            frame = pygame.Surface((TILE_SIZE, TILE_SIZE)).convert()
            if base:
                frame.blit(base, (0, 0))
            else:
                frame.fill((59, 130, 246))
            offset = i * 8
            for wy in [(offset) % TILE_SIZE, (offset + 16) % TILE_SIZE]:
                pygame.draw.line(frame, (120, 180, 255), (2, wy), (TILE_SIZE-2, wy), 1)
            self.water_frames.append(frame)

            dark2 = pygame.Surface((TILE_SIZE, TILE_SIZE)).convert()
            dark2.blit(frame, (0, 0))
            dark_ov = pygame.Surface((TILE_SIZE, TILE_SIZE)).convert()
            dark_ov.fill((40, 40, 40))
            dark2.blit(dark_ov, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
            self.water_frames_dark.append(dark2)


    def _load_player_sprite(self):
        self.player_sprite = self._load_sprite(PLAYER_SPRITE_FILE, TILE_SIZE)


    def _draw_loading(self, message):
        self.screen.fill(COLOR_DARK)
        f1 = pygame.font.SysFont("Segoe UI", 32, bold=True)
        f2 = pygame.font.SysFont("Segoe UI", 16)
        t1 = f1.render("AI WORLD EXPLORER", True, (125, 211, 252))
        t2 = f2.render(message, True, (148, 163, 184))

      
        f3 = pygame.font.SysFont("Segoe UI", 14)
        t3 = f3.render(f"Seed: {self.seed}", True, (51, 65, 85))

        self.screen.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, SCREEN_HEIGHT//2 + 10))
        self.screen.blit(t3, (SCREEN_WIDTH//2 - t3.get_width()//2, SCREEN_HEIGHT//2 + 35))
        pygame.display.flip()


    def load_world(self, seed=None):
        if seed is None:
            seed = random.randint(1, 99999)
        self.seed  = seed
        self.state = STATE_LOADING

        steps = [
            ("Loading AI model...",   self._step_model),
            ("Generating terrain...", self._step_terrain),
            ("Classifying tiles...",  self._step_classify),
            ("Placing villages...",   self._step_place),
            ("Setting up game...",    self._step_setup),
        ]
        for msg, fn in steps:
            self._draw_loading(msg)
            fn()

        self.hud._anim_timer = 0
        self.state = STATE_PLAYING

    def _step_model(self):
        self.model = load_model(os.path.join(BASE_DIR, "models", "tile_classifier.pkl"))

    def _step_terrain(self):
        self.features = generate_terrain_features(
            width=self.world_w, height=self.world_h, seed=self.seed
        )

    def _step_classify(self):
        self.tile_map = classify_world(self.features, self.model)

    def _step_place(self):
        self._villages_list = place_villages(
            self.tile_map, self.features["heightmap"],
            num_villages=self._total_villages, seed=self.seed
        )
        enemy_zones   = place_enemy_zones(
            self.tile_map, self._villages_list, num_enemies=6, seed=self.seed
        )
        self.tile_map = apply_placements(
            self.tile_map, self._villages_list, enemy_zones
        )

    def _step_setup(self):
        spawn_x, spawn_y     = Player.find_spawn(self.tile_map)
        self.player          = Player(spawn_x, spawn_y)
        self.camera          = Camera(self.world_w, self.world_h)
        self.fog             = FogOfWar(self.world_w, self.world_h)
        self.hud             = HUD()
        self._found_villages = set()
        self._last_tile_id   = -1
        self.camera.snap_to(self.player.x, self.player.y)
        self.fog.update(self.player.tile_x, self.player.tile_y)


    def _check_win(self):
        if len(self._found_villages) >= self._total_villages:
            self.state = STATE_WIN

    def _check_loss(self):
        if not self.player.alive:
            self.state = STATE_LOSS


    def _check_tile_events(self):
        if not self.player or self.tile_map is None:
            return
        tx, ty = self.player.tile_x, self.player.tile_y
        rows   = len(self.tile_map)
        cols   = len(self.tile_map[0])
        if not (0 <= ty < rows and 0 <= tx < cols):
            return
        tile_id = int(self.tile_map[ty][tx])
        if tile_id != self._last_tile_id:
            self._last_tile_id = tile_id
            if tile_id == TILE_VILLAGE:
                self.hud.trigger_village_popup("Castle🫅 Safe zone.")
                self._found_villages.add((tx, ty))
            elif tile_id == TILE_ENEMY:
                self.hud.trigger_enemy_flash()


    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            #  Start Screen 
            if self.state == STATE_START:
                # Seed input active ho to keyboard handle karo
                if self.hud.seed_input_active:
                    seed = self.hud.handle_seed_input(event)
                    if seed is not None:
                        self.load_world(seed=seed)
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        b1_hover, b2_hover = self.hud.draw_start_screen(
                            self.screen, mouse_pos
                        )
                        if b1_hover:   # Random Map
                            self.load_world(seed=random.randint(1, 99999))
                        elif b2_hover: # Custom Seed
                            self.hud.seed_input_active = True
                            self.hud.seed_input_text   = ""

            #  Playing 
            elif self.state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.state = STATE_QUIT
                    if event.key == pygame.K_m:      self.show_minimap = not self.show_minimap
                    if event.key == pygame.K_r:      self.load_world()

            #  Quit Dialog 
            elif self.state == STATE_QUIT:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_PLAYING
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    yes_h, no_h = self.hud.draw_quit_dialog(self.screen, mouse_pos)
                    if yes_h:  self.running = False
                    elif no_h: self.state = STATE_PLAYING

            #  Win / Loss 
            elif self.state in (STATE_WIN, STATE_LOSS):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pw, ph = 600, 380
                    px_    = SCREEN_WIDTH//2  - pw//2
                    py_    = SCREEN_HEIGHT//2 - ph//2
                    btn_y  = py_ + ph - 65
                    b1x    = px_ + pw//2 - 175
                    b2x    = px_ + pw//2 + 15
                    mx, my = mouse_pos
                    if b1x <= mx <= b1x + 160 and btn_y <= my <= btn_y + 44:
                        self.load_world()   # Random new world
                    elif b2x <= mx <= b2x + 160 and btn_y <= my <= btn_y + 44:
                        self.running = False


    def update(self):
        if self.state != STATE_PLAYING:
            return

        self.water_frame_timer += 1
        if self.water_frame_timer >= WATER_ANIM_SPEED:
            self.water_frame_timer = 0
            self.water_frame_idx   = (self.water_frame_idx + 1) % WATER_ANIM_FRAMES

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, self.tile_map)
        self.player.update()
        self.player.update_health(self.tile_map)
        self.camera.update(self.player.x, self.player.y)
        self.fog.update(self.player.tile_x, self.player.tile_y)
        self._check_tile_events()
        self._check_win()
        self._check_loss()


    def draw_world(self):
        start_x, start_y, end_x, end_y = self.camera.get_visible_tile_range()
        rows    = len(self.tile_map)
        cols    = len(self.tile_map[0])
        fog_map = self.fog.fog_map

        w_frame      = self.water_frames[self.water_frame_idx]
        w_frame_dark = self.water_frames_dark[self.water_frame_idx]
        default      = self.tile_surfaces.get(2)
        default_dark = self.tile_surfaces_dark.get(2)

        for ty in range(start_y, end_y):
            for tx in range(start_x, end_x):
                if not (0 <= ty < rows and 0 <= tx < cols):
                    continue
                fog_state = fog_map[ty][tx]
                if fog_state == 0:
                    continue

                tile_id  = int(self.tile_map[ty][tx])
                screen_x = tx * TILE_SIZE - self.camera.offset_x
                screen_y = ty * TILE_SIZE - self.camera.offset_y

                if tile_id == 0:
                    surf = w_frame if fog_state == 2 else w_frame_dark
                elif fog_state == 2:
                    surf = self.tile_surfaces.get(tile_id, default)
                else:
                    surf = self.tile_surfaces_dark.get(tile_id, default_dark)

                self.screen.blit(surf, (screen_x, screen_y))


    def draw_player(self):
        sx = int(self.player.x - self.camera.offset_x)
        sy = int(self.player.y - self.camera.offset_y)
        if self.player_sprite:
            rect = self.player_sprite.get_rect(center=(sx, sy))
            self.screen.blit(self.player_sprite, rect)
        else:
            self.player.draw(self.screen, self.camera.offset_x, self.camera.offset_y)


    def draw(self):
        mouse_pos = pygame.mouse.get_pos()

       
        if self.state == STATE_START:
            self.hud.draw_start_screen(self.screen, mouse_pos)
            pygame.display.flip()
            return

        if self.state == STATE_LOADING:
            pygame.display.flip()
            return

        self.screen.fill(COLOR_BLACK)
        self.draw_world()
        self.draw_player()
        self.fog.draw(self.screen, self.camera.offset_x, self.camera.offset_y)

        tile_id = int(self.tile_map[self.player.tile_y][self.player.tile_x])
        self.hud.draw(
            self.screen, self.tile_map, self.fog,
            self.player.get_stats(),
            self.fog.get_stats(),
            tile_id, self.show_minimap,
            found_villages = len(self._found_villages),
            total_villages = self._total_villages,
            seed           = self.seed,
        )

        fps  = int(self.clock.get_fps())
        font = pygame.font.SysFont("Segoe UI", 12)
        self.screen.blit(
            font.render(f"FPS: {fps}", True, (100, 100, 100)),
            (SCREEN_WIDTH - 70, 10)
        )

        if self.state == STATE_QUIT:
            self.hud.draw_quit_dialog(self.screen, mouse_pos)
        elif self.state == STATE_WIN:
            self.hud.draw_win_screen(
                self.screen, self.player.get_stats(),
                self.fog.get_stats(), mouse_pos, self._total_villages
            )
        elif self.state == STATE_LOSS:
            self.hud.draw_loss_screen(
                self.screen, self.player.get_stats(),
                self.fog.get_stats(), mouse_pos,
                self._total_villages, len(self._found_villages)
            )

        pygame.display.flip()


    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--width",  type=int, default=80)
    parser.add_argument("--height", type=int, default=50)
    args = parser.parse_args()
    Game(world_w=args.width, world_h=args.height).run()