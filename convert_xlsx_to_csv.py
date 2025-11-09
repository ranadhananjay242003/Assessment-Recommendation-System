import pandas as pd
from pathlib import Path

EXCEL_FILE = "Gen_AI Dataset.xlsx"  
OUTPUT_CSV = "data/assessments.csv"

def convert():
    if not Path(EXCEL_FILE).exists():
        print(f"Error: {EXCEL_FILE} not found!")
        print("Please update EXCEL_FILE variable in this script with your actual file path.")
        return
    
    df = pd.read_excel(EXCEL_FILE)
    
    print(f"Original columns: {list(df.columns)}")
    print(f"Shape: {df.shape}")
    
    column_mapping = {
        # 'your_excel_column': 'required_column'
        # Example mappings (uncomment and adjust):
        # 'Link': 'Assessment_url',
        # 'Description': 'Query',
    }
    
    required_cols = ['Assessment_url', 'Query']
    
    if all(col in df.columns for col in required_cols):
        result = df[required_cols].copy()
    elif column_mapping:
        result = df.rename(columns=column_mapping)[required_cols]
    else:
        print("\nPlease map your Excel columns to required format:")
        print("Required columns: Assessment_url, Query")
        print("\nEdit the column_mapping dictionary in this script.")
        return
    
    result['Assessment_url'] = result['Assessment_url'].fillna('').astype(str)
    result['Query'] = result['Query'].fillna('').astype(str)

    
    Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_CSV, index=False)
    print(f"\nConverted {len(result)} rows to {OUTPUT_CSV}")
    print(f"Sample:\n{result.head()}")

if __name__ == "__main__":
    convert()

