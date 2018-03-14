#!usr/bin/env python3

from flask import Flask, render_template, request, url_for, redirect
import model


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        log = model.users()
        username = request.form['username']
        password = request.form['password']
        if username == log[0]:
            if password == log[1]:
                balance = model.check_balance()
                return render_template('homepage.html', balance=balance)
        else:
            return render_template('login.html', message='Error: Bad Credentials')

@app.route('/welcome/', methods=['GET'])
def welcome():
    if request.method == 'GET':
        return render_template('welcome.html')

@app.route('/home/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        balance = model.check_balance()
        x = ' '
        return render_template('homepage.html', x=x, balance=balance)

@app.route('/buy/', methods=['GET', 'POST'])
def buy():
    balance = model.check_balance()
    if request.method == 'GET':
        return render_template('buy_menu.html', balance=balance)
    else:
        ticker_symbol = (request.form['ticker_symbol']).upper()
        trade_volume = request.form['trade_volume']
        x = model.buy(ticker_symbol, trade_volume)
        return render_template('homepage.html', x=x, balance=balance)

@app.route('/sell/', methods=['GET', 'POST'])
def sell():
    balance = model.check_balance()
    if request.method == 'GET':
        return render_template('sell_menu.html', balance=balance)
    else:
        ticker_symbol = (request.form['ticker_symbol']).upper()
        trade_volume = request.form['trade_volume']
        x = model.sell(ticker_symbol, trade_volume)
        return render_template('homepage.html', x=x, balance=balance)

@app.route('/lookup/', methods=['GET', 'POST'])
def lookup():
    balance = model.check_balance()
    if request.method == 'GET':
        return render_template('lookup.html', balance=balance)
    else:
        company_name = request.form['company_name']
        x = model.lookup(company_name)
        return render_template('homepage.html', x=x, balance=balance)

@app.route('/quote/', methods=['GET', 'POST'])
def quote():
    balance = model.check_balance()
    if request.method == 'GET':
        return render_template('quote_menu.html', balance=balance)
    else:
        ticker_symbol = (request.form['ticker_symbol']).upper()
        x = model.quote(ticker_symbol)
        return render_template('homepage.html', x=x, balance=balance)

@app.route('/portfolio/', methods=['GET', 'POST'])
def portfolio():
    balance = model.check_balance()
    x = model.view_portfolio()
    name = []
    num_shares = []
    shares_value = []
    position_list = []
    shares=0
    for row in x:
        shares += row[2]
    for row in x:
        num_shares.append(row[2])
    for row in x:
        b = model.portfolio_value(row[1], row[2])
        name.append(b[0])
        shares_value.append(b[1])
    net_bal = round((balance-25000), 2)
    for num in range(0, len(name)):
        position_list.append((name[num], num_shares[num], shares_value[num]))
    if request.method == 'GET':
        return render_template('portfolio.html', balance=balance, net_bal=net_bal, shares=shares, position_list=position_list)
    #else:
        #return render_template('continue.html', continue_text = 'Greg')

@app.route('/graph/', methods=['GET', 'POST'])
def graph():
    balance = model.check_balance()
    if request.method == 'GET':
        return render_template('graph_shit.html', balance=balance)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
