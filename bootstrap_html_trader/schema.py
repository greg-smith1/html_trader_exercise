#!usr/bin/env python3

import sqlite3


connection = sqlite3.connect('master.db', check_same_thread=False)
cursor     = connection.cursor()

cursor.execute(
    """CREATE TABLE users(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(16),
        password VARCHAR(32)
    );"""
)


cursor.execute(
    """CREATE TABLE positions(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker_symbol VARCHAR,
        number_of_shares INTEGER
    );"""
)


cursor.execute(
    """CREATE TABLE transactions(
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        unix_time FLOAT,
        transaction_type BOOL,
        last_price FLOAT,
        trade_volume INTEGER
    );"""
)



connection.commit()
cursor.close()
connection.close()
