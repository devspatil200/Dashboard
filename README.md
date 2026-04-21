# 📊 Stock Analysis Dashboard
**Money Financial Services** — Professional Stock Research Tool

Built with Python + Streamlit + yfinance

---

## ✅ Features
- **Watchlist** – Add any NSE/BSE/US stock ticker
- **Fundamentals** – PE, D/E, ROE, FCF, Margins, Growth
- **Technicals** – 200 DMA distance, RSI, 52W range, Volume analysis
- **Decision Checklist** – 10-point scoring engine with grade
- **Research Notes** – Save personal insights per stock in SQLite
- **Light/White Theme** – Clean, professional UI

---

## 🚀 STEP-BY-STEP DEPLOYMENT GUIDE

### STEP 1 – Create GitHub Repository

1. Go to **https://github.com** and sign in (or create a free account)
2. Click the **"+"** icon → **"New repository"**
3. Name it: `stock-dashboard`
4. Set to **Public**
5. Click **"Create repository"**

---

### STEP 2 – Upload Files to GitHub

You need to upload **3 files**:
- `app.py`
- `requirements.txt`
- `README.md` (this file)

**Option A – Web Upload (Easiest for mobile):**
1. Open your new repository on GitHub
2. Click **"Add file"** → **"Upload files"**
3. Drag & drop all 3 files
4. Click **"Commit changes"**

**Option B – GitHub Desktop:**
1. Download GitHub Desktop app
2. Clone your repo
3. Copy files into the folder
4. Commit and Push

---

### STEP 3 – Deploy on Streamlit Cloud (FREE)

1. Go to **https://streamlit.io/cloud**
2. Click **"Sign in"** → Choose **"Sign in with GitHub"**
3. Authorize Streamlit to access your GitHub
4. Click **"New app"**
5. Fill in:
   - **Repository:** `your-username/stock-dashboard`
   - **Branch:** `main`
   - **Main file path:** `app.py`
6. Click **"Deploy!"**

Wait 2–3 minutes. Your app will be live at:
```
https://your-username-stock-dashboard-app-xxxxx.streamlit.app
```

---

### STEP 4 – Access from Mobile

1. Open the Streamlit URL in **Chrome on Android**
2. Tap the **three-dot menu** → **"Add to Home screen"**
3. Name it: `Stock Dashboard`
4. It will work like a PWA app on your phone! 📱

---

## 🔧 Run Locally (Optional)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

App opens at: http://localhost:8501

---

## 📌 Indian Stock Ticker Format

| Exchange | Format     | Example          |
|----------|-----------|------------------|
| NSE      | NAME.NS   | RELIANCE.NS      |
| BSE      | NAME.BO   | RELIANCE.BO      |
| US Stock | Plain     | AAPL, MSFT       |

**Popular NSE Tickers:**
`RELIANCE.NS` · `TCS.NS` · `INFY.NS` · `HDFCBANK.NS` · `ICICIBANK.NS`
`WIPRO.NS` · `BAJFINANCE.NS` · `SUNPHARMA.NS` · `TATAMOTORS.NS`

---

## ⚠️ Important Notes

- **Data Source:** Yahoo Finance (yfinance) — free but may have slight delays
- **Delivery %:** For exact NSE/BSE delivery data, a broker API is needed (Zerodha Kite, Upstox)
- **Not SEBI Advice:** This tool is for research purposes only. Always do your own due diligence.
- **SQLite DB:** Research notes are saved in `research_notes.db` in the same folder. On Streamlit Cloud, notes reset when the app restarts. For permanent storage, use `st.secrets` + Google Sheets or Supabase.

---

## 🔄 Updating the App

1. Edit `app.py` on GitHub (click the file → pencil icon)
2. Commit changes
3. Streamlit Cloud auto-deploys in ~1 minute

---

## 📞 Support
Built by Money Financial Services, Nashik
