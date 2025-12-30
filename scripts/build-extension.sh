#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_EXTENSION_DIR="$ROOT_DIR/../tmb-activity-downloader"
EXTENSION_DIR="${TRACKMYBETS_EXTENSION_DIR:-$DEFAULT_EXTENSION_DIR}"
OUTPUT_ZIP="$ROOT_DIR/frontend/public/trackmybets-helper-extension.zip"

if [[ ! -d "$EXTENSION_DIR" ]]; then
  echo "Error: extension source not found at '$EXTENSION_DIR'." >&2
  echo "Set TRACKMYBETS_EXTENSION_DIR to override the location." >&2
  exit 1
fi

echo "Building extension ZIP from: $EXTENSION_DIR"

pushd "$EXTENSION_DIR" >/dev/null
zip -rq "$OUTPUT_ZIP" .
popd >/dev/null

echo "Extension bundle written to $OUTPUT_ZIP"
