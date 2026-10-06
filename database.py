from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config import DATABASE_URL

class DatabaseManager:
    """
    Singleton class to manage the SQLAlchemy database engine.
    Ensures only one engine instance is created and shared across the app.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._engine = None
        return cls._instance

    def get_engine(self):
        """Returns the SQLAlchemy engine, creating it if it doesn't exist."""
        if self._engine is None:
            try:
                # pool_pre_ping=True ensures the connection is alive before using it
                self._engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            except SQLAlchemyError as e:
                raise RuntimeError(f"CRITICAL ERROR: Failed to create SQLAlchemy engine: {e}")
        return self._engine

    def test_connection(self):
        """Tests if the database connection can actually be established."""
        try:
            engine = self.get_engine()
            with engine.connect() as connection:
                # Run a simple query to verify connection
                result = connection.execute(text("SELECT 1;"))
                result.fetchone()
            return True, "Successfully connected to the PostgreSQL database!"
        except Exception as e:
            return False, f"Failed to connect to the database: {e}"

if __name__ == "__main__":
    # Test block: Run this file directly to verify the connection
    print("--- Database Connection Test ---")
    db = DatabaseManager()
    
    # Test singleton behavior
    db2 = DatabaseManager()
    if db is db2:
        print("Singleton check: PASSED (Both instances are the same object)")
    else:
        print("Singleton check: FAILED")

    # Test actual connection
    success, message = db.test_connection()
    if success:
        print(f"Connection check: PASSED - {message}")
    else:
        print(f"Connection check: FAILED - {message}")