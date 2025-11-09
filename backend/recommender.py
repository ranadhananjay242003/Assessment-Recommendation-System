import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


class Recommender:
    def __init__(
        self,
        data_csv: str = "data/assessments.csv",
        embeddings_path: str = "data/embeddings.npy",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        self.data_csv = data_csv
        self.embeddings_path = embeddings_path
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.df = pd.read_csv(self.data_csv)
        self._ensure_type_column()
        self.embeddings = self._load_or_build_embeddings()
        # Pre-compute normalized embeddings for cosine similarity
        self.embeddings = self._normalize(self.embeddings)
        # Prototypes to infer user's intent (technical vs behavioral)
        self.proto = {
            "Knowledge & Skills": self._embed_text("technical knowledge and skills assessment for job candidates"),
            "Personality & Behavior": self._embed_text("personality and behavioral assessment for job candidates"),
        }

    def _ensure_type_column(self) -> None:
        if "type" not in self.df.columns:
            self.df["type"] = ""
        self.df["type"] = self.df["type"].fillna("")

    def _load_or_build_embeddings(self) -> np.ndarray:
        p = Path(self.embeddings_path)
        if p.exists():
            return np.load(p)
        return self._build_and_save_embeddings()

    def _build_and_save_embeddings(self) -> np.ndarray:
        texts: List[str] = (
            self.df["description"].fillna("").astype(str).tolist()
        )
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
        # a: (d,), b: (n, d) -> (n,)
        return b @ a

    def search(self, query: str, top_n: int = 20) -> List[Tuple[int, float]]:
        q = self._embed_text(query)
        sims = self._cosine_sim(q, self.embeddings)
        idx = np.argpartition(-sims, kth=min(top_n, len(sims) - 1))[:top_n]
        # Sort exact top_n by score desc
        idx = idx[np.argsort(sims[idx])[::-1]]
        return [(int(i), float(sims[i])) for i in idx]

    def infer_needs(self, query: str) -> str:
        q = self._embed_text(query)
        s_tech = float(self._cosine_sim(q, self.proto["Knowledge & Skills"].reshape(1, -1))[0])
        s_beh = float(self._cosine_sim(q, self.proto["Personality & Behavior"].reshape(1, -1))[0])
        # If the scores are close, assume both; else pick the higher
        if abs(s_tech - s_beh) <= 0.05:
            return "both"
        return "Knowledge & Skills" if s_tech > s_beh else "Personality & Behavior"

    def rerank_balanced(
        self,
        query: str,
        candidates: List[Tuple[int, float]],
        top_k: int = 10,
        min_each_if_both: int = 3,
    ) -> List[Tuple[int, float]]:
        need = self.infer_needs(query)
        if need != "both":
            return candidates[:top_k]

        # Split candidates by type
        tech_ids = []
        beh_ids = []
        other = []
        for i, score in candidates:
            t = str(self.df.iloc[i].get("type", "")).strip()
            if t.lower().startswith("knowledge"):
                tech_ids.append((i, score))
            elif t.lower().startswith("personality"):
                beh_ids.append((i, score))
            else:
                other.append((i, score))

        out: List[Tuple[int, float]] = []
        # Ensure some balance first
        out.extend(tech_ids[:min_each_if_both])
        out.extend(beh_ids[:min_each_if_both])
        # Fill remaining by overall candidate order, skipping duplicates
        used = {i for i, _ in out}
        for pair in candidates:
            if len(out) >= top_k:
                break
            if pair[0] not in used:
                out.append(pair)
                used.add(pair[0])
        return out[:top_k]

    def recommend(self, query: str, top_k: int = 10) -> List[Dict]:
        cands = self.search(query, top_n=max(20, top_k * 2))
        final = self.rerank_balanced(query, cands, top_k=top_k)
        results: List[Dict] = []
        for idx, score in final:
            row = self.df.iloc[idx].to_dict()
            # Extract test type from the description or type field
            test_type_str = row.get("type", "Knowledge & Skills")
            test_types = [test_type_str] if test_type_str else ["Knowledge & Skills"]
            
            results.append({
                "url": row.get("url", ""),
                "name": row.get("name", ""),
                "adaptive_support": "No",  # Default value, can be inferred from description
                "description": row.get("description", ""),
                "duration": 60,  # Default duration in minutes
                "remote_support": "Yes",  # Default value for SHL assessments
                "test_type": test_types,
            })
        return results

