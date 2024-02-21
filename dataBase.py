"""sqlite3.ProgrammingError: SQLite objects created in a thread can only
be used in that same thread. The object was created in thread id
140647884693568 and this is thread id 140647075927744.

For flask I have to use flask `g` object which is Proxy created with werkzeug
LocalProxy class. `g` will handle multi threading support for sqlite3."""


import sqlite3

# from flask import g

from config import DATA_BASE_PATH


db = sqlite3.connect(DATA_BASE_PATH)
db.row_factory = sqlite3.Row


def init_users_table():
    cursor = db.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            phone_number TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        );
        '''
    )
    cursor.close()
    db.commit()


def init_notes_table():
    cursor = db.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT,
            created TEXT NOT NULL,
            author_username TEXT NOT NULL,
            author_id INTEGER NOT NULL
        );
        '''
    )
    cursor.close()
    db.commit()
