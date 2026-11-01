# Qwen3.8 Fable — dedicated RunPod Serverless (96GB Blackwell)

**Independent from the existing SuperGemma4 endpoint and repository.** This repository contains only RunPod worker code, Docker build configuration, tests and deployment documentation. No SillyTavern files.

## RunPod GPU compatibility — all three variants

The new endpoint must use **`BLACKWELL_96`** GPU pool with **no exclusions** of these GPU types:

| RunPod name | GPU | VRAM | CUDA |
| --- | --- | --- | --- |
| RTX PRO 6000 MaxQ | Blackwell Max-Q Workstation Edition | 96GB | 12.0 |
| RTX PRO 6000 | Blackwell Server Edition | 96GB | 12.0 |
| RTX PRO 6000 WK | Blackwell Workstation Edition | 96GB | 12.0 |

The Dockerfile compiles a single native CUDA **`120a-real`** target compatible with all three. The RunPod hub template selects `BLACKWELL_96`; the new Endpoint GPU selection must also be set in the RunPod console. Allowing all three means RunPod can select an available model; it does not guarantee availability (the MaxQ model may be out of capacity).

## Model
- Hugging Face repo: `DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF`
- Model: `Qwen3.8-27B-TurboFCFusion-735-882-Here-Uncen-NEO-CODER-MAX-Q6_K.gguf` (Q6_K, ordinary non-MTP ~23.6GB)
- CUDA image: 12.8.1 with pinned llama.cpp commit `0a1ef309c`.
- The 96GB GPU tier makes a higher quant such as Q8_0 possible to **test later**; keep Q6_K as the known configured baseline during initial deployment.

## NEW endpoint environment variables

```text
LLAMA_CACHED_MODEL=DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF
LLAMA_CACHED_GGUF_PATH=Qwen3.8-27B-TurboFCFusion-735-882-Here-Uncen-NEO-CODER-MAX-Q6_K.gguf
LLAMA_SERVER_CMD_ARGS=--ctx-size 262144 --n-gpu-layers 99 --parallel 1 --flash-attn on --cache-type-k q8_0 --cache-type-v q8_0 --reasoning off
MAX_CONCURRENCY=1
LLAMA_STARTUP_TIMEOUT=600
```

**Important:** This worker requires the model cached in the *new endpoint's* attached Network Volume at `/runpod-volume/huggingface-cache/hub`. If using cache variables, omit `-m/-hf` in command args. 262144 tokens is a target, not yet validated with the new worker; verify VRAM and model context support.

See [RunPod deployment guide](docs/RUNPOD-DEPLOY.md). GitHub CI tests Python and configuration only. Successful CI is not proof of a CUDA build or actual inference.
