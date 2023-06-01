import feedparser

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'
}

tickers = ['^GSPC', 'AAPL', 'GOOG', 'MSFT', 'AMZN', 'FB', 'JPM', 'TSLA','BTC-USD', 'ETH-USD']

# Get news for the S&P 500 index
sp500_feedurl = 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC&region=US&lang=en-US'
sp500_news = feedparser.parse(sp500_feedurl)

# Print news for the S&P 500 index
print("News for S&P 500:")
for i in sp500_news.entries:
  print(i)

# Get news for the individual companies
for ticker in tickers:
  rssfeedurl = f'https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US'
  NewsFeed = feedparser.parse(rssfeedurl)
  print(f"News for {ticker}:")
  for i in NewsFeed.entries:
    print(i)
