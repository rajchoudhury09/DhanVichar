import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import urllib3
import io

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def read_transcript_pdf_robust(pdf_url):
    """Read ANY PDF transcript - handles EOF errors + multiple formats"""
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        # Download PDF
        resp = requests.get(pdf_url, headers=headers, verify=False, stream=True)
        pdf_content = resp.content
        
        # METHOD 1: pdfplumber (most robust)
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                if text.strip():
                    return text.strip()
        except ImportError:
            pass
        
        # METHOD 2: PyMuPDF (Fitz) - handles malformed PDFs
        try:
            import fitz  # pip install PyMuPDF
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            if text.strip():
                return text.strip()
        except ImportError:
            pass
        
        # METHOD 3: FIXED PyPDF2 with strict=False + EOF repair
        try:
            from PyPDF2 import PdfReader
            # Repair EOF marker
            if b'%%EOF' not in pdf_content:
                pdf_content = pdf_content + b'\n%%EOF\n'
            
            reader = PdfReader(io.BytesIO(pdf_content), strict=False)
            text = ""
            for page in reader.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except:
                    continue
            if text.strip():
                return text.strip()
        except ImportError:
            pass
        
        # METHOD 4: pdftotext fallback
        try:
            import pdftotext
            pdf_file = io.BytesIO(pdf_content)
            text = "\n\n".join(pdftotext.get_pages(pdf_file))
            return text.strip()
        except ImportError:
            pass
            
    except Exception as e:
        return f"PDF Error: {str(e)[:100]}"
    
    return "No text extracted"

def find_transcript_pdf(company, quarter="Q4 2025"):
    """Find PDF URL (simplified from previous)"""
    
    # Direct known patterns for top companies
    company_patterns = {
        'HDFC': [
            'https://www.hdfc.bank.in/content/dam/hdfcbankpws/in/en/pdf/financial-results/2024-2025/quarter-4/earnings-call-transcript-q4fy25.pdf',
            'https://www.hdfcbank.com/content/bbp/repositories/723fb80a-2dde-42a3-9793-7ae1be57c87f/?path=/Footer/About Us/About+Investors'
        ],
        'ICICI': ['https://www.icicibank.com/content/icicibank/investor-services/earnings-calls.html'],
        'SBI': ['https://sbi.co.in/web/investor-relations']
    }
    
    if company.upper() in company_patterns:
        for url in company_patterns[company.upper()]:
            try:
                resp = requests.head(url, verify=False)
                if resp.status_code == 200:
                    return pd.DataFrame([{
                        'company': company,
                        'quarter': quarter,
                        'url': url,
                        'title': f"{company} {quarter} Transcript"
                    }])
            except:
                continue
    
    return pd.DataFrame()

# USAGE
company = "HDFC"
quarter = "Q4 2025"

# 1. Find PDF
df = find_transcript_pdf(company, quarter)
if not df.empty:
    pdf_url = df.iloc[0]['url']
    print(f"📄 Found: {pdf_url}")
    
    # 2. Extract text (EOF-proof)
    transcript = read_transcript_pdf_robust(pdf_url)
    print(f"\n📝 Transcript ({len(transcript)} chars):")
    print(transcript[:1500] + "..." if len(transcript) > 1500 else transcript)
else:
    print(f"❌ No PDF found for {company}")