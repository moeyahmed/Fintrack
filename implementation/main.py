from flask import Flask, redirect, request, url_for, session
from pyhtml import h1, html, body, form, input_, div, br, head,h2,h3, p,td,th,tr, table,link, a, img, ul, li, hr
import json
from pyhtml import *
import feedparser
import yfinance as yahooFinance
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = "super secret key"

data = {'users': []}

stocks = {}
crypto = {}
stock_table_rows = []
crypto_table_rows = []
# Store user credentials in a JSON file
user_credentials = {}


search = ''

watch_list = []

 
def loaddata():
    global user_credentials
    with open('users.json', 'r') as f:
        user_credentials = json.load(f)


@app.route('/')
def homepage():
    """
    The landing page for your project. This is the first thing your users will
    see, so you should be careful to design it to be useful to new users.
    """
    response = html(
        head(
            link(rel='stylesheet', href='/static/style.css')
        ),
        body(
            h1("FinTrack"),
            div(style="text-align: center")(
                form(action='/login', method='POST')(
                    input_(type='text', name='username', placeholder='Enter your username'),
                    input_(type='password', name='password', placeholder='Enter your password'),
                    input_(type='submit', value='Login')
                )
            ),
            form(action='/signup', method='GET')(
                input_(type='submit', value='Signup')
            )
        )
    )

    return str(response)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error_message = ""

    if request.method == 'POST':
        # Get user input from the form
        first_name = request.form['first_name']
        surname = request.form['surname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        dob = request.form['dob']

        # Check if the username already exists
        if username in user_credentials:
            error_message = "This username already exists. Please choose a different username."
        else:
            # Update the user credentials with the new user
            user_credentials[username] = {
                'username': username,
                'first_name': first_name,
                'surname': surname,
                'email': email,
                'password': password,
                'dob': dob
            }

            # Write the updated user credentials to the JSON file
            with open('users.json', 'w') as f:
                json.dump(user_credentials, f)

            # Redirect to the login page
            return redirect(url_for('homepage'))

    response = html(
        head(
            link(rel='stylesheet', href='/static/style.css')
        ),
        body(
            h1("FinTrack Signup"),
            div(style="text-align: center")(
                form(action='/signup', method='POST')(
                    input_(type='text', name='first_name', placeholder='Enter First Name'),
                    input_(type='text', name='surname', placeholder='Enter surname'),
                    input_(type='email', name='email', placeholder='Enter your email'),
                    input_(type='text', name='username', placeholder='Enter your username'),
                    input_(type='password', name='password', placeholder='Enter your password'),
                    input_(type='date', name='dob', placeholder='Enter your date of birth'),
                    input_(type='submit', value='Signup'),
                    p(style='color: red')(error_message)  # Display error message if there is one
                )
            ),

        )
    )

    return str(response)


@app.route('/login', methods=['POST'])
def login():
    # Get user input from the form
    username = request.form['username']
    password = request.form['password']
    print(username, password)

    for user in user_credentials.values():
        print(user)
        if user['username'] == username and user['password'] == password:
            # Redirect to the dashboard page if the login was successful
            return redirect(url_for('dashboard'))

    # Return an error message as JSON if the login was unsuccessful
    return json.dumps({'success': False, 'message': 'Invalid username or password.'})



@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """
    A dashboard page that displays stocks, crypto, and account balances.
    """
    global total_balance

    # Handle POST request to add a stock
    if request.method == 'POST' and request.form['submit'] == 'Add Stock':
        stock_symbol = request.form['stock_symbol']
        purchase_price = float(request.form['purchase_price'])
        purchase_amount = int(request.form['purchase_amount'])

        stock_exists = False

        # Check if the stock already exists in the table
        for row in stock_table_rows:
            if row[0] == stock_symbol:
                average_purchase_price = (row[1] * row[2] + purchase_price * purchase_amount) / (
                        row[2] + purchase_amount)
                row[1] = round(average_purchase_price, 2)
                row[2] += purchase_amount
                stock_exists = True
                break

        # If the stock doesn't exist, add it to the table
        if not stock_exists:
            stock_table_rows.append([stock_symbol, purchase_price, purchase_amount])




    # Handle POST request to add a crypto
    elif request.method == 'POST' and request.form['submit'] == 'Add Crypto':
        crypto_symbol = request.form['crypto_symbol']
        purchase_price = float(request.form['purchase_price'])
        purchase_amount = int(request.form['purchase_amount'])
        crypto_exists = False

        # Check if the crypto already exists in the table
        for row in crypto_table_rows:
            if row[0] == crypto_symbol:
                average_purchase_price = (row[1] * row[2] + purchase_price * purchase_amount) / (
                        row[2] + purchase_amount)
                row[1] = round(average_purchase_price, 2)
                row[2] += purchase_amount
                crypto_exists = True
                break

        # If the crypto doesn't exist, add it to the table
        if not crypto_exists:
            crypto_table_rows.append([crypto_symbol, purchase_price, purchase_amount])


    # Build the response HTML
    response = html(
        head(
            link(rel='stylesheet', href='static/styles1.css')
        ),
        body(
            div(id='menu-bar')(
                a(href='/dashboard', class_='menu-item')('My dashboard'),
                a(href='/charts', class_='menu-item')('Charts'),
                a(href='/watchlist', class_='menu-item')('Watchlist'),
                a(href='/news', class_='menu-item')('News'),
                a(href='resources', class_='menu-item')('Tutorial and Resourses')
            ),
            h1("FinTrack Dashboard"),
            div(
                h2("My Dashboard"),

                form(action='/dashboard/stocks', method='POST')(
                    h2("Add a Stock"),
                    input_(type='text', name='stock_symbol', placeholder='Enter a stock symbol'),
                    br(),
                    input_(type='text', name='purchase_price', placeholder='Enter purchase price'),
                    br(),
                    input_(type='text', name='purchase_amount', placeholder='Enter purchase amount'),
                    br(),
                    input_(type='submit', value='Add Stock'),
                ),
                form(action='/dashboard/crypto', method='POST')(
                    h2("Add Crypto"),
                    input_(type='text', name='crypto_symbol', placeholder='Enter a crypto symbol'),
                    br(),
                    input_(type='text', name='purchase_price', placeholder='Enter purchase price'),
                    br(),
                    input_(type='text', name='purchase_amount', placeholder='Enter purchase amount'),
                    br(),
                    input_(type='submit', value='Add Crypto'),
                ),
                div(id='stock-table')(
                    h2("My Investments"),
                    table(
                        tr(
                            th("Symbol"),
                            th("Average Purchase Price"),
                            th("Purchase Amount"),
                            th("Total Value"),
                        ),
                        *[tr(
                            td(symbol),
                            td("{:.2f}".format(purchase_price)),
                            td(purchase_amount),
                            td("{:.2f}".format(purchase_price * purchase_amount)),
                        ) for symbol, (purchase_price, purchase_amount) in stocks.items()],
                        *[tr(
                            td(symbol),
                            td("{:.2f}".format(purchase_price)),
                            td(purchase_amount),
                            td("{:.2f}".format(purchase_price * purchase_amount)),
                        ) for symbol, (purchase_price, purchase_amount) in crypto.items()],
                    ),
                ),
            ),
        )
    )

    return str(response)

@app.route('/dashboard/stocks', methods=['POST'])
def add_stock():
    stock_symbol = request.form['stock_symbol']
    purchase_price = float(request.form['purchase_price'])
    purchase_amount = float(request.form['purchase_amount'])

    if stock_symbol in stocks:
        # Update average purchase price and purchase amount
        current_purchase_price, current_purchase_amount = stocks[stock_symbol]
        average_purchase_price = (
            current_purchase_price * current_purchase_amount + purchase_price * purchase_amount) / (
            current_purchase_amount + purchase_amount)
        stocks[stock_symbol] = (average_purchase_price, current_purchase_amount + purchase_amount)
    else:
        stocks[stock_symbol] = (purchase_price, purchase_amount)
    return redirect('/dashboard')

@app.route('/dashboard/crypto', methods=['POST'])
def add_crypto():
    crypto_symbol = request.form['crypto_symbol']
    purchase_price = float(request.form['purchase_price'])
    purchase_amount = float(request.form['purchase_amount'])


    if crypto_symbol in crypto:
        # Update average purchase price and purchase amount
        current_purchase_price, current_purchase_amount = crypto[crypto_symbol]
        average_purchase_price = (
            current_purchase_price * current_purchase_amount + purchase_price * purchase_amount) / (
            current_purchase_amount + purchase_amount)
        crypto[crypto_symbol] = (average_purchase_price, current_purchase_amount + purchase_amount)
    else:
        crypto[crypto_symbol] = (purchase_price, purchase_amount)
    return redirect('/dashboard')



@app.route('/news', methods=['GET', 'POST'])
def yahoofinancenews():

    tickers = ['^GSPC', 'AAPL', 'GOOG', 'MSFT', 'AMZN', 'FB', 'JPM', 'TSLA','BTC-USD', 'ETH-USD']

    # Get news for the S&P 500 index
    sp500_feedurl = 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC&region=US&lang=en-US'
    sp500_news = feedparser.parse(sp500_feedurl)

    # Get news for the individual companies
    company_news = []
    for ticker in tickers:
        rssfeedurl = f'https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US'
        NewsFeed = feedparser.parse(rssfeedurl)
        company_news.append((ticker, NewsFeed.entries[:5]))  # Save only the first 5 entries

    # Build the response HTML
    response = html(
        head(
            link(rel='stylesheet', href='static/styles1.css')
        ),
        body(
            div(id='menu-bar')(
                a(href='/dashboard', class_='menu-item')('My dashboard'),
                a(href='/charts', class_='menu-item')('Charts'),
                a(href='/watchlist', class_='menu-item')('Watchlist'),
                a(href='/news', class_='menu-item')('News'),
                a(href='resources', class_='menu-item')('Tutorial and Resourses')
            ),
            h1("FinTrack News"),
            div(
                div(id='sp500-table')(
                    h2("S&P 500 News"),
                    *[div(
                        h3(i['title']),
                        p(i['summary']),
                        p(i['published']),
                        hr()  # Add a horizontal line between each news item
                    ) for i in sp500_news.entries[:5]]
                ),
                *[
                    div(id=f'{ticker}-table')(
                        h2(f"{ticker} News"),
                        *[div(
                            h3(i['title']),
                            p(i['summary']),
                            p(i['published']),
                            hr()  # Add a horizontal line between each news item
                        ) for i in entries]
                    ) for ticker, entries in company_news
                ]
            )
        )
    )

    return str(response)


import requests
import matplotlib
matplotlib.use('agg')
from io import BytesIO


api_key = 'C2EOAFSOUTDFUKUH'
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={{symbol}}&apikey={api_key}'


def get_chart_data(symbol):
    response = requests.get(url.format(symbol=symbol))
    data = response.json()
    
    if 'Time Series (Daily)' not in data:
        print(f"No daily data found for symbol {symbol}")
        return pd.DataFrame()

    df = pd.DataFrame(data['Time Series (Daily)']).T  
    df.index = pd.to_datetime(df.index)  
    last_week = datetime.now() - timedelta(days=7)
    df = df[df.index >= last_week.strftime("%Y-%m-%d")]  
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, df['4. close'])
    ax.set(xlabel='Date', ylabel='Price', title=symbol)
    ax.grid()
    ax.invert_yaxis()
    buffer = BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer.getvalue()




