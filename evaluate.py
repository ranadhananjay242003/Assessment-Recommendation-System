import pandas as pd
from pathlib import Path
from backend.recommender import Recommender
from collections import defaultdict

def calculate_recall_at_k(recommended_urls, relevant_urls, k=10):
    """Calculate Recall@K for a single query"""
    recommended_set = set(recommended_urls[:k])
    relevant_set = set(relevant_urls)
    
    if len(relevant_set) == 0:
        return 0.0
    
    hits = len(recommended_set.intersection(relevant_set))
    recall = hits / len(relevant_set)
    return recall

def evaluate_on_dataset(recommender, data_csv, k=10):
    """Evaluate recommender on labeled dataset"""
    df = pd.read_csv(data_csv)
    
    # Group by query to get all relevant URLs for each query
    query_to_relevant = defaultdict(list)
    for _, row in df.iterrows():
        query = str(row['Query']).strip()
        url = str(row['Assessment_url']).strip()
        if url:
            query_to_relevant[query].append(url)
    
    print(f"\nEvaluating on {len(query_to_relevant)} unique queries...")
    print("=" * 80)
    
    recalls = []
    for i, (query, relevant_urls) in enumerate(query_to_relevant.items(), 1):
        # Get recommendations
        results = recommender.recommend(query, top_k=k)
        recommended_urls = [r['url'] for r in results]
        
        # Calculate recall
        recall = calculate_recall_at_k(recommended_urls, relevant_urls, k=k)
        recalls.append(recall)
        
        print(f"\nQuery {i}: {query[:80]}...")
        print(f"Relevant URLs: {len(relevant_urls)}")
        print(f"Recommended URLs: {len(recommended_urls)}")
        print(f"Recall@{k}: {recall:.4f}")
        
        # Show which relevant URLs were found
        hits = set(recommended_urls).intersection(set(relevant_urls))
        if hits:
            print(f"[OK] Found {len(hits)}/{len(relevant_urls)} relevant assessments")
            print(f"Sample hits: {list(hits)[:2]}")
        else:
            print(f"[FAIL] No relevant assessments found in top {k}")
            print(f"Sample recommended: {recommended_urls[:2]}")
            print(f"Sample relevant: {relevant_urls[:2]}")
    
    mean_recall = sum(recalls) / len(recalls) if recalls else 0.0
    
    print("\n" + "=" * 80)
    print(f"MEAN RECALL@{k}: {mean_recall:.4f}")
    print(f"Best Recall: {max(recalls):.4f}")
    print(f"Worst Recall: {min(recalls):.4f}")
    print("=" * 80)
    
    return mean_recall, recalls

def main():
    print("Loading recommender model...")
    recommender = Recommender()
    
    # Evaluate on train+test data
    train_test_csv = Path("data/train_test_data.csv")
    if train_test_csv.exists():
        print(f"\n{'=' * 80}")
        print("EVALUATING ON FULL DATASET (Train + Test)")
        print('=' * 80)
        mean_recall, recalls = evaluate_on_dataset(recommender, train_test_csv, k=10)
    else:
        print(f"Dataset not found at {train_test_csv}")

if __name__ == "__main__":
    main()

