---
title: Graphs Basics Part II - BFS/DFS Traversal
slug: graphs-basics-part-ii
date: 2026-10-25
categories:
- Data Structures and Algorithms
description: Basics of Graphs Part II - BFS/DFS Traversal
comments: true
---

# Graphs Basics Part II: BFS/DFS Traversal

Part I ended with a graph stored in an adjacency list. This part walks it: the two most important traversal algorithms — BFS and DFS — with an interactive animation, the mark-on-push vs mark-on-pop variants, and worked grid examples (reachable region, connected components).

<!-- more -->

## BFS/DFS Traversal Algorithms (Iterative)

* The two most important graph traversal algorithms.
* BFS (or Breadth First Search) visits the adjacent vertices (all the neighbours) first before visiting the other vertices.
* On the other hand, DFS (or Depth First Search) visits the next vertex recursively before going to the rest of its adjacent vertices (or neighbours).
* Below is an animation to help visualising BFS/DFS traversal in a graph (Made by Qwen 3.8 Flash Next).

<!-- BEGIN interactive BFS/DFS demo -------------------------------------------------
     Styles: docs/stylesheets/extra.css (already linked by extra_css in mkdocs.yml).
     Logic:  docs/javascripts/graph-traversal.js, which also holds the graph itself.
     data-mode: "bfs" or "dfs"   data-start: any vertex A..H
     Move this block anywhere in the post; it is self-contained. The code samples in
     the post must use the same adjacency list and the same sorted neighbour order as
     that JS file, otherwise the animation will not match the text.
     Legend labels below are plain text - rewrite them freely, but keep the <p>
     inside the div: CSS grid draws it as the caption row along the bottom of the
     card, and it only gets that treatment while it is a child of .gt.
------------------------------------------------------------------ END BEGIN demo -->
<div class="gt" data-graph-traversal data-mode="bfs" data-start="A">

<p class="gt-legend">
    <span><span class="gt-swatch is-seen"></span>in the frontier (seen, not finished)</span>
    <span><span class="gt-swatch is-current"></span>the vertex being expanded</span>
    <span><span class="gt-swatch is-done"></span>done</span>
    <span><span class="gt-swatch is-rejected"></span>edge blocked by the visited set</span>
</p>

</div>

<script src="/javascripts/graph-traversal.js"></script>

### Build the Graph

* Before showing the traversal code, with [Part I](/blog/2026-10-24/graphs-basics-part-i/) knowledge, let's build the graph in adjacency list first.
* Below code will store each vertex as a string.

```py
# build the edge_list
edge_list: list[tuple[str, str]] = [
    ("A", "B"), ("A", "C"),
    ("B", "D"), ("B", "E"),
    ("C", "F"), ("C", "G"),
    ("D", "H"), ("E", "H"), ("F", "H"), ("G", "H")
]

# build the adjacency list
vertex_names: list[str] = ["A", "B", "C", "D", "E", "F", "G", "H"]
adjacency_list: dict[str, list[str]] = {}
for vertex_name in vertex_names:
    if (adjacency_list.get(vertex_name) is None):
        adjacency_list[vertex_name] = []

# add the edges
for u, v in edge_list:
    adjacency_list.get(u).append(v)
    adjacency_list.get(v).append(u)
```

* The code above will output the below.

```py
adjacency_list: dict[str, list[str]] = {
    'A': ['B', 'C'], 
    'B': ['A', 'D', 'E'], 
    'C': ['A', 'F', 'G'], 
    'D': ['B', 'H'], 
    'E': ['B', 'H'], 
    'F': ['C', 'H'], 
    'G': ['C', 'H'], 
    'H': ['D', 'E', 'F', 'G']
}
```

* Below table shows the space and time complexity of both DFS and BFS algorithms.

    |   | DFS & BFS |
    |---|:---------------:|
    | Time Complexity | $O(V+E)$ |
    | Space Complexity | $O(V)$ |

* Both codes below show the iterative algorithm because some programming languages have a recursion-depth. For example, `python -c "import sys; print(sys.getrecursionlimit())"` will show the recursion-depth.