@app.route('/charts', methods=['GET', 'POST'])
def charts():

    # Initialize charts list in session
    if 'charts' not in session:
        session['charts'] = []

    # Handle POST requests to add a new chart
    if request.method == 'POST':
        symbol = request.form.get('search')
        try:
            # Check if the symbol is valid
            GetInformation = yahooFinance.Ticker(symbol)
            info = GetInformation.info
            session['charts'].append(symbol)
        except:
            session['message'] = "Stock or crypto does not exist."

    # Handle GET requests to delete a chart
    if request.method == 'GET' and 'delete' in request.args:
        delete_index = int(request.args.get('delete'))
        if delete_index < len(session['charts']):
            del session['charts'][delete_index]

    # Build the chart table
    rows = []
    for index, symbol in enumerate(session['charts']):
        chart_data = get_chart_data(symbol)
        chart_src = f"data:image/png;base64,{base64.b64encode(chart_data).decode('utf-8')}"
        rows.append(tr(
            td(symbol),
            td(img(src=chart_src)),
            td(form(
                action='/charts',
                method='GET',
                style='margin:0',
            )(
                input_(type='hidden', name='delete', value=index),
                input_(type='submit', value='X', class_='delete-btn'),
            ))
        ))

    # Build the response HTML
    response = html(
        head(
            link(rel='stylesheet', href='static/styles1.css')
        ),
        body(
            div(id='menu-bar')(
                a(href='/dashboard', class_='menu-item')('My dashboard'),
                a(href='/charts', class_='menu-item')('Charts'),
                a(href='/watchlist', class_='menu-item')('Watchlist'),
                a(href='/news', class_='menu-item')('News'),
                a(href='resources', class_='menu-item')('Tutorial and Resourses')
            ),
            h1("FinTrack Charts"),
            div(
                form(action='/charts', method='POST')(
                    h2("Add Chart"),
                    input_(type='text', name='search', placeholder='Enter Symbol'),
                    br(),
                    input_(type='submit', value='Search'),
                ),
                div(id='chart-table')(
                    h2("My Charts"),
                    table(
                        tr(
                            th("Symbol"),
                            th("Chart"),
                            th("Delete"),
                        ),
                        *rows,
                    ),
                ),
            ),
            div(id='message')(session.pop('message', "")),
        )
    )

    return str(response)




