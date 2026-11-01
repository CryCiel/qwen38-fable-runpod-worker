# Qwen3.8 Fable — dedicated RunPod Serverless (96GB Blackwell)

**Independent from the existing SuperGemma4 endpoint and repository.** Only RunPod worker code, deployment scripts, tests and documentation belong here. No SillyTavern files.

## GPU compatibility
GPU pool `BLACKWELL_96`, allowing all three **RTX PRO 6000 96GB** variants: MaxQ, Server, Workstation. The Dockerfile builds llama.cpp with CUDA `120a-real`.

## Model
- Source HF repo: `DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF`
- GGUF: `Qwen3.8-27B-TurboFCFusion-735-882-Here-Uncen-NEO-CODER-MAX-Q6_K.gguf` (ordinary, non-MTP ~23.6 GB)
- Runtime: CUDA 12.8.1, pinned llama.cpp `0a1ef309c`, OpenSSL HTTPS support.
- Context target: 262144; verify performance and available GPU memory for real workloads.

## Cached Models — recommended production configuration

**Do NOT attach the 389 GB upstream model repository directly to RunPod Cached Models.** RunPod currently downloads *all* quantizations in a model repository.

Prepare a one-GGUF public Hugging Face model repo using `scripts/prepare_cached_model.py`. Then configure **only the Qwen endpoint**:

```text
Model=YOUR_HF_USERNAME/qwen38-fable-q6k-cache
LLAMA_CACHED_MODEL=YOUR_HF_USERNAME/qwen38-fable-q6k-cache
LLAMA_CACHED_GGUF_PATH=Qwen3.8-27B-TurboFCFusion-735-882-Here-Uncen-NEO-CODER-MAX-Q6_K.gguf
LLAMA_SERVER_CMD_ARGS=--ctx-size 262144 --n-gpu-layers 99 --parallel 1 --flash-attn on --cache-type-k q8_0 --cache-type-v q8_0 --reasoning off
MAX_CONCURRENCY=1
LLAMA_STARTUP_TIMEOUT=600
```

The `Model` field is a RunPod endpoint setting, not an environment variable. With the cache variables present, `src/start.sh` resolves the cached snapshot and supplies `-m` to `llama-server`. **Do not keep `-hf` or `-hff` in `LLAMA_SERVER_CMD_ARGS`.** No separate Network Volume is required.

See **[Cached Models migration guide](docs/RUNPOD-DEPLOY.md)** for setup, verification, troubleshooting and attribution. The existing Qwen worker was previously validated with direct Hugging Face downloads, but cache-mode success must be verified separately. GitHub CI is not proof of a new CUDA build or of cache availability.

SillyTavern configuration stays local and separate.
