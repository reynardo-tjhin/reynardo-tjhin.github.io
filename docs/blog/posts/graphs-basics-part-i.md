---
title: Graphs Basics Part I - Representation
slug: graphs-basics-part-i
date: 2026-10-24
categories:
- Data Structures and Algorithms
description: Basics of Graphs Part I - Representation
comments: true
---

# Graphs Basics Part I: Representation

Before we can run BFS, DFS, or Dijkstra, we need a way to actually store a graph. This part covers the three standard representations — adjacency matrix, adjacency list, and edge list — with Python code and a cheat sheet for picking between them.

<!-- more -->

A **graph** $G = (V, E)$ is a set of vertices (nodes) $V$ together with a set of edges $E$, where each edge connects a pair of vertices. Examples of how graphs can be used in our daily lives: a road map (intersections are vertices, roads are edges), a social network (people, follow relationships), a build system (tasks, dependency order).

On the other hand, a **tree** is a graph — specifically a connected graph with no cycles. Trees have a root and a parent-before-child hierarchy; general graphs have neither, which means an edge can point "backwards," a vertex can have many neighbours with no hierarchy between them, and you can walk in circles, so traversal algorithms need a visited set.

This post assumes undirected, unweighted graphs — directed edges and weights change the picture and are out of scope here.

## Representations

There are 3 ways to represent a graph:

1. Adjacency Matrix (2D Matrix)
2. Adjacency List
3. Edge List

Our running example throughout this post will be a 4-cycle:

```txt
0 - 1
|   |
2 - 3
```

The four edges are $(0,1), (0,2), (1,3), (2,3)$: keep that list in mind, it appears in every code sample. In the following examples, each vertex in the graph is represented as an integer.

### 1. Adjacency Matrix

* a 2D matrix: Edge $(i,j)$ is stored at `matrix[i][j]` (and `matrix[j][i]` since the graph is undirected); the cell is `1` if the edge exists, `0` otherwise.

| | Details |
|---|---|
| Advantages | <ul><li>$O(1)$ edge lookup</li><li>very simple</li><li>great for dense graphs — when $E \approx V^2$ the matrix wastes almost nothing and its $O(1)$ lookup beats the list's $O(\deg(u))$</li></ul> |
| Disadvantages | <ul><li>$O(V^{2})$ memory: unusable for $\lvert V \rvert = 10^{5}$</li><li>getting the neighbours requires $O(V)$</li></ul> |

* An example representation in Python code would be:

```py
# define the number of vertices
V: int = 4

# adjacency matrix is a 2D matrix of size |V| * |V|
matrix: list[list[int]] = [[0] * V for _ in range(V)]

# define the function to add edge in the graph
def add_edge(matrix: list[list[int]], u: int, v: int) -> None:
    matrix[u][v] = 1
    matrix[v][u] = 1

# define the edges list
edges: list[tuple[int, int]] = [(0,1), (0,2), (1,3), (2,3)]

# add the edges for the graph
for u, v in edges:
    add_edge(matrix, u, v)
```

* After running, the structure is:

```py
matrix: list[list[int]] = [
# vertex 0, 1, 2, 3
       [ 0, 1, 1, 0 ], # vertex 0
       [ 1, 0, 0, 1 ], # vertex 1
       [ 1, 0, 0, 1 ], # vertex 2
       [ 0, 1, 1, 0 ], # vertex 3
]
```

* Notice that the matrix is symmetric along the diagonal axis because the graph is undirected.
* If the value in `matrix[i][j]` where `i = j` is equal to `1`, then there is a self-loop within the vertex.

* Common operations:

```py
# getting the neighbours of u
def neighbours(matrix: list[list[int]], u: int) -> list[int]:
    return [v for v in range(len(matrix)) if matrix[u][v]]

# edge check: does vertex u and v have an edge
def has_edge(matrix: list[list[int]], u: int, v: int) -> bool:
    return matrix[u][v] != 0
```

### 2. Adjacency List

* The default choice — $O(V+E)$ memory handles the sparse graphs real problems have.
* The list at index $u$ stores all of $u$'s neighbours.

| | Details |
|---|---|
| Advantages | <ul><li>$O(V + E)$ memory</li><li>$O(\deg(u))$ neighbour iteration</li></ul> |
| Disadvantages | <ul><li>$O(\deg(u))$ edge lookup</li></ul> |

