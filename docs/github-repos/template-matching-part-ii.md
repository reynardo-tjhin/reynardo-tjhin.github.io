---
comments: True
---

# Template Matching Part II

[GitHub Repository](https://github.com/reynardo-tjhin/template-matching/)

The continuation of Template Matching Part I. In this page, we will focus on how to optimise the algorithm, mainly on generating the SSD map. 

Generating the SSD map requires sliding each window and perform SSD calculation between each window and the template. 

In the lab exercie:

- the image has $1,053$ rows and $745$ columns of pixels, and 
- the template has $108$ rows and $81$ columns of pixels. 

That's $(1,053 - 108 + 1) * (745 - 81 + 1) = 946 * 665 = 629,090$ **_SSD_** calculations. 

And each SSD calculation, we need to perform

- $108 * 81 = 8,748$ subtractions
- $108 * 81 = 8,748$ power of 2 calculations
- $108 * 81 = 8,748$ additions

That brings us to $8,748 * 3 * 629,090 = 16,509,837,960$ calculations. Of course, the calculation involving power of 2 is way more expensive than subtraction and addition so the number alone is sort of an exaggeration. But, you get the point. Hence, we need to speed up generating the SSD map.

## Optimisation I: Parallel Programming

Running the heavy maths operation using the CPU will take a very long time since it performs the calculations sequentially (around 20 minutes in this exercise). Since I have an NVIDIA RTX 3050 Ti Mobile, I thought why not write a parallel code to speed up the calculations 🤔? So, I learnt how to code CUDA programming 🙂.

Read the docs here 📖: [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/index.html).

### CUDA Programming: Basic Terms

| Term | Meaning |
|:-----|:--------|
| host | the CPU |
| host memory | memory (or the RAM) |
| device | the GPU |
| device memory | GPU memory (or the VRAM) |
| device code | the code an application executes on the GPU |
| kernel | the function that is invoked for execution on the GPU |

### CUDA Programming: Basic Points to Know

- Applications always start the executions on the CPU first.
- Then, the data is copied from the host memory to the device memory using CUDA APIs. 
- The code on the GPU will then get executed once the data transfer is completed.

### CUDA Programming: GPU Hardware Model

- A GPU consists of the following components
    - PCIe or NVLINK
    - L2 Cache
    - Memory Controller
    - Groups of Graphics Processing Clusters (GPCs)
- A single **__Graphics Processing Cluster (GPC)__** consists of multiple **__Streaming Multiprocessors (SMs)__**.
- Each **__Streaming Multiprocessor (SM)__** contains a local register file, a unified data cache, and a number of functional units that perform computations.
- Each SM has one or more **__active thread blocks__**.
- **__Thread blocks__** contains many **__threads__**, and these thread blocks are organised into a **__grid__**.
    - A kernel launch defines a grid of thread blocks.
    - For e.g. we could launch 3 separate kernels, each with a grid of 10 blocks of 100 threads. Then we have the total threads across all kernels $= 3 * 10 * 100 = 3,000$ threads.
    - At any moment, an SM might have only **__a few active blocks__** from any of those kernels (depending on resources). If an SM holds **__3 active blocks__** (from whatever kernel), then **__at most 300 threads__** are executing concurrently on that SM.
    - A little caveat: Not all $3,000$ threads will run at once.

!!! info Thread Block Clusters

    Since my CUDA compute capability is 8.6, I won't discuss thread block clusters, which is only available to GPUs with compute capability of 9.0 or higher.

```txt
+------------------------- GPU --------------------------+
|                                                        |
| +------------+  +--------------------+  +------------+ |
| | PCIe or    |  | L2                 |  | Memory     | |
| | NVLINK     |  | Cache              |  | Controller | |
| +------------+  +--------------------+  +------------+ |
|                                                        |
|                                                        |
|  +--------- GPC --------+    +--------- GPC --------+  |
|  | +----+ +----+ +----+ |    | +----+ +----+ +----+ |  |
|  | | SM | | SM | | SM | |    | | SM | | SM | | SM | |  |
|  | +----+ +----+ +----+ |    | +----+ +----+ +----+ |  |
|  +----------------------+    +----------------------+  |
|                                                        |
+--------------------------------------------------------+


 ________________ SM __________________
| Register File   | Unified Data Cache |
| File            | (L1 Cache +        |
|                 | Shared Memory)     |
|_________________|____________________|
|__|__|__|__|__|__|__|__|__|__|__|__|__|
|__|__|__|__|__|__|__|__|__|__|__|__|__|
|__|__|__|__|__|__|__|__|__|__|__|__|__|


A grid contains x * y * z number of thread blocks
↓: indicates a single thread
+------------------- Grid -------------------+
|  __________     __________     __________  |
| |  Thread  |   |  Thread  |   |  Thread  | |
| |  Block   |   |  Block   |   |  Block   | |
| |          |   |          |   |          | |
| | ↓↓↓↓↓↓↓↓ |   | ↓↓↓↓↓↓↓↓ |   | ↓↓↓↓↓↓↓↓ | |
| |__________|   |__________|   |__________| |
|                                            |
|  __________     __________     __________  |
| |  Thread  |   |  Thread  |   |  Thread  | |
| |  Block   |   |  Block   |   |  Block   | |
| |          |   |          |   |          | |
| | ↓↓↓↓↓↓↓↓ |   | ↓↓↓↓↓↓↓↓ |   | ↓↓↓↓↓↓↓↓ | |
| |__________|   |__________|   |__________| |
|____________________________________________|
```

### Consolidating

Okay, so we understand the basics of the NVIDIA GPU hardware but so what? Parallel programming means we are essentially distributing the workload to different computing nodes. In this case, the workload is calculating the SSD and the computing nodes are the threads in the GPU.

For e.g. My GPU is the NVIDIA Corporation GA107BM [GeForce RTX 3050 Ti Mobile]. It has the following properties.

- SM Count:	$20$
- CUDA Cores: $2,560$
- Max Threads per Thread Block: $1,024$
- Max Grid Dimensions: 
    - $2,147,483,647$ thread blocks ($x$-dimension), 
    - $65,535$ thread blocks ($y$-dimension), 
    - $65,535$ thread blocks ($z$-dimension)
- Max Threads per SM: $1,536$

We assign each thread to calculate the SSD between a window of the input image and the template. Each thread has its own ID. The ID can be calculated like this: `int threadId = blockIdx.x * blockDim.x + threadIdx.x;`

For instance, if the thread belongs to block no $1$ and within the block, the thread has an ID of $512$ (each thread in the block starts from $0$ to $1,023$), then we have the `int threadId = 1 * 1024 + 512 = 1536;`.

Also, my GPU has an SM count of $20$ and each SM has a maximum number of threads of $1,536$. Technically, the maximum number of threads that can be in flight simultaneously across all SMs is $20 * 1,536 = 30,720$. Since we have $629,090$ SSDs, we cannot compute all of them at the same time. But we don't need to worry because the hardware automatically schedules blocks in waves. 

Therefore, we will have $629,090$ number of threads to calculate $629,090$ SSDs in a single kernel launch.

In the previous part, we created a function called `generate_ssd_map(input_img, template)` to create the SSD map. In CUDA programming, we call this function **__a kernel__**. Both perform the same operations. Each thread will execute the kernel operation. Below is the kernel operation.

```cpp title="ssd.cu"
// kernel function
__global__ void ssd(
    int *temp_img, int *inpt_img, double *res, \
    int res_row, int res_col, \
    int temp_row, int temp_col, \
    int input_row, int input_col
) {
    // get the threadId
    int threadId = blockIdx.x * blockDim.x + threadIdx.x;

    // SSD map's shape: (946 rows, 665 cols)
    int start_pos_x = threadId / res_col;
    int start_pos_y = threadId % res_col;

    // template's shape: (108 rows, 81 cols)
    // calculate the ssd
    double sum = 0;
    for (int i = 0; i < 108; i++) {
        for (int j = 0; j < 81; j++) {
            int inpt_img_index = start_pos_x * input_col + start_pos_y;
            int temp_img_index = i * temp_col + j;

            int inpt_img_pixel = inpt_img[inpt_img_index];
            int temp_img_pixel = temp_img[temp_img_index];

            // calculate
            double ssd = pow((temp_img_pixel - inpt_img_pixel), 2);
            sum += ssd;

            start_pos_y += 1;
        }
        start_pos_y = threadId % res_col;
        start_pos_x += 1;
    }
    // store the SSD
    res[threadId] = sum;
}
```

And there we have it, at any instant, we can compute up to $30,720$ SSDs in parallel, compared to only $1$ SSD on a single CPU core. 

## Optimisation? II: Maths

In the first part of optimisation, we use parallel programming to perform the heavy math calculations in generating SSD Map asynchronously. However, it turns out that there is another bottleneck that I found while writing this page. The bottleneck is actually in the maths operations. Let me explain below.

Let's revisit calculating an SSD between an input image and the template. Assuming we have selected a window from an input image.
```txt
window 1                              template
[                                     [
  [ 255., 255., 255.,   0., ... ],      [   0.,   0.,   0., 255., ... ],
  [ 255., 255., 255., 255., ... ],      [   0.,   0.,   0.,   0., ... ],
  [   0.,   0., 255., 255., ... ],      [ 255., 255.,   0.,   0., ... ],
    ...                                    ...
  [ 255., 255., 255.,   0., ... ],      [   0.,   0.,   0., 255., ... ],
]                                     ]
```

Calculating the SSD will be something like this:
```txt
SSD = (0. - 255.)^2 + (0. - 255.)^2 + (0. - 255.)^2 + (255. - 0.)^2 + ...
      + (  0. - 255.)^2 + (  0. - 255.)^2 + (  0. - 255.)^2 + (  0. -   0.)^2 + ...
      + (255. -   0.)^2 + (255. -   0.)^2 + (  0. - 255.)^2 + (  0. - 255.)^2 + ...
      + ...
      + (  0. - 255.)^2 + (  0. - 255.)^2 + (  0. - 255.)^2 + (255. -   0.)^2 + ...
      
SSD = ( -255. )^2 + ( -255. )^2 + ( -255. )^2 + ( 255. )^2 + ...
      + ( -255. )^2 + ( -255. )^2 + ( -255. )^2 + (    0. )^2 + ...
      + (  255. )^2 + (  255. )^2 + ( -255. )^2 + ( -255. )^2 + ...
      + ...
      + ( -255. )^2 + ( -255. )^2 + ( -255. )^2 + (  255. )^2 + ...
```

As we can see, there are lots of calculations involving $255^2$. If we consider the exercise's input image and template size ($108$ rows and $81$ cols), in the worst case scenario, we will need to calculate $108 * 81 = 8,748$ number of times of $255^2$ . And that is only a single SSD. The code will end up performing many power of 2 calculations.

One way to solve this issue is by caching the result of $255^2$ and reuse it instead of recalculating it. However, I have another idea in mind. Since we only use two numbers (0 and 255) to represent a pixel, what if we change 255 to 1 to represent the number "255" pixel? It should still work because we are still dealing with only two numbers. We are also still using the same formula. However, after generating the SSD map, we will need to revert back the number "1" to number "255".

We can change "255" to "1" by modifying the preprocessing step.
```py
# perform the image preprocessing
template[template < 128] = 0
template[template > 127] = 1 # instead of 255
template = 1 - template
```

We also need to add a postprocessing step to revert back to 255.
```py
# perform the image postprocessing
template[template >= 1] = 255 # revert back to 255
```

This cuts down the time taken to generate the SSD using ONLY the CPU from 20+ minutes to only about 5+ seconds. If we use GPU to execute the parallel programming, this will take only around 2+ seconds, which shows minimal improvement. Therefore, one key takeaway from this exercise is that we should not only see an optimisation problem as an engineering problem. Sometimes, a bit of maths tricks can speed up the solution as well.

A little caveat is that if the image has a wide range of pixels (for e.g. in colorful images), then this optimisation step will not work.

## Afterword

What's the point? Yes, the CUDA code may not be portable. Yes, the CUDA code uses hardcoded numbers which are not considered a good practice. However, I am happy that I can write basic CUDA code and understand how it works from reading the documentation. It is my first time writing CUDA code, and may be my last time depending on my work in the future. I hope I can look back and see how stupid I am in writing all these 😁.
