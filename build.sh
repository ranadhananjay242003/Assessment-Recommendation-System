#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install all the Python dependencies from requirements.txt
echo "--- Installing dependencies ---"
pip install -r requirements.txt

# 2. (Optional but Recommended) Run the script that builds the embeddings
# This pre-builds the .npy file so your app starts faster.
echo "--- Pre-building sentence embeddings ---"
python -c "from backend.recommender import Recommender; Recommender()"

echo "--- Build finished ---"
