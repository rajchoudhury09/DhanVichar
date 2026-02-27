Stock Analysis using AI agents -

Core Architecture
Multi-agent system: User queries trigger specialized agents (Data Fetcher, News Analyst, Predictor, Summarizer) that collaborate via a central orchestrator. 
Backend uses Flask/FastAPI; 
store data in SQLite/PostgreSQL; 
frontend via Streamlit or Flet for cross-platform UI.

Agents communicate in a chain: 
Data → Analysis → Prediction → Report. 
Use LangChain/AutoGen for agent logic, with tools for APIs.


Data Flow
User inputs stock symbol (e.g., RELIANCE.NS).
Orchestrator agent routes to Data Agent (fetches price/history).
Parallel: News Agent pulls articles; Sentiment Agent analyzes social/news.
Predictor Agent runs ML model on data.


Summarizer generates report with charts.

| Category     | API/Tool                | Key Features                   | Free Tier?   |
| ------------ | ----------------------- | ------------------------------ | ------------ |
| Stock Data   | Indian Stock Market API | NSE/BSE real-time, no key      | Yes          |
| News         | MarketAux               | Global finance news, sentiment | Yes          |
| Prediction   | Finnhub or yfinance     | Historical + basic forecasts   | Yes (limits) |
| ML Framework | scikit-learn/Prophet    | Time-series forecasting        | Open-source  |