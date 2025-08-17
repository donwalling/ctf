
import json

def load_map(path):
    with open(path, 'r') as f:
        return json.load(f)

def simple_map():
    # 9 x 15 grid with border walls and two base markers
    grid = [['.' for _ in range(15)] for _ in range(9)]
    for r in [0,8]:
        for c in range(15):
            grid[r][c] = '#'
    for r in range(9):
        grid[r][0] = '#'
        grid[r][14] = '#'
    # Base/flag markers (for rendering convenience)
    grid[4][1] = 'A'
    grid[4][13] = 'B'
    return {
        'rows': 9,
        'cols': 15,
        'grid': grid,
        'flags': {
            'Team Alpha': [4,1],
            'Team Bravo': [4,13]
        }
    }