@app.route('/watchlist', methods=['GET', 'POST'])
def Watch():

    if request.method == 'POST':
        search = request.form.get('search')
        print(search)

        try:
            GetInformation = yahooFinance.Ticker(search)
            info = GetInformation.info
            symbol = info['symbol']
            price = info['regularMarketDayHigh']
            watch_list.append([symbol, price])
        except:
            message = "Stock or crypto does not exist."

    elif request.method == 'GET' and 'delete' in request.args:
        delete_index = int(request.args.get('delete'))
        if delete_index < len(watch_list):
            del watch_list[delete_index]

    # Build the response HTML
    response = html(
        head(
            link(rel='stylesheet', href='static/styles1.css')
        ),
        body(
            div(id='menu-bar')(
                a(href='/dashboard', class_='menu-item')('My dashboard'),
                a(href='/charts', class_='menu-item')('Charts'),
                a(href='/watchlist', class_='menu-item')('Watchlist'),
                a(href='/news', class_='menu-item')('News'),
                a(href='resources', class_='menu-item')('Tutorial and Resourses')
            ),
            h1("FinTrack Watch-list"),
            div(
                form(action='/watchlist', method='POST')(
                    h2("Add an invesment"),
                    input_(type='text', name='search', placeholder='Enter Name'),
                    br(),
                    input_(type='submit', value='search'),
                ),
                div(id='stock-table')(
                    h2("My WatchList"),
                    table(
                        tr(
                            th("Symbol"),
                            th("Price"),
                            th("Delete"),
                        ),
                        *[tr(
                            td(i[0]),
                            td(i[1]),
                            td(
                                form(
                                    action='/watchlist',
                                    method='GET',
                                    style='margin:0',
                                )(
                                    input_(type='hidden', name='delete', value=index),
                                    input_(type='submit', value='X', class_='delete-btn'),
                                )
                            )
                        ) for index, i in enumerate(watch_list)],
                    ),
                ),
            ),
            div(id='message')(message) if 'message' in locals() else ""
        )
    )

    return str(response)

