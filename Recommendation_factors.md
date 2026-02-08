To build a truly "intelligent" advisor, your agents should move beyond just fetching prices. They need to perform **Triangulation**: comparing the Stock/Fund against its Sector, its History, and its Management's Promises.

Here is a detailed framework for the decision logic you can program into your **LangGraph Agents**.

---

### 1. Stock Investment Logic (Equity Analyst Agent)

To propose a "Good Time to Invest," the agent should evaluate three pillars:

#### A. Sectoral Tailwinds (The "Top Performing" Check)
*   **Metric:** Compare the **Sectoral Index** (e.g., NIFTY IT, NIFTY BANK, NIFTY AUTO) against the **NIFTY 50**.
*   **Logic:** If the Sector Index is outperforming Nifty over the last 3 months, the organization has a "Tailwind."
*   **Reason to Avoid:** If the sector is at an all-time high RSI (>75), it is "Overheated." Even a good company in a tired sector will see a correction.

#### B. Valuation & Entry Price (The "Fair Value" Check)
*   **Historical P/E vs. Current P/E:** Fetch the 5-year average P/E for the company. 
    *   *Entry:* If Current P/E < 5-Year Average.
    *   *Avoid:* If Current P/E is >2 standard deviations above the mean.
*   **Technical Support:** Look for the **200-Day Moving Average (DMA)**. 
    *   *Ideal Entry:* When the price is within 5% of the 200-DMA (Mean Reversion).

#### C. Management Credibility (The Transcript Check)
*   **The Delta:** Compare the *Sentiment Score* of the transcript from 2 quarters ago with the *Revenue Growth* of the current quarter.
*   **The "Proof":** If management promised 20% growth but delivered 10%, the agent should flag a "Credibility Gap" regardless of how good the stock looks.

---

### 2. Mutual Fund Investment Logic (MF Specialist Agent)

Mutual funds require a different "lens" because you are betting on the fund manager, not just the assets.

#### A. Performance vs. Benchmark (Alpha Generation)
*   **Metric:** Compare the Fund’s 3-year CAGR against its Category Benchmark (e.g., Nifty Next 50).
*   **Logic:** A fund is only "Good" if it provides **Alpha** (Excess return). If it is returning the same as the Index, advise the user to buy a low-cost Index Fund instead to save on Expense Ratio.

#### B. Portfolio "Freshness" (The Trend Check)
*   **Logic:** Look at the latest "Additions" to the portfolio. If the fund manager is buying sectors that are currently in a downturn (Contrarian) or sectors that are breaking out (Momentum).
*   **Entry Signal:** If the fund has a high **Cash Level** (>10%), it means the manager is waiting for a market dip. This is a good time for a **Lumpsum** entry.

#### C. Timing for Lumpsum vs. SIP
*   **Nifty PE Ratio:** If the broader Nifty 50 PE is >25, the agent should advise **"SIP Only"** (too expensive for lumpsum).
*   **Nifty PE Ratio:** If Nifty 50 PE is <18, the agent should advise **"Aggressive Lumpsum"** (market is undervalued).

---

### 3. Detailed Decision Matrix for your Agent Output

When your Final Agent generates the report, it should follow this structure:

| Consideration | Signal: "BUY/ACCUMULATE" | Signal: "AVOID/WAIT" |
| :--- | :--- | :--- |
| **Sector Status** | Under-valued sector starting to show momentum. | Sector is "Overcrowded" with high retail participation. |
| **Price Point** | Near 200-DMA or Support levels. | Price is "Parabolic" (too far from Moving Averages). |
| **Earnings Call** | Management addressed risks transparently. | Management gave vague answers on debt or margins. |
| **Delivery %** | High delivery percentage (indicates big players are buying). | Low delivery, high volume (indicates day-trading/speculation). |
| **MF Holdings** | Fund is exiting "Low Growth" and entering "High ROCE" stocks. | Fund is "Closet Indexing" (simply mimicking the Nifty). |

---

### 4. Example "Reasoning" the AI should provide:

**If the AI says "AVOID":**
> "While **Company X** has strong profits, the **Nifty IT Sector** has an RSI of 82, indicating it is overbought. Furthermore, in the last **Earnings Transcript**, the CEO mentioned 'Headwinds in US markets' which has not yet been reflected in the current stock price. **Recommendation:** Wait for a 5-10% correction toward the ₹XXXX price level."

**If the AI says "LUMPSUM BUY" (Mutual Fund):**
> "The **Fund Y** has outperformed its benchmark by 4% Alpha. Currently, the broader market (Nifty 50) is trading at a PE of 19, which is historically a 'Value Zone'. The fund has recently increased its weightage in the **Banking Sector**, which is currently a top-performing sector. **Recommendation:** Good time for Lumpsum investment."

---

### Best Practice for implementation:
1.  **Step-by-Step State:** Your LangGraph should have a "Research" state that collects all these variables before the "Decision" node is triggered.
2.  **External Knowledge:** Feed your agent a "Market Sentiment" score (Fear & Greed Index for India) as a global variable.
3.  **Proof of Analysis:** Always make the agent cite the specific line from the transcript or the specific P/E number so the user trusts the "Proof."

#### Data Sources
Data Sources
## Stocks
1.	NSE Direct (https://www.nseindia.com/get-quotes/equity?symbol=<name>)
2.	yfinance
3.	TrueData/Global Datafeeds
## Mutual Fund
1.	AMFI (https://www.amfiindia.com/spages/NAVAll.txt)
2.	MFAPI.in (https://api.mfapi.in/mf/{scheme_code})
