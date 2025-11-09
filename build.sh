#!/bin/bash
set -e

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Checking for data files..."
if [ ! -f "data/assessments.csv" ]; then
    echo "Running scraper to collect assessment data..."
    python scraper/scrape_shl.py
fi

if [ ! -f "data/embeddings.npy" ]; then
    echo "Generating embeddings..."
    python backend/prepare_embeddings.py
fi

echo "Build complete!"

