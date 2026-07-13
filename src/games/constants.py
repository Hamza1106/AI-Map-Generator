"""
constants.py - Game Settings & Constants
"""

# Screen Settings
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS           = 60
TITLE         = "AI World Explorer"

# Tile Settings
TILE_SIZE     = 32  
PLAYER_SPEED  = 4

# World Settings
WORLD_WIDTH   = 80
WORLD_HEIGHT  = 50
WORLD_SEED    = 42

# Fog of War 
FOG_RADIUS        = 6
FOG_REVEAL_RADIUS = 4

# Health Settings 
PLAYER_MAX_HP       = 100
ENEMY_DAMAGE_RATE   = 60   
ENEMY_DAMAGE_AMOUNT = 10   
VILLAGE_HEAL_AMOUNT = 15   
VILLAGE_HEAL_RATE   = 60   


TILE_WATER    = 0
TILE_BEACH    = 1
TILE_PLAINS   = 2
TILE_FOREST   = 3
TILE_MOUNTAIN = 4
TILE_SNOW     = 5
TILE_VILLAGE  = 10
TILE_ENEMY    = 11


TILE_COLORS = {
    0:  (59,  130, 246),
    1:  (251, 191,  36),
    2:  (134, 239, 172),
    3:  (22,  163,  74),
    4:  (120, 113, 108),
    5:  (226, 232, 240),
    10: (168,  85, 247),
    11: (239,  68,  68),
}

TILE_COLORS_DARK = {
    k: tuple(max(0, c // 2) for c in v)
    for k, v in TILE_COLORS.items()
}


WATER_ANIM_FRAMES = 4
WATER_ANIM_SPEED  = 20


FOG_HIDDEN  = (0, 0, 0)
FOG_VISITED = (0, 0, 0, 160)


COLOR_BLACK  = (0,   0,   0)
COLOR_WHITE  = (255, 255, 255)
COLOR_DARK   = (15,  23,  42)
COLOR_PANEL  = (30,  41,  59)
COLOR_BORDER = (51,  65,  85)
COLOR_ACCENT = (125, 211, 252)
COLOR_GREEN  = (74,  222, 128)
COLOR_RED    = (248, 113, 113)
COLOR_YELLOW = (251, 191,  36)
COLOR_PURPLE = (168,  85, 247)
COLOR_ORANGE = (251, 146,  60)

# Player
PLAYER_COLOR   = (255, 255, 255)
PLAYER_OUTLINE = (125, 211, 252)
PLAYER_RADIUS  = 8

# HUD / Minimap
MINIMAP_WIDTH     = 200
MINIMAP_HEIGHT    = 120
MINIMAP_X         = SCREEN_WIDTH  - MINIMAP_WIDTH  - 10
MINIMAP_Y         = SCREEN_HEIGHT - MINIMAP_HEIGHT - 10
MINIMAP_TILE_SIZE = 3

# Tile Names
TILE_NAMES = {
    0:  "Water",     1:  "Beach",
    2:  "Plains",    3:  "Forest",
    4:  "Mountain",  5:  "Snow Peak",
    10: "Village",   11: "Enemy Zone",
}


WALKABLE_TILES = {
    0: False, 1: True,  2: True,
    3: True,  4: False, 5: False,
    10: True, 11: True,
}


TILE_EVENTS = {
    10: "Castle🫅 Safe zone.",
    11: "Danger area 🤯 Enemy zone.",
}