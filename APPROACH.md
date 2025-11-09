# SHL Assessment Recommendation System - Technical Approach

## Overview
This document outlines the methodology, optimization efforts, and technical implementation of an intelligent recommendation system for SHL assessments. The system takes natural language queries or job descriptions and returns relevant assessment recommendations.

## 1. Solution Approach

### 1.1 Methodology
The solution employs a **semantic search-based recommendation engine** using sentence embeddings and cosine similarity:

1. **Data Collection**: Web scraping of SHL's product catalog to build a comprehensive assessment database
2. **Embedding Generation**: Converting assessment descriptions into dense vector representations using SentenceTransformer
3. **Query Processing**: Encoding user queries and computing semantic similarity with the assessment corpus
4. **Balanced Ranking**: Intelligent re-ranking to balance technical (Knowledge & Skills) and behavioral (Personality & Behavior) assessments

### 1.2 Data Pipeline

#### Data Crawling
- **Target**: `https://www.shl.com/solutions/products/product-catalog/`
- **Implementation**: Python with `requests` and `BeautifulSoup4`
- **Strategy**: 
  - Extracted individual test solutions (excluded pre-packaged job solutions)
  - Captured: assessment name, URL, description, test type
  - Rate-limited requests (1 sec between requests) to be polite
  - Handled multiple URL patterns (`/products/...` and `/solutions/products/...`)

#### Initial Results
- **Baseline scrape**: 126 assessments from catalog
- **Problem identified**: Training data contained 55/65 URLs with different path pattern
- **Solution**: Implemented supplementary fetcher to crawl missing assessments from training URLs
- **Final dataset**: 179 unique assessments

#### Data Representation
```
Assessment Schema:
- name: string (assessment title)
- url: string (canonical SHL URL)
- description: string (detailed description for embedding)
- type: string (Knowledge & Skills / Personality & Behavior)
```

#### Storage
- **Format**: CSV (data/assessments.csv)
- **Embeddings**: NumPy array (179 × 384 dimensions, float32)
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
  - Fast inference
  - Good quality-to-size ratio
  - 384-dimensional embeddings

### 1.3 Technology Stack

**Backend:**
- FastAPI (API framework)
- SentenceTransformers (embedding model)
- NumPy (vector operations)
- Pandas (data handling)

**Frontend:**
- Vanilla HTML/CSS/JavaScript
- Responsive design with dark theme
- Tabular results display

**Deployment:**
- Platform: Render / Railway (free tier)
- Runtime: Python 3.11
- Automated build pipeline with data preparation

### 1.4 Evaluation & Tracing

#### Metrics
Primary metric: **Mean Recall@10**
```
Recall@K = (# relevant assessments in top K) / (total relevant assessments)
Mean Recall@10 = average Recall@10 across all test queries
```

#### Evaluation Process
1. Load labeled training data (10 unique queries, 65 query-URL pairs)
2. Generate top-10 recommendations for each query
3. Calculate recall by comparing recommended URLs with ground truth
4. Aggregate results to compute mean performance

## 2. Performance and Optimization

### 2.1 Initial Results (Baseline)
- **Mean Recall@10**: 0.0167 (1.67%)
- **Issue**: URL pattern mismatch - scraped catalog used different URL structure than training data
- **Root cause**: Incomplete catalog coverage

### 2.2 Optimization Iteration 1: Data Augmentation
**Change**: Fetched missing assessments from training data URLs
- Added 53 assessments that were missing from initial scrape
- Total dataset: 126 → 179 assessments (+42%)
- Rebuilt embeddings with expanded corpus

**Results**:
- **Mean Recall@10**: 0.2922 (29.22%)
- **Improvement**: +27.55 percentage points (~17x improvement)
- **Best query**: 0.6000 recall
- **Worst query**: 0.0000 recall (1/10 queries)

### 2.3 Balancing Logic
**Implementation**: Test type aware re-ranking
```python
def infer_needs(query):
    # Compare query embedding with prototypes
    - "Knowledge & Skills" prototype
    - "Personality & Behavior" prototype
    
    if similarity scores are close:
        return "both"  # Mixed requirement
    else:
        return dominant type
```

**Balancing Strategy**:
- For "both" queries: Ensure minimum 3 assessments from each type
- Fill remaining slots by overall similarity ranking
- Prevents recommendation bias toward single assessment category

**Example**: "Java developer who collaborates with teams"
- Technical signal: "Java developer" → Knowledge & Skills tests
- Behavioral signal: "collaborates with teams" → Personality & Behavior tests
- Result: Balanced mix of coding tests and teamwork assessments

### 2.4 Final Performance Summary
| Metric | Value |
|--------|-------|
| Mean Recall@10 | 0.2922 |
| Best Recall | 0.6000 |
| Worst Recall | 0.0000 |
| Queries with hits | 9/10 (90%) |
| Total assessments | 179 |
| Avg recommendations/query | 10 |

### 2.5 Remaining Limitations
1. **One zero-recall query**: System failed to find relevant assessments for 1 query
   - Likely due to highly specific or niche requirements
   - Could improve with query expansion or fallback strategies

2. **Limited test type diversity**: Current catalog mostly contains "Knowledge & Skills" assessments
   - Need more "Personality & Behavior" assessments for better balance

3. **Description quality**: Embedding quality depends on assessment description richness
   - Some assessments have minimal descriptions

## 3. API Structure

### Endpoints
**GET /health**
- Returns: `{"status": "healthy"}`

**POST /recommend**
- Request: `{"query": "natural language query or JD"}`
- Response:
```json
{
  "recommended_assessments": [
    {
      "url": "https://www.shl.com/...",
      "name": "Assessment Name",
      "adaptive_support": "Yes/No",
      "description": "Detailed description",
      "duration": 60,
      "remote_support": "Yes/No",
      "test_type": ["Knowledge & Skills"]
    }
  ]
}
```

## 4. Future Improvements
1. **Query expansion**: Use LLM to expand queries with synonyms and related terms
2. **Reranking with LLM**: Use Gemini API for intelligent reranking based on context
3. **User feedback loop**: Collect click data to improve recommendations
4. **Duration filtering**: Allow users to filter by assessment duration
5. **Multi-language support**: Extend to non-English job descriptions

