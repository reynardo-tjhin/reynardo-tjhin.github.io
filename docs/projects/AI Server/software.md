---
comments: true
---

# Software

## Basic Tests for New PC

- Memory tests: use `memtest86+` (from bootable USB)
- CPU stress test: `stress-ng1
    - Install in Linux systems by using this command - `sudo apt install stress-ng`
    - Run a simple test - `stress-ng --cpu 24 --timeout 600s` (24 threads)
- Monitor CPU usage: `htop`
    - Press F2 to get to setup
    - To get temperature, install `lm-sensors` - `sudo apt install lm-sensors`
- To check for GPUs
    - command - `lspci -nn | egrep -i "3d|display|vga"`
- To check for Linux OS version - `lsb_release -a`

<!-- ## Preparing the OS, drivers

Picking the OS and NVIDIA drivers -->

## Backend: llama.cpp

The OG!

- Read tutorial here: [llama.cpp Guide](https://blog.steelph0enix.dev/posts/llama-cpp-guide/)

- Faster for NVIDIA CUDA - https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md#CUDA

- Using cmake to build: `apt install cmake`
    - requires Ninja dependencies: `apt install ninja-build`
    - requires curl (depending on what is built): `apt install curl libssl-dev libcurl4-openssl-dev`
- Build codes
    - `cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=~/Desktop/llama.cpp -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=ON -DLLAMA_BUILD_SERVER=ON`
    - `cmake --build build --config Release -j 12` - since my cpu has 12 cores
    - `cmake --install build --config Release`
- If there are no errors in building, go to "~/Desktop/llama.cpp/build/bin" and then run something like `./llama-cli --help`
- The above uses CPU
- To reset/pull updates from the repository
    1. `cd llama.cpp`
    2. `git clean -xdf`
    3. `git pull`
    4. `git submodule update --recursive`
    5. `cmake -B build -DGGML_CUDA=ON`
    6. `cmake --build build --config Release`
- To use CUDA, install the nvidia toolkit: `sudo apt install nvidia-cuda-toolkit`

<!-- 
# Comms

NoMachine -->