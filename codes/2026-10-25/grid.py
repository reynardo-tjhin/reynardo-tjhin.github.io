from collections import deque

def build_graph(grid: list[list[str]]) -> dict[tuple[int, int], set[tuple[int, int]]]:
    
    # get number of rows and number of columns
    no_of_rows: int = len(grid)
    no_of_cols: int = len(grid[0])
    
    # each vertex is indicated by its coordinate (x,y)
    adjacency_list: dict[tuple[int, int], set[tuple[int, int]]] = {} # init the adjacency_list
    edge_list: list[tuple[tuple[int, int], tuple[int, int]]] = [] # build the edge list
    for i in range(no_of_rows):
        for j in range(no_of_cols):
            
            if (grid[i][j] == "#"):
                continue
            
            # initialise the adjacent vertex list
            adjacency_list[(i,j)] = set()
            
            # add edge for "right" direction
            right: int = j + 1
            if (right <= no_of_cols - 1 and grid[i][right] != "#"):
                edge_list.append(((i,j), (i,right)))
                
            # add edge for "left" direction
            left: int = j - 1
            if (left >= 0 and grid[i][left] != "#"):
                edge_list.append(((i,j), (i,left)))
            
            # add edge for "up" direction
            up: int = i - 1
            if (up >= 0 and grid[up][j] != "#"):
                edge_list.append(((i,j), (up,j)))
            
            # add edge for "down" direction
            down: int = i + 1
            if (down <= no_of_rows - 1 and grid[down][j] != "#"):
                edge_list.append(((i,j), (down,j)))

    # add the edge
    for u, v in edge_list:
        adjacency_list[u].add(v)
        adjacency_list[v].add(u)
    
    return adjacency_list

def count_open_cells(adjacency_list: dict[tuple[int, int], set[tuple[int, int]]], start_coor: tuple[int, int]) -> int:
    
    # initialise the count
    count: int = 0

    # perform the BFS traversal
    queue: deque[tuple[int, int]] = deque([start_coor])
    visited: set[tuple[int, int]] = {start_coor}
    cur_node: tuple[int, int] = start_coor
    while (len(queue) != 0):
        print(queue)
        cur_node = queue.popleft()
        count += 1
        for v in adjacency_list.get(cur_node):
            if (v not in visited):
                queue.append(v)
                visited.add(v)

    return count

def faster_count_open_cells(grid: list[list[str]], start_coor: tuple[int, int]) -> int:
    # assumes the cell in start coordinate is an open cell

    no_of_rows: int = len(grid)
    no_of_cols: int = len(grid[0])

    # direction array: up, down, left and right respectively
    directions: list[tuple[int, int]] = [(-1,0), (1,0), (0,-1), (0,1)]

    # initialise the count
    count: int = 0

    # perform the BFS traversal directly
    # no need to build the graph
    queue: deque[tuple[int, int]] = deque([start_coor])
    visited: set[tuple[int, int]] = {start_coor}
    cur_node: tuple[int, int] = start_coor
    while (len(queue) != 0):
        cur_node = queue.popleft()
        count += 1
        for row, col in directions:
            new_row: int = cur_node[0] + row
            new_col: int = cur_node[1] + col
            if (0 <= new_row < no_of_rows and 0 <= new_col < no_of_cols and grid[new_row][new_col] != "#" and (new_row, new_col) not in visited):
                queue.append((new_row, new_col))
                visited.add((new_row, new_col))
    
    return count

def main():
    
    # "." indicates open cell
    # "#" indicates wall
    grid: list[list[str]] = [
        [".", ".", "#", ".", "."],
        [".", ".", "#", "#", "#"],
        [".", ".", "#", ".", "."],
    ]
    # grid: list[list[str]] = [
    #     [".", "."],
    #     [".", "#"],
    # ]
    start: tuple[int, int] = (0, 0)
    print(count_open_cells(build_graph(grid), start))
    print(faster_count_open_cells(grid, start))

if (__name__ == "__main__"):
    main()
