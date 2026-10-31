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


def dfs_mark_on_push(adjacency_list: dict[str, list[str]], start_node: str) -> list[str]:
    
    # define three variables: stack, visited and the current node
    visited: set[str] = {start_node}
    stack: list[str] = [start_node]
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


def main():
    
    # step 1: build the graph
    adjacency_list: dict[str, list[str]] = build_graph(example=2)
    
    # step 2: dfs mark on push variant
    order: list[str] = dfs_mark_on_push(adjacency_list, "A")
    for o in order:
        print(o, end=" ")
    print()
    
    # step 3: dfs mark on pop variant
    order: list[str] = dfs_mark_on_pop(adjacency_list, "A")
    for o in order:
        print(o, end=" ")
    print()
    

if (__name__ == "__main__"):
    main()