### DFS Algorithm (Iterative)

```py linenums="1"
def dfs(adjacency_list: dict[str, list[str]], start_node: str) -> list[str]:
    
    # define three variables: stack, visited and the current node
    stack: list[str] = [start_node] # stack is last-in-first-out (LIFO)
    visited: set[str] = {start_node}
    cur_node: str = start_node

    # define the output
    order: list[str] = []

    # iteratively perform the DFS traversal
    while (len(stack) != 0):
        cur_node = stack.pop() # get the current node
        order.append(cur_node)
        for v in adjacency_list.get(cur_node):
            if (v not in visited):
                stack.append(v)
                visited.add(v)

    return order
```

### BFS Algorithm (Iterative)

* BFS differs from DFS by using a queue instead of a stack.

* Use `collections.deque` to initialise as a queue.

```py linenums="1"
from collections import deque

def bfs(adjacency_list: dict[str, list[str]], start_node: str) -> list[str]:

    # define the three variables: queue, visited and the current node
    queue: deque[str] = deque([start_node]) # queue is first-in-first-out (FIFO)
    visited: set[str] = {start_node}
    cur_node: str = start_node
    
    # define the output
    order: list[str] = []
    
    # iteratively perform the BFS traversal
    while (len(queue) != 0):
        cur_node = queue.popleft()
        order.append(cur_node)
        for v in adjacency_list.get(cur_node):
            if (v not in visited):
                queue.append(v)
                visited.add(v)
                
    return order
```

!!! info

    The above algorithms are using the "mark-on-push" and "mark-on-enqueue" variants for DFS and BFS respectively. This means that the node is marked as visited after it is pushed/enqueued to the stack/queue (as shown in lines 17 and 18 for DFS and lines 19 and 20 for BFS).
    
    Another variant is the "mark-on-pop" and "mark-on-dequeue" where the node is marked as visited after it is popped/dequeued from the stack/queue. For DFS the visit order can change: on the animated graph starting from A, mark-on-push gives `A C G H E D F B` while mark-on-pop gives `A C G H F E B D`. For BFS the visit order never changes between the two variants (`A B C D E F G H` from A either way) — what changes is only how much the stack/queue swells, as discussed below.

    Although both variants work, "mark-on-pop" and "mark-on-dequeue" variants are more **_inefficient_** than their counterpart. This is evident when the graph is a complete graph, i.e. each vertex has an edge to every other vertex except itself. This is because the node is only marked visited after it is popped/dequeued. Each neighbour will be added because it has not been visited yet — including neighbours that are already sitting in the stack/queue. Therefore, there will be duplicate nodes in the stack/queue: mark-on-push/mark-on-enqueue enters every vertex at most once ($O(V)$ pushes/enqueues in total), while mark-on-pop/mark-on-dequeue can reach $O(E)$. Concretely, on the complete graph $K_{6}$ a traversal from any start vertex performs exactly 6 pushes/enqueues with mark-on-push/mark-on-enqueue, but 16 with mark-on-pop/mark-on-dequeue — in general, $n$ versus $n + \frac{(n-1)(n-2)}{2}$ for $K_{n}$.
    
    **DFS mark on pop variant**

    ```py linenums="1"
    def dfs_mark_on_pop(adjacency_list: dict[str, list[str]], start_node: str) -> list[str]:

        # define the three variables: stack, visited and the current node
        stack: list[str] = [start_node]
        cur_node: str = start_node
        
        # === diff from mark on push variant ===
        visited: set[str] = set()
        # === diff ends ===

        # define the output
        order: list[str] = []

        # iteratively perform the DFS traversal
        while (len(stack) != 0):
            cur_node = stack.pop() # get the current node

            # === here's where it differs from "mark-on-push" ===
            if (cur_node in visited):
                continue
            visited.add(cur_node)
            # === diff end ===

            order.append(cur_node)
            for v in adjacency_list.get(cur_node):
                if (v not in visited):
                    stack.append(v)

        return order
    ```

    **BFS mark on dequeue variant**

    ```py linenums="1"
    def bfs_mark_on_dequeue(adjacency_list: dict[str, list[str]], start_node: str) -> list[str]:
        
        # define the three variables: queue, visited and the current node
        queue: deque[str] = deque([start_node])
        cur_node: str = start_node

        # === diff from mark on enqueue variant ===
        visited: set[str] = set()
        # === diff ends ===
        
        # define the output
        order: list[str] = []
        
        # iteratively perform the BFS traversal
        while (len(queue) != 0):
            cur_node = queue.popleft() # queue is first-in-first-out (FIFO)

            # === here's where it differs from "mark-on-enqueue" ===
            if (cur_node in visited):
                continue
            visited.add(cur_node)
            # === diff end ===
            
            order.append(cur_node)
            for v in adjacency_list.get(cur_node):
                if (v not in visited):
                    queue.append(v)
                    
        return order
    ```

