"""
placer.py - Smart Village & Enemy Zone Placement

"""

import numpy as np
import random


WATER    = 0
BEACH    = 1
PLAINS   = 2
FOREST   = 3
MOUNTAIN = 4
SNOW     = 5

VILLAGE    = 10
ENEMY_ZONE = 11


def find_valid_tiles(tile_map: np.ndarray, allowed_types: list) -> list:
    """
    Finding valid tile positions for placement.
    Returns: list of (y, x) tuples
    """
    positions = []
    height, width = tile_map.shape

    for y in range(height):
        for x in range(width):
            if tile_map[y][x] in allowed_types:
                positions.append((y, x))

    return positions


def is_far_enough(pos: tuple, existing: list, min_dist: int) -> bool:
    
    y1, x1 = pos
    for y2, x2 in existing:
        dist = abs(y1 - y2) + abs(x1 - x2)  # Manhattan distance
        if dist < min_dist:
            return False
    return True


def score_village_position(pos: tuple, tile_map: np.ndarray,
                            height_map: np.ndarray) -> float:
    """
    Rules:
    - On the plains
    - Near to water (fresh water access)
    - Away from mountains
    - Near to forests 
    """
    y, x = pos
    rows, cols = tile_map.shape
    score = 0.0

    for dy in range(-3, 4):
        for dx in range(-3, 4):
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols:
                tile = tile_map[ny][nx]
                dist = abs(dy) + abs(dx)
                weight = 1.0 / (dist + 1)  

                if tile == WATER:
                    score += 2.0 * weight    
                if tile == FOREST:
                    score += 1.0 * weight  
                if tile == PLAINS:
                    score += 0.5 * weight    
                if tile == MOUNTAIN:
                    score -= 1.5 * weight    
                if tile == SNOW:
                    score -= 2.0 * weight   

    h = height_map[y][x]
    if 0.3 < h < 0.6:
        score += 2.0   
    elif h < 0.3 or h > 0.7:
        score -= 1.0   

    return score


def place_villages(tile_map: np.ndarray, height_map: np.ndarray,
                   num_villages: int = 3, seed: int = 42) -> list:
    """
    Smart village placement:
    1. Find all plains tiles 
    2. Score each tile based on proximity to water, forests, mountains, and height
    3. choose Best scored positions 
    4. Minimum distance 
    """
    random.seed(seed)

    
    candidates = find_valid_tiles(tile_map, [PLAINS])

    if not candidates:
        return []

    scored = []
    for pos in candidates:
        s = score_village_position(pos, tile_map, height_map)
        scored.append((s, pos))

    scored.sort(reverse=True)

   
    villages = []
    min_distance = 8  

    for score, pos in scored:
        if len(villages) >= num_villages:
            break
        if is_far_enough(pos, villages, min_distance):
            villages.append(pos)

    return villages


def score_enemy_position(pos: tuple, tile_map: np.ndarray,
                          villages: list) -> float:
    """
    Enemy zone position score karo.

    Rules:
    - Forest or Mountain (hiding spots)
    - Far from Villages (but not too far)
    - Far from water (enemies don't want to be near water)
    """
    y, x = pos
    rows, cols = tile_map.shape
    score = 0.0

    
    tile = tile_map[y][x]
    if tile == FOREST:
        score += 3.0   
    if tile == MOUNTAIN:
        score += 2.0   

    
    if villages:
        min_dist_to_village = min(
            abs(y - vy) + abs(x - vx)
            for vy, vx in villages
        )
       
        if 5 <= min_dist_to_village <= 15:
            score += 3.0
        elif min_dist_to_village < 5:
            score -= 3.0  
        else:
            score += 1.0

    
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            ny, nx = y + dy, x + dx
            if 0 <= ny < rows and 0 <= nx < cols:
                if tile_map[ny][nx] == WATER:
                    score -= 1.0

    return score


def place_enemy_zones(tile_map: np.ndarray, villages: list,
                      num_enemies: int = 4, seed: int = 42) -> list:
    """
    Smart enemy zone placement:
    - Prefer Forests aur Mountains
    - Near Villages (challenge!)
    - Minimum distance between zones
    """
    random.seed(seed + 100)

    
    candidates = find_valid_tiles(tile_map, [FOREST, MOUNTAIN])

    if not candidates:
        return []


    scored = []
    for pos in candidates:
        s = score_enemy_position(pos, tile_map, villages)
        scored.append((s, pos))

    scored.sort(reverse=True)

    enemy_zones = []
    min_distance = 5 

    for score, pos in scored:
        if len(enemy_zones) >= num_enemies:
            break
        if is_far_enough(pos, enemy_zones, min_distance):
           
            if pos not in villages:
                enemy_zones.append(pos)

    return enemy_zones


def apply_placements(tile_map: np.ndarray, villages: list,
                     enemy_zones: list) -> np.ndarray:
    """
    Overlay village and enemy zone placements on the tile map.
    """
    result = tile_map.copy()

    for y, x in villages:
        result[y][x] = VILLAGE      

    for y, x in enemy_zones:
        result[y][x] = ENEMY_ZONE   

    return result


def get_placement_stats(villages: list, enemy_zones: list) -> dict:
    
    return {
        "villages":    len(villages),
        "enemy_zones": len(enemy_zones),
        "village_positions":    villages,
        "enemy_positions":      enemy_zones
    }



if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    from noise import generate_terrain_features
    from classifier import load_model, classify_world

    print("=" * 50)
    print("   AI World Generator — Placer Test")
    print("=" * 50)

    print("\n[1/4] Loading model...")
    model = load_model("models/tile_classifier.pkl")

    print("\n[2/4] Generating terrain...")
    features = generate_terrain_features(width=40, height=20, seed=42)

    print("\n[3/4] Classifying world...")
    tile_map = classify_world(features, model)

    print("\n[4/4] Placing villages & enemy zones...")
    villages    = place_villages(tile_map, features["heightmap"],
                                  num_villages=3, seed=42)
    enemy_zones = place_enemy_zones(tile_map, villages,
                                     num_enemies=5, seed=42)
    final_map   = apply_placements(tile_map, villages, enemy_zones)
    stats       = get_placement_stats(villages, enemy_zones)

    print(f"\n  Villages placed    : {stats['villages']}")
    for i, (y, x) in enumerate(stats['village_positions']):
        print(f"    Village {i+1}: ({x}, {y})")

    print(f"\n  Enemy zones placed : {stats['enemy_zones']}")
    for i, (y, x) in enumerate(stats['enemy_positions']):
        print(f"    Enemy {i+1}: ({x}, {y})")

    print("\n placer.py working correctly!")