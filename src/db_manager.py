from sqlalchemy import create_engine, text
import pandas as pd
from datetime import date

class TGVMaxDB:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.init_table()

    def init_table(self):
        """Create the table if it does not exists
        """
        with self.engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS tgvmax (
                    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    origin TEXT,
                    destination TEXT,
                    date DATE,
                    hour TIME,
                    found BOOLEAN
                );
            """))

    def load_trains_to_search(self):
        today = date.today()
        query = """
            SELECT * FROM tgvmax
            WHERE found IS NULL OR date >= %(today)s;
        """
        df = pd.read_sql(query, self.engine, params={"today": today})
        return df

    def add_train(self, origin, destination, date, hour, found=None):
        with self.engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO tgvmax (origin, destination, date, hour, found)
                VALUES (:origin, :destination, :date, :hour, :found);
            """), {
                "origin": origin,
                "destination": destination,
                "date": date,
                "hour": hour,
                "found": found
            })

    def update_cell(self, df, row_index, column_name):
        row_id = df.iloc[row_index]["id"]
        new_value = df.iloc[row_index][column_name]
        with self.engine.begin() as conn:
            conn.execute(text(f"""
                UPDATE tgvmax SET {column_name} = :new_value WHERE id = :row_id;
            """), {
                "new_value": new_value,
                "row_id": int(row_id)
            })
