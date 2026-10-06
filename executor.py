import time
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import DatabaseManager
from sql_validator import validate_sql

def execute_query(sql_query: str) -> tuple[pd.DataFrame | None, int, float, str | None]:
    """
    Executes a SQL query after validating it.
    Returns:
        - df: pandas DataFrame of results (or None if failed)
        - row_count: number of rows returned (0 if failed)
        - execution_time: time taken in seconds
        - error_message: string error message if failed (or None if success)
    """
    # 1. Validate the SQL first
    is_safe, validation_error = validate_sql(sql_query)
    if not is_safe:
        return None, 0, 0.0, validation_error

    db = DatabaseManager()
    engine = db.get_engine()
    
    start_time = time.time()
    try:
        # Execute query and load into pandas DataFrame
        with engine.connect() as connection:
            df = pd.read_sql(text(sql_query), connection)
            
        execution_time = round(time.time() - start_time, 4)
        row_count = len(df)
        return df, row_count, execution_time, None

    except SQLAlchemyError as e:
        execution_time = round(time.time() - start_time, 4)
        # Extract clean error text from SQLAlchemy/Postgres exception
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        return None, 0, execution_time, error_msg
    except Exception as e:
        execution_time = round(time.time() - start_time, 4)
        return None, 0, execution_time, str(e)

if __name__ == "__main__":
    # Test block: Run this file directly to test query execution
    print("--- Query Executor Test ---")
    
    # Test 1: Valid query
    valid_sql = "SELECT customerid, customername, city FROM customers LIMIT 3;"
    print(f"\nExecuting: {valid_sql}")
    df, rows, exec_time, err = execute_query(valid_sql)
    
    if err:
        print(f"Test 1 Failed with error: {err}")
    else:
        print(f"Test 1 PASSED | Rows: {rows} | Time: {exec_time}s")
        print(df)

    # Test 2: Invalid SQL syntax (testing error capture for retry loop)
    bad_sql = "SELECT * FROM non_existent_table_xyz;"
    print(f"\nExecuting invalid SQL: {bad_sql}")
    df, rows, exec_time, err = execute_query(bad_sql)
    
    if err:
        print(f"Test 2 PASSED (Correctly captured error) | Error message: {err}")
    else:
        print("Test 2 FAILED (Expected an error but got none)")