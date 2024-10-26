import sqlite3
from config import db_file
from dataclasses import dataclass
import datetime

@dataclass
class Offer:
    id: int
    title: str
    link: str
    desc: str
    date: datetime.datetime | str
    price: int

@dataclass
class AvitoRequest:
    id: int
    link: str
    latest_offer_id: int
    latest_offer_link: str
    latest_offer_date: datetime.datetime
    name: str


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