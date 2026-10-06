import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def generate_chart(df: pd.DataFrame) -> go.Figure | None:
    """
    Inspects a pandas DataFrame and automatically generates an appropriate Plotly chart:
    - Bar / Pie: 1 categorical column + 1 numeric column
    - Line chart: Date/Time column + 1 numeric column
    Returns None if unchartable.
    """
    if df is None or df.empty or len(df.columns) < 2 or len(df) == 0:
        return None

    # Identify column types
    cols = df.columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()

    # Also check if an object column can be parsed as dates (e.g., 'orderdate' stored as text/string)
    if not date_cols:
        for col in categorical_cols:
            try:
                pd.to_datetime(df[col], errors='raise')
                date_cols.append(col)
                categorical_cols.remove(col)
                break
            except (ValueError, TypeError):
                continue

    # Case 1: Time-series / Date trend (Date column + Numeric column) -> Line Chart
    if len(date_cols) >= 1 and len(numeric_cols) >= 1:
        x_col = date_cols[0]
        y_col = numeric_cols[0]
        
        # Sort values by date to ensure clean line charts
        df_sorted = df.sort_values(by=x_col)
        
        fig = px.line(
            df_sorted, 
            x=x_col, 
            y=y_col, 
            markers=True, 
            title=f"Trend of {y_col} over {x_col}",
            template="plotly_white"
        )
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=400)
        return fig

    # Case 2: Categorical comparison (1 Categorical column + 1 Numeric column) -> Bar Chart
    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        x_col = categorical_cols[0]
        y_col = numeric_cols[0]
        
        # If there are too many rows (e.g. > 30), limit or use top categories for readability
        plot_df = df.head(25) if len(df) > 25 else df

        fig = px.bar(
            plot_df, 
            x=x_col, 
            y=y_col, 
            text_auto='.2s',
            title=f"{y_col} by {x_col}",
            template="plotly_white"
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            margin=dict(l=20, r=20, t=40, b=80),
            height=400
        )
        return fig

    # Default fallback: Unchartable configuration
    return None

if __name__ == "__main__":
    print("--- Chart Generator Test ---")
    
    # Test 1: Categorical + Numeric (Should produce a Bar chart)
    df_bar = pd.DataFrame({
        "CategoryName": ["Electronics", "Fashion", "Books"],
        "TotalRevenue": [125000, 45000, 12000]
    })
    fig1 = generate_chart(df_bar)
    print(f"Test 1 (Bar Chart): {'PASSED' if fig1 is not None else 'FAILED'}")

    # Test 2: Unchartable (Single scalar value)
    df_scalar = pd.DataFrame({"total": [500000]})
    fig2 = generate_chart(df_scalar)
    print(f"Test 2 (Scalar Fallback): {'PASSED' if fig2 is None else 'FAILED'}")