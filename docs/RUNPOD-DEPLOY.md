# Qwen3.8 Fable Q6_K — RunPod Cached Models

**This guide applies only to** `CryCiel/qwen38-fable-runpod-worker`. Do not modify the existing SuperGemma4 repository or endpoint.

## Why a small mirror is required

The upstream Hugging Face repository contains approximately **389 GB** of multiple GGUF variants. As of November 2026, RunPod Cached Models downloads **every variant** in the selected Hugging Face repository, not only the GGUF passed to llama.cpp.

**Do not enter the original DavidAU repository into RunPod's Model field.** Instead, create a separate Hugging Face model repo containing just the ordinary, non-MTP Q6_K file (~23.6 GB). The GGUF bytes remain unchanged.

## Step 1: Prepare a one-GGUF Hugging Face repository

On your own PC, with Python and a Hugging Face account:

```powershell
py -m pip install --upgrade huggingface_hub
hf auth login
py scripts/prepare_cached_model.py
```

Run these commands from a clone/download of **this Qwen GitHub repository** (not SuperGemma4). For Linux/macOS use `python3` instead of `py`.

The script:
- Reads credentials locally from `hf auth login`; **never put a Hugging Face token in GitHub code, RunPod logs, or ChatGPT**.
- Creates `YOUR_HF_USERNAME/qwen38-fable-q6k-cache` as a **public** model repository.
- Copies the Q6_K file **server-side**, without downloading 23.6 GB to the PC or uploading it again.
- Verifies that the destination contains the expected filename; rejects unrelated GGUFs.
- Prints the destination model ID and RunPod environment variable values.

Hugging Face server-side copying requires source and destination storage regions to be compatible. If it fails, do not fall back to downloading the entire upstream repository.

Source GGUF:

```text
DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF
Qwen3.8-27B-TurboFCFusion-735-882-Here-Uncen-NEO-CODER-MAX-Q6_K.gguf
```

## Step 2: Attach model caching to the EXISTING Qwen v2 endpoint

In RunPod Serverless, open the **Qwen endpoint** (not SuperGemma4) → `Manage` → `Edit Endpoint`.

Under `Model` / `Cached Models`, enter the model repo printed by the script, for example:

```text
YOUR_HF_USERNAME/qwen38-fable-q6k-cache
```

No Network Volume is needed. RunPod exposes the model at `/runpod-volume/huggingface-cache/hub` on the host cache mount. Initial cache population can still require a download but is managed by RunPod rather than repeated separately in each worker.

## Step 3: Replace ONLY the Qwen endpoint environment variables

```text
LLAMA_CACHED_MODEL=YOUR_HF_USERNAME/qwen38-fable-q6k-cache
LLAMA_CACHED_GGUF_PATH=Qwen3.8-27B-TurboFCFusion-735-882-Here-Uncen-NEO-CODER-MAX-Q6_K.gguf
LLAMA_SERVER_CMD_ARGS=--ctx-size 262144 --n-gpu-layers 99 --parallel 1 --flash-attn on --cache-type-k q8_0 --cache-type-v q8_0 --reasoning off
MAX_CONCURRENCY=1
LLAMA_STARTUP_TIMEOUT=600
```

**Important:** Remove `-hf`, `-hff`, and `-m` from `LLAMA_SERVER_CMD_ARGS` when using `LLAMA_CACHED_MODEL`. Both cache vars must be present. The existing `src/start.sh` already finds the snapshot dynamically and loads the exact local GGUF by `-m`; it does not need a code change.

Keep GPU pool `BLACKWELL_96`, all three RTX PRO 6000 96 GB variants checked, `Active workers = 0` and `MAX_CONCURRENCY=1`. Keep container disk at **80 GB for the first smoke test**; after confirmed cache load, it may be reduced based on observed actual runtime usage.

## Step 4: Verify with one RunPod Request

Submit:

```json
{"input":{"messages":[{"role":"user","content":"비 내리는 카페를 한국어로 세 문장 묘사해 줘."}],"max_tokens":150,"stream":false}}
```

Expected worker logs:

```text
Found model: /runpod-volume/huggingface-cache/hub/models--.../snapshots/.../Qwen3.8-27B-TurboFCFusion-735-882-Here-Uncen-NEO-CODER-MAX-Q6_K.gguf
llama-server is READY.
```

Verify a completed request and a Korean response. If you see `ERROR: GGUF not found`, verify Model matches `LLAMA_CACHED_MODEL`, snapshot mount is available, and target filename is exact. If logs say `Using model selection from LLAMA_SERVER_CMD_ARGS`, the cache variables were not set. If the model still downloads to `/root/.cache/huggingface`, remove the `-hf/-hff` options.

Keep model repo text-only for now. Previously `-hf` could auto-fetch `mmproj-BF16.gguf` for multimodal tasks; this cache setup intentionally includes only Q6_K, so vision input needs separate projector setup later.

References:
- https://docs.runpod.io/serverless/endpoints/model-caching
- https://huggingface.co/docs/huggingface_hub/main/en/guides/repository
