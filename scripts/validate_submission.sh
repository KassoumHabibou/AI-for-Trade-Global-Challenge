#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 path/to/submission.csv"
  exit 1
fi

python -m src.validate_submission --file "$1"
