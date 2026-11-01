# Qwen3.8 Fable Uncensored — Dedicated RunPod Worker

**Standalone repository:** `CryCiel/qwen38-fable-runpod-worker`. The original SuperGemma4 GitHub repository and endpoint remain unchanged. **Only RunPod-related code, config, tests and deployment documentation are kept here.**

## Model

- Hugging Face repository: `DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF`
- GGUF filename: `Qwen3.8-27B-TurboFCFusion-735-882-Here-Uncen-NEO-CODER-MAX-Q6_K.gguf`
- Quantization: Q6_K, 23.6 GB download; standard non-MTP model
- Backend: pinned llama.cpp `0a1ef309c`, CUDA 12.8.1
- CUDA targets: `89-real;120a-real` for Ada + RTX PRO 6000 Blackwell MIG
- RunPod Serverless GPU pool: `ADA_48_PRO`. RunPod's worker-sglang documentation notes that Blackwell `PRO 6000 MIG 48GB` can be placed in this 48GB pool; choose the specific GPU if the endpoint UI allows it.

## Endpoint environment variables

```text
LLAMA_CACHED_MODEL=DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF
LLAMA_CACHED_GGUF_PATH=Qwen3.8-27B-TurboFCFusion-735-882-Here-Uncen-NEO-CODER-MAX-Q6_K.gguf
LLAMA_SERVER_CMD_ARGS=--ctx-size 262144 --n-gpu-layers 99 --parallel 1 --flash-attn on --cache-type-k q8_0 --cache-type-v q8_0 --reasoning off
MAX_CONCURRENCY=1
LLAMA_STARTUP_TIMEOUT=600
```

The GGUF must be cached into the **new** network volume before worker startup, in `/runpod-volume/huggingface-cache/hub`. If cache variables are set, **do not** include `-m` or `-hf` in `LLAMA_SERVER_CMD_ARGS`.

**Important:** 48GB is the VRAM of the MIG instance. 262144 context and Q6_K are *experimental* and not yet tested on actual RunPod hardware; KV cache and other buffers also occupy GPU memory. If out-of-memory, test `--ctx-size 131072` first, then increase gradually.

See [RunPod deployment guide](docs/RUNPOD-DEPLOY.md). GitHub Actions only checks code and configuration; it does **not** test a GPU build or inference.
