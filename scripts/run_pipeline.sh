#!/bin/bash

# Run the complete AI4Trade data processing pipeline
# Usage: bash scripts/run_pipeline.sh [--fred-api-key KEY]

set -e  # Exit on error

echo "==========================================="
echo "AI4TRADE DATA PROCESSING PIPELINE"
echo "==========================================="

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python not found. Please install Python 3.10+"
    exit 1
fi

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "Warning: No virtual environment detected."
    echo "Consider activating your venv: source .venv/bin/activate"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Parse command line arguments
FRED_API_KEY=""
SKIP_EXTERNAL=false
SKIP_COMTRADE=false
SKIP_INDICATORS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --fred-api-key)
            FRED_API_KEY="$2"
            shift 2
            ;;
        --skip-external)
            SKIP_EXTERNAL=true
            shift
            ;;
        --skip-comtrade)
            SKIP_COMTRADE=true
            shift
            ;;
        --skip-indicators)
            SKIP_INDICATORS=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--fred-api-key KEY] [--skip-external] [--skip-comtrade] [--skip-indicators]"
            exit 1
            ;;
    esac
done

# Build command
CMD="python src/pipeline.py"

if [ -n "$FRED_API_KEY" ]; then
    CMD="$CMD --fred-api-key $FRED_API_KEY"
fi

if [ "$SKIP_EXTERNAL" = true ]; then
    CMD="$CMD --skip-external"
fi

if [ "$SKIP_COMTRADE" = true ]; then
    CMD="$CMD --skip-comtrade"
fi

if [ "$SKIP_INDICATORS" = true ]; then
    CMD="$CMD --skip-indicators"
fi

# Show what we're running
echo "Running: $CMD"
echo

# Run the pipeline
$CMD

echo
echo "==========================================="
echo "PIPELINE COMPLETED SUCCESSFULLY"
echo "==========================================="
echo "Processed data available in: outputs/processed/"
echo "Intermediate files in: outputs/interim/"
echo
echo "Next steps:"
echo "1. Explore data: jupyter notebook notebooks/exploratory_analysis.ipynb"
echo "2. Train models: jupyter notebook notebooks/SABLE_12_model_training.ipynb"
echo "3. Generate forecast: python src/forecast.py"

