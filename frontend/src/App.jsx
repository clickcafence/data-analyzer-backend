// frontend/src/App.js

import React, { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [fileContent, setFileContent] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [charts, setCharts] = useState({});
  const [summary, setSummary] = useState("");
  const [fileInfo, setFileInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  // Comparison state
  const [selectedGroupCol, setSelectedGroupCol] = useState("");
  const [selectedValueCol, setSelectedValueCol] = useState("");
  const [comparisonResult, setComparisonResult] = useState(null);
  const [comparisonLoading, setComparisonLoading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setError("");
    
    // Read file content for comparison analysis
    if (selectedFile) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setFileContent(event.target.result);
      };
      reader.readAsText(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first");
      return;
    }

    setLoading(true);
    setError("");
    setComparisonResult(null);
    setSelectedGroupCol("");
    setSelectedValueCol("");
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      const data = await response.json();

      setAnalysis(data.analysis);
      setCharts(data.charts);
      setSummary(data.summary);
      setFileInfo(data.file_info);
    } catch (err) {
      console.error("Upload failed:", err);
      setError(err.message || "Failed to analyze file. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleCompare = async () => {
    if (!selectedGroupCol || !selectedValueCol) {
      setError("Please select both columns");
      return;
    }

    if (!fileContent) {
      setError("File content not loaded. Please upload the file again.");
      return;
    }

    setComparisonLoading(true);
    setError("");

    try {
      console.log("Sending comparison request...");
      console.log("Group column:", selectedGroupCol);
      console.log("Value column:", selectedValueCol);
      console.log("File content size:", fileContent.length);

      const response = await fetch("http://127.0.0.1:8000/compare", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({
          group_col: selectedGroupCol,
          value_col: selectedValueCol,
          file_content: fileContent
        })
      });

      console.log("Response status:", response.status);
      
      if (!response.ok) {
        let errorMessage = `Server error: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorMessage;
        } catch (e) {
          console.log("Could not parse error response");
        }
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      console.log("Comparison result:", data);
      setComparisonResult(data);
    } catch (err) {
      console.error("Comparison failed:", err);
      setError(err.message || "Failed to compare columns. Check browser console for details.");
    } finally {
      setComparisonLoading(false);
    }
  };

  const renderComparisonResult = () => {
    if (!comparisonResult) return null;

    if (comparisonResult.type === "group_comparison") {
      return (
        <div className="comparison-result">
          <h3>📊 Comparison: {comparisonResult.value_column} by {comparisonResult.group_column}</h3>
          
          <div className="comparison-table">
            <table>
              <thead>
                <tr>
                  <th>{comparisonResult.group_column}</th>
                  <th>Mean</th>
                  <th>Median</th>
                  <th>Min</th>
                  <th>Max</th>
                  <th>Std Dev</th>
                  <th>Count</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(comparisonResult.data).map(([group, stats]) => (
                  <tr key={group}>
                    <td><strong>{group}</strong></td>
                    <td>{stats.mean}</td>
                    <td>{stats.median}</td>
                    <td>{stats.min}</td>
                    <td>{stats.max}</td>
                    <td>{stats.std}</td>
                    <td>{stats.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {comparisonResult.chart && (
            <div className="chart-card">
              <img 
                src={`data:image/png;base64,${comparisonResult.chart}`} 
                alt="Comparison chart" 
              />
            </div>
          )}
        </div>
      );
    }

    if (comparisonResult.type === "correlation") {
      return (
        <div className="comparison-result">
          <h3>📈 Correlation: {comparisonResult.group_column} vs {comparisonResult.value_column}</h3>
          <p><strong>Correlation coefficient:</strong> {comparisonResult.data.correlation}</p>
          
          {comparisonResult.chart && (
            <div className="chart-card">
              <img 
                src={`data:image/png;base64,${comparisonResult.chart}`} 
                alt="Correlation chart" 
              />
            </div>
          )}
        </div>
      );
    }

    return null;
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>📊 Excel/CSV Data Analyzer</h1>
        <p>Upload your CSV or Excel file to get instant statistical analysis</p>
      </header>

      <div className="upload-section">
        <input 
          type="file" 
          accept=".csv,.xlsx" 
          onChange={handleFileChange}
          disabled={loading}
          id="file-input"
        />
        <label htmlFor="file-input" className="file-label">
          {file ? file.name : "Choose File"}
        </label>
        <button 
          onClick={handleUpload} 
          disabled={loading || !file}
          className="upload-btn"
        >
          {loading ? "Analyzing..." : "Upload & Analyze"}
        </button>
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {fileInfo && (
        <div className="file-info">
          <h3>📄 File Information</h3>
          <p><strong>Rows:</strong> {fileInfo.rows.toLocaleString()} | <strong>Columns:</strong> {fileInfo.columns}</p>
        </div>
      )}

      {summary && (
        <div className="summary-box">
          <h3>📋 Summary</h3>
          <pre>{summary}</pre>
        </div>
      )}

      {analysis && (
        <>
          <div className="analysis-section">
            <h2>📈 Column Statistics</h2>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Column Name</th>
                    <th>Type</th>
                    <th>Missing %</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {analysis.map((col) => (
                    <tr key={col.name}>
                      <td><strong>{col.name}</strong></td>
                      <td>
                        <span className={`badge ${col.type}`}>
                          {col.type === "numeric" ? "🔢 Numeric" : "📝 Categorical"}
                        </span>
                      </td>
                      <td>{col.missing_percent}%</td>
                      <td className="details-cell">
                        {col.type === "numeric" ? (
                          <div className="stats-grid">
                            <div><strong>Min:</strong> {col.stats.min}</div>
                            <div><strong>Max:</strong> {col.stats.max}</div>
                            <div><strong>Mean:</strong> {col.stats.mean}</div>
                            <div><strong>Median:</strong> {col.stats.median}</div>
                          </div>
                        ) : (
                          <div className="top-values">
                            {Object.entries(col.top_values).map(([key, value]) => (
                              <div key={key}>
                                <strong>{key}:</strong> {value}
                              </div>
                            ))}
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {charts && Object.keys(charts).length > 0 && (
            <div className="charts-section">
              <h2>📊 Column Visualizations</h2>
              <div className="charts-grid">
                {Object.entries(charts).map(([col, base64]) => (
                  <div key={col} className="chart-card">
                    <h3>{col}</h3>
                    <img src={`data:image/png;base64,${base64}`} alt={`${col} chart`} />
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="comparison-section">
            <h2>🔍 Comparative Analysis (Optional)</h2>
            <p>Select two columns to compare and find relationships in your data</p>
            
            <div className="comparison-controls">
              <div className="control-group">
                <label>Group Column (usually categorical):</label>
                <select 
                  value={selectedGroupCol} 
                  onChange={(e) => setSelectedGroupCol(e.target.value)}
                >
                  <option value="">-- Select Column --</option>
                  {analysis.map((col) => (
                    <option key={col.name} value={col.name}>{col.name}</option>
                  ))}
                </select>
              </div>

              <div className="control-group">
                <label>Value Column (usually numeric):</label>
                <select 
                  value={selectedValueCol} 
                  onChange={(e) => setSelectedValueCol(e.target.value)}
                >
                  <option value="">-- Select Column --</option>
                  {analysis.map((col) => (
                    <option key={col.name} value={col.name}>{col.name}</option>
                  ))}
                </select>
              </div>

              <button 
                onClick={handleCompare}
                disabled={comparisonLoading || !selectedGroupCol || !selectedValueCol}
                className="compare-btn"
              >
                {comparisonLoading ? "Analyzing..." : "Compare"}
              </button>
            </div>

            {renderComparisonResult()}
          </div>
        </>
      )}

      {!analysis && !loading && (
        <div className="empty-state">
          <p>👆 Select a CSV or Excel file to begin analysis</p>
        </div>
      )}
    </div>
  );
}

export default App;
