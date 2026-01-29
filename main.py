# backend/main.py

from fastapi import FastAPI, UploadFile, File, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import traceback

app = FastAPI(title="Excel/CSV Analyzer")

# Add CORS middleware BEFORE other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_plot(df, column_name):
    """Generate histogram or bar chart for a single column"""
    try:
        col_data = df[column_name]
        plt.figure(figsize=(6, 4))
        
        if pd.api.types.is_numeric_dtype(col_data):
            col_data.hist(bins=10, color='skyblue', edgecolor='black')
            plt.title(f'Histogram of {column_name}')
            plt.xlabel(column_name)
            plt.ylabel('Frequency')
        else:
            col_counts = col_data.value_counts().head(10)
            col_counts.plot(kind='bar', color='skyblue', edgecolor='black')
            plt.title(f'Top values of {column_name}')
            plt.xlabel(column_name)
            plt.ylabel('Count')
            plt.xticks(rotation=45, ha='right')

        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return img_base64
    except Exception as e:
        print(f"Error in generate_plot: {str(e)}")
        traceback.print_exc()
        return None

def generate_summary(df):
    """Generate file summary"""
    summary_text = f"File has {df.shape[0]} rows and {df.shape[1]} columns.\n"
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    categorical_cols = df.select_dtypes(exclude='number').columns.tolist()
    summary_text += f"Numeric columns: {', '.join(numeric_cols) if numeric_cols else 'None'}.\n"
    summary_text += f"Categorical columns: {', '.join(categorical_cols) if categorical_cols else 'None'}.\n"
    return summary_text

def generate_comparison_chart(df, group_col, value_col):
    """Generate bar chart comparing groups (sorted by value)"""
    try:
        # Check how many unique values in group_col
        unique_count = df[group_col].nunique()
        print(f"Unique values in {group_col}: {unique_count}")
        
        # If too many unique values, just return None (don't generate chart)
        if unique_count > 50:
            print(f"Too many unique values ({unique_count}) for chart. Skipping chart generation.")
            return None
        
        plt.figure(figsize=(12, 6))
        
        # Get top categories if there are many (show top 15 max)
        if unique_count > 15:
            top_categories = df[group_col].value_counts().head(15).index
            df_filtered = df[df[group_col].isin(top_categories)]
        else:
            df_filtered = df
        
        # Calculate mean values and sort by them
        grouped_means = df_filtered.groupby(group_col)[value_col].mean().sort_values(ascending=False)
        
        # Create horizontal bar chart (better for long labels)
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(grouped_means)))
        grouped_means.plot(kind='barh', color=colors, edgecolor='black')
        
        plt.xlabel(f'Average {value_col}')
        plt.ylabel(group_col)
        plt.title(f'Average {value_col} by {group_col} (Sorted)')
        plt.gca().invert_yaxis()  # Highest value at top
        
        # Add value labels on bars
        for i, v in enumerate(grouped_means):
            plt.text(v, i, f' {v:.2f}', va='center', fontweight='bold')
        
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    except Exception as e:
        print(f"Error in generate_comparison_chart: {str(e)}")
        traceback.print_exc()
        return None

