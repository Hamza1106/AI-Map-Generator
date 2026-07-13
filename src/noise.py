"""
terrain_noise.py - Terrain Generation using Perlin Noise
Generates heightmap and moisture map for the world
"""

import numpy as np
from perlin_noise import PerlinNoise


def generate_heightmap(width: int, height: int, seed: int = 42) -> np.ndarray:
    """
    Generate heightmap using Perlin noise with multiple octaves for realism.
    Returns: 2D numpy array with values 0.0 to 1.0
    """
    # Octaves = detail level 
    noise1 = PerlinNoise(octaves=3, seed=seed)
    noise2 = PerlinNoise(octaves=6, seed=seed)
    noise3 = PerlinNoise(octaves=12, seed=seed)

    heightmap = np.zeros((height, width))

    for y in range(height):
        for x in range(width):
            nx = x / width
            ny = y / height

            
            value  = 1.0 * noise1([nx, ny])
            value += 0.5 * noise2([nx, ny])
            value += 0.25 * noise3([nx, ny])

            heightmap[y][x] = value

    # Normalize to 0.0 - 1.0
    heightmap = (heightmap - heightmap.min()) / (heightmap.max() - heightmap.min())
    return heightmap


def generate_moisture_map(width: int, height: int, seed: int = 42) -> np.ndarray:
    """
    Generate moisture map using Perlin noise with a different seed for independence.
    Moisture decides weather: dry plains vs lush forests
    Returns: 2D numpy array with values 0.0 to 1.0
    """
    
    noise1 = PerlinNoise(octaves=3, seed=seed + 999)
    noise2 = PerlinNoise(octaves=6, seed=seed + 999)

    moisture = np.zeros((height, width))

    for y in range(height):
        for x in range(width):
            nx = x / width
            ny = y / height

            value  = 1.0 * noise1([nx, ny])
            value += 0.5 * noise2([nx, ny])

            moisture[y][x] = value

    # Normalize to 0.0 - 1.0
    moisture = (moisture - moisture.min()) / (moisture.max() - moisture.min())
    return moisture


def calculate_slope(heightmap: np.ndarray) -> np.ndarray:
    """
    Calculate slope of each tile based on height differences with neighbors.
    High slope = steep mountain, Low slope = flat plains
    Returns: 2D numpy array with values 0.0 to 1.0
    """
    height, width = heightmap.shape
    slope = np.zeros((height, width))

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            dx = abs(heightmap[y][x+1] - heightmap[y][x-1]) / 2
            dy = abs(heightmap[y+1][x] - heightmap[y-1][x]) / 2
            slope[y][x] = np.sqrt(dx**2 + dy**2)

    # Normalize
    if slope.max() > 0:
        slope = slope / slope.max()

    return slope


def calculate_neighbor_avg(heightmap: np.ndarray) -> np.ndarray:
    """
    Calculate average height of each tile's 8 neighbors.
    This serves as a context feature for the ML classifier.
    Returns: 2D numpy array
    """
    height, width = heightmap.shape
    neighbor_avg = np.zeros((height, width))

    for y in range(height):
        for x in range(width):
            neighbors = []
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width:
                        neighbors.append(heightmap[ny][nx])
            neighbor_avg[y][x] = np.mean(neighbors)

    return neighbor_avg


def generate_terrain_features(width: int, height: int, seed: int = 42) -> dict:
    """
    Generate all terrain features together.
    This dict will be fed to the ML classifier.

    """
    print(f"  -> Generating heightmap (seed={seed})...")
    heightmap = generate_heightmap(width, height, seed)

    print(f"  -> Generating moisture map...")
    moisture = generate_moisture_map(width, height, seed)

    print(f"  -> Calculating slope...")
    slope = calculate_slope(heightmap)

    print(f"  -> Calculating neighbor averages...")
    neighbor_avg = calculate_neighbor_avg(heightmap)

    return {
        "heightmap":    heightmap,
        "moisture":     moisture,
        "slope":        slope,
        "neighbor_avg": neighbor_avg,
        "width":        width,
        "height":       height,
        "seed":         seed
    }



if __name__ == "__main__":
    print("Testing terrain_noise.py...\n")

    features = generate_terrain_features(width=20, height=10, seed=42)

    print("\nHeightmap sample (first row):")
    print(np.round(features["heightmap"][0], 2))

    print("\nMoisture sample (first row):")
    print(np.round(features["moisture"][0], 2))

    print("\nSlope sample (first row):")
    print(np.round(features["slope"][0], 2))

    print("\nterrain_noise.py working correctly!")