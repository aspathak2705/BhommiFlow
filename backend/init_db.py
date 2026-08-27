import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

def main():
    # Connect to the default 'postgres' database first to create the application database
    url = "postgresql://postgres:Aaksp%402705@localhost:5432/postgres"
    engine = create_engine(url)
    
    # Enable autocommit for database creation
    conn = engine.connect().execution_options(isolation_level="AUTOCOMMIT")
    
    try:
        conn.execute(text("CREATE DATABASE shikshaflow"))
        print("Database 'shikshaflow' created successfully.")
    except ProgrammingError as e:
        if "already exists" in str(e):
            print("Database 'shikshaflow' already exists.")
        else:
            print("Failed to create database:", e)
            sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
