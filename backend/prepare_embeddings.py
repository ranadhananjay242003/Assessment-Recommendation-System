from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

DATA_CSV = Path("data/assessments.csv")
EMB_PATH = Path("data/embeddings.npy")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    if not DATA_CSV.exists():
        raise SystemExit(f"Missing {DATA_CSV}. Run the scraper first.")

    df = pd.read_csv(DATA_CSV)
    texts = df["description"].fillna("").astype(str).tolist()

    model = SentenceTransformer(MODEL_NAME)
    embs = model.encode(texts, batch_size=64, show_progress_bar=True)
    embs = np.asarray(embs, dtype=np.float32)

    EMB_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.save(EMB_PATH, embs)
    print(f"Saved embeddings to {EMB_PATH} with shape {embs.shape}")


if __name__ == "__main__":
    main()

