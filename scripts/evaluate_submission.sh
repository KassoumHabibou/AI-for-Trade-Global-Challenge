#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 path/to/submission.csv path/to/truth.csv"
  exit 1
fi

python -m src.evaluate --submission "$1" --truth "$2"