def generate_scatter_chart(df, x_col, y_col):
    """Generate scatter plot to show correlation"""
    try:
        plt.figure(figsize=(8, 5))
        
        # Sample data if too large
        if len(df) > 1000:
            df_sample = df.sample(1000)
        else:
            df_sample = df
        
        plt.scatter(df_sample[x_col], df_sample[y_col], alpha=0.5, color='steelblue')
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f'{y_col} vs {x_col}')
        
        # Add trend line if both are numeric
        try:
            z = np.polyfit(df_sample[x_col].dropna(), df_sample[y_col].dropna(), 1)
            p = np.poly1d(z)
            plt.plot(df_sample[x_col], p(df_sample[x_col]), "r--", alpha=0.8, linewidth=2)
        except:
            pass
        
        # Calculate correlation if both are numeric
        try:
            correlation = df[x_col].corr(df[y_col])
            plt.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                     transform=plt.gca().transAxes, verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        except:
            pass
        
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    except Exception as e:
        print(f"Error in generate_scatter_chart: {str(e)}")
        traceback.print_exc()
        return None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Data Analyzer Backend Running"}

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    """Basic analysis - no comparisons, just individual column stats"""
    try:
        file.file.seek(0)
        
        # Read file
        try:
            if file.filename.endswith(".csv"):
                # Try reading with different encodings
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'ascii']
                df = None
                for encoding in encodings:
                    try:
                        file.file.seek(0)  # Reset file pointer
                        df = pd.read_csv(file.file, encoding=encoding)
                        print(f"Successfully read CSV with encoding: {encoding}")
                        break
                    except (UnicodeDecodeError, UnicodeError):
                        continue
                
                if df is None:
                    return JSONResponse(status_code=400, content={"error": "Could not read CSV file. Unsupported encoding. Please use UTF-8, Latin-1, or CP1252 encoding."})
            elif file.filename.endswith(".xlsx"):
                file.file.seek(0)  # Reset file pointer
                df = pd.read_excel(file.file)
            else:
                return JSONResponse(status_code=400, content={"error": "Unsupported file format"})
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return JSONResponse(status_code=500, content={"error": f"Failed to read file: {str(e)}"})

        analysis = []
        charts = {}

        # Generate basic analysis for each column
        for col in df.columns:
            col_data = df[col]
            missing_percent = round(col_data.isna().mean() * 100, 2)
            column_info = {
                "name": col,
                "missing_percent": missing_percent
            }

            if pd.api.types.is_numeric_dtype(col_data):
                column_info["type"] = "numeric"
                column_info["stats"] = {
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "mean": round(float(col_data.mean()), 2),
                    "median": float(col_data.median())
                }
            else:
                column_info["type"] = "categorical"
                column_info["top_values"] = col_data.value_counts().head(5).to_dict()

            analysis.append(column_info)
            charts[col] = generate_plot(df, col)

        summary = generate_summary(df)

        return {
            "file_info": {
                "rows": df.shape[0],
                "columns": df.shape[1]
            },
            "summary": summary,
            "analysis": analysis,
            "charts": charts,
            "columns": [col for col in df.columns]
        }
    except Exception as e:
        print(f"Unexpected error in /analyze: {str(e)}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Server error: {str(e)}"})

