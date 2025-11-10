# backend/recommender.py

import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

class Recommender:
    def _init_(
        self,
        data_csv: str = "data/assessments.csv",
        embeddings_path: str = "data/embeddings.npy",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        # --- START OF THE FIX ---
        # The model must be initialized FIRST.
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

        # THEN, we define and use the absolute paths.
        BASE_PATH = Path(_file_).resolve().parent.parent
        self.data_csv = BASE_PATH / data_csv
        self.embeddings_path = BASE_PATH / embeddings_path
        # --- END OF THE FIX ---
        
        self.df = pd.read_csv(self.data_csv)
        self._ensure_type_column()
        self.embeddings = self._load_or_build_embeddings()
        self.embeddings = self._normalize(self.embeddings)
        self.proto = {
            "Knowledge & Skills": self._embed_text("technical knowledge and skills assessment for job candidates"),
            "Personality & Behavior": self._embed_text("personality and behavioral assessment for job candidates"),
        }

    # ... The rest of the file is correct and can remain the same ...
    def _ensure_type_column(self) -> None:
        if "type" not in self.df.columns: self.df["type"] = ""
        self.df["type"] = self.df["type"].fillna("")

    def _load_or_build_embeddings(self) -> np.ndarray:
        p = Path(self.embeddings_path)
        if p.exists(): return np.load(p)
        return self._build_and_save_embeddings()

    def _build_and_save_embeddings(self) -> np.ndarray:
        texts: List[str] = self.df["description"].fillna("").astype(str).tolist()
        # This line uses self.model, so it must be initialized before this is called.
        embs = self.model.encode(texts, batch_size=64, show_progress_bar=True)
        embs = np.array(embs, dtype=np.float32)
        Path(self.embeddings_path).parent.mkdir(parents=True, exist_ok=True)
        np.save(self.embeddings_path, embs)
        return embs

    def _embed_text(self, text: str) -> np.ndarray:
        v = self.model.encode([text])
        v = np.array(v, dtype=np.float32)[0]
        return self._normalize(v)

    def _normalize(self, x: np.ndarray) -> np.ndarray:
        if x.ndim == 1:
            denom = np.linalg.norm(x) + 1e-12
            return x / denom
        denom = np.linalg.norm(x, axis=1, keepdims=True) + 1e-12
        return x / denom

    def _cosine_sim(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        return b @ a

    def search(self, query: str, top_n: int = 20) -> List[Tuple[int, float]]:
        q = self._embed_text(query)
        sims = self._cosine_sim(q, self.embeddings)
        idx = np.argpartition(-sims, kth=min(top_n, len(sims) - 1))[:top_n]
        idx = idx[np.argsort(sims[idx])[::-1]]
        return [(int(i), float(sims[i])) for i in idx]

    def recommend(self, query: str, top_k: int = 10) -> List[Dict]:
        cands = self.search(query, top_n=max(20, top_k * 2))
        final = cands[:top_k]
        results: List[Dict] = []
        for idx, score in final:
            row = self.df.iloc[idx].to_dict()
            test_type_str = row.get("type", "Knowledge & Skills")
            test_types = [test_type_str] if test_type_str else ["Knowledge & Skills"]
            results.append({
                "url": row.get("url", ""), "name": row.get("name", ""),
                "adaptive_support": "No", "description": row.get("description", ""),
                "duration": 60, "remote_support": "Yes",
                "test_type": test_types,
            })
        return results
