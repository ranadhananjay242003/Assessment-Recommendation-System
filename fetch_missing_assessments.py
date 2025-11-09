import pandas as pd
import csv
import time
import logging
from pathlib import Path
from scraper.scrape_shl import get_soup, parse_product_page

logging.basicConfig(level=logging.INFO)

def main():
    # Load train/test data to get all unique assessment URLs
    train_test = pd.read_csv("data/train_test_data.csv")
    unique_urls = train_test['Assessment_url'].unique()
    
    # Load existing assessments
    existing_df = pd.read_csv("data/assessments.csv")
    existing_urls = set(existing_df['url'].tolist())
    
    print(f"Found {len(unique_urls)} unique URLs in train/test data")
    print(f"Found {len(existing_urls)} existing URLs in assessments.csv")
    
    # Find missing URLs
    missing_urls = [url for url in unique_urls if url not in existing_urls]
    print(f"Missing {len(missing_urls)} URLs")
    
    # Fetch missing assessments
    new_assessments = []
    for i, url in enumerate(missing_urls, 1):
        print(f"[{i}/{len(missing_urls)}] Fetching: {url}")
        assessment = parse_product_page(url)
        if assessment and assessment.description:
            new_assessments.append(assessment)
            print(f"  [OK] Added: {assessment.name}")
        else:
            print(f"  [FAIL] Failed to parse")
        time.sleep(0.5)  # Be polite
    
    if new_assessments:
        # Append to existing CSV
        with open("data/assessments.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for a in new_assessments:
                writer.writerow([a.name, a.url, a.description, a.a_type])
        
        print(f"\n[OK] Added {len(new_assessments)} new assessments to data/assessments.csv")
        
        # Reload and rebuild embeddings
        print("\nRebuilding embeddings...")
        from backend.prepare_embeddings import main as rebuild_embeddings
        rebuild_embeddings()
    else:
        print("\nNo new assessments to add")

if __name__ == "__main__":
    main()

