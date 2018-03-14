#!/usr/bin/env python3b

import json
import sqlite3
import time
import requests


def users():
    log = []
    connection = sqlite3.connect('master.db', check_same_thread = False)
    cursor     = connection.cursor()
    cursor.execute("""SELECT username FROM users;""")
    username = cursor.fetchone()[0]
    log.append(username)
    cursor.execute("""SELECT password FROM users;""")
    password = cursor.fetchone()[0]
    log.append(password)
    return log

def buy(ticker_symbol, trade_volume):
    try:
        deep_link = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json?symbol={ticker_symbol}'.format(ticker_symbol=ticker_symbol)
        response = json.loads(requests.get(deep_link).text)
        last_price = response['LastPrice']
        balance = check_balance()
        friction = 8.00
        transaction_cost = (int(trade_volume) * float(last_price)) + friction

        if transaction_cost > balance:
            return 'You do not have enough money in your Balance'

        else:
            store_transaction(time.time(), 0, float(last_price), int(trade_volume))
            position_exist = lookup_position(ticker_symbol)
            if position_exist is None:
                store_position(ticker_symbol, trade_volume)
            else:
                update_position(ticker_symbol, trade_volume)
            return ' Transaction complete!'
    except:
        return 'That company or quantity does not exist'
        # TODO Calculate VWAP


def sell(ts, trade_volume):
    try:
        deep_link = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json?symbol={ts}'.format(ts=ts)
        response = json.loads(requests.get(deep_link).text)
        last_price = response['LastPrice']

        connection = sqlite3.connect('master.db', check_same_thread = False)
        cursor     = connection.cursor()

        cursor.execute("""SELECT number_of_shares FROM positions WHERE ticker_symbol = '{ts}';""".format(ts=ts))
        number = cursor.fetchone()

        balance = check_balance()
        if number is None:
            print(" You don't have enough shares!")

        else:
            if number[0] >= int(trade_volume):
                friction = 8.00
                if friction > balance:
                    return 'you a bum'

                else:
                    subtract_position(ts, trade_volume)
                    store_transaction(time.time(), 1, float(last_price), int(trade_volume))
                    return "Transaction complete"
            else:
                print(" You don't have enough shares")
    except:
        return 'That company or quantity does not exist'


def lookup(company_name):
    try:
        deep_link = 'http://dev.markitondemand.com/MODApis/Api/v2/Lookup/json?input={company_name}'.format(company_name=company_name)
        response = json.loads(requests.get(deep_link).text)
        ticker_symbol = response[0]['Symbol']
        return ticker_symbol
    except:
        return 'This company name does not exist'

def quote(ticker_symbol):
    try:
        deep_link = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json?symbol={ticker_symbol}'.format(ticker_symbol=ticker_symbol)
        response = json.loads(requests.get(deep_link).text)
        last_price = response['LastPrice']
        return last_price
    except:
        return 'That symbol does not exist'

def check_balance():
    connection = sqlite3.connect('master.db', check_same_thread = False)
    cursor     = connection.cursor()
    cursor.execute("""SELECT SUM(last_price * trade_volume) FROM transactions WHERE transaction_type = 1;""")
    gain = cursor.fetchone()
    cursor.execute("""SELECT SUM(last_price * trade_volume) FROM transactions WHERE transaction_type = 0;""")
    loss = cursor.fetchone()
    cursor.execute("""SELECT COUNT(*) FROM transactions;""")
    friction = cursor.fetchone()
    balance = 25000 + gain[0] - loss[0] - (8 * (friction[0]-2))
    return round(balance, 2)

def lookup_position(ticker):
    ts = str(ticker.upper())
    connection = sqlite3.connect('master.db', check_same_thread = False)
    cursor     = connection.cursor()
    cursor.execute("SELECT ticker_symbol FROM positions WHERE ticker_symbol= '{ts}';".format(ts=ts))
    position_exists = cursor.fetchone()
    return position_exists

def view_portfolio():
    connection = sqlite3.connect('master.db', check_same_thread = False)
    cursor     = connection.cursor()
    cursor.execute("""SELECT * FROM positions WHERE number_of_shares > 0;""")
    portfolio = cursor.fetchall()
    return portfolio

def portfolio_value(a, b):
    try:
        deep_link = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json?symbol={a}'.format(a=a)
        response = json.loads(requests.get(deep_link).text)
        last_price = response['LastPrice']
        b = int(b)
        return a, round(b*last_price, 2)
    except:
        return 'Connection error'

def store_position(ticker_symbol, number_of_shares):
    connection = sqlite3.connect('master.db', check_same_thread = False)
    cursor     = connection.cursor()
    cursor.execute("""INSERT INTO positions(
        ticker_symbol,
        number_of_shares
    ) VALUES(
        '{ticker_symbol}',
        {number_of_shares}
    );""".format(
        ticker_symbol=ticker_symbol,
        number_of_shares=number_of_shares
    )
    )
    connection.commit()
    cursor.close()
    connection.close()

def update_position(ts, trade_volume):
    connection = sqlite3.connect('master.db', check_same_thread = False)
    cursor     = connection.cursor()
    cursor.execute("""SELECT number_of_shares FROM positions WHERE ticker_symbol = '{ts}';""".format(ts=ts))
    number = cursor.fetchone()
    new_shares = number[0] + int(trade_volume)
    cursor.execute("""UPDATE positions SET number_of_shares = {new_shares} WHERE ticker_symbol = '{ts}';""".format(new_shares = new_shares, ts = ts))
    connection.commit()
    cursor.close()
    connection.close()

def subtract_position(ts, trade_volume):
    connection = sqlite3.connect('master.db', check_same_thread = False)
    cursor     = connection.cursor()
    cursor.execute("""SELECT number_of_shares FROM positions WHERE ticker_symbol = '{ts}';""".format(ts=ts))
    number = cursor.fetchone()
    new_shares = number[0] - int(trade_volume)
    cursor.execute("""UPDATE positions SET number_of_shares = {new_shares} WHERE ticker_symbol = '{ts}';""".format(new_shares = new_shares, ts = ts))
    connection.commit()
    cursor.close()
    connection.close()

def store_transaction(time, type, price, volume):
    connection = sqlite3.connect('master.db', check_same_thread = False)
    cursor     = connection.cursor()
    cursor.execute("""INSERT INTO transactions(
        unix_time,
        transaction_type,
        last_price,
        trade_volume
    ) VALUES(
        {unix_time},
        {transaction_type},
        {last_price},
        {trade_volume}
    );""".format(
        unix_time=time,
        transaction_type=type,
        last_price=price,
        trade_volume=volume)
    )

    connection.commit()
    cursor.close()
    connection.close()

def vwap(old_price, old_quantity, new_price, new_quantity):
    a = (old_price * old_quantity) + (new_price * new_quantity)
    b = old_quantity + new_quantity
    vwap = a/b
    return vwap

def portfolio_earnings():
    pass

def net_earning():
    pass


if __name__ == '__main__':
    # kind of a testing area
    from pprint import pprint
    #pprint(buy('tsla', 4))
    pprint(users())
