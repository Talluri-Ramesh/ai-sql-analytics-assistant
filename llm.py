import json
from groq import Groq
from config import GROQ_API_KEY

def get_groq_client():
    """Initializes and returns the Groq client."""
    return Groq(api_key=GROQ_API_KEY)

def generate_sql(question: str, live_schema: str) -> str:
    """
    Generates a PostgreSQL query based on the user question and live schema.
    Enforces strict rules:
    - Must use exact schema items only.
    - Ambiguous columns must be aliased.
    - Nested aggregates must use CTEs.
    """
    client = get_groq_client()
    
    system_prompt = (
        "You are an expert PostgreSQL developer for an E-Commerce database.\n"
        "Your task is to generate a single, valid PostgreSQL query to answer the user's question.\n"
        "CRITICAL RULES:\n"
        "1. Grounding: Use ONLY the tables, columns, and relationships present in the live schema provided below. Do not invent or fabricate tables, columns, or relationships.\n"
        "2. Aliasing/Ambiguity: When joining two or more tables where a column name exists in more than one table (e.g., orderid, productid), you MUST explicitly qualify that column with its table alias (e.g., o.orderid, not just orderid) to prevent ambiguous column errors.\n"
        "3. Nested Aggregates: Never nest aggregate functions directly (e.g., PERCENTILE_CONT inside SUM is invalid). Compute inner aggregates in a CTE (WITH clause) first, then apply outer functions to the CTE.\n"
        "4. Output format: Return ONLY valid SQL inside a markdown block (e.g., ```sql ... ```) with no extra conversational text.\n"
    )

    user_prompt = f"LIVE DATABASE SCHEMA:\n{live_schema}\n\nUSER QUESTION:\n{question}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0
    )

    raw_content = response.choices[0].message.content.strip()
    
    # Extract SQL from markdown code block if present
    if "```sql" in raw_content:
        parts = raw_content.split("```sql")
        sql_part = parts[1].split("```")[0].strip()
        return sql_part
    elif "```" in raw_content:
        parts = raw_content.split("```")
        sql_part = parts[1].strip()
        return sql_part
    
    return raw_content

def fix_sql(question: str, live_schema: str, failed_sql: str, error_message: str) -> str:
    """
    Self-correction retry method: takes a failed query and its PostgreSQL error message,
    and asks the LLM to fix it.
    """
    client = get_groq_client()
    
    system_prompt = (
        "You are an expert PostgreSQL debugging assistant.\n"
        "A previously generated SQL query failed to execute against the database.\n"
        "Analyze the schema, the user question, the failed SQL, and the exact database error message.\n"
        "Produce a corrected, valid PostgreSQL query.\n"
        "Return ONLY the corrected SQL inside a markdown code block (```sql ... ```).\n"
    )

    user_prompt = (
        f"LIVE DATABASE SCHEMA:\n{live_schema}\n\n"
        f"USER QUESTION:\n{question}\n\n"
        f"FAILED SQL:\n{failed_sql}\n\n"
        f"POSTGRES ERROR MESSAGE:\n{error_message}"
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0
    )

    raw_content = response.choices[0].message.content.strip()
    
    if "```sql" in raw_content:
        parts = raw_content.split("```sql")
        sql_part = parts[1].split("```")[0].strip()
        return sql_part
    elif "```" in raw_content:
        parts = raw_content.split("```")
        sql_part = parts[1].strip()
        return sql_part
        
    return raw_content

def explain_sql(sql_query: str) -> str:
    """Generates a brief, plain-English explanation of what a SQL query does."""
    client = get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Explain the following SQL query clearly and concisely in plain English for a business user."},
            {"role": "user", "content": sql_query}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def generate_narrative_insight(question: str, df_head_str: str) -> str:
    """Generates a short narrative business insight from query result sample data."""
    client = get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a business intelligence analyst. Provide a short, insightful narrative takeaway (1-2 sentences) based on the query and result data provided."},
            {"role": "user", "content": f"Question: {question}\n\nResult Data (Sample):\n{df_head_str}"}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def general_chat(question: str) -> str:
    """Handles Case B: general non-database chat queries."""
    client = get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful general-purpose AI assistant. Answer the user clearly and professionally."},
            {"role": "user", "content": question}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    print("--- LLM Wrapper Test ---")
    from schema import get_live_schema
    schema = get_live_schema()
    
    test_q = "Display customers from Hyderabad"
    print(f"Testing SQL generation for question: '{test_q}'")
    sql = generate_sql(test_q, schema)
    print(f"Generated SQL:\n{sql}")