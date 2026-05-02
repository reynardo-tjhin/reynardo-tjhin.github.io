---
comments: true
---

# Sudoku Generator

[GitHub Repository](https://github.com/reynardo-tjhin/sudoku-generator)

The sudoku generator was implemented in Python. It uses a modified version of Fisher-Yates' Algorithm. The algorithm is used to randomise the numbers within an array.

## About the Game

Before going to the implementation, we should try to understand the Sudoku game. In sudoku, the rule is basically a number cannot appear twice in the same row, same column or same box.

For e.g. the 4x4 sudoku below
```txt
+-----+-----+
| 1 2 | 3 4 |
| 3 4 | 1 2 |
+-----+-----+
| 2 1 | 4 3 |
| 4 3 | 2 1 |
+-----+-----+
```

Notice that "1" does not appear in the same row, same column and the same box.
```txt
# the first row
+-----+-----+
| 1 2 | 3 4 |

# the first column
+---
| 1
| 3
+---
| 2
| 4
----

# the first box
+-----+
| 1 2 |
| 3 4 |
+-----+
```
All the numbers in the sudoku will also need to follow the same rule. The same goes for 9x9 sudoku.

And... basically that's it 😊!

## Understanding Fisher-Yates' Algorithm

The Fisher-Yates' algorithm focuses on swapping items within the data structure holding the items. The algorithm can be defined like the following
```txt
def FisherYates(A):
    # permute A in place
    n = length of array A

    for i in {0, 1, ..., n - 1} do
        # swap A[i] with random position
        j = random number in {i, ..., n - 1}
        A[i], A[j] = A[j], A[i]
    
    return A
```

For e.g. if we want to randomise the numbers inside the following array.
```txt
arr = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

i = 0:  randomly generate a no from a range of [0, 9] for j
        we swap i = 0 with j = 3 
        arr = [3, 1, 2, 0, 4, 5, 6, 7, 8, 9]

i = 1:  randomly generate a no from a range of [1, 9]; cannot be smaller than 0
        we swap i = 1 with j = 1 
        arr = [3, 1, 2, 0, 4, 5, 6, 7, 8, 9] # did not change

i = 2   randomly generate a no from a range of [2, 9]
        we swap i = 2 with j = 6 
        arr = [3, 1, 6, 0, 4, 5, 2, 7, 8, 9]

and so on...
```
At the end of the iteration, we will see an array with random numbers.

## Implementation

Let's simplify to a 4x4 sudoku. Basically, we start with a solved sudoku.
```txt
+-----+-----+
| 1 2 | 3 4 |
| 3 4 | 1 2 |
+-----+-----+
| 2 1 | 4 3 |
| 4 3 | 2 1 |
+-----+-----+
```

To randomise the sudoku using Fisher-Yates' Algorithm, we need to perform swapping but it needs to follow two main rules.

### First Rule

We can **only** swap the number with the numbers that are within the same row, same column or same box. For e.g. the first row first column number "1" in the above example can only be swapped within the same row, same column and same box.

Reason is explained in the ['Continuation' section](/docs/github-repos/sudoku-generator/#continuation)

### Second Rule

We can **only** swap the next number. The reason why we do not swap with numbers before is because the previous numbers are already randomised. Hence, there might be a possibility that we will swap the same number again and retain the same sudoku.

For example for the second rule
```txt
            swap                       swap
            (0,0)                      (3,0)
            and                        and
            (0,3)                      (0,0)
+-----+-----+     +-----+-----+             +-----+-----+
| 1 2 | 3 4 |     | 4 2 | 3 1 |             | 1 2 | 3 4 |
| 3 4 | 1 2 |     | 3 1 | 4 2 |             | 3 4 | 1 2 |
+-----+-----+ --> +-----+-----+ --> ... --> +-----+-----+
| 2 1 | 4 3 |     | 2 4 | 1 3 |             | 2 1 | 4 3 |
| 4 3 | 2 1 |     | 1 3 | 2 4 |             | 4 3 | 2 1 |
+-----+-----+     +-----+-----+             +-----+-----+
```

### Continuation

Let's continue. From the solved sudoku, suppose we swap **1st row 1st column** with the **2nd row 4th column** which is a number "2". We will get the following.
```txt
+-----+-----+
| 2 2 | 3 4 |
| 3 4 | 1 1 |
+-----+-----+
| 2 1 | 4 3 |
| 4 3 | 2 1 |
+-----+-----+
```

We now notice that the sudoku is incorrect. Hence, we have to swap the other numbers "1" and "2" which results to this:
```txt
+-----+-----+
| 2 1 | 3 4 |
| 3 4 | 2 1 |
+-----+-----+
| 1 2 | 4 3 |
| 4 3 | 1 2 |
+-----+-----+
```
The sudoku is now correct.

Now, why can't we just randomly swap? Why do we have to follow the first rule? Let's say if we don't follow that rule. Assuming that we can swap with any number within the sudoku, take the above sudoku as an example, we can swap the **1st row 1st column** (number "1") with **3rd row 3rd column** (number "4"). Now, we have
```txt
+-----+-----+
| 4 2 | 3 4 |
| 3 4 | 1 2 |
+-----+-----+
| 2 1 | 1 3 |
| 4 3 | 2 1 |
+-----+-----+
```
We can't swap the rest of the "1"s and "4"s because in the first row, we already have a conflict of "4"s. Hence, we cannot just randomly swap the numbers.

Now, we just need to keep going through the whole sudoku and swap random numbers. We will finally have a random sudoku.

## Afterward

I realise I suck at explaining. I hope you can understand my explanation 🫣.
