from collections import deque

def build_graph(example: int = 1) -> dict[str, list[str]]:
    
    # initialise the edge list and vertex names
    edge_list: list[tuple[str, str]] = []
    vertex_names: list[str] = []

    # example 1
    if (example == 1):
        # build the edge list
        edge_list = [
            ("A", "B"), ("A", "C"),
            ("B", "D"), ("B", "E"),
            ("C", "F"), ("C", "G"),
            ("D", "H"), ("E", "H"), ("F", "H"), ("G", "H")
        ]
        vertex_names = ["A", "B", "C", "D", "E", "F", "G", "H"]
    
    # example 2: complete graph
    else:
        # build the edge list
        edge_list = [
            ("A", "B"), ("A", "C"), ("A", "D"),
            ("B", "C"), ("B", "D"),
            ("C", "D")
        ]
        vertex_names = ["A", "B", "C", "D"]

    # build the adjacency list
    adjacency_list: dict[str, list[str]] = {}
    for vertex_name in vertex_names:
        if (adjacency_list.get(vertex_name) is None):
            adjacency_list[vertex_name] = []
    
    # add the edges
    for u, v in edge_list:
        adjacency_list.get(u).append(v)
        adjacency_list.get(v).append(u)

    return adjacency_list


def bfs_mark_on_enqueue(adjacency_list: dict[str, list[str]], start_node: str) -> list[str]:
    """
    the preferred way - the efficient way
    """
    # define the three variables: queue, visited and the current node
    queue: deque[str] = deque([start_node])
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


def bfs_mark_on_dequeue(adjacency_list: dict[str, list[str]], start_node: str) -> list[str]:
    """
    the inefficient way
    """
    # define the three variables: queue, visited and the current node
    queue: deque[str] = deque([start_node])
    visited: set[str] = set()
    cur_node: str = start_node
    
    # define the output
    order: list[str] = []
    
    # iteratively perform the BFS traversal
    while (len(queue) != 0):
        cur_node = queue.popleft() # queue is first-in-first-out (FIFO)
        if (cur_node in visited):
            continue
        visited.add(cur_node)
        order.append(cur_node)
        for v in adjacency_list.get(cur_node):
            if (v not in visited):
                queue.append(v)
                
    return order


def main():
    
    # step 1: build the graph
    adjacency_list: dict[str, list[str]] = build_graph(example=2)
    
    # step 2: bfs mark on enqueue
    order: list[str] = bfs_mark_on_enqueue(adjacency_list, "A")
    for o in order:
        print(o, end=" ")
    print()

    # step 3: bfs mark on dequeue
    order: list[str] = bfs_mark_on_dequeue(adjacency_list, "A")
    for o in order:
        print(o, end=" ")
    print()


if (__name__ == "__main__"):
    main()