from sqlalchemy import create_engine, Engine, Table


#creating an engine
def connect_to_database(db_url: str) -> Engine:
    engine = create_engine(db_url)
    return engine
#closing the engine
def close_db_connection(engine: Engine):
    engine.dispose()
    return 200


#basic crud operations on the database
def add_to_db(engine: Engine, table: Table, data) -> int:
    with engine.connect() as connection: 
        try:
            connection.execute(table.insert(), data)
            connection.commit()
            return 200 #success
        except Exception as e:
            print(f"Error adding to database: {e}")
            return 500 #error
def fetch_from_db(engine, table, query):
    with engine.connect() as connection:
        try:
            result = connection.execute(query.select().where(table.c.id == query))
            return result.fetchall()
        except Exception as e:
            print(f"Error fetching from database: {e}")
            return 500 #error
def update_db(engine, table, query, data):
    with engine.connect() as connection:
        try:
            connection.execute(query.update().where(table.c.id == query), data)
            connection.commit()
            return 200 #success
        except Exception as e:
            print(f"Error updating database: {e}")
            return 500 #error
def delete_from_db(engine, table, query):
    with engine.connect() as connection:
        try:
            connection.execute(query.delete().where(table.c.id == query))
            connection.commit()
            return 200 #success
        except Exception as e:
            print(f"Error deleting from database: {e}")
            return 500 #error

#Function to execute raw sql queries
def execute_raw_query(engine, raw_query):
    with engine.connect() as connection:
        try:
            result = connection.execute(raw_query)
            return result.fetchall()
        except Exception as e:
            print(f"Error executing raw query: {e}")
            return 500 #error
