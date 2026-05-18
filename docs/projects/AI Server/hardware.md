---
comments: true
---

# Hardware

I'll cover the hardware specs on this page. I built the AI server (well, a PC) from individual components - it was my first time building a computer 😱. I call it the AI server because I mainly use it to run AI models. It took me about 5 hours to put together. By the time I had finished, the sun had already set and I had to get ready for bed because I had work the next day 🫩.

Before building, I needed to choose the parts (obviously 😅). The right specs depend on what AI models you want to run, and the kind of tasks the you're doing. For those of us on a tight budget, we are mostly limited to MoE models. Luckily, companies are releasing more MoE models than dense ones these days.

!!! info

    In deep learning, models have something called parameters. These parameters represent the strength of connections between artificial neurons, loosely inspired by synapses in the human brain. The AI model learns and tweaks these parameters when undergoing training. These parameters end up storing knowledge gained from the data. Generally, the more parameters an AI model has, the "smarter" it can become. A parameter is considered "active" when it is being used during the forward pass. MoE models (or Mixture of Experts models) are models with a much smaller number of active parameters compared to dense models. For example, an MoE model with 60 billion parameters may only have 3 billion active parameters, whereas a dense model with 60 billion parameters uses all of them at once. Therefore, dense models are slower to process a prompt and generate a response.

## TLDR

Here is the list of my PC parts and its prices when I bought them. The prices are all in AUD. Just recording them here to show how prices have skyrocketed.

| PC Part | Choice | Price |
|:--------|:----------|:------|
| CPU | AMD Ryzen 9 7900 Desktop Processor | $588 |
| CPU cooler | Thermalright Peerless Assassin 120 SE 66.17 CFM CPU Cooler | $55 |
| Motherboard | ASRock X870E Taichi Lite Motherboard | $699 |
| GPU | Gigabyte WINDFORCE OC Rev 2.0 GeForce RTX 3060 12GB Video Card | $469 |
| RAM | Corsair Vengeance Grey 96GB (2x 48GB) 6000MHz DDR5 | $369 |
| Storage | Samsung 990 EVO Plus 2 TB M.2-2280 PCIe 5.0 x2 NVME SSD | $245 |
| PSU | Silverstone Strider Platinum S 1200 W 80+ Platinum Certified Fully Modular ATX Power Supply | $269 |
| PC Case | Antec C8 Wood ATX Full Tower Case | $139 |
|  | Total | $3,302 |

## GPU

The first part that I chose was the GPU. An ideal GPU to run AI models requires large VRAM capacity and high memory bandwidth.

### Large VRAM Capacity

AI models have parameters (often called weights) that store the knowledge gained from training data. These weights are essentially numbers, stored in memory so they can be loaded when needed. The process usually starts by loading the models: the weights are read into the system RAM. To speed up calculations, we run them on the GPUs. The catch is that GPUs can't access RAM directly, so the weights must be transferred to the GPU's own memory (or VRAM). Therefore, if we have limited VRAM, we can't load all the model's weights. The computation is then limited to what's loaded on the GPU, and the remaining calculations must be done by the CPU, which drastically slows down the entire process.

For example, let's say we have a dense model A with 32 layers, each containing 5 parameters (weights).

```txt
Layer  0   0.34139  0.63202  0.77341  0.23715  0.51363

Layer  1   0.32411  0.29561  0.26702  0.57794  0.12664

Layer  2   0.81017  0.67015  0.66623  0.49524  0.40469

...

Layer 30   0.80561  0.78221  0.28076  0.65090  0.23813

Layer 31   0.57023  0.64495  0.48769  0.83089  0.21492
```

Let's assume each weight (which is like a $5$-decimal float) takes 4 bytes. That means this dense model A has a total space of $4 \text{ byte} * 5 \text{ parameters} * 32 \text{ layers} = 640$ bytes. Let's assume that we **only** count the weights. The next step requires us to read these weights and put them into the system memory (or RAM).

If the GPU only has $320$ bytes, then it can hold half the layers of the dense model A (let's say layers $0$ to $15$), so the CPU handles layers $16$ to $31$. However, if the GPU has more than $640$ bytes, it can hold the whole dense model A; all calculations run on the GPU, with the CPU's mainly just shuttling data back and forth, speeding up the whole process. That's why I chose the RTX 3060 due to its considerably large VRAM capacity within the consumer GPU space while still being affordable.

### High Memory Bandwidth

Now we know that the model's weights live in the GPU. The GPU then performs the calculations  and transfers the result back from VRAM to system memory. The transfer between the VRAM and RAM happens only twice: sending the input from the system RAM to the VRAM, and sending the output back from the VRAM to the system RAM. But what we're interested is in the memory bandwidth inside the GPU.

A GPU architecture is similar to a computer's. It has its own processing unit that performs calculations, and its own VRAM. The weights and the input need to be moved from the VRAM to the GPU's caches, then the results are written back to the VRAM. If this movement of data is slow, then the overall calculation speed suffers. More time is wasted on shuttling data back and forth than actually crunching numbers. Therefore, GPUs with high memory bandwidth are more desirable. However, GPUs with high memory bandwidth tend to be more expensive, so I settled on a lower memory bandwidth NVIDIA RTX 3060 (with memory bandwidth around 360 GBps).

### Optional: Software Support

Another reason I chose NVIDIA GPUs is the software support. Generally, NVIDIA GPUs are well-supported in the AI ecosystem (compared to AMD and Intel GPUs). The GPUs work right out of the box. I don't have to worry about hunting down the right drivers and software stack to run the AI models.

## CPU & Motherboard

Most consumer motherboards support PCIe bifurcation, but they often split lanes unevenly: x16 to the primary GPU and x4 to the secondary. However, the ASRock X870E Taichi Lite allows x8/x8 bifurcation, so data can travel to each GPU at the same speed. That's really the only reason I chose this particular board. Still, PCIe bandwidth isn't as critical as memory bandwidth inside the GPU.

Honestly, this is **_the wrong_** way to choose a motherboard for an AI server. Ideally, the board should support as many GPUs as possible, and that kind of board is usually a server or workstation model. This is because consumer CPUs have limited PCIe lanes.

For example, an AM5 AMD CPU is limited to 28 PCIe lanes:

- 4 lanes are reserved for the chipset in the motherboard
- 16 lanes are for the primary graphics card
- 4 lanes are for the primary M.2 NVME SSD drive, and 
- the other 4 lanes are for secondary devices (WiFi, second M.2 NVME SSD, etc.)

If you can find a GPU that fits the entire model, you don't really have to worry about the PCIe lanes. However, the industry is shifting toward MoE models with huge parameter counts. Therefore, fitting a whole model into a single consumer GPU is becoming impractical and unaffordable. 

I wouldn't recommend my CPU and motherboard combo. I should have taken a bit more risk and picked a used server/workstation motherboard and CPU from a trusted seller on eBay or another second-hand market.

## RAM & the Rest

The layers that can't fit in the GPUs are placed in the system RAM. Hence, I chose 96 GB of system memory because that was the only capacity that fit my budget (now, I regret a bit 🥲). I won't go deep into the the rest of the components as they do not play as big a part in building an effective AI server.

## Afterword

Overall, I'd rate my system a 6/10. I believe that used enterprise PC offers better value than building from scratch. Still, I chose to build the PC because it was my first time. Moreover, I'm not used to buying used parts online.