## Grid Traversal Algorithm

* A grid is an implicit graph.
* Each cell `(row, column)` is a vertex.
* Each of its up/down/left/right/(optionally)diagonals neighbours is an edge. For example, if `(0,0)` and `(0,1)` are both `.` (open cell), then there's an edge from `(0,0)` to `(0,1)`.
* "Grid traversal" is essentially a BFS or DFS over the implicit graph.

### Example Problem

* You're given an `R × C` grid of characters. `'.'` is open, `'#'` is a wall. Given a starting cell `(sr, sc)` which is guaranteed open, count how many open cells are reachable from it by moving up/down/left/right through open cells.

    ```txt
    row 0:  .  .  #  .  .
    row 1:  .  .  #  #  #
    row 2:  .  .  #  .  .
    ```

* Start at `(0,0)`, solutions: `6` (the connected open region containing the start).
* Start at `(0,3)`, solutions: `2`.

#### Step 1: Build the Graph (Adjacency List)

```py linenums="1"
def build_graph(grid: list[list[str]]) -> dict[tuple[int, int], set[tuple[int, int]]]:
    
    # get number of rows and number of columns
    no_of_rows: int = len(grid)
    no_of_cols: int = len(grid[0])
    
    # each vertex is indicated by its coordinate (row,col)
    adjacency_list: dict[tuple[int, int], set[tuple[int, int]]] = {} # init the adjacency_list
    edge_list: list[tuple[tuple[int, int], tuple[int, int]]] = [] # build the edge list
    for i in range(no_of_rows):
        for j in range(no_of_cols):
            
            if (grid[i][j] == "#"):
                continue
            
            # initialise the adjacent vertex list
            adjacency_list[(i,j)] = set()
            
            # add an edge for "right" direction
            right: int = j + 1
            if (right <= no_of_cols - 1 and grid[i][right] != "#"):
                edge_list.append(((i,j), (i,right)))
                
            # add an edge for "left" direction
            left: int = j - 1
            if (left >= 0 and grid[i][left] != "#"):
                edge_list.append(((i,j), (i,left)))
            
            # add an edge for "up" direction
            up: int = i - 1
            if (up >= 0 and grid[up][j] != "#"):
                edge_list.append(((i,j), (up,j)))
            
            # add an edge for "down" direction
            down: int = i + 1
            if (down <= no_of_rows - 1 and grid[down][j] != "#"):
                edge_list.append(((i,j), (down,j)))

    # add the edge
    for u, v in edge_list:
        adjacency_list[u].add(v)
        adjacency_list[v].add(u)
    
    return adjacency_list
```

#### Step 2: Count the Number of Open Cells Using BFS (or DFS if you prefer)

```py linenums="1"
def count_open_cells(adjacency_list: dict[tuple[int, int], set[tuple[int, int]]], start_coor: tuple[int, int]) -> int:
    
    # initialise the count
    count: int = 0

    # perform the BFS traversal
    queue: deque[tuple[int, int]] = deque([start_coor])
    visited: set[tuple[int, int]] = {start_coor}
    cur_node: tuple[int, int] = start_coor
    while (len(queue) != 0):
        cur_node = queue.popleft()
        count += 1
        for v in adjacency_list.get(cur_node):
            if (v not in visited):
                queue.append(v)
                visited.add(v)

    return count
```

