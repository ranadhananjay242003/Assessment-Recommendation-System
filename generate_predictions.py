import pandas as pd
from backend.recommender import Recommender
import csv

def main():
    # Load the recommender
    print("Loading recommender...")
    recommender = Recommender()
    
    # Load train/test data
    df = pd.read_csv("data/train_test_data.csv")
    
    # Get unique queries
    unique_queries = df['Query'].unique()
    print(f"Found {len(unique_queries)} unique queries")
    
    # Generate predictions
    predictions = []
    for i, query in enumerate(unique_queries, 1):
        print(f"\n[{i}/{len(unique_queries)}] Query: {query[:80]}...")
        results = recommender.recommend(query, top_k=10)
        
        for result in results:
            predictions.append({
                'Query': query,
                'Assessment_url': result['url']
            })
        
        print(f"  -> Generated {len(results)} recommendations")
    
    # Save to CSV
    output_file = "predictions.csv"
    df_pred = pd.DataFrame(predictions)
    df_pred.to_csv(output_file, index=False)
    
    print(f"\n[OK] Saved {len(predictions)} predictions to {output_file}")
    print(f"Total queries: {len(unique_queries)}")
    print(f"Predictions per query: {len(predictions) / len(unique_queries):.1f} avg")

if __name__ == "__main__":
    main()

