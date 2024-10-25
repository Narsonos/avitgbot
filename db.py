import sqlite3
from config import db_file


def init_db():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link TEXT NOT NULL,
                latest_offer_id INTEGER,
                latest_offer_link TEXT,
                latest_offer_date TIMESTAMP,
                name TEXT NOT NULL
            )
        ''')
        conn.commit()


if __name__ == "__main__":
	import re 
	r = re.match(r'^\d+ (недел|дн|час|минут)','3 часа')
	print(r)