### A Shorter Solution: Skip the Graph

* The previous steps show a clearer way to solve the problem. However, building the graph is not needed.
* The problem can be solved with fewer steps: skipping building the graph directly.
* A direction array stores the (row, col) offsets of the allowed moves; for diagonals, just add `(-1,-1), (-1,1), (1,-1), (1,1)` to `directions`.
* Every edge in this problem goes from a cell to an adjacent cell, so a neighbour is fully described by:
    
    1. within bounds (`0 <= new_row < no_of_rows and 0 <= new_col < no_of_cols`)
    2. not a wall (`grid[new_row][new_col] != "#"`)
    3. and not visited yet

* That is all BFS needs — no graph required.

```py linenums="1"
def count_open_cells_v2(grid: list[list[str]], start_coor: tuple[int, int]) -> int:

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
        for d_row, d_col in directions:
            new_row: int = cur_node[0] + d_row
            new_col: int = cur_node[1] + d_col
            if (0 <= new_row < no_of_rows and 0 <= new_col < no_of_cols and grid[new_row][new_col] != "#" and (new_row, new_col) not in visited):
                queue.append((new_row, new_col))
                visited.add((new_row, new_col))
    
    return count
```

* Both solutions end up at $O(R \cdot C)$ time and $O(R \cdot C)$ memory in the worst case, so either is fast enough.
* The real difference is *when* and *where* the work happens:
    * Step 1 pays $O(R \cdot C)$ **before** the traversal even starts — it inspects every cell of the grid to build the graph, even if the reachable region turns out to be a handful of cells.
    * The direction-array version only ever touches the reachable region itself: each cell is dequeued once and checks its 4 directions, so it is $O(\text{reachable cells})$.
* Memory tells the same story: the Step 1 version keeps the whole adjacency list (every open cell and its edges) for the entire traversal, while the direction-array version only keeps `visited` and the queue.
* As a rule of thumb: BFS/DFS on an adjacency list costs $O(V + E)$ — every vertex is dequeued once and every edge is scanned once — and here $V \le R \cdot C$ and $E \le 2 \cdot R \cdot C$, which is why both collapse to $O(R \cdot C)$.

## Connected Components

* A **connected component** is a group of cells where every cell can reach every other cell in the same group; cells in different components cannot reach each other — that is what separates them.
* One BFS/DFS run only ever discovers the start cell's own component. 
* So the pattern is:
    1. run a traversal from a cell
    2. keep a `visited` set of the cells it found
    3. then start a new traversal from the next cell that is not in `visited` yet
    4. and repeat until there are no unvisited cells left.

### Example Problem

* You're given an $R \times C$ grid of `'.'` (open) and `'#'` (wall). Two open cells are in the same component if you can walk between them through open cells using up/down/left/right moves. Return the list of connected components.

* On the Example Problem's grid, the answer is 3 components:
    * sizes `6`, `2` and `2`:
        * `{(0,0),(0,1),(1,0),(1,1),(2,0),(2,1)}`
        * `{(0,3),(0,4)}` and
        * `{(2,3),(2,4)}`.
    * The order in which the components — and the cells within each — come out depends on dict order and stack order, so compare contents, not positions.

* Use the `build_graph` function above to build the graph

* Below is the code for finding the list of connected components

```py linenums="1"
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
        
        # visited is already defined above at line 6
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
        for v in connected:
            visited.add(v)
        output.append(connected)
    
    return output
```

* This isn't grid-specific: for any graph, `for u in adjacency_list: if u not in visited: dfs(u)` is the standard pattern for enumerating components.
* The same outer loop is exactly what is needed when a traversal must cover a possibly-disconnected graph.
* Complexity: Every cell is pushed and popped across all the DFS runs combined at most once, so the whole function is $O(V + E)$ — the same cost as a single traversal.

## Acknowledgement

Reviewed by DeepSeek AI model and ISTA-DASLab/Qwen3.8 Flash Next GSQ RCO.
