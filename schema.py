from sqlalchemy import inspect
from database import DatabaseManager

def get_live_schema(schema_name: str = "public") -> str:
    """
    Dynamically inspects the database to build a live schema representation
    including tables, columns, data types, and primary/foreign keys.
    """
    db = DatabaseManager()
    engine = db.get_engine()
    inspector = inspect(engine)
    
    schema_text = []
    
    # Retrieve all tables in the database
    table_names = inspector.get_table_names(schema=schema_name)
    
    if not table_names:
        return "No tables found in the database."
    
    for table in table_names:
        table_info = [f"Table: {table}"]
        
        # Extract Primary Keys
        pk_constraint = inspector.get_pk_constraint(table, schema=schema_name)
        pks = pk_constraint.get('constrained_columns', [])
        
        # Extract Foreign Keys
        fks = inspector.get_foreign_keys(table, schema=schema_name)
        fk_map = {}
        for fk in fks:
            for col, ref_col in zip(fk['constrained_columns'], fk['referred_columns']):
                fk_map[col] = f"{fk['referred_table']}.{ref_col}"
        
        # Extract Columns and Data Types
        columns = inspector.get_columns(table, schema=schema_name)
        table_info.append("Columns:")
        for col in columns:
            col_name = col['name']
            col_type = str(col['type'])
            
            attributes = []
            if col_name in pks:
                attributes.append("PRIMARY KEY")
            if col_name in fk_map:
                attributes.append(f"FOREIGN KEY -> {fk_map[col_name]}")
                
            attr_str = f" [{', '.join(attributes)}]" if attributes else ""
            table_info.append(f"  - {col_name} ({col_type}){attr_str}")
        
        # Join the table's details into a single string block
        schema_text.append("\n".join(table_info))
        
    # Join all table blocks with double newlines for clear separation
    return "\n\n".join(schema_text)

if __name__ == "__main__":
    # Test block: Run this file directly to verify schema extraction
    print("--- Live Schema Extraction Test ---\n")
    try:
        live_schema = get_live_schema()
        print("Successfully extracted schema. See output below:\n")
        print("="*50)
        print(live_schema)
        print("="*50)
        
        # Sanity check: Ensure at least one known table from the requirements is present
        if "Table: customers" in live_schema.lower() or "Table: products" in live_schema.lower():
            print("\nSanity Check: PASSED (Found expected tables like Customers or Products)")
        else:
            print("\nSanity Check: WARNING (Did not find expected tables. Check if database is populated.)")
            
    except Exception as e:
        print(f"Error extracting schema: {e}")