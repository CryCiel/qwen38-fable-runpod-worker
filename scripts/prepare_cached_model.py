#!/usr/bin/env python3
"""Prepare a Q6_K-only Hugging Face model repo for RunPod Cached Models.

This performs a server-side Hub copy: no 23.6 GB download or local upload.
Requires: python -m pip install -U huggingface_hub; hf auth login
"""
import argparse
from huggingface_hub import HfApi

SOURCE_REPO = "DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF"
GGUF = "Qwen3.8-27B-TurboFCFusion-735-882-Here-Uncen-NEO-CODER-MAX-Q6_K.gguf"
DEFAULT_REPO_NAME = "qwen38-fable-q6k-cache"

MODEL_CARD = """---
tags:
- gguf
- qwen3_8
---

# Qwen3.8 Fable Q6_K — RunPod cache-only mirror

This repository contains the unmodified **Q6_K non-MTP GGUF** copied
server-side from:
https://huggingface.co/DavidAU/Qwen3.8-27B-TURBO-Fable-Cold-Fusion-735-882-Heretic-Uncensored-NEO-CODER-MAX-MTP-GGUF

For source model details, license and attribution, refer to the original model.
The mirror is intended for RunPod Cached Models and text inference.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-id",
        help="Destination HF model repo ID (default: your-username/qwen38-fable-q6k-cache)",
    )
    args = parser.parse_args()

    api = HfApi()
    user = api.whoami()["name"]
    repo_id = args.repo_id or f"{user}/{DEFAULT_REPO_NAME}"
    if repo_id == SOURCE_REPO:
        parser.error("Destination cannot be the upstream model repository.")

    print(f"Source:      {SOURCE_REPO}/{GGUF}")
    print(f"Destination: {repo_id}/{GGUF}")
    print("No large GGUF data will be downloaded to this machine.")

    exists = api.repo_exists(repo_id, repo_type="model")
    if exists:
        files = api.list_repo_files(repo_id, repo_type="model")
        extra_ggufs = [f for f in files if f.lower().endswith(".gguf") and f != GGUF]
        if extra_ggufs:
            raise SystemExit(
                "Destination contains other GGUFs. Refusing to create a large cache: "
                + ", ".join(extra_ggufs)
            )
        if api.model_info(repo_id).private:
            raise SystemExit(
                "Destination is private. Make it public, or configure an HF token "
                "in RunPod Model caching before continuing."
            )
    else:
        api.create_repo(repo_id=repo_id, repo_type="model", private=False)
        files = []

    if GGUF not in files:
        print("Copying Q6_K inside Hugging Face (server-side)...")
        api.copy_files(
            f"hf://{SOURCE_REPO}/{GGUF}",
            f"hf://{repo_id}/{GGUF}",
        )
    else:
        print("Q6_K already exists in destination; skipping copy.")

    if "README.md" not in files:
        api.upload_file(
            path_or_fileobj=MODEL_CARD.encode("utf-8"),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="model",
            commit_message="Document source of RunPod Q6_K cache mirror",
        )

    result = api.list_repo_files(repo_id, repo_type="model")
    if GGUF not in result:
        raise RuntimeError("GGUF is missing from the destination after copy.")

    print(f"READY: https://huggingface.co/{repo_id}")
    print("RunPod Endpoint -> Manage -> Edit Endpoint -> Model:", repo_id)
    print("LLAMA_CACHED_MODEL=", repo_id, sep="")
    print("LLAMA_CACHED_GGUF_PATH=", GGUF, sep="")


if __name__ == "__main__":
    main()
