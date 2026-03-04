import heapq


def find_path(start_tile, end_tile, tiles, variation_seed=0):
    """A* pathfinding algorithm to find path between two tiles.
    
    variation_seed: unique value per enemy to create path diversity
    """
    if start_tile == end_tile:
        return [end_tile]
    
    rows = len(tiles)
    cols = len(tiles[0])
    
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def tile_cost(pos):
        if variation_seed == 0:
            return 0
        x, y = pos
        return ((x * 7 + y * 13 + variation_seed) % 5) * 0.3
    
    def get_neighbors(pos):
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and tiles[ny][nx] == 0:
                neighbors.append((nx, ny))
        return neighbors
    
    open_set = []
    heapq.heappush(open_set, (0, start_tile))
    came_from = {}
    g_score = {start_tile: 0}
    f_score = {start_tile: heuristic(start_tile, end_tile)}
    open_set_hash = {start_tile}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        open_set_hash.discard(current)
        
        if current == end_tile:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        
        for neighbor in get_neighbors(current):
            tentative_g = g_score[current] + 1 + tile_cost(neighbor)
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, end_tile)
                
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)
    
    return []


def find_path_for_large_entity(start_tile, end_tile, tiles, tile_size, entity_width, entity_height):
    """A* pathfinding for large entities that span multiple tiles.
    
    Checks that all tiles the entity would occupy are walkable.
    """
    if start_tile == end_tile:
        return [end_tile]
    
    rows = len(tiles)
    cols = len(tiles[0])
    
    tiles_wide = (entity_width // tile_size) + 1
    tiles_tall = (entity_height // tile_size) + 1
    
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def is_valid_for_entity(tx, ty):
        for ox in range(-1, tiles_wide + 1):
            for oy in range(-1, tiles_tall + 1):
                check_x = tx + ox
                check_y = ty + oy
                if check_x < 0 or check_x >= cols or check_y < 0 or check_y >= rows:
                    if ox >= 0 and ox < tiles_wide and oy >= 0 and oy < tiles_tall:
                        return False
                    continue
                if tiles[check_y][check_x] != 0:
                    if ox >= 0 and ox < tiles_wide and oy >= 0 and oy < tiles_tall:
                        return False
        return True
    
    def get_neighbors(pos):
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if is_valid_for_entity(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
    
    if not is_valid_for_entity(start_tile[0], start_tile[1]):
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                nx, ny = start_tile[0] + dx, start_tile[1] + dy
                if is_valid_for_entity(nx, ny):
                    start_tile = (nx, ny)
                    break
            else:
                continue
            break
    
    open_set = []
    heapq.heappush(open_set, (0, start_tile))
    came_from = {}
    g_score = {start_tile: 0}
    f_score = {start_tile: heuristic(start_tile, end_tile)}
    open_set_hash = {start_tile}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        open_set_hash.discard(current)
        
        if heuristic(current, end_tile) <= 2:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        
        for neighbor in get_neighbors(current):
            tentative_g = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, end_tile)
                
                if neighbor not in open_set_hash:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)
    
    return []
