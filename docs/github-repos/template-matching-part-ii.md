---
comments: True
---

# Template Matching Part II

[GitHub Repository](https://github.com/reynardo-tjhin/template-matching/)

The continuation of Template Matching Part I. In this page, we will focus on how to optimise the algorithm, mainly generating the SSD map. Generating the SSD map requires sliding each window and perform SSD calculation in each window. In this exercies, that's $946 * 665 = 629,090$ windows 😱. Hence, generating the SSD map is the bottleneck.

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
    - Not all $3,000$ threads will run at once.

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

Now that we are familiar with the CUDA GPU Hardware model, we should be ready to speed up generating the SSD map.

!!! info My GPU

    My GPU is the NVIDIA Corporation GA107BM [GeForce RTX 3050 Ti Mobile]. Each grid has 946 thread blocks and each thread block has 665 threads.

The idea is that we want each thread to calculate the SSD of one window (of the input image) and the template. In the previous part, we created a function called `generate_ssd_map(input_img, template)` to create the SSD map. In CUDA programming, we call this function **__a kernel__**. Both perform the same operations. Each thread will execute the kernel operation.

```cpp title="ssd.cu" linenums="1"
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

## Afterword

What's the point? Yes, the CUDA code is not portable. Yes, the CUDA code uses hardcoded numbers which are not considered a good practice. However, I am happy that I can write basic CUDA code and understand how it works from reading the documentation. It is my first time writing CUDA code, and may be my last time depending on my work in the future. I hope I can look back and see how stupid I am in writing all these 😁.
