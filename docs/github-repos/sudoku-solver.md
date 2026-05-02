---
comments: true
---

# Sudoku Solver

[GitHub Repository](https://github.com/reynardo-tjhin/sudoku-solver)

The Sudoku Solver is written in C. The purpose of this project is to challenge myself to implement Depth-First Search (DFS) Algorithm in C.

## How to Solve Sudoku

If you don't know how to play Sudoku, please read [Sudoku Generator](../sudoku-generator/#about-the-game).

We can solve a Sudoku by using a brute-force approach. Consider the following unsolved simpler 4x4 sudoku:

```txt
+-----+-----+
| 1 - | - 4 |
| - 4 | - 2 |
+-----+-----+
| 2 - | 4 - |
| - 3 | - 1 |
+-----+-----+
```

For the first row second column, we can try with the numbers "2" or "3". For demonstration purposes, let's start with "3".

```txt
+-----+-----+
| 1 3 | - 4 |
```

We can then do the same for the next block (first row third column). We input the number "2" (since the only number left is "2").

```txt
+-----+-----+
| 1 3 | 2 4 |
| - 4 | - 2 |
+-----+-----+
```

However, we then realise that the number "2" breaks the rule of Sudoku - two of the same numbers cannot appear in the same box. Therefore, we have to **backtrack** to the first row second column. Since we have used up "3", the correct and only answer would be "2". Hence, we have the following:

```txt
+-----+-----+
| 1 2 | - 4 |
| - 4 | - 2 |
+-----+-----+
```

We can do the same to the next unsolved block until we solve the whole Sudoku.

## The Implementation

### Data Structure

A 9x9 sudoku is an array of `sudoku_node` with a length of 81.

Each `sudoku_node` has next and previous pointers to another `sudoku_node`. The first row first column of the sudoku has no previous pointer, while the last row last column of the sudoku has no next pointer.

```c
// @ sudoku.h
struct sudoku_node {
    int id; // unique id for each node
    int data; // stores data; if data is 0 means it is not solved yet

    struct sudoku_node* next; // next sudoku node
    struct sudoku_node* prev; // prev sudoku node
    
    int is_solved; // indicates whether it is already there

    // if it is solved, array is full of zeroes
    int* possible_solutions; // [ 1, 2, 3, 4, 5, 6, 7, 8, 9 ]

    // there are 20 neighbours for each node
    struct sudoku_node** neighbours;
};
```

Each `sudoku_node` has 20 `sudoku_node` as neighbours. A neighbour is the node that is either on the same row, same column or same box.

- For each row, a sudoku node has 8 neighbors.
- For each column, a sudoku node has another 8 neighbors.
- For each box, there are an additional 4 neighbors since 4 are already counted in the rows and the columns.

Visually (where x is the target node and n is the neighbor of the target node)
```txt
+-------+-------+-------+
| x n n | n n n | n n n |
| n n n |       |       |
| n n n |       |       |
+-------+-------+-------+
| n     |       |       |
| n     |       |       |
| n     |       |       |
+-------+-------+-------+
| n     |       |       |
| n     |       |       |
| n     |       |       |
+-------+-------+-------+
```

### Flow

The repository strictly only solves 9x9 sudoku. It first takes in the unsolved sudoku from an external file.
```c
// get the file
FILE* fpointer = fopen(argv[1], "r");
```

Then create an array of `sudoku_node` with a length of 81 nodes.
```c
sudoku_node** sudoku = (struct sudoku_node **) malloc(sizeof(struct sudoku_node *) * 81);
```

We read the file with sudoku and create a `sudoku_node` as we find each number
```c
// create the sudoku node here
sudoku_node* new_sudoku_node = (struct sudoku_node *) malloc(sizeof(sudoku_node));
new_sudoku_node->id = id;
new_sudoku_node->data = data;
if (data != 0) { // means the node is already solved
    new_sudoku_node->is_solved = 1;
    // initialize the possible solutions as NULL since it is already solved
    new_sudoku_node->possible_solutions = NULL;
} else {
    new_sudoku_node->is_solved = 0;
    // initialize the possible solutions
    new_sudoku_node->possible_solutions = (int *) calloc(9, sizeof(int));
    for (int i = 1; i < 10; i++) {
        new_sudoku_node->possible_solutions[i - 1] = i;
    }
}
```

The `id` in the sudoku is like the following
```txt
+----------+----------+----------+
|  0  1  2 |  3  4  5 |  6  7  8 |
|  9 10 11 | 12 13 14 | 15 16 17 |
...
| 72 73 74 | 75 76 77 | 78 79 80 |
+----------+----------+----------+
```

After initialising all 81 of the `sudoku_node`, we can then update the `prev` and `next` pointers of each `sudoku_node`. While iterating each of the `sudoku_node`, we also update the neighbours of the nodes. This is evident from Lines 94 to 178.

After all the `sudoku_node` are initialised completely, we perform the DFS.
```c
int no_solution = 0;
int has_backtrack = 0;
sudoku_node* current_sudoku_node = sudoku[0];
while (current_sudoku_node != NULL) {

    // we first check if the current node is already solved
    // if it is solved, there are two posibilities
    // 1. we are currently backtracking, therefore, we need to go to the previous node
    //    because we saw the next node broke the rule of sudoku
    // 2. we are not backtracking, therefore, we have found a potential solution

    // backtrack flag is set
    // perform the backtrack
    if (has_backtrack) {
        // reset the backtrack flag
        has_backtrack = 0;

        // get the most recent data
        int i = 0;
        for (i = 0; i < 9; i++) {
            if (current_sudoku_node->possible_solutions[i] != 0) {
                int data = current_sudoku_node->possible_solutions[i];
                current_sudoku_node->data = data;
                // remove the found index
                current_sudoku_node->possible_solutions[i] = 0;
                break;
            }
        }

        // check if need to backtrack again
        if (i == 9) {
            has_backtrack = 1;
            // reset the data
            current_sudoku_node->data = 0;
            // reset the possible solutions
            for (int j = 1; j < 10; j++) {
                current_sudoku_node->possible_solutions[j - 1] = j;
            }
            current_sudoku_node = current_sudoku_node->prev;
            if (current_sudoku_node == NULL) {
                no_solution = 1;
                printf("program can't solve! author is dumb!\n");
            }
        }
        else {
            current_sudoku_node = current_sudoku_node->next;
        }
    }
    // backtrack flag is not set
    // we continue solving like normal
}
```

## Afterword

My small project obviously can be further improved. There are better ways to solve a sudoku than using DFS or bruteforce approach. I will look into this again when I have the motivation (or when I'm better at DSA) 🤫.
