# Data Analyzer Project - AI Coding Assistant Instructions

## Architecture Overview

This is a **monorepo** containing a data analysis application with two main components:

- **Backend** (root): FastAPI server in [main.py](../main.py) - handles CSV/Excel upload, generates statistics, and creates matplotlib charts
- **Frontend** ([frontend/](../frontend/)): React + Vite SPA - provides file upload interface and displays analysis results

**Data flow**: User uploads file → Frontend POSTs to `/analyze` → Backend returns JSON with analysis + base64-encoded chart images → Frontend renders in tables and `<img>` tags

## Project-Specific Patterns

### Backend ([main.py](../main.py))

- **Single-file FastAPI app** with no route separation - all endpoints and helper functions in one file
- **Two helper functions** define the analysis logic:
  - `generate_plot(df, column_name)`: Creates matplotlib histograms (numeric) or bar charts (categorical), returns base64-encoded PNG
  - `generate_summary(df)`: Returns text summary with row/column counts and column type breakdown
- **File handling**: Supports `.csv` (pandas `read_csv`) and `.xlsx` (pandas `read_excel`)
- **Column analysis pattern**: 
  - Numeric columns: min, max, mean, median stats
  - Categorical columns: top 5 value counts
  - All columns: missing percentage
- **No CORS middleware configured** - add `CORSMiddleware` if frontend runs on different origin
- **No database** - stateless request/response only

### Frontend ([frontend/src/App.jsx](../frontend/src/App.jsx))

- **Vanilla React** (no state management library) - all state in `App` component using `useState`
- **Hardcoded backend URL**: `http://127.0.0.1:8000/analyze` - update for production deployment
- **No error handling UI** - errors logged to console only
- **Data display**: Analysis table shows raw JSON strings for stats/top_values - consider formatting
- **Charts rendered as base64 images** directly in `<img src="data:image/png;base64,..." />`

## Development Workflow

### Running the application

**Backend** (from root directory):
```bash
uvicorn main:app --reload
# Runs on http://127.0.0.1:8000
```

**Frontend** (from `frontend/` directory):
```bash
npm install  # First time only
npm run dev
# Runs on http://localhost:5173
```

### Testing with sample data

- Use [medical.csv](../medical.csv) (sample insurance data with 7 columns: age, sex, bmi, children, smoker, region, charges)
- Test both numeric (age, bmi, charges) and categorical (sex, smoker, region) column handling

## Key Integration Points

- **API contract**: Single POST endpoint `/analyze` with `multipart/form-data` file upload
- **Response structure**:
  ```json
  {
    "file_info": { "rows": int, "columns": int },
    "summary": "string",
    "analysis": [{ "name": str, "type": "numeric"|"categorical", "missing_percent": float, ... }],
    "charts": { "column_name": "base64_string", ... }
  }
  ```
- **No authentication or rate limiting** - add if deploying publicly

## Dependencies

- **Backend**: FastAPI, pandas, matplotlib (no requirements.txt - dependencies in venv)
- **Frontend**: React 19, Vite 7, no UI library

## What NOT to assume

- Don't expect TypeScript - frontend uses vanilla JavaScript (.jsx)
- Don't look for API client abstractions - frontend uses raw `fetch()`
- Don't expect environment variables - URLs and configs are hardcoded
