""" Creates connection with database for our wsgi application, handles table
    creating processes for our db.
"""
import sqlite3

from config import DATA_BASE_PATH


db = sqlite3.connect(DATA_BASE_PATH)
db.row_factory = sqlite3.Row


def init_users_table():
    """Creates users table inside db
    """
    cursor = db.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE CHECK(LENGTH(email) <= 36),
            phone_number TEXT UNIQUE CHECK(LENGTH(phone_number) <= 36),
            username TEXT NOT NULL CHECK(LENGTH(username) <= 16),
            password TEXT NOT NULL CHECK(LENGTH(password) <= 128)
        );
        '''
    )
    cursor.close()
    db.commit()


def init_notes_table():
    """Creates notes table inside db
    """
    cursor = db.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL CHECK(LENGTH(title) <= 150),
            body TEXT CHECK(LENGTH(body) <= 10000),
            created TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            deleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (author_id) REFERENCES users(id)
        );
        '''
    )
    cursor.close()
    db.commit()
