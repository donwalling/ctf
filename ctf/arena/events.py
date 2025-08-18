
def in_bounds(pos, rows, cols):
    r,c = pos
    return 0 <= r < rows and 0 <= c < cols

DIRECTIONS = {
    'up': (-1,0),
    'down': (1,0),
    'left': (0,-1),
    'right': (0,1),
}
