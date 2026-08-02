import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import DATABASE_URL

engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

def add_column_if_not_exists(table_name, column_name, column_type):
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    if column_name not in columns:
        print(f"Adding column {column_name} to {table_name}...")
        with engine.connect() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
            conn.commit()
        print("Done.")
    else:
        print(f"Column {column_name} already exists in {table_name}.")

if __name__ == "__main__":
    print("Checking database schema...")
    # SQLite uses TEXT, PostgreSQL uses TEXT. Both are compatible.
    add_column_if_not_exists("transactions", "embedding", "TEXT")
    add_column_if_not_exists("budgets", "embedding", "TEXT")
    print("Schema update complete.")
