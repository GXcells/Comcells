# Comcells-GGUF
GGUF Quantization support for native Comcells models

This is currently very much WIP. These custom nodes provide support for model files stored in the GGUF format popularized by [llama.cpp](https://github.com/ggerganov/llama.cpp).

While quantization wasn't feasible for regular UNET models (conv2d), transformer/DiT models such as flux seem less affected by quantization. This allows running it in much lower bits per weight variable bitrate quants on low-end GPUs.

![Comfy_Flux1_dev_Q4_0_GGUF_1024](https://github.com/user-attachments/assets/70d16d97-c522-4ef4-9435-633f128644c8)

Note: The "Force/Set CLIP Device" is **NOT** part of this node pack. Do not install it if you only have one GPU. Do not set it to cuda:0 then complain about OOM errors if you do not undestand what it is for. There is not need to copy the workflow above, just use your own workflow and replace the stock "Load Diffusion Model" with the "Unet Loader (GGUF)" node.

## Installation

> [!IMPORTANT]  
> Make sure your Comcells is on a recent-enough version to support custom ops when loading the UNET-only.

To install the custom node normally, git clone this repository and install the only dependency for inference (`pip install --upgrade gguf`)

```
git clone https://github.com/city96/Comcells-GGUF
```

To install the custom node on standalone, open a CMD inside the "Comcells_windows_portable" folder (where your `run_nvidia_gpu.bat` file is) and use the following commands:

```
git clone https://github.com/city96/Comcells-GGUF Comcells/custom_nodes/Comcells-GGUF
.\python_embeded\python.exe -s -m pip install -r .\Comcells\custom_nodes\Comcells-GGUF\requirements.txt
```

## Usage

Simply use the GGUF Unet loader found under the `bootleg` category. Place the .gguf model files in your `Comcells/models/unet` folder.

LoRA loading is experimental but it should work with just the built-in LoRA loader node(s).

Pre-quantized models:

- [flux1-dev GGUF](https://huggingface.co/city96/FLUX.1-dev-gguf)
- [flux1-schnell GGUF](https://huggingface.co/city96/FLUX.1-schnell-gguf)