@app.route('/resources', methods=['GET', 'POST'])
def resource():
     
     response = html(
        head(
            link(rel='stylesheet', href='static/styles1.css')
        ),
        body(
            div(id='menu-bar')(
                a(href='/dashboard', class_='menu-item')('My dashboard'),
                a(href='/charts', class_='menu-item')('Charts'),
                a(href='/watchlist', class_='menu-item')('Watchlist'),
                a(href='/news', class_='menu-item')('News'),
                a(href='resources', class_='menu-item')('Tutorial and Resources')
            ),
            div(id='safest-places')(
                h1('Safest Places to Buy Crypto and Stocks'),
                p('Check out these safe and reliable platforms to buy and trade cryptocurrencies and stocks!'),
                ul(
                    li('Crypto: Coinbase - Coinbase is one of the most trusted and popular cryptocurrency exchanges in the world, providing a secure and user-friendly platform for buying, selling, and storing cryptocurrencies.'),
                    li('Stocks: Webull - webull is a well-established and reputable brokerage firm that provides a wide range of investment options and services, including commission-free trading, research tools, and educational resources.'),
                )
            ),
            div(id='educational-resources')(
                h1('Educational Resources'),
                p('Expand your knowledge with these educational resources!'),
                ul(
                    li(a(href='https://www.investopedia.com/')('Investopedia')),
                    li(a(href='https://www.bloomberg.com/')('Bloomberg')),
                    li(a(href='https://www.cnbc.com/')('CNBC')),
                )
            ),
            div(id='articles')(
                h1('Helpful Finance Articles'),
                p('Read these informative articles to expand your knowledge about finance and investing!'),
                ul(
                    li(a(href='https://www.investopedia.com/')('What Is Investing and How Do You Start?')),
                    li(a(href='https://www.bloomberg.com/')('Warren Buffett on the Stock Market: Oracle of Omaha Talks Investing During a Crisis')),
                    li(a(href='https://www.cnbc.com/')('10 best personal finance books of all time')),
                )
            ),
            div(id='youtube-videos')(
                h1('YouTube Videos'),
                p('Watch these videos to learn more about investing safely and smartly!'),
                ul(
                    li(a(href='https://www.youtube.com/watch?v=gFQNPmLKj1k')('How to Invest in Stocks for Beginners (2021)')),
                    li(a(href='https://www.youtube.com/watch?v=vffTJV0IzHM')('How to Buy Cryptocurrency for Beginners (UPDATED Ultimate Guide)')),
                    li(a(href='https://www.youtube.com/watch?v=TMpULJwCLZk')('5 Tips for Investing in Cryptocurrency Safely (2021)')),
                )
            )
        ),
    )
     return str(response)

# Start our app
if __name__ == "__main__":
    loaddata()
    app.run(debug=True, port=5003)