* An example representation in Python code would be:

```py
# define the number of vertices in the graph
V: int = 4

# define the adjacency list
adjacency_list: list[list[int]] = [[] for _ in range(V)]

# define the function to add edge in the graph
def add_edge(adjacency_list: list[list[int]], u: int, v: int):
    adjacency_list[u].append(v)
    adjacency_list[v].append(u)

# define the edges list
edges: list[tuple[int, int]] = [(0,1), (0,2), (1,3), (2,3)]

# add each edge to the adjacency list
for u, v in edges:
    add_edge(adjacency_list, u, v)
```

* After running, the structure is:

```py
adjacency_list: list[list[int]] = [
    [ 1, 2 ], # vertex 0
    [ 0, 3 ], # vertex 1
    [ 0, 3 ], # vertex 2
    [ 1, 2 ], # vertex 3
]
```

* Notice that `adjacency_list[0] = [1, 2]` is exactly the 1-positions of row `0` of the adjacency matrix.
* Note: Storing each neighbour list as a **_set_** instead of a **_list_** turns the $O(\deg(u))$ edge lookup into expected $O(1)$, at a slightly higher memory cost. It's the single most common practical upgrade.

* Common operations:

```py
# getting the neighbours of u
def neighbours(adjacency_list: list[list[int]], u: int) -> list[int]:
    return adjacency_list[u]

# edge check: does vertex u and v have an edge
def has_edge(adjacency_list: list[list[int]], u: int, v: int) -> bool:
    return v in adjacency_list[u]
```

### 3. Edge List

* A list in which each tuple $(u, v)$ is a single edge of the graph.

| | Details |
|---|---|
| Advantages | <ul><li>$O(E)$ memory</li><li>ideal when the algorithm only needs to iterate all edges once, e.g. Kruskal's, Bellman-Ford, building an adjacency list, DSU-driven problems</li></ul> |
| Disadvantages | <ul><li>neighbours and edge lookup are both $O(E)$ full scans</li><li>useless for BFS/DFS/matching directly</li></ul> |

* An example representation in Python code would be:

```py
# define the number of vertices
V: int = 4

# define the edge list
edge_list: list[tuple[int, int]] = [ (0,1), (0,2), (1,3), (2,3) ]
```

* Notice that the edge list is exactly the input format most problems give: "the next $E$ lines each contain two vertices."
* Nothing is converted or restructured: read the edges and store them as-is, which is why it costs $O(1)$ to build.
* That's what makes it ideal for algorithms that sweep every edge exactly once — Kruskal's, Bellman-Ford, DSU (all algorithms that work on weighted graphs which are not discussed in this post) — and for one very common job: turning the raw edges into an adjacency list.

* Common Operations:

```py
# getting the neighbours of u
def neighbours(edge_list: list[tuple[int, int]], u: int) -> list[int]:
    n: list[int] = []
    for v_u, v_v in edge_list:
        if u == v_u:
            n.append(v_v)
        elif u == v_v:
            n.append(v_u)
    return n

# edge check: does vertex u and v have an edge
def has_edge(edge_list: list[tuple[int, int]], u: int, v: int) -> bool:
    for v_u, v_v in edge_list:
        if ((u == v_u and v == v_v) or (u == v_v and v == v_u)):
            return True
    return False
```

## Cheat Sheet

| | Adjacency Matrix | Adjacency List | Edge List   |
|---|----------------|----------------|-------------|
| Memory | $O(V^{2})$ | $O(V + E)$ | $O(E)$ |
| Neighbour Iteration | $O(V)$ | $O(\deg(u))$ | $O(E)$ |
| Edge lookup | $O(1)$ | $O(\deg(u))$ | $O(E)$ |
| Build from edges | $O(E)$ | $O(E)$ | $O(1)$ |
| Best for | <ul><li>Dense graphs</li><li>Floyd-Warshall</li></ul> | <ul><li>BFS/DFS</li><li>Matching</li><li>Most problems</li></ul> | <ul><li>Kruskal</li><li>Bellman-Ford</li><li>Input format</li></ul> |

## Acknowledgement

Reviewed by DeepSeek AI model and ISTA-DASLab/Qwen3.8 Flash Next GSQ RCO.
