---
comments: true
---

# Template Matching Part I

[GitHub Repository](https://github.com/reynardo-tjhin/template-matching/)

Template matching is a digital image processing technique used to find the coordinates/location of a small template image in a given input image.

For example, given the following input and template, the input image contains the template in 2 areas (`[(1,1), (2,2)]` and `[(2,7), (3,8)]`).
```txt
               input_image:        template:

          0    0000000000          11
          1    0110000000          11
          2    0110000110
          3    0000000110
          4    0000000000
          5    0000000000

coordinates    0123456789          01
```

It uses several concepts including:

- Sum of Square Distances (SSD)But how do we measure the difference
- Sliding Window technique
- Non-min Suppression or Non-max Supression (NMS)

## Concept 1: Sum of Squared Distance (SSD)

### Distance Between 2 Pixels

Imagine we have two points on a linear plane.
```txt
       A                    B
<---|--|--|--|--|--|--|--|--|--|--->
    0  1  2  3  4  5  6  7  8  9
```

We observe that

- If the distance between the two points is $> 0$, then both points are different.
- Otherwise, if the distance between the two points is excatly $0$, then both points are the same.

Based on the linear plane above, the distance between A and B is $(8 - 1) = 7$ and $7 > 0$, hence points A and B are different. Since we don't want the distances to be negative, we perform a power of 2 on the distance calculation. Hence, the "distance" between A and B becomes $(8 - 1)^2 = 49$.

!!! info Absolute Distance

    Technically, we can use absolute operation ($|A - B|$) instead of power of 2 on the distance calculation. But, we want to **emphasise** the differences. It means that the points that are very different will have a way higher distance number compared to the points that are closer to each other. Therefore, it will be easier to recognise the points that are similar/the same. Also, it makes much more sense to use power of two in higher dimensions like in the next section.
    
!!! info Square Root

    We don't have to calculate the square root of the result because we are just checking whether the "distance" number is 0 or not.

To wrap up this section, we can conclude that given a one-dimensional plane, two points are the same if the distance between them is 0, otherwise, they are different. The "distance" can be calculated using the following.

$$
distance^2 = (A - B)^2
$$

### Sum of Squared Distance (SSD)

Previously, we only compare whether two points are the same in a one-dimensional plane. What if we have to compare between two points that are in two-dimensional plane? We can map the two points in a two-dimensional plane like below.

```txt
   |
6 -+                        B (5,6)
   |                        |
5 -+                        |
   |                        |
4 -+                        |
   |                        |
3 -+                        |
   |                        |
2 -+    A ------------------+
   |  (1,2)
1 -+
   |
0 -+----+----+----+----+----+----+--->
   0    1    2    3    4    5    6
```

Then to determine whether the two points are the same, we can use the same approach like the one-dimensional plane example, i.e. we calculate the distance.

$$
distance^2 = (6 - 2)^2 + (5 - 1)^2 = 16 + 16 = 32
$$

Since the distance is greater than $0$, we can say that points A and B are different. What if we increase the dimension from two dimensions to three dimensions? We can actually use the same formula to calculate the distance. Sadly, I cannot show the 3D graph here 😔.

$$
distance^2 = (A_{1} - B_{1})^2 + (A_{2} - B_{2})^2 + (A_{3} - B_{3})^2
$$

My brain cannot imagine how 4-dimensions work. But I believe that we can use the same formula to calculate the distance. I am not maths PhD (or maths master, anyway I suck at maths) so I cannot prove, unfortunately 😔. Therefore, we arrive at

$$
distance^2 = \sum_{i = 1}^{n}{(A_{i} - B_{i})^{2}}
$$

But how do we relate this to image? An image is essentially a 2-dimensional array (Don't confuse this dimension with the above. Just treat it as different.). This sounds confusing but not really. Let's say we have the following black and white image where "1" represents the white pixel and "0" represents the black pixel.
```txt
image.png

   0000110000
   0011110000
   0010110000
   0000110000
   0011111100
```

If we encode the image to python numpy array, we will see something like the following.
```py
img = [
    [0., 0., 0., 0., 1., 1., 0., 0., 0., 0.],
    [0., 0., 1., 1., 1., 1., 0., 0., 0., 0.],
    [0., 0., 1., 0., 1., 1., 0., 0., 0., 0.],
    [0., 0., 0., 0., 1., 1., 0., 0., 0., 0.],
    [0., 0., 1., 1., 1., 1., 1., 1., 0., 0.],
]
```

But it is no different from
```py
# collapse
img = [
    0., 0., 0., 0., 1., 1., 0., 0., 0., 0.,
    0., 0., 1., 1., 1., 1., 0., 0., 0., 0.,
    # and so on...
]
```

Now we can use the same formula to calculate the distance. But with a little tweak, we don't have to collapse the image 2d array to 1d. Hence, we get the following formula to calculate the distance.

$$
distance^2 = \sum_{(x,y) \in A,B}{(A(x, y) - B(x,y))^{2}}
$$

As an example, let's assume we have a target image (2x2 pixels) and another image (2x2 pixels).

```txt
target:    image:
1 1        1 1
0 1        1 1
```

From a glance, we can tell that the image is not the same as the target. But computers don't know, so we have to ask them to calculate and deduce from the result.

**Note**: I start $x$ and $y$ from $1$ to indicate the row and column numbers.

To calculate the "distance" between the image and the target

$$
distance^2 = (T(1,1) - I(1,1))^2 + (T(1,2) - I(1,2))^2 + (T(2,1) - I(2,1))^2 + (T(2,2) - I(2,2))^2
$$

$$
distance^2 = (1 - 1)^2 + (1 - 1)^2 + (0 - 1)^2 + (1 - 1)^2 = 1
$$

Since the $distance^2$ is non-zero, we can conclude that the image and target are not the same. And there we have it. $distance^2$ is essentially Sum of Squared Distances. Formally,

$$
SSD_{M} = \sum_{(x,y) \in P_{M}}{(T(x, y) - P_{M}(x,y))^{2}}
$$

If $SSD_{M} > 0$, then the image and the template are the same. Otherwise, they are different. 

## Concept 2: Sliding Window Technique

We know how to calculate the $SSD_{M}$, and we know that we need two images of the same shape to calculate the $SSD_{M}$. However, what if the image is bigger than the other image (or the template)? Hence, we need to use a technique called the Sliding Window Technique.

We create a window of the same size as the template image. And then we slide this window from left to right, top to bottom, and calculate the SSD between each window to the template image.

Consider we have an input image of size $6*10$ pixels ($6$ rows and $10$ columns of pixels) and we have a template image of $2*2$ pixels ($2$ rows and $2$ columns of pixels). Each number represents a single pixel.

```txt
input_image:    template:

0000000000      11
0110000000      11
0110000000
0000000110
0000000110
0000000000
```

The window size matches the template's size. We slide the window from left to right, top to bottom, like below:

```txt
1st window      2nd window     3rd window   ... 9th window
+--+             +--+            +--+                   +--+
|00|00000000    0|00|0000000   00|00|000000     00000000|00|
|01|10000000    0|11|0000000   01|10|000000     01100000|00|
+--+             +--+            +--+                   +--+
 01 10000000    0 11 0000000   01 10 000000     01100000 00
 00 00000110    0 00 0000110   00 00 000110     00000001 10
 00 00000110    0 00 0000110   00 00 000110     00000001 10
 00 00000000    0 00 0000000   00 00 000000     00000000 00


10th window     11th window    12th window  ... 18th window
 00 00000000    0 00 0000000   00 00 000000     00000000 00
+--+             +--+            +--+                   +--+
|01|10000000    0|11|0000000   01|10|000000     01100000|00|
|01|10000000    0|11|0000000   01|10|000000     01100000|00|
+--+             +--+            +--+                   +--+
 00 00000110    0 00 0000110   00 00 000110     00000001 10
 00 00000110    0 00 0000110   00 00 000110     00000001 10
 00 00000000    0 00 0000000   00 00 000000     00000000 00

and so on...
```

In the above example, we would have $9*5$ windows ($45$ windows in total). This can be calculated by the following steps

1. Calculate the number of times the window has to slide left to right and top to bottom
    - Number of times the window slides from left to right = (number of cols in the input image - number of cols in the template) + 1 = $(10 - 2) + 1 = 9$
    - Number of times the window slides from top to bottom = (number of rows in the input image - number of rows in the template) + 1 = $(6 - 2) + 1 = 5$

2. Calculate the total number of windows
    - Then the total number of windows is the multiplication of the above results.

The $9*5$ windows is also called the **_SSD map_**. Then as we slide each window, we calculate the SSD between that window and the template. In the above example, we will have an **_SSD map_** that looks like the below.

```txt
SSD_map

323444444
202444444
323444323
444444202
444444323
```

Notice there are two spots with $SSD = 0$. That means we have two windows that exactly match the template in the image.

## Concept 3: Non-min Suppression or Non-max Supression (NMS)

From the **_SSD map_**, we can easily spot the 2 windows that exactly match the template in the image. But how do we find the location? We use Non-min Suppression or Non-max Suppression (NMS) to locate them.

I will explain using the above example.

1. Firstly, we need to find the first coordinate in the **_SSD map_** that has the **lowest SSD value**. It is located in the **second row, second column**.

    ```txt
    3 2 3444444
     +-+
    2|0|2444444
     +-+
    3 2 3444323
    4 4 4444202
    4 4 4444323
    ```
2. We store this coordinate as a match. Then, we need to set the value in this coordinate and its neighbors to the maximum value found in the SSD map.

    ```txt
    444444444
    444444444
    444444323
    444444202
    444444323
    ```

3. We repeat the steps 1 and 2 again. Notice that the first coordinate we found that has the lowest SSD value is now in the **fourth row, eighth column** because we have set the previous coordinate to the maximum. And then we continue with step 2.

4. After all the iterations, we have found all the target coordinates.

!!! info

    In this exercise, we hardcoded the number of targets (or target coordinates) as 5. Therefore, we don't necessarily have to find the coordinate with the SSD value as 0.

## Combining Everything

In the GitHub repository, we have the input image (`./input/input.png`) and the template image (`./input/template.png`).

Firstly, we need to load both images as numpy arrays
```py title="main.py"
template = imread('./input/template.png', pilmode='L') # grayscale
input_img = imread('./input/input.png', pilmode='L') # grayscale
```

We then perform image preprocessing.
```py title="main.py"
template[template < 128] = 0
template[template > 127] = 255
template = 255 - template # 255 is the max value for a single channel
```

Afterwards, we generate the SSD map.
```py title="main.py"
def generate_ssd_map(
    input_img: np.ndarray,
    template: np.ndarray,
) -> np.ndarray:
    """
    Generate an SSD map.

    :param input_img: the input image in np array
    :param template: the template in np array
    """
    # get the shape
    input_img_rows = input_img.shape[0]
    input_img_cols = input_img.shape[1]

    template_rows = template.shape[0]
    template_cols = template.shape[1]

    # get the ssd_map shape
    ssd_map_no_of_rows = input_img_rows - template_rows + 1
    ssd_map_no_of_cols = input_img_cols - template_cols + 1

    # generate the ssd_map
    ssd_map = np.zeros((ssd_map_no_of_rows, ssd_map_no_of_cols))
    for row in range(ssd_map_no_of_rows):
        for col in range(ssd_map_no_of_cols):

            row_start = row
            row_end = row_start + template_rows

            col_start = col
            col_end = col_start + template_cols

            # create the window in the input image
            input_img_intermediate = input_img[row_start:row_end, col_start:col_end]

            # step 1: diff
            diff = template - input_img_intermediate

            # step 2: square
            square = diff ** 2
            
            # step 3: sum
            total = np.sum(square)

            # step 4: assign valueget_ssd_map to ssd_map
            ssd_map[row, col] = total

    return ssd_map
```

We then use NMS to locate the matches.

```py title="main.py"
temp_row = template.shape[0]
temp_col = template.shape[1]

target_num = 5 # hardcoded number
target_res = []

i = 0
while (i < target_num):

    local_max = np.max(ssd_map)
    local_min = np.min(ssd_map)
    x, y = np.where(ssd_map == local_min)
    x, y = x[0], y[0]

    # store the match
    target_res.append((x, y))

    # set the match and its neighbors to max value
    for row in range(x-temp_row, x+temp_row):
        for col in range(y-temp_row, y+temp_col):
            if (row >= ssd_map.shape[0] or row < 0 or col >= ssd_map.shape[1] or col < 0):
                continue
            ssd_map[row, col] = local_max

    i += 1
```

## Afterword

In this part, I try to explain how template matching can be performed on images. I first explain how to calculate the SSD between two images. Then, I describe how sliding window technique can be used to locate the create an SSD map that helps to locate the matches. In the next section, I will be discussing on how I "optimised" the code 😊.
