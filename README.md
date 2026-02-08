Slide 1: Project Title & Mission
Title: DhanVichar: An Agentic Framework for Multi-Modal Financial Analysis.
Mission: Empowering Indian retail investors by bridging the gap between raw market data and qualitative corporate insights using autonomous AI agents.

Slide 2: The Problem Statement (The "Why")
Information Fragmentation: Retail users must visit 4-5 different platforms (NSE for price, Moneycontrol for news, YouTube for IR calls, AMFI for NAVs) to make one decision.
The "Credibility Gap": Corporate management often paints an optimistic picture in transcripts/videos that doesn't align with financial health or market performance.
Analysis Paralysis: High-frequency data (price) changes every second, while high-value data (transcripts/PDFs) is buried in 50-page documents. Retail users cannot synthesize both.

Slide 3: Proposed Solution (The "What")
A Unified Agentic Advisor: A system that doesn't just "search" but "reasons" across multiple data types (Numerical, Textual, and Audio).
Triangulation Engine: The app uses a multi-agent workflow to cross-verify "What management says" (Transcripts) with "What the data shows" (P&L/Price) to give an unbiased recommendation.

Slide 4: Initial Feature Set
Automated Asset Classification: Master agent identifies if the user wants to discuss a Stock or a Mutual Fund.
Stock "Deep-Dive": Automated retrieval of CMP, Volume, PE Ratio, and Balance Sheet health.
MF "Lumpsum vs. SIP" Advisor: Historical NAV analysis to determine if the fund is currently at a "Value Zone."
Management Sentiment Audit: Automatic transcription of the latest earnings call and comparison against the last 3 months' stock returns.

Slide 5: Data Sources & Input/Output Model
User Inputs: Simple text input (e.g., "Reliance Industries" or "HDFC Mid-Cap Opportunities Fund").
Data Sources:
Equity: Yahoo Finance API & nsepython (Real-time & Historical).
Mutual Funds: AMFI (Association of Mutual Funds in India) Open Data.
Qualitative: YouTube (Investor Relations channels) & BSE India (PDF Transcripts).
Expected Output:
Investment Verdict: (Invest / Wait / Avoid).
Analysis Proof: A table of core financials + A summary of management sentiment.
Mismatch Alert: A warning if management sentiment is high but financials are declining.

Slide 6: High-Level Technical Architecture
UI Layer: Streamlit (For a reactive, dashboard-style interface).
API Layer: FastAPI (To handle asynchronous requests between the UI and the AI).
Orchestration Layer (The Brain): LangGraph.
Why LangGraph? It allows for "Cyclical Reasoning"—if an agent finds a financial red flag, it can loop back to the transcript agent to look for an explanation.
Intelligence Layer: Hybrid LLM (OpenAI for logic; Gemini for long-context PDF/Video text analysis).

Slide 7: Implementation & Installation Plan
Environment: Python 3.10+ in a Virtual Environment.
Installation for Initial Users (Developer/Beta):
Clone Repository: git clone https://github.com/rajchoudhury09/DhanVichar.git
Install Dependencies: pip install -r requirements.txt (including langgraph, fastapi, yfinance, mftool, whisper).
Environment Setup: Create a .env file with API keys for OpenAI/Gemini.
Run Application: Launch via streamlit run app.py.

Slide 8: Roadmap & Expected Milestones
Phase 1: Core Agent development (Routing and Stock data retrieval).
Phase 2: Multi-modal integration (PDF and Video transcription).
Phase 3: Decision Logic refinement (The "Investment Verdict" algorithm).
Phase 4: Beta release to a closed group for feedback.

Slide 9: Existing App list which are similar