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


def get_connected_components(adjacency_list: dict[tuple[int, int], set[tuple[int, int]]]) -> list[list[tuple[int, int]]]:
    
    # every cell must still be checked once by the loop below, but cells already
    # assigned to a component must not start a second DFS — otherwise the same
    # component is found again (and again)
    visited: set[tuple[int, int]] = set()

    def dfs(adjacency_list: dict[tuple[int, int], set[tuple[int, int]]], start_coor: tuple[int, int]):
        
        # initialise the variable that stores the cells that are connected in the grid
        connected: list[tuple[int, int]] = []
        
        # initialise the common variables to perform the DFS traversal
        start_node: tuple[int, int] = start_coor
        stack: list[tuple[int, int]] = [start_node]
        curr_node: tuple[int, int] = start_node
        
        # visited is already defined above
        visited.add(start_node)

        # iteratively perform the DFS traversal
        while (len(stack) != 0):
            curr_node = stack.pop()
            connected.append(curr_node)
            for v in adjacency_list.get(curr_node):
                if (v not in visited):
                    stack.append(v)
                    visited.add(v)
        
        return connected
    
    output: list[list[tuple[int, int]]] = []
    for u in adjacency_list:
        if u in visited:
            continue
        connected: list[tuple[int, int]] = dfs(adjacency_list, u)
        output.append(connected)
    
    return output


def main():
    
    # "." indicates open cell
    # "#" indicates wall
    grid: list[list[str]] = [
    #     0    1    2    3    4
        [".", ".", "#", ".", "."], # 0
        [".", ".", "#", ".", "."], # 1
        ["#", "#", ".", ".", "#"], # 2
        [".", ".", ".", "#", "."], # 3
    ]
    
    # build the graph
    adjacency_list: dict[tuple[int, int], set[tuple[int, int]]] = build_graph(grid)
    
    # get the connected components
    print(get_connected_components(adjacency_list))    
    

if (__name__ == "__main__"):
    main()