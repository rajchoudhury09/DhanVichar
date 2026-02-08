import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
session.verify = False  # Disable SSL verification
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# Visit page first for cookies
session.get('https://www.nseindia.com/get-quotes/equity?symbol=HAL', verify=False)

# Get quote
response = session.get('https://www.nseindia.com/api/quote-equity?symbol=HAL', verify=False)
print(response.json())



session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Quick 3-step process
session.get('https://www.nseindia.com/')
session.get('https://www.nseindia.com/get-quotes/equity?symbol=HAL')
data = session.get('https://www.nseindia.com/api/quote-equity?symbol=HAL').json()

print(f"HAL: ₹{data['priceInfo']['lastPrice']}")