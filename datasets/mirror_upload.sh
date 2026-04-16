#!/usr/bin/env bash
# 원본 소스(LTSF + GIFT-Eval)에서 로컬로 받은 뒤 본인 HF repo로 재업로드.
# 사전: huggingface-cli login
#       export TSF_HF_REPO="<your-hf-id>/tsf-benchmarks"
#       export TSF_DATA_DIR="D:/Users/tsf_data"  (옵션)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${TSF_DATA_DIR:-$SCRIPT_DIR}"
REPO="${TSF_HF_REPO:-Yotto3108/tsf-benchmarks}"

mkdir -p "$TARGET_DIR/ltsf" "$TARGET_DIR/gift_eval"
echo "Staging at: $TARGET_DIR"

python - <<PY
from huggingface_hub import snapshot_download, create_repo, upload_folder

# 1) 원본에서 받기
print("[1/3] LTSF from thuml/autoformer-ltsf-benchmark")
snapshot_download("thuml/autoformer-ltsf-benchmark", repo_type="dataset",
                  local_dir="$TARGET_DIR/ltsf", local_dir_use_symlinks=False)

print("[2/3] GIFT-Eval from Salesforce/GiftEval")
snapshot_download("Salesforce/GiftEval", repo_type="dataset",
                  local_dir="$TARGET_DIR/gift_eval", local_dir_use_symlinks=False)

# 2) 본인 repo에 업로드
print(f"[3/3] Uploading to $REPO")
create_repo("$REPO", repo_type="dataset", exist_ok=True, private=False)
upload_folder(repo_id="$REPO", repo_type="dataset",
              folder_path="$TARGET_DIR",
              ignore_patterns=["*.lock", ".cache/*", ".git/*"])
print("Mirror upload complete.")
PY
