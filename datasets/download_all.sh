#!/usr/bin/env bash
# 본인 HF 미러 repo에서 LTSF + GIFT-Eval 통합 다운로드.
# 사전: export TSF_HF_REPO="<your-hf-id>/tsf-benchmarks"
#       export TSF_DATA_DIR="D:/Users/tsf_data"  (옵션, 기본은 이 폴더)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${TSF_DATA_DIR:-$SCRIPT_DIR}"
REPO="${TSF_HF_REPO:-Yotto3108/tsf-benchmarks}"

mkdir -p "$TARGET_DIR"
echo "Saving to: $TARGET_DIR"
echo "Repo:      $REPO"

python - <<PY
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="$REPO",
    repo_type="dataset",
    local_dir="$TARGET_DIR",
    local_dir_use_symlinks=False,
)
PY

echo "Done."
