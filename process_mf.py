###########Working code#####################333
import requests
import pandas as pd
import urllib3
from io import StringIO
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def verify_mf_data():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    nav_url = "https://www.amfiindia.com/spages/NAVAll.txt"
    response = session.get(nav_url)
    
    if response.status_code == 200:
        df = pd.read_csv(StringIO(response.text), sep='|', header=None, skiprows=1,
                        names=['Scheme_Code', 'ISIN_Div_Payout', 'ISIN_Div_Reinvestment', 
                               'Scheme_Name', 'Net_Asset_Value', 'Date'])
        
        # Clean whitespace and convert to string for matching
        df['Scheme_Code'] = df['Scheme_Code'].astype(str).str.strip()
        scheme_code_str = str(scheme_code).strip()
        
        print("Sample scheme codes:", df['Scheme_Code'].head().tolist())


# Get ALL scheme codes from AMFI
def get_all_scheme_codes():
    session = requests.Session()
    session.verify = False
    nav_url = "https://www.amfiindia.com/spages/NAVAll.txt"
    df = pd.read_csv(StringIO(session.get(nav_url).text), sep=';', header=None)
    #print(df.head())
    return df

df = get_all_scheme_codes()
print(df.head(6))

def get_mf_quote(scheme_code):
    """Get NAV using AMFI's current semicolon format"""
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    response = session.get("https://www.amfiindia.com/spages/NAVAll.txt")
    
    if response.status_code == 200:
        for line_num, line in enumerate(response.text.splitlines()[1:], 2):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Try both | and ; delimiters
            parts = None
            for delimiter in ['|', ';']:
                parts = [p.strip() for p in line.split(delimiter)]
                if len(parts) >= 6 and parts[0].isdigit():
                    break
            
            if parts and parts[0] == str(scheme_code):
                print(f"✅ Found at line {line_num} (delimiter: '{delimiter}')")
                return {
                    'scheme_name': parts[3],
                    'nav': float(parts[4]),
                    'date': parts[5],
                    'isin_payout': parts[1]
                }
        
        # Debug: Find ANY scheme to verify parsing
        print("Searching for first scheme...")
        for line in response.text.splitlines()[20:30]:
            line = line.strip()
            if line:
                parts = [p.strip() for p in line.split(';')]
                if len(parts) >= 6 and parts[0].isdigit():
                    print(f"First scheme: {parts[0]} - {parts[3][:40]}...")
                    break
    
    return None

# Test
scheme_code = '119551'
quote = get_mf_quote(scheme_code)
if quote:
    print(f"✅ Scheme: {quote['scheme_name']}")
    print(f"NAV: ₹{quote['nav']:.4f}")
    print(f"Date: {quote['date']}")
else:
    print("❌ Scheme 119551 not in current NAV data")

