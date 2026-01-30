# Data Analyzer Backend

A FastAPI-powered web application for analyzing CSV and Excel files with statistical insights, visualizations, and comparative analysis. Built with a React frontend and Python backend.

## Features

- **File Upload**: Support for CSV and Excel (.xlsx) files
- **Statistical Analysis**: Automatic analysis of numeric and categorical columns
- **Visualizations**: Generate histograms, bar charts, and scatter plots
- **Comparative Analysis**: Compare columns to find relationships and correlations
- **Responsive UI**: Modern React interface with real-time analysis

## Tech Stack

- **Backend**: FastAPI, Pandas, Matplotlib, NumPy
- **Frontend**: React 19, Vite, JavaScript
- **Deployment**: Render, Docker-ready

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/clickcafence/data-analyzer-backend.git
cd data-analyzer-backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend:
```bash
uvicorn main:app --reload
```
Backend will be available at `http://127.0.0.1:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```
Frontend will be available at `http://localhost:5173`

## API Endpoints

### POST `/analyze`
Upload a CSV/Excel file for analysis.

**Request:**
- `file`: Multipart form data (CSV or XLSX)

**Response:**
```json
{
  "file_info": { "rows": int, "columns": int },
  "summary": "string",
  "analysis": [
    {
      "name": "column_name",
      "type": "numeric|categorical",
      "missing_percent": float,
      "stats": { "min": float, "max": float, "mean": float, "median": float },
      "top_values": { "key": count }
    }
  ],
  "charts": { "column_name": "base64_encoded_png" }
}
```

### POST `/compare`
Compare two columns for relationships.

**Request:**
```json
{
  "group_col": "column_name",
  "value_col": "column_name",
  "file_content": "csv_as_string"
}
```

**Response:**
```json
{
  "type": "group_comparison|correlation|cross_tabulation",
  "data": {...},
  "chart": "base64_encoded_png"
}
```

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions using Render, Heroku, or other platforms.

### Quick Deploy to Render

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Create new Web Service from GitHub
4. Configure with provided `render.yaml` file
5. Deploy!

## Project Structure

```
.
├── main.py                 # FastAPI backend
├── requirements.txt        # Python dependencies
├── render.yaml            # Render deployment config
├── Procfile               # Heroku deployment config
├── DEPLOYMENT.md          # Detailed deployment guide
├── medical.csv            # Sample data
├── vgsales.csv            # Sample data
├── population_total.csv   # Sample data
└── frontend/
    ├── package.json       # Node dependencies
    ├── vite.config.js     # Vite configuration
    ├── index.html         # HTML entry point
    └── src/
        ├── App.jsx        # Main React component
        ├── App.css        # Styles
        └── main.jsx       # React entry point
```

## Sample Data

The repository includes sample datasets:
- `medical.csv`: Insurance data with age, BMI, charges, etc.
- `vgsales.csv`: Video game sales data
- `population_total.csv`: Population statistics

## Configuration

### Environment Variables

**Development** (optional):
```
VITE_API_URL=http://127.0.0.1:8000
```

**Production**:
Set `VITE_API_URL` to your deployed backend URL in Render environment variables.

## Troubleshooting

### Backend Issues
- **502 Bad Gateway**: Check Render logs - backend might not be starting
- **CORS errors**: Verify CORS middleware is enabled in `main.py`
- **File upload fails**: Check file size and format (.csv or .xlsx)

### Frontend Issues
- **API calls fail**: Ensure `VITE_API_URL` is set correctly
- **Charts don't display**: Backend must be running
- **Build errors**: Run `npm install` in frontend directory

### File Encoding Issues
If CSV upload fails, try:
- Saving file as UTF-8 encoding
- Using Excel to resave as CSV
- Removing special characters from column names

## License

MIT

## Author

[@clickcafence](https://github.com/clickcafence)

## Support

For issues and questions, open a GitHub issue or check the [DEPLOYMENT.md](./DEPLOYMENT.md) guide.
