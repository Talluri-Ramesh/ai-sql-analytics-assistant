import re

def validate_sql(sql_query: str) -> tuple[bool, str]:
    """
    Validates that a SQL query is safe to execute:
    - Must be a single statement (no multiple semicolons).
    - Must start with SELECT or WITH (CTE).
    - Must not contain any destructive or modification keywords.
    """
    if not sql_query or not isinstance(sql_query, str):
        return False, "Query is empty or invalid."

    # Clean up whitespace and trailing semicolons for analysis
    cleaned_sql = sql_query.strip().rstrip(";")

    # 1. Check for multiple statements (semicolon inside the query body)
    if ";" in cleaned_sql:
        return False, "Validation Error: Multiple SQL statements (stacked queries) are not allowed."

    # 2. Convert to uppercase for keyword checking
    sql_upper = cleaned_sql.upper()

    # 3. Must start with SELECT or WITH
    if not (sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")):
        return False, "Validation Error: Query must start with SELECT or WITH (read-only)."

    # 4. Blacklist of forbidden destructive/modification keywords
    forbidden_keywords = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", 
        "TRUNCATE", "CREATE", "GRANT", "REVOKE", "EXEC", "CALL", "REPLACE"
    ]

    # Use regex word boundaries to prevent false positives (e.g., a column named 'updated_at' won't trigger 'UPDATE')
    for keyword in forbidden_keywords:
        pattern = rf"\b{keyword}\b"
        if re.search(pattern, sql_upper):
            return False, f"Validation Error: Destructive or unauthorized keyword found: '{keyword}'."

    return True, "SQL is safe."

if __name__ == "__main__":
    # Test block: Run this file directly to verify safety checks
    print("--- SQL Validator Test ---")
    
    test_queries = [
        ("SELECT * FROM customers;", True),
        ("WITH cte AS (SELECT * FROM products) SELECT * FROM cte;", True),
        ("SELECT * FROM orders; DROP TABLE customers;", False),
        ("UPDATE products SET price = 0 WHERE productid = 201;", False),
        ("SELECT * FROM employees WHERE department = 'Sales';", True),
        ("DELETE FROM payments WHERE paymentid = 1;", False)
    ]

    all_passed = True
    for query, expected in test_queries:
        is_safe, msg = validate_sql(query)
        status = "PASSED" if is_safe == expected else "FAILED"
        if status == "FAILED":
            all_passed = False
        print(f"[{status}] Expected: {expected} | Result: {is_safe} | Query: {query}")

    print("\nValidator testing completed!")