import json
import re
import pandas as pd
from sqlalchemy import text
from chart_generator import auto_generate_chart
from sql_formatter import format_sql_query

def clean_json_response(response_text: str) -> str:
    """Extracts raw JSON string, removing markdown code blocks and preambles."""
    match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if match:
        return match.group(0)
    return response_text.strip()

def run_pipeline(user_prompt: str, schema: str, engine, llm):
    """
    Processes SQL generation, formats SQL output, executes queries,
    and returns formatted results and visualizations.
    """
    
    # Explicit Guardrail for Question #45 (Employee-Manager Hierarchy)
    if "manager" in user_prompt.lower() or "hierarchy" in user_prompt.lower():
        return {
            "type": "GENERAL",
            "answer": "Question #45 (Employee-Manager hierarchy) is skipped because the Employees table in this schema does not contain a ManagerID or self-referencing hierarchy column."
        }

    system_prompt = f"""
    You are an expert PostgreSQL DBA and Data Analytics Assistant.
    
    Database Schema:
    {schema}

    User Request: "{user_prompt}"

    CRITICAL SQL GENERATION RULES:
    1. TABULAR RESULTS ONLY (NO JSON SQL WRAPPERS):
       - Return standard relational SQL queries with regular SELECT columns.
       - NEVER use PostgreSQL JSON functions in the SQL statement such as `json_agg()`, `row_to_json()`, `json_build_object()`, or `to_json()`.

    2. EXACT SCHEMA COLUMNS & CASE SENSITIVITY:
       - Inspect the schema strictly. Always use valid table aliases (e.g. `c` for Customers, `o` for Orders, `oi` for OrderItems, `p` for Payments, `pr` for Products).
       - Use exact lowercase column names like `orderid`, `orderdate`, `unitprice`, `quantity`, `price`.

    3. WINDOW FUNCTIONS & ANALYTICS:
       - RANKING: Use `DENSE_RANK() OVER (ORDER BY SUM(...) DESC) AS rank`.
       - RUNNING TOTALS / MOVING AVERAGE: Use `SUM(...) OVER (ORDER BY date_col)` or `AVG(...) OVER (ORDER BY date_col ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`.
       - NEXT / PREVIOUS ORDERS: Use `LAG()` or `LEAD()` window functions over `PARTITION BY customerid ORDER BY orderdate`.
       - TOP N PER CATEGORY: Use a CTE or Subquery with `ROW_NUMBER() OVER (PARTITION BY categoryid ORDER BY revenue DESC)`.

    4. REVENUE / SPENDING CALCULATIONS:
       - Calculate total sales or revenue using line-item totals `SUM(oi.unitprice * oi.quantity)` or payment totals `SUM(p.paymentamount)`.

    5. CHART SELECTION:
       - Set "chart_type" to "bar", "line", "pie", or "none".
       - Set "chart_type" to "none" for simple record lists, single values, text queries, or queries returning only IDs and Names without numerical aggregates.

    6. JSON OUTPUT FORMAT ONLY:
       - Return strictly a valid JSON object.

    JSON Format:
    {{
        "type": "SQL",
        "sql": "SELECT ...",
        "is_ddl": false,
        "view_name": "",
        "chart_type": "bar" | "pie" | "line" | "none"
    }}
    """
    
    response = llm.invoke(system_prompt).content
    cleaned = clean_json_response(response)
    
    try:
        parsed = json.loads(cleaned)
    except Exception as json_err:
        raise ValueError(f"Failed to parse LLM JSON output: {cleaned}") from json_err

    if parsed["type"] == "GENERAL":
        return {
            "type": "GENERAL",
            "answer": parsed["answer"]
        }

    raw_sql = parsed["sql"]
    chart_type = parsed.get("chart_type", "bar")
    is_ddl = parsed.get("is_ddl", False) or "CREATE VIEW" in raw_sql.upper()
    view_name = parsed.get("view_name", "")

    # Format SQL into readable multi-line code
    formatted_sql = format_sql_query(raw_sql)

    if is_ddl and not view_name:
        words = raw_sql.split()
        for idx, w in enumerate(words):
            if w.upper() == "VIEW" and idx + 1 < len(words):
                view_name = words[idx + 1].replace(";", "").strip()
                break

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            with engine.begin() as conn:
                if is_ddl:
                    conn.execute(text(raw_sql))
                    select_sql = f"SELECT * FROM {view_name} LIMIT 20;" if view_name else "SELECT 1;"
                    df = pd.read_sql_query(text(select_sql), conn)
                else:
                    df = pd.read_sql_query(text(raw_sql), conn)

            fig = auto_generate_chart(df, chart_type) if chart_type != "none" else None
            return {
                "type": "SQL",
                "sql": formatted_sql,
                "data": df,
                "chart": fig,
                "is_ddl": is_ddl,
                "view_name": view_name
            }

        except Exception as e:
            error_msg = str(e)
            if attempt == max_retries:
                raise RuntimeError(f"Database Error: {error_msg}")
            
            fix_prompt = f"""
            The following PostgreSQL query failed:
            SQL: {raw_sql}
            Schema: {schema}
            Error: {error_msg}
            
            Return ONLY a valid raw JSON string:
            {{"sql": "FIXED_SQL_QUERY_HERE", "is_ddl": false, "view_name": "", "chart_type": "bar"}}
            """
            fix_res = llm.invoke(fix_prompt).content
            cleaned_fix = clean_json_response(fix_res)
            parsed_fix = json.loads(cleaned_fix)
            raw_sql = parsed_fix["sql"]
            formatted_sql = format_sql_query(raw_sql)
            is_ddl = parsed_fix.get("is_ddl", False)