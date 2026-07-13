"""
hud.py - HUD, Health Bar, Win/Loss Screens
"""

import pygame
import math
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    TILE_COLORS, TILE_NAMES,
    MINIMAP_WIDTH, MINIMAP_HEIGHT, MINIMAP_X, MINIMAP_Y,
    COLOR_DARK, COLOR_PANEL, COLOR_BORDER,
    COLOR_ACCENT, COLOR_WHITE, COLOR_BLACK,
    COLOR_GREEN, COLOR_RED, COLOR_YELLOW,
    COLOR_PURPLE, COLOR_ORANGE,
)


class HUD:
    def __init__(self):
        pygame.font.init()

        self.font_large  = pygame.font.SysFont("Segoe UI", 18, bold=True)
        self.font_medium = pygame.font.SysFont("Segoe UI", 14)
        self.font_small  = pygame.font.SysFont("Segoe UI", 12)
        self.font_title  = pygame.font.SysFont("Segoe UI", 48, bold=True)
        self.font_huge   = pygame.font.SysFont("Segoe UI", 72, bold=True)
        self.font_btn    = pygame.font.SysFont("Segoe UI", 22, bold=True)

        self.minimap_surface = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT))

        self.popup_msg      = ""
        self.popup_timer    = 0
        self.POPUP_DURATION = 180

        self.flash_timer    = 0
        self.FLASH_DURATION = 40
        self.flash_surface  = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )

        self.controls_timer = 300
        self._anim_timer    = 0

        # Seed input state
        self.seed_input_active = False
        self.seed_input_text   = ""


    def trigger_village_popup(self, msg):
        self.popup_msg   = msg
        self.popup_timer = self.POPUP_DURATION

    def trigger_enemy_flash(self):
        self.flash_timer = self.FLASH_DURATION


    def _draw_panel(self, surface, x, y, w, h, alpha=200, color=(30, 41, 59)):
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((*color, alpha))
        surface.blit(panel, (x, y))
        pygame.draw.rect(surface, COLOR_BORDER, (x, y, w, h), 1)


    # Start Screen 
    def draw_start_screen(self, surface, mouse_pos):
        """
        Returns: ('random', None) | ('custom', seed_str) | None
        """
        surface.fill(COLOR_DARK)

        t = pygame.time.get_ticks() / 1000
        for x in range(0, SCREEN_WIDTH, 32):
            pygame.draw.line(surface, (20, 30, 50), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 32):
            pygame.draw.line(surface, (20, 30, 50), (0, y), (SCREEN_WIDTH, y), 1)

        # Title
        title = self.font_huge.render("AI WORLD", True, COLOR_ACCENT)
        sub   = self.font_title.render("EXPLORER", True, COLOR_WHITE)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 200))
        surface.blit(sub,   (SCREEN_WIDTH//2 - sub.get_width()//2,   SCREEN_HEIGHT//2 - 125))

        tag = self.font_medium.render(
            "Procedurally Generated World  •  Powered by Random Forest ML",
            True, (71, 85, 105)
        )
        surface.blit(tag, (SCREEN_WIDTH//2 - tag.get_width()//2, SCREEN_HEIGHT//2 - 65))

        mx, my = mouse_pos

        #Random Game Button
        b1w, b1h = 220, 55
        b1x = SCREEN_WIDTH//2 - b1w - 15
        b1y = SCREEN_HEIGHT//2 - 15
        b1_hover = (b1x <= mx <= b1x + b1w and b1y <= my <= b1y + b1h)
        pygame.draw.rect(surface,
                         (56, 189, 248) if b1_hover else (14, 165, 233),
                         (b1x, b1y, b1w, b1h), border_radius=12)
        pygame.draw.rect(surface, COLOR_WHITE, (b1x, b1y, b1w, b1h), 2, border_radius=12)
        t1 = self.font_btn.render("🎲  Random Map", True, COLOR_WHITE)
        surface.blit(t1, (b1x + b1w//2 - t1.get_width()//2,
                           b1y + b1h//2 - t1.get_height()//2))

        #  Custom Seed Button 
        b2w, b2h = 220, 55
        b2x = SCREEN_WIDTH//2 + 15
        b2y = SCREEN_HEIGHT//2 - 15
        b2_hover = (b2x <= mx <= b2x + b2w and b2y <= my <= b2y + b2h)
        pygame.draw.rect(surface,
                         (52, 211, 153) if b2_hover else (16, 185, 129),
                         (b2x, b2y, b2w, b2h), border_radius=12)
        pygame.draw.rect(surface, COLOR_WHITE, (b2x, b2y, b2w, b2h), 2, border_radius=12)
        t2 = self.font_btn.render("🔢  Custom Seed", True, COLOR_WHITE)
        surface.blit(t2, (b2x + b2w//2 - t2.get_width()//2,
                           b2y + b2h//2 - t2.get_height()//2))

        # Seed Input Box 
        if self.seed_input_active:
            inp_w, inp_h = 300, 44
            inp_x = SCREEN_WIDTH//2 - inp_w//2
            inp_y = SCREEN_HEIGHT//2 + 60

            # Input box
            pygame.draw.rect(surface, (30, 41, 59),
                             (inp_x, inp_y, inp_w, inp_h), border_radius=8)
            pygame.draw.rect(surface, COLOR_ACCENT,
                             (inp_x, inp_y, inp_w, inp_h), 2, border_radius=8)

            # Input text
            display_text = self.seed_input_text if self.seed_input_text else "Enter seed number..."
            color = COLOR_WHITE if self.seed_input_text else (71, 85, 105)
            t_surf = self.font_btn.render(display_text, True, color)
            surface.blit(t_surf, (inp_x + 12, inp_y + inp_h//2 - t_surf.get_height()//2))

            # Cursor blink
            if int(pygame.time.get_ticks() / 500) % 2 == 0 and self.seed_input_text:
                cx = inp_x + 12 + t_surf.get_width() + 2
                pygame.draw.line(surface, COLOR_WHITE,
                                 (cx, inp_y + 8), (cx, inp_y + inp_h - 8), 2)

            # Hint
            hint = self.font_small.render("Press ENTER to start  •  ESC to cancel",
                                           True, (71, 85, 105))
            surface.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, inp_y + inp_h + 8))

        # Hint boxes 
        hints = [
            ("🌍", "AI Generated", "Unique worlds"),
            ("⚔️",  "Explore",      "Fog of war"),
            ("🏘️", "Discover",     "Find Castles"),
            ("❤️",  "Survive",      "Avoid enemies"),
        ]
        box_w   = 135
        total_w = len(hints) * box_w + (len(hints)-1) * 10
        sbx     = SCREEN_WIDTH//2 - total_w//2
        by_off  = SCREEN_HEIGHT//2 + (130 if self.seed_input_active else 80)

        for i, (icon, title_h, desc) in enumerate(hints):
            bx = sbx + i * (box_w + 10)
            self._draw_panel(surface, bx, by_off, box_w, 70, alpha=150)
            ic = self.font_large.render(icon,    True, COLOR_ACCENT)
            ti = self.font_small.render(title_h, True, COLOR_WHITE)
            de = self.font_small.render(desc,    True, (100, 116, 139))
            surface.blit(ic, (bx + box_w//2 - ic.get_width()//2, by_off + 6))
            surface.blit(ti, (bx + box_w//2 - ti.get_width()//2, by_off + 30))
            surface.blit(de, (bx + box_w//2 - de.get_width()//2, by_off + 48))

        ct = self.font_small.render(
            "WASD — Move    •    M — Minimap    •    ESC — Quit",
            True, (51, 65, 85)
        )
        surface.blit(ct, (SCREEN_WIDTH//2 - ct.get_width()//2, SCREEN_HEIGHT - 30))

        return b1_hover, b2_hover


    def handle_seed_input(self, event):
        """
        For Seed input handle keyboard events.
        Returns: seed (int) if press Enter 
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.seed_input_text:
                    try:
                        seed = int(self.seed_input_text)
                        self.seed_input_active = False
                        self.seed_input_text   = ""
                        return seed
                    except ValueError:
                        self.seed_input_text = ""
            elif event.key == pygame.K_ESCAPE:
                self.seed_input_active = False
                self.seed_input_text   = ""
            elif event.key == pygame.K_BACKSPACE:
                self.seed_input_text = self.seed_input_text[:-1]
            else:
                if event.unicode.isdigit() and len(self.seed_input_text) < 6:
                    self.seed_input_text += event.unicode
        return None


    # Health Bar
    def draw_health_bar(self, surface, hp, max_hp, hp_flash, hp_heal):
        bx, by, bw, bh = 10, 170, 220, 20
        self._draw_panel(surface, bx, by, bw, bh + 4, alpha=180)

        hp_pct = hp / max_hp
        fw     = max(0, int((bw - 4) * hp_pct))

        if hp_pct > 0.6:   bar_color = COLOR_GREEN
        elif hp_pct > 0.3: bar_color = COLOR_YELLOW
        else:              bar_color = COLOR_RED

        if hp_flash:  bar_color = (255, 255, 255)
        elif hp_heal: bar_color = (100, 255, 150)

        if fw > 0:
            pygame.draw.rect(surface, bar_color, (bx + 2, by + 2, fw, bh))

        t = self.font_small.render(f"♥  {hp} / {max_hp}", True, COLOR_WHITE)
        surface.blit(t, (bx + 6, by + 3))


    #  Win Screen
    def draw_win_screen(self, surface, player_stats, fog_stats, mouse_pos, total_villages):
        self._anim_timer += 1
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        for i in range(30):
            t  = self._anim_timer * 0.05 + i * 0.7
            px = int(SCREEN_WIDTH//2  + math.cos(t) * (100 + i * 15))
            py = int(SCREEN_HEIGHT//2 + math.sin(t) * (60  + i * 8))
            r  = max(1, int(3 + math.sin(t * 2) * 2))
            c  = [COLOR_YELLOW, COLOR_GREEN, COLOR_ACCENT][i % 3]
            pygame.draw.circle(surface, c, (px, py), r)

        pw, ph = 600, 380
        px_ = SCREEN_WIDTH//2  - pw//2
        py_ = SCREEN_HEIGHT//2 - ph//2
        self._draw_panel(surface, px_, py_, pw, ph, alpha=230, color=(10, 30, 20))
        pygame.draw.rect(surface, COLOR_GREEN, (px_, py_, pw, ph), 3, border_radius=16)

        trophy = self.font_huge.render("🏆", True, COLOR_YELLOW)
        title  = self.font_huge.render("YOU WIN!", True, COLOR_GREEN)
        surface.blit(trophy, (SCREEN_WIDTH//2 - trophy.get_width()//2, py_ + 20))
        surface.blit(title,  (SCREEN_WIDTH//2 - title.get_width()//2,  py_ + 90))

        sub = self.font_large.render(
            f"All {total_villages} Castles discovered!", True, COLOR_WHITE
        )
        surface.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, py_ + 165))

        stats = [
            ("Steps Taken",    str(player_stats['steps'])),
            ("Tiles Explored", f"{fog_stats['explored_pct']}%"),
            ("HP Remaining",   f"{player_stats['hp']} / {player_stats['max_hp']}"),
        ]
        for i, (label, val) in enumerate(stats):
            sy = py_ + 210 + i * 28
            surface.blit(self.font_medium.render(f"{label}:", True, (100, 116, 139)), (px_ + 60, sy))
            surface.blit(self.font_medium.render(val, True, COLOR_WHITE), (px_ + 260, sy))

        self._draw_action_buttons(surface, mouse_pos, py_ + ph - 65, pw, px_)


    # Loss Screen 
    def draw_loss_screen(self, surface, player_stats, fog_stats, mouse_pos,
                         total_villages, found_villages):
        self._anim_timer += 1
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        pulse = int(128 + 80 * abs(math.sin(self._anim_timer * 0.05)))
        bs    = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(bs, (200, 0, 0, pulse), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 20)
        surface.blit(bs, (0, 0))

        pw, ph = 600, 380
        px_ = SCREEN_WIDTH//2  - pw//2
        py_ = SCREEN_HEIGHT//2 - ph//2
        self._draw_panel(surface, px_, py_, pw, ph, alpha=230, color=(30, 10, 10))
        pygame.draw.rect(surface, COLOR_RED, (px_, py_, pw, ph), 3, border_radius=16)

        skull = self.font_huge.render("💀", True, COLOR_RED)
        title = self.font_huge.render("GAME OVER", True, COLOR_RED)
        surface.blit(skull, (SCREEN_WIDTH//2 - skull.get_width()//2, py_ + 20))
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, py_ + 90))

        sub = self.font_large.render(
            "You were defeated in the enemy zone!", True, (200, 100, 100)
        )
        surface.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, py_ + 165))

        stats = [
            ("Steps Taken",    str(player_stats['steps'])),
            ("Tiles Explored", f"{fog_stats['explored_pct']}%"),
            ("Castles Found", f"{found_villages} / {total_villages}"),
        ]
        for i, (label, val) in enumerate(stats):
            sy = py_ + 210 + i * 28
            surface.blit(self.font_medium.render(f"{label}:", True, (100, 116, 139)), (px_ + 60, sy))
            surface.blit(self.font_medium.render(val, True, COLOR_WHITE), (px_ + 260, sy))

        self._draw_action_buttons(surface, mouse_pos, py_ + ph - 65, pw, px_)


    def _draw_action_buttons(self, surface, mouse_pos, btn_y, pw, px_):
        mx, my = mouse_pos
        b1w, b1h = 160, 44
        b1x = px_ + pw//2 - b1w - 15
        b1h_ = (b1x <= mx <= b1x + b1w and btn_y <= my <= btn_y + b1h)
        pygame.draw.rect(surface, (56, 189, 248) if b1h_ else (14, 165, 233),
                         (b1x, btn_y, b1w, b1h), border_radius=10)
        t1 = self.font_btn.render("▶  Play Again", True, COLOR_WHITE)
        surface.blit(t1, (b1x + b1w//2 - t1.get_width()//2,
                           btn_y + b1h//2 - t1.get_height()//2))

        b2w, b2h = 160, 44
        b2x = px_ + pw//2 + 15
        b2h_ = (b2x <= mx <= b2x + b2w and btn_y <= my <= btn_y + b2h)
        pygame.draw.rect(surface, (100, 116, 139) if b2h_ else (51, 65, 85),
                         (b2x, btn_y, b2w, b2h), border_radius=10)
        t2 = self.font_btn.render("✕  Quit", True, COLOR_WHITE)
        surface.blit(t2, (b2x + b2w//2 - t2.get_width()//2,
                           btn_y + b2h//2 - t2.get_height()//2))

        return b1h_, b2h_


    # Quit Dialog 
    def draw_quit_dialog(self, surface, mouse_pos):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        dw, dh = 400, 200
        dx = SCREEN_WIDTH//2  - dw//2
        dy = SCREEN_HEIGHT//2 - dh//2
        self._draw_panel(surface, dx, dy, dw, dh, alpha=240)

        t1 = self.font_large.render("Quit Game?", True, COLOR_ACCENT)
        surface.blit(t1, (dx + dw//2 - t1.get_width()//2, dy + 30))
        t2 = self.font_medium.render("Do you want to quit the game?",
                                      True, (148, 163, 184))
        surface.blit(t2, (dx + dw//2 - t2.get_width()//2, dy + 70))

        mx, my = mouse_pos
        yx, yy, yw, yh = dx + 60, dy + 130, 110, 42
        yh_ = (yx <= mx <= yx + yw and yy <= my <= yy + yh)
        pygame.draw.rect(surface, (239, 68, 68) if yh_ else (185, 28, 28),
                         (yx, yy, yw, yh), border_radius=8)
        yt = self.font_btn.render("Yes", True, COLOR_WHITE)
        surface.blit(yt, (yx + yw//2 - yt.get_width()//2,
                           yy + yh//2 - yt.get_height()//2))

        nx, ny, nw, nh = dx + 230, dy + 130, 110, 42
        nh_ = (nx <= mx <= nx + nw and ny <= my <= ny + nh)
        pygame.draw.rect(surface, (74, 222, 128) if nh_ else (21, 128, 61),
                         (nx, ny, nw, nh), border_radius=8)
        nt = self.font_btn.render("No", True, COLOR_WHITE)
        surface.blit(nt, (nx + nw//2 - nt.get_width()//2,
                           ny + nh//2 - nt.get_height()//2))

        return yh_, nh_


    # Village Popup
    def draw_village_popup(self, surface):
        if self.popup_timer <= 0 or not self.popup_msg:
            return
        self.popup_timer -= 1

        if self.popup_timer > self.POPUP_DURATION - 20:
            alpha = int((self.POPUP_DURATION - self.popup_timer) / 20 * 255)
        elif self.popup_timer < 40:
            alpha = int(self.popup_timer / 40 * 255)
        else:
            alpha = 255

        text = self.font_large.render(self.popup_msg, True, COLOR_WHITE)
        x    = SCREEN_WIDTH//2  - text.get_width()//2
        y    = SCREEN_HEIGHT//2 - 60
        panel = pygame.Surface((text.get_width() + 40, text.get_height() + 24),
                                pygame.SRCALPHA)
        panel.fill((168, 85, 247, min(alpha, 200)))
        surface.blit(panel, (x - 20, y - 12))
        text.set_alpha(alpha)
        surface.blit(text, (x, y))


    #  Enemy Flash 
    def draw_enemy_flash(self, surface):
        if self.flash_timer <= 0:
            return
        self.flash_timer -= 1
        alpha = int((self.flash_timer / self.FLASH_DURATION) * 120)
        self.flash_surface.fill((239, 68, 68, alpha))
        surface.blit(self.flash_surface, (0, 0))
        bs = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(bs, (239, 68, 68, int(alpha * 1.5)),
                         (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 12)
        surface.blit(bs, (0, 0))


    #  Minimap 
    def draw_minimap(self, surface, tile_map, fog, px, py):
        self.minimap_surface.fill((15, 23, 42))
        rows = len(tile_map)
        cols = len(tile_map[0])
        for ty in range(rows):
            for tx in range(cols):
                fs = fog.fog_map[ty][tx]
                if fs == 0:
                    color = (5, 5, 10)
                else:
                    tid   = int(tile_map[ty][tx])
                    color = TILE_COLORS.get(tid, (50, 50, 50))
                    if fs == 1:
                        color = tuple(max(0, c // 2) for c in color)
                mx_ = int(tx * MINIMAP_WIDTH  / cols)
                my_ = int(ty * MINIMAP_HEIGHT / rows)
                mw  = max(1, int(MINIMAP_WIDTH  / cols) + 1)
                mh  = max(1, int(MINIMAP_HEIGHT / rows) + 1)
                pygame.draw.rect(self.minimap_surface, color, (mx_, my_, mw, mh))

        ppx = int(px * MINIMAP_WIDTH  / cols)
        ppy = int(py * MINIMAP_HEIGHT / rows)
        pygame.draw.circle(self.minimap_surface, (255,255,255), (ppx, ppy), 2)
        pygame.draw.circle(self.minimap_surface, COLOR_ACCENT,  (ppx, ppy), 3, 1)

        self._draw_panel(surface, MINIMAP_X-6, MINIMAP_Y-22,
                         MINIMAP_WIDTH+12, MINIMAP_HEIGHT+28)
        t = self.font_small.render("MINIMAP", True, COLOR_ACCENT)
        surface.blit(t, (MINIMAP_X, MINIMAP_Y - 18))
        surface.blit(self.minimap_surface, (MINIMAP_X, MINIMAP_Y))
        pygame.draw.rect(surface, COLOR_BORDER,
                         (MINIMAP_X, MINIMAP_Y, MINIMAP_WIDTH, MINIMAP_HEIGHT), 1)


    #  Stats 
    def draw_stats(self, surface, player_stats, fog_stats, tile_name):
        newtile_name = tile_name
        if tile_name == "Village":
            newtile_name = 'Castle'
        

        self._draw_panel(surface, 10, 10, 220, 130)
        t = self.font_large.render("AI WORLD EXPLORER", True, COLOR_ACCENT)
        surface.blit(t, (20, 18))
        pygame.draw.line(surface, COLOR_BORDER, (20, 38), (220, 38), 1)
        data = [
            ("Position",   f"({player_stats['position'][0]}, {player_stats['position'][1]})"),
            ("Tile",       newtile_name ),
            ("Steps",      str(player_stats['steps'])),
            ("Explored",   f"{fog_stats['explored_pct']}%"),
            ("Discovered", f"{fog_stats['visited'] + fog_stats['visible']} tiles"),
        ]
        for i, (label, value) in enumerate(data):
            y = 46 + i * 18
            surface.blit(self.font_small.render(f"{label}:", True, COLOR_BORDER), (20, y))
            surface.blit(self.font_small.render(value, True, COLOR_WHITE), (110, y))


    def draw_exploration_bar(self, surface, explored_pct):
        bx, by, bw, bh = 10, 148, 220, 16
        self._draw_panel(surface, bx, by, bw, bh + 4, alpha=180)
        fw = int((explored_pct / 100) * (bw - 4))
        if fw > 0:
            c = COLOR_RED if explored_pct < 30 else \
                COLOR_YELLOW if explored_pct < 60 else COLOR_GREEN
            pygame.draw.rect(surface, c, (bx + 2, by + 2, fw, bh))
        t = self.font_small.render(f"Explored: {explored_pct}%", True, COLOR_WHITE)
        surface.blit(t, (bx + 6, by + 2))


    def draw_tile_tooltip(self, surface, tile_name, tile_id):
        color  = TILE_COLORS.get(tile_id, (100, 100, 100))
        newtile_name = tile_name
        if(tile_name == "Village"):
            newtile_name = "Castle"
        text   = self.font_medium.render(f"  {newtile_name}", True, COLOR_WHITE)
        text_w = text.get_width() + 30
        x = SCREEN_WIDTH//2 - text_w//2
        self._draw_panel(surface, x, 10, text_w + 10, 26)
        pygame.draw.circle(surface, color,       (x + 16, 23), 6)
        pygame.draw.circle(surface, COLOR_WHITE, (x + 16, 23), 6, 1)
        surface.blit(text, (x + 10, 15))


    def draw_controls(self, surface):
        if self.controls_timer <= 0:
            return
        self.controls_timer -= 1
        controls = ["WASD — Move", "M — Minimap", "ESC — Quit"]
        pw       = 180
        ph       = 16 + len(controls) * 18
        x        = SCREEN_WIDTH//2  - pw//2
        y        = SCREEN_HEIGHT - ph - 20
        alpha    = min(200, self.controls_timer * 2)
        self._draw_panel(surface, x, y, pw, ph, alpha=alpha)
        for i, ctrl in enumerate(controls):
            t = self.font_small.render(ctrl, True, COLOR_ACCENT)
            surface.blit(t, (x + 10, y + 8 + i * 18))


    def draw_village_counter(self, surface, found, total):
        text = self.font_medium.render(
            f"🏘  Castle: {found} / {total}", True, COLOR_WHITE
        )
        x = SCREEN_WIDTH - text.get_width() - 20
        self._draw_panel(surface, x - 10, 25, text.get_width() + 20, 28, alpha=180)
        surface.blit(text, (x, 30))

    #  Seed display 
    def draw_seed_info(self, surface, seed):
        t = self.font_small.render(f"Seed: {seed}", True, (51, 65, 85))
        surface.blit(t, (SCREEN_WIDTH - t.get_width() - 10, SCREEN_HEIGHT - 20))


    #  Main Draw 
    def draw(self, surface, tile_map, fog, player_stats,
             fog_stats, tile_id, show_minimap,
             found_villages=0, total_villages=4, seed=42):

        tile_name = TILE_NAMES.get(tile_id, "Unknown")

        self.draw_stats(surface, player_stats, fog_stats, tile_name)
        self.draw_exploration_bar(surface, fog_stats['explored_pct'])
        self.draw_health_bar(
            surface,
            player_stats['hp'],    player_stats['max_hp'],
            player_stats['hp_flash'], player_stats['hp_heal'],
        )

        if show_minimap:
            self.draw_minimap(surface, tile_map, fog,
                              player_stats['position'][0],
                              player_stats['position'][1])

        self.draw_tile_tooltip(surface, tile_name, tile_id)
        self.draw_village_popup(surface)
        self.draw_enemy_flash(surface)
        self.draw_controls(surface)
        self.draw_village_counter(surface, found_villages, total_villages)
        self.draw_seed_info(surface, seed)