@app.post("/compare")
async def compare_columns(request: Request):
    """Comparative analysis based on user selection"""
    try:
        # Parse JSON body
        body = await request.json()
        group_col = body.get("group_col")
        value_col = body.get("value_col")
        file_content = body.get("file_content")
        
        print(f"\n=== COMPARE REQUEST ===")
        print(f"group_col: {group_col}")
        print(f"value_col: {value_col}")
        print(f"file_content length: {len(file_content) if file_content else 0}")
        
        if not file_content or len(file_content) == 0:
            return JSONResponse(status_code=400, content={"error": "No file content provided"})
        
        # Parse the CSV data from request
        from io import StringIO
        df = pd.read_csv(StringIO(file_content))
        
        print(f"DataFrame shape: {df.shape}")
        print(f"DataFrame columns: {list(df.columns)}")
        
        # Validate columns exist
        if group_col not in df.columns:
            error_msg = f"Column '{group_col}' not found. Available: {list(df.columns)}"
            print(f"ERROR: {error_msg}")
            return JSONResponse(status_code=400, content={"error": error_msg})
        
        if value_col not in df.columns:
            error_msg = f"Column '{value_col}' not found. Available: {list(df.columns)}"
            print(f"ERROR: {error_msg}")
            return JSONResponse(status_code=400, content={"error": error_msg})
        
        comparison_result = {
            "group_column": group_col,
            "value_column": value_col,
            "type": None,
            "chart": None,
            "data": None
        }
        
        # Check column types
        group_is_numeric = pd.api.types.is_numeric_dtype(df[group_col])
        value_is_numeric = pd.api.types.is_numeric_dtype(df[value_col])
        
        print(f"group_is_numeric: {group_is_numeric}, value_is_numeric: {value_is_numeric}")
        
        # Helper function to convert NaN to None for JSON serialization
        def convert_to_json_safe(val):
            """Convert numpy/pandas types to JSON-safe Python types"""
            if pd.isna(val) or (isinstance(val, float) and np.isnan(val)):
                return None
            if isinstance(val, (np.integer, np.floating)):
                return float(val) if isinstance(val, np.floating) else int(val)
            return val
        
        # Case 1: Categorical vs Numeric (Group by category, show numeric stats)
        if not group_is_numeric and value_is_numeric:
            print("CASE 1: Group Comparison (Categorical vs Numeric)")
            comparison_result["type"] = "group_comparison"
            
            unique_count = df[group_col].nunique()
            
            # For high-cardinality columns (like Name with thousands of values),
            # just show top 20 instead of trying to group all
            if unique_count > 50:
                print(f"High cardinality detected ({unique_count} unique values). Showing top 20.")
                # Get top 20 by value_col (sorted by mean descending)
                top_groups = df.groupby(group_col)[value_col].mean().nlargest(20)
                df_filtered = df[df[group_col].isin(top_groups.index)]
                grouped = df_filtered.groupby(group_col)[value_col].agg(['mean', 'median', 'min', 'max', 'std', 'count'])
            else:
                grouped = df.groupby(group_col)[value_col].agg(['mean', 'median', 'min', 'max', 'std', 'count'])
            
            # Sort by mean descending (highest values first)
            grouped = grouped.sort_values('mean', ascending=False)
            
            data = {}
            for group_name, row in grouped.iterrows():
                # Convert all numpy types to Python native types and handle NaN
                data[str(group_name)] = {
                    "mean": convert_to_json_safe(round(float(row['mean']), 2) if pd.notna(row['mean']) else None),
                    "median": convert_to_json_safe(round(float(row['median']), 2) if pd.notna(row['median']) else None),
                    "min": convert_to_json_safe(round(float(row['min']), 2) if pd.notna(row['min']) else None),
                    "max": convert_to_json_safe(round(float(row['max']), 2) if pd.notna(row['max']) else None),
                    "std": convert_to_json_safe(round(float(row['std']), 2) if pd.notna(row['std']) else None),
                    "count": int(row['count'])
                }
            
            comparison_result["data"] = data
            comparison_result["chart"] = generate_comparison_chart(df, group_col, value_col)
            print(f"Groups found: {list(data.keys())}")
        
        # Case 2: Numeric vs Numeric (Correlation scatter plot)
        elif value_is_numeric and group_is_numeric:
            print("CASE 2: Correlation (Numeric vs Numeric)")
            comparison_result["type"] = "correlation"
            
            try:
                correlation = float(df[group_col].corr(df[value_col]))
                if np.isnan(correlation):
                    correlation = 0.0
            except:
                correlation = 0.0
            
            comparison_result["data"] = {
                "correlation": float(round(correlation, 3)),
                "group_column": group_col,
                "value_column": value_col
            }
            comparison_result["chart"] = generate_scatter_chart(df, group_col, value_col)
            print(f"Correlation: {correlation:.3f}")
        
        # Case 3: Categorical vs Categorical (Cross tabulation)
        elif not group_is_numeric and not value_is_numeric:
            print("CASE 3: Cross Tabulation (Categorical vs Categorical)")
            comparison_result["type"] = "cross_tabulation"
            crosstab = pd.crosstab(df[group_col], df[value_col])
            # Convert to dict with proper type conversion
            data_dict = {}
            for row_name in crosstab.index:
                data_dict[str(row_name)] = {str(col): int(crosstab.loc[row_name, col]) for col in crosstab.columns}
            comparison_result["data"] = data_dict
        
        # Case 4: Numeric vs Categorical (doesn't make sense)
        else:
            print("CASE 4: Invalid combination")
            comparison_result["type"] = "invalid"
            comparison_result["data"] = {"error": "Please select appropriate columns for comparison"}
        
        print(f"Result type: {comparison_result['type']}")
        print("=== COMPARE SUCCESS ===\n")
        
        # Return using JSONResponse which handles serialization
        return JSONResponse(content=comparison_result)
        
    except Exception as e:
        print(f"=== ERROR IN /COMPARE ===")
        print(f"Error: {str(e)}")
        traceback.print_exc()
        print("=== ERROR END ===\n")
        return JSONResponse(status_code=500, content={"error": f"Comparison failed: {str(e)}"})
