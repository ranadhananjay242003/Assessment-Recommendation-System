# SHL Assessment Recommendation System

An intelligent recommendation system that helps hiring managers find relevant SHL assessments based on natural language queries or job descriptions.

## Features

- **Semantic Search**: Uses sentence embeddings to understand query intent and match with relevant assessments
- **Balanced Recommendations**: Intelligently balances Knowledge & Skills vs Personality & Behavior assessments
- **Web Interface**: Clean, responsive frontend for easy querying
- **REST API**: FastAPI backend with standardized endpoints
- **Automated Data Collection**: Web scraper for SHL product catalog

## Performance

- **Mean Recall@10**: 0.2922 (29.22%)
- **Coverage**: 179 unique assessments from SHL catalog
- **Model**: sentence-transformers/all-MiniLM-L6-v2 (384-dim embeddings)

## Project Structure

```
├── backend/
│   ├── app.py                    # FastAPI application
│   ├── recommender.py            # Recommendation engine
│   └── prepare_embeddings.py     # Embedding generation
├── frontend/
│   ├── index.html                # Web UI
│   ├── app.js                    # Frontend logic
│   └── styles.css                # Styling
├── scraper/
│   └── scrape_shl.py            # Web scraper for SHL catalog
├── data/
│   ├── assessments.csv          # Assessment database
│   ├── embeddings.npy           # Pre-computed embeddings
│   └── train_test_data.csv      # Labeled data for evaluation
├── evaluate.py                   # Evaluation script
├── generate_predictions.py       # Generate submission predictions
├── fetch_missing_assessments.py  # Fetch missing URLs
└── requirements.txt              # Python dependencies
```

## Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

1. **Clone and setup**
```bash
git clone <repo-url>
cd task_SHL

# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Collect assessment data**
```bash
python scraper/scrape_shl.py
# Generates: data/assessments.csv
```

4. **Generate embeddings**
```bash
python backend/prepare_embeddings.py
# Generates: data/embeddings.npy
```

5. **Start the API server**
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

6. **Open the web interface**
- Open `frontend/index.html` in your browser
- Or use the API directly at `http://localhost:8000`

## API Endpoints

### Health Check
```http
GET /health
```
Response:
```json
{"status": "healthy"}
```

### Get Recommendations
```http
POST /recommend
Content-Type: application/json

{
  "query": "I am hiring for Java developers who can also collaborate effectively with my business teams."
}
```

Response:
```json
{
  "recommended_assessments": [
    {
      "url": "https://www.shl.com/...",
      "name": "Java 8 (New)",
      "adaptive_support": "No",
      "description": "Multi-choice test that measures...",
      "duration": 60,
      "remote_support": "Yes",
      "test_type": ["Knowledge & Skills"]
    }
  ]
}
```

## Evaluation

Run evaluation on labeled dataset:
```bash
python evaluate.py
```

Generate predictions for submission:
```bash
python generate_predictions.py
# Generates: predictions.csv
```

## Technical Approach

See [APPROACH.md](APPROACH.md) for detailed documentation on:
- Solution methodology
- Data pipeline architecture
- Optimization iterations
- Performance metrics

## Deployment

The project includes deployment configurations for Render/Railway:
- `render.yaml`: Service configuration
- `build.sh`: Build script
- `start.sh`: Start script

## Troubleshooting

**Model download takes long**: First run downloads the embedding model (~80MB). This is normal.

**Empty results from scraper**: If SHL changes their site structure, adjust selectors in `scraper/scrape_shl.py`.

**API not responding**: Ensure embeddings are generated before starting the API.

## License

MIT License

