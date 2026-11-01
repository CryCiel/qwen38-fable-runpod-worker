# New RunPod Endpoint — Blackwell 96 GB Qwen3.8 Fable

**Do not change the original SuperGemma4 endpoint.**

1. Create a **new** RunPod Serverless endpoint and connect `CryCiel/qwen38-fable-runpod-worker`.
2. Choose GPU pool **BLACKWELL_96 (96 GB)**, permitting **RTX PRO 6000 MaxQ**, **RTX PRO 6000**, and **RTX PRO 6000 WK**. Do not exclude any of these three. This pool is separate from `ADA_48_PRO`.
3. Attach a new or independently managed Network Volume; create the Hugging Face cache in it.

In a shell where **that** volume is mounted at `/runpod-volume`:

```bash
python3 -m pip install -U huggingface_hub
hf download 'DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF' 'Qwen3.8-27B-TurboFCFusion-735-882-Here-Uncen-NEO-CODER-MAX-Q6_K.gguf' --cache-dir /runpod-volume/huggingface-cache/hub
```

4. Configure new endpoint environment variables:

```text
LLAMA_CACHED_MODEL=DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF
LLAMA_CACHED_GGUF_PATH=Qwen3.8-27B-TurboFCFusion-735-882-Here-Uncen-NEO-CODER-MAX-Q6_K.gguf
LLAMA_SERVER_CMD_ARGS=--ctx-size 262144 --n-gpu-layers 99 --parallel 1 --flash-attn on --cache-type-k q8_0 --cache-type-v q8_0 --reasoning off
MAX_CONCURRENCY=1
LLAMA_STARTUP_TIMEOUT=600
```

5. Confirm RunPod build completion, correct 96GB GPU allocation, `llama-server is READY.` in worker logs, then short and long-context inference.

Q6_K and 260K context are the initial test target, not a verified performance claim. Keep Q6_K before considering Q8_0; if an error occurs, adjust one variable at a time. GitHub Actions do not compile CUDA.

Only RunPod code and documentation live here. SillyTavern is configured locally, separately.
