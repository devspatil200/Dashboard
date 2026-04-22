"""
Professional Stock Analysis Dashboard — v3.0
Author : Money Financial Services
Features: Smart Groups, Piotroski F-Score, Intrinsic Value, AI Verdict (0-100),
          Volume Analysis, Smart Data Fetcher with fallback calculations
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import datetime
import math

# ══════════════════════════════════════════════════════
# PAGE CONFIG  ← must be first Streamlit call
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="Stock Analysis Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

/* ── Variables ── */
:root {
  --bg:        #f5f6fa;
  --card:      #ffffff;
  --border:    #e2e5ed;
  --primary:   #2563eb;
  --primary-lt:#eff6ff;
  --success:   #059669;
  --success-lt:#ecfdf5;
  --warn:      #d97706;
  --warn-lt:   #fffbeb;
  --danger:    #dc2626;
  --danger-lt: #fef2f2;
  --neutral:   #6b7280;
  --text:      #0f172a;
  --text-2:    #475569;
  --radius:    10px;
  --radius-lg: 14px;
  --shadow:    0 1px 3px rgba(0,0,0,.06), 0 4px 16px rgba(0,0,0,.05);
  --shadow-md: 0 2px 8px rgba(0,0,0,.08), 0 8px 24px rgba(0,0,0,.06);
}

/* ── Base ── */
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: #ffffff !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stMarkdown p { font-size: 0.85rem; }

/* ── Main content ── */
.block-container { padding: 1.75rem 2.5rem 4rem !important; max-width: 1440px !important; }

/* ── Cards ── */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow);
  margin-bottom: 1rem;
  transition: box-shadow .2s;
}
.card:hover { box-shadow: var(--shadow-md); }

.metric-label {
  font-size: 0.72rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: .07em;
  color: var(--neutral); margin-bottom: .3rem;
}
.metric-value {
  font-size: 1.65rem; font-weight: 700;
  color: var(--text); line-height: 1.1;
}
.metric-sub { font-size: .78rem; color: var(--neutral); margin-top: .2rem; }

/* ── Section header ── */
.sec-hdr {
  font-size: .95rem; font-weight: 700; color: var(--text);
  border-left: 3px solid var(--primary); padding-left: .65rem;
  margin: 1.75rem 0 .9rem;
}

/* ── Badges ── */
.badge {
  display: inline-block; padding: .22rem .7rem;
  border-radius: 999px; font-size: .74rem; font-weight: 700;
  letter-spacing: .03em; white-space: nowrap;
}
.b-green  { background: #dcfce7; color: #166534; }
.b-yellow { background: #fef9c3; color: #854d0e; }
.b-red    { background: #fee2e2; color: #991b1b; }
.b-blue   { background: #dbeafe; color: #1e40af; }
.b-gray   { background: #f1f5f9; color: #475569; }

/* ── Progress bar ── */
.prog-wrap { background: #e2e8f0; border-radius: 999px; height: 7px; width: 100%; margin: .4rem 0; }
.prog-fill { height: 7px; border-radius: 999px; }

/* ── AI Score ring ── */
.score-ring-wrap {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 1.5rem 1rem;
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius-lg); box-shadow: var(--shadow);
}
.score-number {
  font-size: 4rem; font-weight: 800; line-height: 1;
  font-family: 'DM Mono', monospace;
}
.score-label { font-size: .82rem; font-weight: 600; margin-top: .35rem; }

/* ── Stock row in list ── */
.stock-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: .65rem 1rem; background: var(--card);
  border: 1px solid var(--border); border-radius: var(--radius);
  margin-bottom: .4rem; cursor: pointer;
  transition: background .15s, border-color .15s;
}
.stock-row:hover { background: var(--primary-lt); border-color: #bfdbfe; }
.stock-row.active { background: var(--primary-lt); border-color: var(--primary); }

/* ── Alert boxes ── */
.box-info    { background: var(--primary-lt); border: 1px solid #bfdbfe; border-radius: var(--radius); padding: .75rem 1rem; font-size: .85rem; color: #1e40af; margin: .5rem 0; }
.box-success { background: var(--success-lt); border: 1px solid #6ee7b7; border-radius: var(--radius); padding: .75rem 1rem; font-size: .85rem; color: #065f46; margin: .5rem 0; }
.box-warn    { background: var(--warn-lt); border: 1px solid #fcd34d; border-radius: var(--radius); padding: .75rem 1rem; font-size: .85rem; color: #92400e; margin: .5rem 0; }
.box-danger  { background: var(--danger-lt); border: 1px solid #fca5a5; border-radius: var(--radius); padding: .75rem 1rem; font-size: .85rem; color: #991b1b; margin: .5rem 0; }

/* ── Checklist row ── */
.chk-row {
  display: flex; align-items: flex-start; gap: .6rem;
  padding: .45rem .8rem; border-radius: 8px; margin-bottom: .3rem;
}
.chk-icon { font-size: 1rem; flex-shrink: 0; padding-top: .05rem; }
.chk-text { font-size: .84rem; font-weight: 500; }
.chk-note { font-size: .74rem; color: var(--neutral); }

/* ── Divider ── */
.divider { border: none; border-top: 1px solid var(--border); margin: 1.25rem 0; }

/* ── Piotroski cell ── */
.pio-cell {
  background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
  padding: .75rem 1rem; margin-bottom: .5rem;
}
.pio-name  { font-size: .8rem; font-weight: 600; color: var(--text-2); }
.pio-value { font-size: .85rem; font-weight: 700; }

/* ── Override Streamlit defaults ── */
[data-testid="stButton"] > button {
  border-radius: 8px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  transition: all .15s !important;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] > div {
  border-radius: 8px !important;
  font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTabs"] [role="tab"] {
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: .88rem !important;
}
/* Remove extra padding on mobile */
@media (max-width: 768px) {
  .block-container { padding: 1rem 1rem 4rem !important; }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# STOCK DATABASE  (100+ popular Indian + US stocks)
# ══════════════════════════════════════════════════════
STOCK_DB = {
    # NSE Large Cap
    "Reliance Industries":     "RELIANCE.NS",
    "TCS":                     "TCS.NS",
    "Infosys":                 "INFY.NS",
    "HDFC Bank":               "HDFCBANK.NS",
    "ICICI Bank":              "ICICIBANK.NS",
    "Kotak Mahindra Bank":     "KOTAKBANK.NS",
    "Axis Bank":               "AXISBANK.NS",
    "SBI":                     "SBIN.NS",
    "Bajaj Finance":           "BAJFINANCE.NS",
    "Bajaj Finserv":           "BAJAJFINSV.NS",
    "Wipro":                   "WIPRO.NS",
    "HCL Technologies":        "HCLTECH.NS",
    "Tech Mahindra":           "TECHM.NS",
    "L&T":                     "LT.NS",
    "ITC":                     "ITC.NS",
    "Hindustan Unilever":      "HINDUNILVR.NS",
    "Nestle India":            "NESTLEIND.NS",
    "Asian Paints":            "ASIANPAINT.NS",
    "Maruti Suzuki":           "MARUTI.NS",
    "Tata Motors":             "TATAMOTORS.NS",
    "Mahindra & Mahindra":     "M&M.NS",
    "Sun Pharma":              "SUNPHARMA.NS",
    "Dr Reddys":               "DRREDDY.NS",
    "Cipla":                   "CIPLA.NS",
    "Divis Lab":               "DIVISLAB.NS",
    "Apollo Hospitals":        "APOLLOHOSP.NS",
    "ONGC":                    "ONGC.NS",
    "Power Grid":              "POWERGRID.NS",
    "NTPC":                    "NTPC.NS",
    "Coal India":              "COALINDIA.NS",
    "Titan":                   "TITAN.NS",
    "Tata Steel":              "TATASTEEL.NS",
    "JSW Steel":               "JSWSTEEL.NS",
    "Hindalco":                "HINDALCO.NS",
    "UltraTech Cement":        "ULTRACEMCO.NS",
    "Grasim":                  "GRASIM.NS",
    "Adani Ports":             "ADANIPORTS.NS",
    "Adani Enterprises":       "ADANIENT.NS",
    "Adani Green":             "ADANIGREEN.NS",
    "Adani Power":             "ADANIPOWER.NS",
    "Shriram Finance":         "SHRIRAMFIN.NS",
    "Muthoot Finance":         "MUTHOOTFIN.NS",
    "Cholamandalam Finance":   "CHOLAFIN.NS",
    "IDFC First Bank":         "IDFCFIRSTB.NS",
    "IndusInd Bank":           "INDUSINDBK.NS",
    "Bank of Baroda":          "BANKBARODA.NS",
    "PNB":                     "PNB.NS",
    "Canara Bank":             "CANBK.NS",
    "Union Bank":              "UNIONBANK.NS",
    "Federal Bank":            "FEDERALBNK.NS",
    "Yes Bank":                "YESBANK.NS",
    "Paytm":                   "PAYTM.NS",
    "Zomato":                  "ZOMATO.NS",
    "Nykaa":                   "NYKAA.NS",
    "Tata Power":              "TATAPOWER.NS",
    "Tata Consumer":           "TATACONSUM.NS",
    "Tata Communications":     "TATACOMM.NS",
    "Godrej Consumer":         "GODREJCP.NS",
    "Godrej Properties":       "GODREJPROP.NS",
    "Pidilite":                "PIDILITIND.NS",
    "Berger Paints":           "BERGEPAINT.NS",
    "Dabur":                   "DABUR.NS",
    "Marico":                  "MARICO.NS",
    "Britannia":               "BRITANNIA.NS",
    "Colgate":                 "COLPAL.NS",
    "Havells":                 "HAVELLS.NS",
    "Voltas":                  "VOLTAS.NS",
    "Dixon Technologies":      "DIXON.NS",
    "Hero MotoCorp":           "HEROMOTOCO.NS",
    "Bajaj Auto":              "BAJAJ-AUTO.NS",
    "Eicher Motors":           "EICHERMOT.NS",
    "Ashok Leyland":           "ASHOKLEY.NS",
    "IndiGo":                  "INDIGO.NS",
    "Lupin":                   "LUPIN.NS",
    "Biocon":                  "BIOCON.NS",
    "Torrent Pharma":          "TORNTPHARM.NS",
    "Aurobindo Pharma":        "AUROPHARMA.NS",
    "Mankind Pharma":          "MANKIND.NS",
    "Zydus Lifesciences":      "ZYDUSLIFE.NS",
    "DLF":                     "DLF.NS",
    "Lodha":                   "LODHA.NS",
    "Prestige Estates":        "PRESTIGE.NS",
    "Oberoi Realty":           "OBEROIRLTY.NS",
    "Varun Beverages":         "VBL.NS",
    "Page Industries":         "PAGEIND.NS",
    "Mphasis":                 "MPHASIS.NS",
    "LTIMindtree":             "LTIM.NS",
    "Persistent Systems":      "PERSISTENT.NS",
    "Coforge":                 "COFORGE.NS",
    "BSE":                     "BSE.NS",
    "MCX":                     "MCX.NS",
    "Angel One":               "ANGELONE.NS",
    "CDSL":                    "CDSL.NS",
    "Polycab":                 "POLYCAB.NS",
    "KEI Industries":          "KEI.NS",
    "Siemens India":           "SIEMENS.NS",
    "ABB India":               "ABB.NS",
    "BEL":                     "BEL.NS",
    "HAL":                     "HAL.NS",
    "Bharat Forge":            "BHARATFORG.NS",
    "IRCTC":                   "IRCTC.NS",
    "IRFC":                    "IRFC.NS",
    "RVNL":                    "RVNL.NS",
    "Max Healthcare":          "MAXHEALTH.NS",
    "Fortis Healthcare":       "FORTIS.NS",
    "Dr Lal PathLabs":         "LALPATHLAB.NS",
    "NHPC":                    "NHPC.NS",
    "Torrent Power":           "TORNTPOWER.NS",
}


# ══════════════════════════════════════════════════════
# DATABASE LAYER
# ══════════════════════════════════════════════════════
DB = "stock_pro_v3.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name  TEXT NOT NULL,
            ticker      TEXT NOT NULL,
            added_at    TEXT,
            UNIQUE(group_name, ticker)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            ticker      TEXT PRIMARY KEY,
            content     TEXT,
            updated_at  TEXT
        )
    """)
    conn.commit()
    conn.close()

def db_exec(sql, params=()):
    conn = sqlite3.connect(DB)
    conn.execute(sql, params)
    conn.commit()
    conn.close()

def db_fetch(sql, params=()):
    conn = sqlite3.connect(DB)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows

def get_groups():
    return [r[0] for r in db_fetch("SELECT DISTINCT group_name FROM groups ORDER BY group_name")]

def get_tickers(grp):
    return [r[0] for r in db_fetch(
        "SELECT ticker FROM groups WHERE group_name=? AND ticker!='__init__' ORDER BY ticker", (grp,))]

def add_ticker(grp, ticker):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    db_exec("INSERT OR IGNORE INTO groups (group_name,ticker,added_at) VALUES (?,?,?)",
            (grp, ticker.upper().strip(), now))

def remove_ticker(grp, ticker):
    db_exec("DELETE FROM groups WHERE group_name=? AND ticker=?", (grp, ticker))

def create_group(name):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    db_exec("INSERT OR IGNORE INTO groups (group_name,ticker,added_at) VALUES (?,?,?)",
            (name, "__init__", now))

def rename_group(old, new):
    db_exec("UPDATE groups SET group_name=? WHERE group_name=?", (new, old))

def delete_group(name):
    db_exec("DELETE FROM groups WHERE group_name=?", (name,))

def save_note(ticker, content):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    db_exec("INSERT OR REPLACE INTO notes VALUES (?,?,?)", (ticker.upper(), content, now))

def load_note(ticker):
    rows = db_fetch("SELECT content,updated_at FROM notes WHERE ticker=?", (ticker.upper(),))
    return (rows[0][0], rows[0][1]) if rows else ("", "")


# ══════════════════════════════════════════════════════
# SMART DATA FETCHER  (with fallback calculations)
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def fetch_all(ticker: str):
    """
    Returns dict with: info, hist, financials, balance_sheet, cashflow
    All keys guaranteed to exist (may be empty DataFrame / {})
    """
    try:
        stk = yf.Ticker(ticker)
        info   = stk.info or {}
        hist   = stk.history(period="1y")
        try:    fin  = stk.financials
        except: fin  = pd.DataFrame()
        try:    bs   = stk.balance_sheet
        except: bs   = pd.DataFrame()
        try:    cf   = stk.cashflow
        except: cf   = pd.DataFrame()
        return {"info": info, "hist": hist, "fin": fin, "bs": bs, "cf": cf}
    except Exception:
        return {"info": {}, "hist": pd.DataFrame(),
                "fin": pd.DataFrame(), "bs": pd.DataFrame(), "cf": pd.DataFrame()}


def _val(d, *keys, default=None):
    """Safe nested value getter with NaN → None handling."""
    for key in keys:
        v = d.get(key) if isinstance(d, dict) else None
        if v is not None and not (isinstance(v, float) and math.isnan(v)):
            return v
    return default

def _row(df, *names):
    """Get first non-None row from a DataFrame by trying multiple row names."""
    if df is None or df.empty:
        return None
    for name in names:
        for idx in df.index:
            if name.lower() in str(idx).lower():
                row = df.loc[idx]
                vals = row.dropna()
                if not vals.empty:
                    return vals
    return None

def _latest(series):
    """Get latest (most recent) non-null value from a pandas Series."""
    if series is None:
        return None
    vals = series.dropna()
    return float(vals.iloc[0]) if not vals.empty else None

def smart_get(data: dict):
    """
    Extract financial metrics using info first, then calculate from
    raw statements if info returns N/A — the 'smart fetcher'.
    Returns a flat dict of all metrics needed for analysis.
    """
    info = data["info"]
    fin  = data["fin"]
    bs   = data["bs"]
    cf   = data["cf"]
    hist = data["hist"]

    m = {}  # master metrics dict

    # ── Basic price info ──
    m["name"]     = _val(info, "longName", "shortName", default=None)
    m["sector"]   = _val(info, "sector", default="—")
    m["industry"] = _val(info, "industry", default="—")
    m["exchange"] = _val(info, "exchange", default="—")
    m["currency"] = _val(info, "currency", default="INR")
    m["price"]    = _val(info, "regularMarketPrice", "currentPrice", default=None)
    m["prev_close"]= _val(info, "regularMarketPreviousClose", default=None)
    m["market_cap"]= _val(info, "marketCap", default=None)
    m["beta"]     = _val(info, "beta", default=None)

    # ── Valuation ──
    m["pe"]  = _val(info, "trailingPE", default=None)
    m["fpe"] = _val(info, "forwardPE",  default=None)
    m["pb"]  = _val(info, "priceToBook", default=None)
    m["ps"]  = _val(info, "priceToSalesTrailing12Months", default=None)
    m["peg"] = _val(info, "pegRatio", default=None)

    # ── Profitability (with fallback) ──
    m["roe"] = _val(info, "returnOnEquity", default=None)
    m["roa"] = _val(info, "returnOnAssets", default=None)
    m["pm"]  = _val(info, "profitMargins",  default=None)
    m["gm"]  = _val(info, "grossMargins",   default=None)
    m["om"]  = _val(info, "operatingMargins", default=None)

    # Fallback ROE = Net Income / Shareholders Equity
    if m["roe"] is None:
        ni_row  = _row(fin, "Net Income")
        eq_row  = _row(bs,  "Stockholders Equity", "Total Stockholder Equity")
        ni = _latest(ni_row); eq = _latest(eq_row)
        if ni and eq and eq != 0:
            m["roe"] = ni / abs(eq)

    # Fallback ROA = Net Income / Total Assets
    if m["roa"] is None:
        ni_row  = _row(fin, "Net Income")
        ta_row  = _row(bs,  "Total Assets")
        ni = _latest(ni_row); ta = _latest(ta_row)
        if ni and ta and ta != 0:
            m["roa"] = ni / abs(ta)

    # Fallback Profit Margin = Net Income / Revenue
    if m["pm"] is None:
        ni_row  = _row(fin, "Net Income")
        rev_row = _row(fin, "Total Revenue")
        ni = _latest(ni_row); rev = _latest(rev_row)
        if ni and rev and rev != 0:
            m["pm"] = ni / abs(rev)

    # ── Debt & Liquidity ──
    m["de"]  = _val(info, "debtToEquity", default=None)  # in % (yfinance style)
    m["cr"]  = _val(info, "currentRatio", default=None)
    m["qr"]  = _val(info, "quickRatio",   default=None)

    # Fallback D/E from balance sheet
    if m["de"] is None:
        td_row = _row(bs, "Total Debt", "Long Term Debt")
        eq_row = _row(bs, "Stockholders Equity", "Total Stockholder Equity")
        td = _latest(td_row); eq = _latest(eq_row)
        if td is not None and eq and eq != 0:
            m["de"] = (td / abs(eq)) * 100  # keep in % to match yfinance

    # ── Cash Flow ──
    m["fcf"]  = _val(info, "freeCashflow", default=None)
    m["ocf"]  = _val(info, "operatingCashflow", default=None)

    # Fallback FCF = Operating CF - CapEx
    if m["fcf"] is None:
        ocf_row  = _row(cf, "Operating Cash Flow", "Cash From Operations")
        capx_row = _row(cf, "Capital Expenditure", "Purchases Of Property Plant And Equipment")
        ocf  = _latest(ocf_row)
        capx = _latest(capx_row)
        if ocf is not None:
            m["ocf"] = ocf
            m["fcf"] = ocf + (capx if capx is not None else 0)

    # ── Growth ──
    m["rev_growth"] = _val(info, "revenueGrowth", default=None)
    m["earn_growth"]= _val(info, "earningsGrowth", default=None)
    m["eps"]        = _val(info, "trailingEps", default=None)
    m["feps"]       = _val(info, "forwardEps",  default=None)
    m["rev_ttm"]    = _val(info, "totalRevenue", default=None)

    # ── Holders ──
    m["insider_pct"]= _val(info, "heldPercentInsiders", default=None)
    m["inst_pct"]   = _val(info, "heldPercentInstitutions", default=None)

    # ── Dividend ──
    m["div_yield"]  = _val(info, "dividendYield", default=None)
    m["payout"]     = _val(info, "payoutRatio",   default=None)

    # ── Volume ──
    m["avg_vol"]    = _val(info, "averageVolume",   default=None)
    m["avg_vol_10"] = _val(info, "averageVolume10Day", default=None)
    if not hist.empty:
        m["curr_vol"] = float(hist["Volume"].iloc[-1])
        m["vol_20d"]  = float(hist["Volume"].rolling(20).mean().iloc[-1]) if len(hist) >= 20 else None
    else:
        m["curr_vol"] = None; m["vol_20d"] = None

    # ── Technical data from hist ──
    if not hist.empty:
        close = hist["Close"]
        m["curr_price_hist"] = float(close.iloc[-1])
        m["dma50"]   = float(close.rolling(50).mean().iloc[-1])  if len(close)>=50  else None
        m["dma200"]  = float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else None
        m["high52"]  = float(close.rolling(252).max().iloc[-1])  if len(close)>=252 else float(close.max())
        m["low52"]   = float(close.rolling(252).min().iloc[-1])  if len(close)>=252 else float(close.min())
        # RSI 14
        delta = close.diff()
        gain  = delta.clip(lower=0).rolling(14).mean()
        loss  = (-delta.clip(upper=0)).rolling(14).mean()
        rs    = gain / loss.replace(0, float("nan"))
        rsi   = 100 - (100 / (1 + rs))
        m["rsi"] = float(rsi.iloc[-1]) if not rsi.empty else None
        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd  = ema12 - ema26
        signal= macd.ewm(span=9).mean()
        m["macd"]        = float(macd.iloc[-1])
        m["macd_signal"] = float(signal.iloc[-1])
        m["macd_hist"]   = float((macd - signal).iloc[-1])
    else:
        for k in ["curr_price_hist","dma50","dma200","high52","low52","rsi","macd","macd_signal","macd_hist"]:
            m[k] = None

    return m


# ══════════════════════════════════════════════════════
# PIOTROSKI F-SCORE
# ══════════════════════════════════════════════════════
def calc_piotroski(data: dict):
    """
    Returns (total_score, list_of_criteria_dicts)
    Each criterion: {group, name, pass_, note}
    """
    info = data["info"]
    fin  = data["fin"]
    bs   = data["bs"]
    cf   = data["cf"]

    criteria = []

    def ni_vals():
        r = _row(fin, "Net Income")
        if r is None or len(r) < 2: return None, None
        return _latest(r), float(r.dropna().iloc[1]) if len(r.dropna()) > 1 else None

    def rev_vals():
        r = _row(fin, "Total Revenue")
        if r is None or len(r) < 2: return None, None
        return _latest(r), float(r.dropna().iloc[1]) if len(r.dropna()) > 1 else None

    def ta_vals():
        r = _row(bs, "Total Assets")
        if r is None or len(r) < 2: return None, None
        return _latest(r), float(r.dropna().iloc[1]) if len(r.dropna()) > 1 else None

    def ocf_val():
        r = _row(cf, "Operating Cash Flow", "Cash From Operations")
        return _latest(r)

    ni_curr, ni_prev = ni_vals()
    rev_curr, rev_prev = rev_vals()
    ta_curr, ta_prev = ta_vals()
    ocf = ocf_val()

    # ── PROFITABILITY (4 points) ──
    # F1: ROA > 0
    roe = _val(info, "returnOnEquity", default=None)
    roa = _val(info, "returnOnAssets", default=None)
    if roa is None and ni_curr and ta_curr and ta_curr != 0:
        roa = ni_curr / ta_curr
    f1 = roa is not None and roa > 0
    criteria.append({"group":"Profitability","name":"F1 — ROA Positive","pass_":f1,
                     "note":f"ROA = {roa*100:.1f}%" if roa else "Data N/A"})

    # F2: Operating Cash Flow > 0
    f2 = ocf is not None and ocf > 0
    criteria.append({"group":"Profitability","name":"F2 — Operating Cash Flow > 0","pass_":f2,
                     "note":f"OCF = ₹{ocf/1e7:.1f} Cr" if ocf else "Data N/A"})

    # F3: ROA improving (curr > prev year)
    if roa is not None and ta_prev and ni_prev:
        roa_prev = ni_prev / ta_prev if ta_prev != 0 else None
        f3 = roa_prev is not None and roa > roa_prev
        criteria.append({"group":"Profitability","name":"F3 — ROA Improving YoY","pass_":f3,
                         "note":f"Curr={roa*100:.1f}% vs Prev={roa_prev*100:.1f}%" if roa_prev else "N/A"})
    else:
        criteria.append({"group":"Profitability","name":"F3 — ROA Improving YoY","pass_":False,"note":"Insufficient data"})

    # F4: Accruals (OCF/TA > ROA)
    if ocf and ta_curr and ta_curr != 0 and roa is not None:
        accruals = ocf / ta_curr
        f4 = accruals > roa
        criteria.append({"group":"Profitability","name":"F4 — Cash Earnings > Paper Earnings","pass_":f4,
                         "note":f"OCF/TA={accruals*100:.1f}% vs ROA={roa*100:.1f}%"})
    else:
        criteria.append({"group":"Profitability","name":"F4 — Cash Earnings > Paper Earnings","pass_":False,"note":"Insufficient data"})

    # ── LEVERAGE & LIQUIDITY (3 points) ──
    # F5: Long-term debt ratio decreasing
    ltd_r = _row(bs, "Long Term Debt")
    if ltd_r is not None and len(ltd_r.dropna()) >= 2 and ta_curr and ta_prev:
        ltd_curr = float(ltd_r.dropna().iloc[0]); ltd_prev = float(ltd_r.dropna().iloc[1])
        ratio_curr = ltd_curr / ta_curr if ta_curr else None
        ratio_prev = ltd_prev / ta_prev if ta_prev else None
        f5 = ratio_curr is not None and ratio_prev is not None and ratio_curr < ratio_prev
        criteria.append({"group":"Leverage","name":"F5 — Debt Ratio Decreasing","pass_":f5,
                         "note":f"Curr={ratio_curr*100:.1f}% vs Prev={ratio_prev*100:.1f}%" if ratio_curr and ratio_prev else "N/A"})
    else:
        criteria.append({"group":"Leverage","name":"F5 — Debt Ratio Decreasing","pass_":False,"note":"Insufficient data"})

    # F6: Current ratio improving
    cr = _val(info, "currentRatio", default=None)
    cr_r = _row(bs, "Current Assets")
    cl_r = _row(bs, "Current Liabilities")
    if cr_r is not None and cl_r is not None and len(cr_r.dropna()) >= 2:
        ca_curr=float(cr_r.dropna().iloc[0]); ca_prev=float(cr_r.dropna().iloc[1])
        cl_curr=float(cl_r.dropna().iloc[0]); cl_prev=float(cl_r.dropna().iloc[1])
        cr_curr_calc = ca_curr/cl_curr if cl_curr!=0 else None
        cr_prev_calc = ca_prev/cl_prev if cl_prev!=0 else None
        f6 = cr_curr_calc is not None and cr_prev_calc is not None and cr_curr_calc > cr_prev_calc
        criteria.append({"group":"Leverage","name":"F6 — Current Ratio Improving","pass_":f6,
                         "note":f"Curr={cr_curr_calc:.2f} vs Prev={cr_prev_calc:.2f}" if cr_curr_calc else "N/A"})
    else:
        cr_from_info = cr
        criteria.append({"group":"Leverage","name":"F6 — Current Ratio Improving","pass_":cr_from_info is not None and cr_from_info > 1.5,
                         "note":f"CR={cr_from_info:.2f}" if cr_from_info else "N/A"})

    # F7: No new share dilution
    shares_r = _row(bs, "Ordinary Shares Number", "Common Stock Shares Outstanding")
    if shares_r is not None and len(shares_r.dropna()) >= 2:
        s_curr=float(shares_r.dropna().iloc[0]); s_prev=float(shares_r.dropna().iloc[1])
        f7 = s_curr <= s_prev
        criteria.append({"group":"Leverage","name":"F7 — No Share Dilution","pass_":f7,
                         "note":f"Curr={s_curr/1e7:.2f}Cr vs Prev={s_prev/1e7:.2f}Cr"})
    else:
        criteria.append({"group":"Leverage","name":"F7 — No Share Dilution","pass_":False,"note":"Data N/A"})

    # ── OPERATING EFFICIENCY (2 points) ──
    # F8: Gross margin improving
    gm = _val(info, "grossMargins", default=None)
    gp_r = _row(fin, "Gross Profit")
    if gp_r is not None and len(gp_r.dropna()) >= 2 and rev_curr and rev_prev:
        gp_curr=float(gp_r.dropna().iloc[0]); gp_prev=float(gp_r.dropna().iloc[1])
        gm_curr = gp_curr/rev_curr if rev_curr!=0 else None
        gm_prev = gp_prev/rev_prev if rev_prev!=0 else None
        f8 = gm_curr is not None and gm_prev is not None and gm_curr > gm_prev
        criteria.append({"group":"Efficiency","name":"F8 — Gross Margin Improving","pass_":f8,
                         "note":f"Curr={gm_curr*100:.1f}% vs Prev={gm_prev*100:.1f}%" if gm_curr else "N/A"})
    else:
        criteria.append({"group":"Efficiency","name":"F8 — Gross Margin Improving","pass_":gm is not None and gm > 0.2,
                         "note":f"GM={gm*100:.1f}%" if gm else "N/A"})

    # F9: Asset turnover improving
    if rev_curr and rev_prev and ta_curr and ta_prev:
        at_curr = rev_curr/ta_curr if ta_curr!=0 else None
        at_prev = rev_prev/ta_prev if ta_prev!=0 else None
        f9 = at_curr is not None and at_prev is not None and at_curr > at_prev
        criteria.append({"group":"Efficiency","name":"F9 — Asset Turnover Improving","pass_":f9,
                         "note":f"Curr={at_curr:.2f}x vs Prev={at_prev:.2f}x" if at_curr else "N/A"})
    else:
        criteria.append({"group":"Efficiency","name":"F9 — Asset Turnover Improving","pass_":False,"note":"Insufficient data"})

    score = sum(1 for c in criteria if c["pass_"])
    return score, criteria


# ══════════════════════════════════════════════════════
# INTRINSIC VALUE  (Graham + DCF blend)
# ══════════════════════════════════════════════════════
def calc_intrinsic_value(m: dict):
    """
    Returns dict: {graham, dcf, avg, margin_of_safety, upside_pct}
    """
    result = {}

    # Graham Number = sqrt(22.5 × EPS × BVPS)
    eps  = m.get("eps")
    bvps = None
    pb   = m.get("pb"); price = m.get("price")
    if pb and price and pb > 0:
        bvps = price / pb

    if eps and eps > 0 and bvps and bvps > 0:
        graham = math.sqrt(22.5 * eps * bvps)
        result["graham"] = graham
    else:
        result["graham"] = None

    # DCF (Simplified): IV = EPS × (8.5 + 2g) × 4.4 / Y
    # Where g = expected growth rate, Y = current AAA bond yield (approx 7% for India)
    growth = m.get("earn_growth")
    if growth is None: growth = m.get("rev_growth")
    if eps and eps > 0 and growth is not None:
        g_pct  = max(-20, min(50, growth * 100))  # clamp growth
        Y      = 7.5  # India 10Y bond yield proxy
        dcf_iv = eps * (8.5 + 2 * g_pct) * 4.4 / Y
        result["dcf"] = dcf_iv if dcf_iv > 0 else None
    else:
        result["dcf"] = None

    # Average & Margin of Safety
    valid = [v for v in [result.get("graham"), result.get("dcf")] if v]
    if valid and price:
        avg = sum(valid) / len(valid)
        result["avg"]   = avg
        result["mos"]   = ((avg - price) / avg) * 100  # margin of safety %
        result["upside"] = ((avg - price) / price) * 100
    else:
        result["avg"] = result["mos"] = result["upside"] = None

    return result


# ══════════════════════════════════════════════════════
# AI VERDICT SCORE  (0-100)
# ══════════════════════════════════════════════════════
def calc_ai_score(m: dict, pio_score: int, iv: dict):
    """
    Composite 0-100 score across 5 pillars.
    Returns (total, breakdown_dict, grade, color)
    """
    breakdown = {}

    # 1. VALUATION (20 pts)
    val = 0
    pe = m.get("pe")
    if pe:
        if pe < 15:   val += 10
        elif pe < 25: val += 7
        elif pe < 40: val += 4
    pb = m.get("pb")
    if pb:
        if pb < 1.5:  val += 10
        elif pb < 3:  val += 7
        elif pb < 5:  val += 3
    breakdown["Valuation"] = min(val, 20)

    # 2. PROFITABILITY (20 pts)
    prof = 0
    roe = m.get("roe")
    if roe:
        if roe > 0.25:   prof += 8
        elif roe > 0.15: prof += 5
        elif roe > 0:    prof += 2
    pm = m.get("pm")
    if pm:
        if pm > 0.20:   prof += 7
        elif pm > 0.10: prof += 4
        elif pm > 0:    prof += 1
    fcf = m.get("fcf")
    if fcf and fcf > 0: prof += 5
    breakdown["Profitability"] = min(prof, 20)

    # 3. FINANCIAL HEALTH (20 pts)
    health = 0
    de = m.get("de")
    if de is not None:
        de_ratio = de / 100
        if de_ratio < 0.3:  health += 8
        elif de_ratio < 0.7: health += 5
        elif de_ratio < 1:   health += 2
    cr = m.get("cr")
    if cr:
        if cr > 2:   health += 7
        elif cr > 1.5: health += 4
        elif cr > 1:   health += 1
    # Piotroski contribution
    health += min(pio_score, 5)  # up to 5 pts from Piotroski
    breakdown["Financial Health"] = min(health, 20)

    # 4. TECHNICAL (20 pts)
    tech = 0
    price = m.get("price") or m.get("curr_price_hist")
    dma200 = m.get("dma200")
    dma50  = m.get("dma50")
    rsi    = m.get("rsi")
    if price and dma200:
        pct = (price - dma200) / dma200 * 100
        if 0 < pct < 20:    tech += 8   # healthy uptrend
        elif pct >= 20:     tech += 4   # overextended
        elif -10 < pct < 0: tech += 3   # just below — borderline
    if price and dma50:
        if price > dma50:   tech += 5
    if rsi:
        if 40 <= rsi <= 65: tech += 7   # ideal zone
        elif 30 <= rsi < 40 or 65 < rsi <= 70: tech += 4
        elif rsi < 30:      tech += 2   # oversold — risky
    macd_h = m.get("macd_hist")
    if macd_h and macd_h > 0: tech += 0  # already captured in above
    breakdown["Technical"] = min(tech, 20)

    # 5. GROWTH & MOMENTUM (20 pts)
    growth = 0
    rg = m.get("rev_growth")
    if rg:
        if rg > 0.20:  growth += 7
        elif rg > 0.10: growth += 4
        elif rg > 0:    growth += 1
    eg = m.get("earn_growth")
    if eg:
        if eg > 0.20:  growth += 7
        elif eg > 0.10: growth += 4
        elif eg > 0:    growth += 1
    # Intrinsic Value upside
    upside = iv.get("upside")
    if upside:
        if upside > 30:  growth += 6
        elif upside > 10: growth += 3
        elif upside > 0:  growth += 1
    breakdown["Growth & Momentum"] = min(growth, 20)

    total = sum(breakdown.values())

    if total >= 75:   grade, color = "Excellent — Strong Buy",  "#059669"
    elif total >= 60: grade, color = "Good — Buy",              "#2563eb"
    elif total >= 45: grade, color = "Average — Hold/Watch",    "#d97706"
    elif total >= 30: grade, color = "Weak — Caution",          "#ea580c"
    else:             grade, color = "Poor — Avoid",            "#dc2626"

    return total, breakdown, grade, color


# ══════════════════════════════════════════════════════
# FORMATTING HELPERS
# ══════════════════════════════════════════════════════
def fc(v, dec=2):
    """Format Crores."""
    if v is None: return "N/A"
    try:
        v = float(v)
        if abs(v) >= 1e12: return f"₹{v/1e12:.2f} T"
        if abs(v) >= 1e7:  return f"₹{v/1e7:.2f} Cr"
        if abs(v) >= 1e5:  return f"₹{v/1e5:.2f} L"
        return f"₹{v:,.0f}"
    except: return "N/A"

def fp(v, dec=1):
    """Format percentage."""
    if v is None: return "N/A"
    try:    return f"{float(v)*100:.{dec}f}%"
    except: return "N/A"

def fn(v, dec=2):
    """Format number."""
    if v is None: return "N/A"
    try:    return f"{float(v):,.{dec}f}"
    except: return "N/A"

def color_roe(v):
    if v is None: return "#6b7280"
    return "#059669" if v > 0.15 else "#dc2626"

def color_de(v):
    if v is None: return "#6b7280"
    return "#059669" if v/100 < 1 else "#dc2626"

def color_pm(v):
    if v is None: return "#6b7280"
    return "#059669" if v > 0.10 else "#dc2626"

def color_pe(v):
    if v is None: return "#6b7280"
    return "#059669" if v < 25 else ("#d97706" if v < 40 else "#dc2626")

def mk_card(label, value, sub="", val_color="#0f172a"):
    return f"""<div class='card'>
      <div class='metric-label'>{label}</div>
      <div class='metric-value' style='color:{val_color};'>{value}</div>
      {'<div class="metric-sub">'+sub+'</div>' if sub else ''}
    </div>"""

def mk_badge(text, cls):
    return f"<span class='badge {cls}'>{text}</span>"

def prog_bar(pct, color="#2563eb"):
    pct = max(0, min(100, pct))
    return f"""<div class='prog-wrap'><div class='prog-fill' style='width:{pct}%;background:{color};'></div></div>"""


# ══════════════════════════════════════════════════════
# FULL ANALYSIS RENDERER
# ══════════════════════════════════════════════════════
def render_analysis(ticker: str):
    """Render the complete deep-dive analysis for one ticker."""

    with st.spinner(f"Fetching data for **{ticker}**…"):
        data = fetch_all(ticker)
        m    = smart_get(data)

    if not m.get("price") and not m.get("curr_price_hist"):
        st.markdown(f"<div class='box-danger'>❌ Could not fetch data for <b>{ticker}</b>. Please verify the ticker symbol (e.g., RELIANCE.NS for NSE).</div>",
                    unsafe_allow_html=True)
        return

    with st.spinner("Computing Piotroski F-Score…"):
        pio_score, pio_criteria = calc_piotroski(data)

    iv = calc_intrinsic_value(m)
    ai_score, ai_breakdown, ai_grade, ai_color = calc_ai_score(m, pio_score, iv)

    # ── Header ──────────────────────────────────────────
    price     = m.get("price") or m.get("curr_price_hist") or 0
    prev      = m.get("prev_close")
    chg       = price - prev if prev else 0
    chg_pct   = chg / prev * 100 if prev else 0
    chg_color = "#059669" if chg >= 0 else "#dc2626"
    chg_arrow = "▲" if chg >= 0 else "▼"
    currency  = m.get("currency","INR")

    st.markdown(f"""
    <div class='card' style='margin-bottom:1.25rem;'>
      <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;'>
        <div>
          <div style='font-size:1.5rem;font-weight:700;color:#0f172a;line-height:1.2;'>
            {m.get("name") or ticker}
          </div>
          <div style='font-size:.82rem;color:#64748b;margin-top:.35rem;display:flex;align-items:center;gap:.5rem;flex-wrap:wrap;'>
            <span class='badge b-blue'>{ticker}</span>
            <span class='badge b-gray'>{m.get("exchange","—")}</span>
            <span>{m.get("sector","—")} · {m.get("industry","—")}</span>
          </div>
        </div>
        <div style='text-align:right;'>
          <div style='font-size:2.2rem;font-weight:800;color:#0f172a;font-family:"DM Mono",monospace;'>
            {currency} {price:,.2f}
          </div>
          <div style='font-size:.95rem;font-weight:600;color:{chg_color};'>
            {chg_arrow} {abs(chg):,.2f} ({chg_pct:+.2f}%)
          </div>
          <div style='font-size:.78rem;color:#94a3b8;margin-top:.2rem;'>Market Cap: {fc(m.get("market_cap"))}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ────────────────────────────────────────────
    t1, t2, t3, t4, t5 = st.tabs([
        "📋 Fundamentals", "📡 Technicals",
        "🏆 Piotroski", "💎 Intrinsic Value",
        "🤖 AI Verdict"
    ])

    # ════════════════════ TAB 1 — FUNDAMENTALS ════════════════════
    with t1:
        st.markdown("<div class='sec-hdr'>Valuation Ratios</div>", unsafe_allow_html=True)
        c1,c2,c3,c4,c5 = st.columns(5)
        cols_data = [
            ("Trailing PE",  fn(m.get("pe"),1),  "< 25 ideal",   color_pe(m.get("pe"))),
            ("Forward PE",   fn(m.get("fpe"),1), "Future earnings","#0f172a"),
            ("Price / Book", fn(m.get("pb"),2),  "< 3 ideal",    "#0f172a"),
            ("Price / Sales",fn(m.get("ps"),2),  "Revenue multiple","#0f172a"),
            ("PEG Ratio",    fn(m.get("peg"),2),  "< 1 undervalued","#0f172a"),
        ]
        for col,(lbl,val,sub,vc) in zip([c1,c2,c3,c4,c5], cols_data):
            col.markdown(mk_card(lbl,val,sub,vc), unsafe_allow_html=True)

        st.markdown("<div class='sec-hdr'>Profitability</div>", unsafe_allow_html=True)
        c1,c2,c3,c4,c5 = st.columns(5)
        roe_v=m.get("roe"); pm_v=m.get("pm"); gm_v=m.get("gm"); om_v=m.get("om"); roa_v=m.get("roa")
        for col,(lbl,val,sub,vc) in zip([c1,c2,c3,c4,c5], [
            ("ROE",         fp(roe_v), "> 15% ideal", color_roe(roe_v)),
            ("ROA",         fp(roa_v), "Asset return", "#0f172a"),
            ("Net Margin",  fp(pm_v),  "> 10% ideal",  color_pm(pm_v)),
            ("Gross Margin",fp(gm_v),  "Revenue quality","#0f172a"),
            ("Oper. Margin",fp(om_v),  "Operating efficiency","#0f172a"),
        ]):
            col.markdown(mk_card(lbl,val,sub,vc), unsafe_allow_html=True)

        st.markdown("<div class='sec-hdr'>Balance Sheet & Cash Flow</div>", unsafe_allow_html=True)
        c1,c2,c3,c4,c5 = st.columns(5)
        de_v=m.get("de"); cr_v=m.get("cr"); qr_v=m.get("qr"); fcf_v=m.get("fcf"); ocf_v=m.get("ocf")
        de_ratio = de_v/100 if de_v is not None else None
        for col,(lbl,val,sub,vc) in zip([c1,c2,c3,c4,c5], [
            ("Debt / Equity",  f"{de_ratio:.2f}x" if de_ratio is not None else "N/A",
             "< 1x ideal", color_de(de_v) if de_v else "#6b7280"),
            ("Current Ratio", fn(cr_v,2), "> 1.5 ideal",
             "#059669" if cr_v and cr_v>1.5 else "#dc2626"),
            ("Quick Ratio",   fn(qr_v,2), "Acid test","#0f172a"),
            ("Free Cash Flow",fc(fcf_v), "Positive = healthy",
             "#059669" if fcf_v and fcf_v>0 else "#dc2626"),
            ("Oper. Cash Flow",fc(ocf_v),"Cash generated","#0f172a"),
        ]):
            col.markdown(mk_card(lbl,val,sub,vc), unsafe_allow_html=True)

        st.markdown("<div class='sec-hdr'>Growth & EPS</div>", unsafe_allow_html=True)
        c1,c2,c3,c4,c5 = st.columns(5)
        rg_v=m.get("rev_growth"); eg_v=m.get("earn_growth"); eps_v=m.get("eps")
        feps_v=m.get("feps"); dy_v=m.get("div_yield")
        for col,(lbl,val,sub,vc) in zip([c1,c2,c3,c4,c5], [
            ("Revenue Growth", fp(rg_v,1), "YoY",
             "#059669" if rg_v and rg_v>0 else "#dc2626"),
            ("Earnings Growth", fp(eg_v,1), "YoY",
             "#059669" if eg_v and eg_v>0 else "#dc2626"),
            ("Trailing EPS",  fn(eps_v,2),  "Per share profit","#0f172a"),
            ("Forward EPS",   fn(feps_v,2), "Estimated","#0f172a"),
            ("Dividend Yield",fp(dy_v,2),   "Annual yield","#0f172a"),
        ]):
            col.markdown(mk_card(lbl,val,sub,vc), unsafe_allow_html=True)

        # Company description
        desc = _val(data["info"], "longBusinessSummary", default="")
        if desc:
            with st.expander("📖 About the Company"):
                st.markdown(f"<p style='font-size:.88rem;line-height:1.8;color:#374151;'>{desc[:1200]}{'…' if len(desc)>1200 else ''}</p>",
                            unsafe_allow_html=True)

    # ════════════════════ TAB 2 — TECHNICALS ════════════════════
    with t2:
        price_h = m.get("curr_price_hist") or price
        dma50   = m.get("dma50")
        dma200  = m.get("dma200")
        rsi_v   = m.get("rsi")
        high52  = m.get("high52")
        low52   = m.get("low52")

        st.markdown("<div class='sec-hdr'>Moving Averages & Trend</div>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)

        with c1:
            st.markdown(mk_card("Current Price", f"₹{price_h:,.2f}", "Live"), unsafe_allow_html=True)
        with c2:
            if dma50:
                p50 = (price_h - dma50)/dma50*100
                col50 = "#059669" if price_h > dma50 else "#dc2626"
                st.markdown(mk_card("50-Day DMA", f"₹{dma50:,.2f}", f"{p50:+.1f}% from price", col50),
                            unsafe_allow_html=True)
            else:
                st.markdown(mk_card("50-Day DMA","N/A","Insufficient history"), unsafe_allow_html=True)
        with c3:
            if dma200:
                p200 = (price_h - dma200)/dma200*100
                col200 = "#059669" if price_h > dma200 else "#dc2626"
                st.markdown(mk_card("200-Day DMA", f"₹{dma200:,.2f}", f"{p200:+.1f}% from price", col200),
                            unsafe_allow_html=True)
            else:
                st.markdown(mk_card("200-Day DMA","N/A","Insufficient history"), unsafe_allow_html=True)
        with c4:
            if rsi_v:
                rsi_lbl = "Overbought ⚠️" if rsi_v>70 else ("Oversold 🔎" if rsi_v<30 else "Neutral Zone ✅")
                rsi_col = "#dc2626" if rsi_v>70 else ("#d97706" if rsi_v<30 else "#059669")
                st.markdown(mk_card("RSI (14)", f"{rsi_v:.1f}", rsi_lbl, rsi_col), unsafe_allow_html=True)
            else:
                st.markdown(mk_card("RSI (14)","N/A",""), unsafe_allow_html=True)

        # 200 DMA distance bar
        if dma200:
            p200 = (price_h - dma200)/dma200*100
            clamped = max(-50, min(50, p200))
            fp200   = (clamped + 50) / 100 * 100
            fc200   = "#059669" if p200>=0 else "#dc2626"

            if p200 > 20:   trap_msg, trap_cls = "⚠️ <b>Overextended above 200 DMA</b> — Risk of pullback. Avoid chasing at these levels.", "box-warn"
            elif p200 > 0:  trap_msg, trap_cls = "✅ <b>Healthy uptrend</b> — Price is comfortably above 200 DMA. Good for positional entry.", "box-success"
            elif p200 > -15:trap_msg, trap_cls = "🔎 <b>Near or below 200 DMA</b> — Borderline zone. Wait for clear recovery signal.", "box-warn"
            else:           trap_msg, trap_cls = "🚨 <b>Far below 200 DMA</b> — Downtrend confirmed. High risk. Avoid unless deep value.", "box-danger"

            st.markdown(f"""
            <div class='card' style='margin-top:.5rem;'>
              <div style='display:flex;justify-content:space-between;margin-bottom:.4rem;'>
                <span style='font-size:.78rem;color:#94a3b8;'>−50% (Deep below)</span>
                <span style='font-size:.92rem;font-weight:700;color:{fc200};'>{p200:+.1f}% from 200 DMA</span>
                <span style='font-size:.78rem;color:#94a3b8;'>+50% (Overextended)</span>
              </div>
              {prog_bar(fp200, fc200)}
              <div style='text-align:center;font-size:.72rem;color:#94a3b8;margin-top:.25rem;'>
                ← Below 200 DMA &nbsp;|&nbsp; Price at 200 DMA &nbsp;|&nbsp; Above 200 DMA →
              </div>
            </div>
            <div class='{trap_cls}'>{trap_msg}</div>
            """, unsafe_allow_html=True)

        # 52-Week Range
        if high52 and low52 and high52 != low52:
            st.markdown("<div class='sec-hdr'>52-Week Range</div>", unsafe_allow_html=True)
            pos_pct = (price_h - low52) / (high52 - low52) * 100
            pfh     = (price_h - high52) / high52 * 100
            c1, c2  = st.columns([3,1])
            with c1:
                st.markdown(f"""
                <div class='card'>
                  <div style='display:flex;justify-content:space-between;margin-bottom:.4rem;'>
                    <span style='font-size:.78rem;color:#6b7280;'>52W Low ₹{low52:,.0f}</span>
                    <span style='font-size:.84rem;font-weight:700;'>📍 ₹{price_h:,.1f} ({pos_pct:.0f}th percentile)</span>
                    <span style='font-size:.78rem;color:#6b7280;'>52W High ₹{high52:,.0f}</span>
                  </div>
                  {prog_bar(pos_pct, f"linear-gradient(90deg,#ef4444 0%,#f59e0b 50%,#10b981 100%)")}
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(mk_card("From 52W High", f"{pfh:+.1f}%", "",
                                     "#059669" if pfh > -5 else "#dc2626"), unsafe_allow_html=True)

        # Volume Analysis
        st.markdown("<div class='sec-hdr'>Volume Analysis</div>", unsafe_allow_html=True)
        cv  = m.get("curr_vol")
        v20 = m.get("vol_20d")
        avg = m.get("avg_vol")
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            st.markdown(mk_card("Today's Volume", f"{cv:,.0f}" if cv else "N/A","Shares traded"), unsafe_allow_html=True)
        with c2:
            st.markdown(mk_card("20-Day Avg Vol", f"{v20:,.0f}" if v20 else "N/A","Rolling average"), unsafe_allow_html=True)
        with c3:
            if cv and v20 and v20>0:
                ratio = cv/v20
                vc2   = "#059669" if ratio>1.5 else ("#d97706" if ratio>0.8 else "#dc2626")
                vlbl  = "📈 High Volume" if ratio>1.5 else ("📉 Low Volume" if ratio<0.8 else "➡️ Normal")
                st.markdown(mk_card("Vol vs 20D Avg", f"{ratio:.2f}×", vlbl, vc2), unsafe_allow_html=True)
            else:
                st.markdown(mk_card("Vol vs 20D Avg","N/A",""), unsafe_allow_html=True)
        with c4:
            if cv and v20:
                vol_signal = "Volume confirming move ✅" if cv > v20*1.5 else ("Volume weak ⚠️" if cv < v20*0.5 else "Volume normal")
                st.markdown(mk_card("Volume Signal", "Spike" if cv>v20*1.5 else ("Dry" if cv<v20*0.5 else "Normal"),
                                    vol_signal,"#059669" if cv>v20*1.5 else "#d97706"), unsafe_allow_html=True)
            else:
                st.markdown(mk_card("Volume Signal","N/A",""), unsafe_allow_html=True)

        # MACD
        macd_v = m.get("macd"); macd_s = m.get("macd_signal"); macd_h = m.get("macd_hist")
        if macd_v and macd_s:
            st.markdown("<div class='sec-hdr'>MACD Signal</div>", unsafe_allow_html=True)
            c1,c2,c3 = st.columns(3)
            macd_signal_txt = "Bullish 🟢" if macd_h and macd_h>0 else "Bearish 🔴"
            macd_color = "#059669" if macd_h and macd_h>0 else "#dc2626"
            with c1: st.markdown(mk_card("MACD Line",f"{macd_v:.2f}","12-26 EMA diff"), unsafe_allow_html=True)
            with c2: st.markdown(mk_card("Signal Line",f"{macd_s:.2f}","9-day EMA of MACD"), unsafe_allow_html=True)
            with c3: st.markdown(mk_card("MACD Histogram",f"{macd_h:.2f}" if macd_h else "N/A",macd_signal_txt,macd_color), unsafe_allow_html=True)

        # Price chart
        hist_df = data.get("hist", pd.DataFrame())
        if not hist_df.empty:
            st.markdown("<div class='sec-hdr'>1-Year Price Chart with MAs</div>", unsafe_allow_html=True)
            chart = hist_df[["Close"]].copy()
            if dma50:  chart["50 DMA"]  = hist_df["Close"].rolling(50).mean()
            if dma200: chart["200 DMA"] = hist_df["Close"].rolling(200).mean()
            st.line_chart(chart, use_container_width=True, height=300)

    # ════════════════════ TAB 3 — PIOTROSKI ════════════════════
    with t3:
        if pio_score >= 7:   pio_cls,pio_verdict = "b-green","Strong — Financially Healthy Company 💪"
        elif pio_score >= 5: pio_cls,pio_verdict = "b-yellow","Moderate — Some Concerns, Monitor Closely"
        else:                pio_cls,pio_verdict = "b-red","Weak — Financial Distress Risk ⚠️"

        c1,c2 = st.columns([1,2])
        with c1:
            pio_color = "#059669" if pio_score>=7 else ("#d97706" if pio_score>=5 else "#dc2626")
            st.markdown(f"""
            <div style='background:#fff;border:1px solid #e2e5ed;border-radius:14px;padding:2rem 1rem;
                        box-shadow:0 1px 3px rgba(0,0,0,.06);text-align:center;'>
              <div style='font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.07em;
                          color:#6b7280;margin-bottom:.5rem;'>PIOTROSKI F-SCORE</div>
              <div style='font-size:5rem;font-weight:800;color:{pio_color};line-height:1;
                          font-family:"DM Mono",monospace;'>{pio_score}</div>
              <div style='font-size:.82rem;color:#6b7280;margin:.25rem 0 .75rem;'>out of 9</div>
              {prog_bar(pio_score/9*100, pio_color)}
              <div style='margin-top:.75rem;'>
                <span class='badge {pio_cls}' style='font-size:.82rem;padding:.3rem .9rem;'>{pio_verdict}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='sec-hdr' style='margin-top:0;'>F-Score Breakdown</div>", unsafe_allow_html=True)
            groups_pio = {}
            for c in pio_criteria:
                groups_pio.setdefault(c["group"], []).append(c)

            for grp, items in groups_pio.items():
                grp_score = sum(1 for x in items if x["pass_"])
                st.markdown(f"<div style='font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#94a3b8;margin:.75rem 0 .35rem;'>{grp} ({grp_score}/{len(items)})</div>",
                            unsafe_allow_html=True)
                for item in items:
                    icon  = "✅" if item["pass_"] else "❌"
                    bg    = "#f0fdf4" if item["pass_"] else "#fef2f2"
                    color = "#065f46" if item["pass_"] else "#991b1b"
                    st.markdown(f"""
                    <div class='chk-row' style='background:{bg};'>
                      <span class='chk-icon'>{icon}</span>
                      <div>
                        <div class='chk-text' style='color:{color};'>{item["name"]}</div>
                        <div class='chk-note'>{item["note"]}</div>
                      </div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("""<div class='box-info' style='margin-top:1rem;'>
        ℹ️ <b>About Piotroski F-Score:</b> A score of 0-9 measuring financial strength.
        <b>7-9 = Strong</b>, <b>4-6 = Moderate</b>, <b>0-3 = Weak</b>.
        Higher scores have historically outperformed the market.
        </div>""", unsafe_allow_html=True)

    # ════════════════════ TAB 4 — INTRINSIC VALUE ════════════════════
    with t4:
        curr_price = m.get("price") or m.get("curr_price_hist")

        st.markdown("<div class='sec-hdr'>Intrinsic Value Estimates</div>", unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)

        with c1:
            gv = iv.get("graham")
            if gv:
                diff = (curr_price - gv)/gv*100 if curr_price else None
                col_g = "#059669" if curr_price and curr_price < gv else "#dc2626"
                st.markdown(mk_card(
                    "Graham Number", f"₹{gv:,.1f}",
                    f"Stock {'undervalued' if curr_price and curr_price<gv else 'overvalued'} by {abs(diff):.1f}%" if diff else "",
                    col_g
                ), unsafe_allow_html=True)
            else:
                st.markdown(mk_card("Graham Number","N/A","EPS or BVPS not available"), unsafe_allow_html=True)

        with c2:
            dv = iv.get("dcf")
            if dv:
                diff2 = (curr_price - dv)/dv*100 if curr_price else None
                col_d = "#059669" if curr_price and curr_price < dv else "#dc2626"
                st.markdown(mk_card(
                    "DCF Value (Benjamin Graham Formula)", f"₹{dv:,.1f}",
                    f"{'Undervalued' if curr_price and curr_price<dv else 'Overvalued'} by {abs(diff2):.1f}%" if diff2 else "",
                    col_d
                ), unsafe_allow_html=True)
            else:
                st.markdown(mk_card("DCF Value","N/A","EPS or Growth not available"), unsafe_allow_html=True)

        with c3:
            avg_iv = iv.get("avg")
            if avg_iv and curr_price:
                mos = iv.get("mos",0)
                upside = iv.get("upside",0)
                col_avg = "#059669" if upside > 0 else "#dc2626"
                st.markdown(mk_card(
                    "Blended Intrinsic Value", f"₹{avg_iv:,.1f}",
                    f"{'↑ Upside' if upside>0 else '↓ Downside'}: {abs(upside):.1f}% | MOS: {mos:.1f}%",
                    col_avg
                ), unsafe_allow_html=True)
            else:
                st.markdown(mk_card("Blended Intrinsic Value","N/A","Insufficient data"), unsafe_allow_html=True)

        # Margin of Safety visual
        if avg_iv and curr_price:
            mos = iv.get("mos", 0)
            upside = iv.get("upside", 0)
            if mos > 0:
                st.markdown(f"""<div class='box-success'>
                ✅ <b>Margin of Safety: {mos:.1f}%</b> — Stock appears undervalued. Current price is {mos:.1f}% below estimated intrinsic value.
                Potential upside: {upside:.1f}%
                </div>""", unsafe_allow_html=True)
            elif mos > -20:
                st.markdown(f"""<div class='box-warn'>
                ⚠️ <b>Near Fair Value</b> — Stock is trading within 20% of intrinsic value.
                Current price is {abs(mos):.1f}% above estimated intrinsic value.
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class='box-danger'>
                🚨 <b>Overvalued by {abs(mos):.1f}%</b> — Stock is significantly above estimated intrinsic value.
                Downside risk: {abs(upside):.1f}%
                </div>""", unsafe_allow_html=True)

        st.markdown("""<div class='box-info' style='margin-top:1rem;'>
        ℹ️ <b>Disclaimer:</b> Graham Number = √(22.5 × EPS × Book Value Per Share).
        DCF uses Benjamin Graham's modified formula with Indian bond yield (~7.5%) as discount rate.
        These are estimates — always combine with qualitative research.
        </div>""", unsafe_allow_html=True)

        # Research Notes
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("<div class='sec-hdr'>📝 My Research Notes</div>", unsafe_allow_html=True)
        existing, last_upd = load_note(ticker)
        tmpl = f"""📌 STOCK: {ticker}
📅 Analysis Date: {datetime.date.today()}

🎯 INVESTMENT THESIS:

📊 KEY METRICS NOTED:
- PE: 
- ROE: 
- D/E: 
- FCF: 
- Piotroski: /9
- AI Score: /100
- Graham Value: ₹
- Current Price: ₹

⚠️ RISKS:

💡 SECTOR / MACRO INSIGHT:

🎯 TRADE PLAN:
- Entry: ₹     | Stop Loss: ₹     | Target: ₹
- Time Horizon:

✅ FINAL DECISION (BUY / HOLD / AVOID):
"""
        if st.button("📋 Load Template", key=f"tmpl2_{ticker}"):
            existing = tmpl
        note_txt = st.text_area("", value=existing, height=320, key=f"note2_{ticker}",
                                label_visibility="collapsed")
        c1,c2 = st.columns([3,1])
        with c1:
            if st.button("💾 Save Research Note", key=f"save2_{ticker}", use_container_width=True, type="primary"):
                save_note(ticker, note_txt)
                st.success(f"✅ Research note saved for {ticker}!")
        with c2:
            if last_upd:
                st.markdown(f"<div style='font-size:.76rem;color:#94a3b8;padding-top:.6rem;'>Last saved: {last_upd}</div>",
                            unsafe_allow_html=True)

    # ════════════════════ TAB 5 — AI VERDICT ════════════════════
    with t5:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f"""
            <div class='score-ring-wrap'>
              <div style='font-size:.75rem;font-weight:600;text-transform:uppercase;
                          letter-spacing:.07em;color:#6b7280;margin-bottom:.5rem;'>AI VERDICT SCORE</div>
              <div class='score-number' style='color:{ai_color};'>{ai_score}</div>
              <div style='font-size:.75rem;color:#94a3b8;font-family:"DM Mono",monospace;margin:.15rem 0;'>out of 100</div>
              {prog_bar(ai_score, ai_color)}
              <div class='score-label' style='color:{ai_color};'>{ai_grade}</div>
              <div style='margin-top:.75rem;font-size:.78rem;color:#64748b;text-align:center;'>
                Powered by 5 analytical pillars across<br>25+ financial data points
              </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='sec-hdr' style='margin-top:0;'>Score Breakdown by Pillar</div>", unsafe_allow_html=True)
            pillar_max = {"Valuation":20,"Profitability":20,"Financial Health":20,"Technical":20,"Growth & Momentum":20}
            colors_map = {"Valuation":"#2563eb","Profitability":"#059669","Financial Health":"#7c3aed",
                         "Technical":"#d97706","Growth & Momentum":"#0891b2"}
            for pillar, pts in ai_breakdown.items():
                max_pts = pillar_max.get(pillar,20)
                pct_pts = pts/max_pts*100
                pc = colors_map.get(pillar,"#6b7280")
                bc = "b-green" if pts>=15 else ("b-yellow" if pts>=10 else "b-red")
                st.markdown(f"""
                <div style='background:#fff;border:1px solid #e2e5ed;border-radius:10px;
                            padding:.75rem 1rem;margin-bottom:.5rem;'>
                  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:.3rem;'>
                    <div style='font-size:.85rem;font-weight:600;color:#0f172a;'>{pillar}</div>
                    <span class='badge {bc}'>{pts}/{max_pts}</span>
                  </div>
                  {prog_bar(pct_pts, pc)}
                </div>
                """, unsafe_allow_html=True)

        # Summary verdict card
        st.markdown("<div class='sec-hdr'>Investment Summary</div>", unsafe_allow_html=True)
        if ai_score >= 75:
            verdict_detail = f"""
            <b>{ticker}</b> scores <b>{ai_score}/100</b> — classified as <b>{ai_grade}</b>.
            Strong fundamentals with healthy ROE ({fp(m.get("roe"))}), manageable debt ({fn(m.get("de") and m.get("de")/100,2)}x D/E),
            and positive free cash flow. Piotroski F-Score of {pio_score}/9 confirms financial strength.
            Technical position is {"above" if (m.get("price") or 0) > (m.get("dma200") or 0) else "below"} the 200 DMA.
            {'Intrinsic value suggests ' + f'{iv.get("upside",0):+.1f}% potential upside.' if iv.get("avg") else ''}
            """
            st.markdown(f"<div class='box-success'>{verdict_detail}</div>", unsafe_allow_html=True)
        elif ai_score >= 45:
            verdict_detail = f"""
            <b>{ticker}</b> scores <b>{ai_score}/100</b> — classified as <b>{ai_grade}</b>.
            Mixed signals across pillars. Consider waiting for improvement in weaker areas
            before committing a large position. Piotroski F-Score: {pio_score}/9.
            Use strict stop-loss if entering.
            """
            st.markdown(f"<div class='box-warn'>{verdict_detail}</div>", unsafe_allow_html=True)
        else:
            verdict_detail = f"""
            <b>{ticker}</b> scores <b>{ai_score}/100</b> — classified as <b>{ai_grade}</b>.
            Multiple red flags detected across fundamental and technical pillars.
            Piotroski F-Score of {pio_score}/9 indicates financial weakness.
            High risk of capital loss. <b>Avoid unless you have strong conviction with strict risk management.</b>
            """
            st.markdown(f"<div class='box-danger'>{verdict_detail}</div>", unsafe_allow_html=True)

        st.markdown("""<div class='box-info' style='margin-top:.5rem;'>
        ⚠️ <b>Disclaimer:</b> This AI score is a quantitative research tool only. It does NOT constitute
        SEBI-registered investment advice. Always do your own research and consult a financial advisor
        before making investment decisions. Past performance does not guarantee future results.
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════
init_db()

with st.sidebar:
    st.markdown("""
    <div style='padding:.75rem 0 1.25rem;'>
      <div style='font-size:1.35rem;font-weight:700;color:#0f172a;'>📊 Stock Analysis Pro</div>
      <div style='font-size:.75rem;color:#94a3b8;margin-top:.15rem;'>Money Financial Services · v3.0</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Mode Toggle ──
    mode = st.radio("Mode", ["📈 Watchlist", "📁 Groups"], horizontal=True, label_visibility="collapsed")
    st.markdown("<hr style='border:none;border-top:1px solid #e2e5ed;margin:.75rem 0;'>", unsafe_allow_html=True)

    # ══════════ WATCHLIST MODE ══════════
    if mode == "📈 Watchlist":
        if "watchlist" not in st.session_state:
            st.session_state.watchlist = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]

        st.markdown("**🔍 Add Stock**")

        # Smart search
        sq = st.text_input("", placeholder="Search: SBI, Bajaj, Wipro…", key="wl_search",
                           label_visibility="collapsed")
        if sq and len(sq) >= 1:
            sql = sq.lower()
            matches = {}; seen = set()
            for name, ticker in STOCK_DB.items():
                if (sql in name.lower() or sql in ticker.lower()) and ticker not in seen:
                    seen.add(ticker); matches[name] = ticker

            if matches:
                for name, ticker in list(matches.items())[:6]:
                    already = ticker in st.session_state.watchlist
                    ca, cb  = st.columns([5,1])
                    with ca:
                        st.markdown(f"<div style='font-size:.78rem;padding:.1rem 0;'><b>{ticker}</b><br><span style='color:#94a3b8;font-size:.7rem;'>{name}</span></div>",
                                    unsafe_allow_html=True)
                    with cb:
                        if already:
                            st.markdown("<div style='padding-top:.35rem;font-size:.9rem;'>✅</div>", unsafe_allow_html=True)
                        elif st.button("＋", key=f"wladd_{ticker}"):
                            st.session_state.watchlist.append(ticker)
                            st.success(f"Added {ticker}!")
                            st.rerun()
            else:
                st.markdown("<div style='font-size:.78rem;color:#dc2626;'>Not found in database.</div>", unsafe_allow_html=True)

        with st.expander("✏️ Add by ticker manually"):
            mt = st.text_input("Ticker", placeholder="e.g. SBIN.NS", key="wl_manual", label_visibility="collapsed")
            if st.button("Add ＋", use_container_width=True, key="wl_manual_add"):
                t = mt.strip().upper()
                if t and t not in st.session_state.watchlist:
                    st.session_state.watchlist.append(t); st.success(f"Added {t}!"); st.rerun()
                elif t in st.session_state.watchlist:
                    st.warning(f"{t} already in watchlist.")

        st.markdown("<hr style='border:none;border-top:1px solid #e2e5ed;margin:.75rem 0;'>", unsafe_allow_html=True)
        st.markdown(f"**📌 Watchlist** ({len(st.session_state.watchlist)} stocks)")

        if not st.session_state.watchlist:
            st.markdown("<div style='font-size:.82rem;color:#94a3b8;'>No stocks yet. Search above to add.</div>", unsafe_allow_html=True)

        selected_wl = None
        for i, t in enumerate(st.session_state.watchlist):
            ca, cb = st.columns([5,1])
            with ca:
                is_sel = st.session_state.get("wl_selected") == t
                btn_style = "primary" if is_sel else "secondary"
                if st.button(f"{'▶ ' if is_sel else ''}{t}", key=f"wlsel_{t}", use_container_width=True):
                    st.session_state.wl_selected = t
                    st.rerun()
            with cb:
                if st.button("✕", key=f"wldel_{i}", help=f"Remove {t}"):
                    st.session_state.watchlist.pop(i)
                    if st.session_state.get("wl_selected") == t:
                        st.session_state.wl_selected = None
                    st.success(f"Removed {t}")
                    st.rerun()

    # ══════════ GROUPS MODE ══════════
    else:
        groups = get_groups()

        # Create group
        with st.expander("➕ Create New Group"):
            ng = st.text_input("", placeholder="e.g. Banking Sector", key="ng_name", label_visibility="collapsed")
            if st.button("Create Group", use_container_width=True, key="create_grp_btn"):
                if ng.strip():
                    if ng.strip() in groups:
                        st.warning(f"'{ng}' already exists.")
                    else:
                        create_group(ng.strip())
                        st.success(f"✅ Group '{ng}' created!")
                        st.rerun()

        groups = get_groups()
        if not groups:
            st.markdown("<div class='box-warn'>No groups yet. Create one above!</div>", unsafe_allow_html=True)
        else:
            # Rename / Delete
            with st.expander("⚙️ Manage Groups"):
                sel_manage = st.selectbox("Group", groups, key="manage_grp")
                new_name   = st.text_input("Rename to", key="rename_val", placeholder="New name…")
                c1,c2 = st.columns(2)
                with c1:
                    if st.button("Rename", use_container_width=True, key="rename_btn"):
                        if new_name.strip():
                            rename_group(sel_manage, new_name.strip())
                            st.success("Renamed!"); st.rerun()
                with c2:
                    if st.button("🗑️ Delete", use_container_width=True, key="del_grp_btn", type="primary"):
                        delete_group(sel_manage)
                        st.success(f"'{sel_manage}' deleted!"); st.rerun()

            # Add stock to group
            with st.expander("📌 Add Stock to Group"):
                tg = st.selectbox("Select Group", groups, key="add_to_grp")
                sq2 = st.text_input("", placeholder="Search stock…", key="grp_sq", label_visibility="collapsed")
                if sq2:
                    sq2l = sq2.lower(); m2 = {}; s2 = set()
                    for name,ticker in STOCK_DB.items():
                        if (sq2l in name.lower() or sq2l in ticker.lower()) and ticker not in s2:
                            s2.add(ticker); m2[name]=ticker
                    for name,ticker in list(m2.items())[:5]:
                        ca2,cb2 = st.columns([5,1])
                        with ca2:
                            st.markdown(f"<div style='font-size:.76rem;'><b>{ticker}</b><br><span style='color:#94a3b8;font-size:.68rem;'>{name}</span></div>",
                                        unsafe_allow_html=True)
                        with cb2:
                            if st.button("＋", key=f"gadd_{ticker}_{tg}"):
                                add_ticker(tg, ticker); st.success(f"Added {ticker} to {tg}!"); st.rerun()
                mt2 = st.text_input("Manual ticker", placeholder="SBIN.NS", key="grp_mt", label_visibility="collapsed")
                if st.button("Add manually", use_container_width=True, key="grp_mt_btn"):
                    if mt2.strip():
                        add_ticker(tg, mt2.strip().upper()); st.success(f"Added!"); st.rerun()

            st.markdown("<hr style='border:none;border-top:1px solid #e2e5ed;margin:.75rem 0;'>", unsafe_allow_html=True)
            st.markdown("**Select Group to Analyse:**")
            sel_grp = st.selectbox("", groups, key="sel_grp_analyse", label_visibility="collapsed")

            if sel_grp:
                gtickers = get_tickers(sel_grp)
                st.markdown(f"<div style='font-size:.78rem;color:#94a3b8;margin-bottom:.4rem;'>{len(gtickers)} stocks in {sel_grp}</div>",
                            unsafe_allow_html=True)

                if gtickers:
                    st.markdown("**Click stock to analyse:**")
                    for t in gtickers:
                        ca3,cb3 = st.columns([5,1])
                        with ca3:
                            is_sel = st.session_state.get("grp_selected_ticker") == t and st.session_state.get("grp_selected_group") == sel_grp
                            if st.button(f"{'▶ ' if is_sel else ''}{t}", key=f"grpsel_{sel_grp}_{t}", use_container_width=True):
                                st.session_state.grp_selected_ticker = t
                                st.session_state.grp_selected_group  = sel_grp
                                st.rerun()
                        with cb3:
                            if st.button("✕", key=f"grprm_{sel_grp}_{t}"):
                                remove_ticker(sel_grp, t)
                                if st.session_state.get("grp_selected_ticker") == t:
                                    st.session_state.grp_selected_ticker = None
                                st.success(f"Removed {t}"); st.rerun()
                else:
                    st.markdown("<div style='font-size:.8rem;color:#94a3b8;'>No stocks yet. Add above.</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border:none;border-top:1px solid #e2e5ed;margin:.75rem 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:.72rem;color:#94a3b8;line-height:1.6;'>
    <b>Ticker Format:</b><br>
    NSE → NAME.NS (e.g. SBIN.NS)<br>
    BSE → NAME.BO (e.g. SBIN.BO)<br>
    US  → Plain (e.g. AAPL, MSFT)
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# MAIN CONTENT AREA
# ══════════════════════════════════════════════════════

if mode == "📈 Watchlist":
    sel = st.session_state.get("wl_selected")
    if not sel:
        # Landing page
        st.markdown("""
        <div style='text-align:center;padding:4rem 2rem;'>
          <div style='font-size:3rem;margin-bottom:1rem;'>📊</div>
          <div style='font-size:1.5rem;font-weight:700;color:#0f172a;margin-bottom:.5rem;'>Stock Analysis Pro v3.0</div>
          <div style='font-size:.95rem;color:#64748b;max-width:500px;margin:0 auto 2rem;line-height:1.7;'>
            Click any stock in your watchlist (sidebar) to see its full
            Fundamental, Technical, Piotroski, Intrinsic Value & AI Verdict analysis.
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Quick ticker tiles
        if st.session_state.get("watchlist"):
            st.markdown("<div class='sec-hdr'>Your Watchlist — Click to Analyse</div>", unsafe_allow_html=True)
            cols = st.columns(min(len(st.session_state.watchlist), 4))
            for i, t in enumerate(st.session_state.watchlist):
                with cols[i % 4]:
                    if st.button(f"📌 {t}", use_container_width=True, key=f"main_wl_{t}"):
                        st.session_state.wl_selected = t
                        st.rerun()
    else:
        st.markdown(f"## 📈 {sel}")
        render_analysis(sel)

else:  # Groups mode
    sel_grp    = st.session_state.get("sel_grp_analyse") or (get_groups()[0] if get_groups() else None)
    sel_ticker = st.session_state.get("grp_selected_ticker")
    sel_grp_t  = st.session_state.get("grp_selected_group")

    if not get_groups():
        st.markdown("""
        <div style='text-align:center;padding:4rem 2rem;'>
          <div style='font-size:3rem;margin-bottom:1rem;'>📁</div>
          <div style='font-size:1.5rem;font-weight:700;color:#0f172a;margin-bottom:.5rem;'>No Groups Yet</div>
          <div style='font-size:.95rem;color:#64748b;'>Create a group from the sidebar, then add stocks to it.</div>
        </div>
        """, unsafe_allow_html=True)
    elif sel_ticker and sel_grp_t:
        # Full analysis for selected stock in group
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:.75rem;margin-bottom:1.25rem;'>
          <span style='font-size:.82rem;color:#94a3b8;'><a href='#' style='color:#94a3b8;text-decoration:none;'>📁 {sel_grp_t}</a> ›</span>
          <span style='font-size:.82rem;font-weight:600;color:#0f172a;'>📌 {sel_ticker}</span>
        </div>
        """, unsafe_allow_html=True)
        render_analysis(sel_ticker)
    else:
        # Group overview — show all stocks as clickable tiles with quick data
        if sel_grp:
            gtickers = get_tickers(sel_grp)
            st.markdown(f"## 📁 {sel_grp}")
            if not gtickers:
                st.markdown("<div class='box-warn'>No stocks in this group yet. Add stocks from the sidebar.</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='font-size:.85rem;color:#64748b;margin-bottom:1rem;'>{len(gtickers)} stocks · Click any stock for full analysis</div>",
                            unsafe_allow_html=True)

                # Show tile grid with quick scores
                cols = st.columns(min(len(gtickers), 4))
                for i, t in enumerate(gtickers):
                    with cols[i % 4]:
                        with st.spinner(f"{t}…"):
                            qdata  = fetch_all(t)
                            qm     = smart_get(qdata)
                            qpio,_ = calc_piotroski(qdata)
                            qiv    = calc_intrinsic_value(qm)
                            qs,_,qg,qc = calc_ai_score(qm, qpio, qiv)

                        qprice = qm.get("price") or qm.get("curr_price_hist")
                        bc2 = "b-green" if qs>=75 else ("b-yellow" if qs>=45 else "b-red")
                        st.markdown(f"""
                        <div class='card' style='text-align:center;'>
                          <div style='font-size:.72rem;font-weight:700;text-transform:uppercase;
                                      color:#94a3b8;letter-spacing:.05em;'>{t}</div>
                          <div style='font-size:.8rem;color:#475569;margin:.15rem 0 .5rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>
                            {(qm.get("name") or t)[:20]}
                          </div>
                          <div style='font-size:2rem;font-weight:800;color:{qc};font-family:"DM Mono",monospace;'>{qs}</div>
                          <div style='font-size:.7rem;color:#94a3b8;margin:.1rem 0 .4rem;'>AI Score / 100</div>
                          <span class='badge {bc2}' style='font-size:.7rem;'>{qg.split("—")[0].strip()}</span>
                          <div style='font-size:.8rem;color:#475569;margin-top:.5rem;'>
                            ₹{f"{qprice:,.1f}" if qprice else "N/A"}
                          </div>
                          <div style='font-size:.72rem;color:#94a3b8;'>Piotroski: {qpio}/9</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"🔍 Analyse", key=f"gt_{sel_grp}_{t}", use_container_width=True):
                            st.session_state.grp_selected_ticker = t
                            st.session_state.grp_selected_group  = sel_grp
                            st.rerun()

# ── Footer ──────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;font-size:.74rem;color:#94a3b8;padding:.5rem 0 1.5rem;'>
  📊 <b>Stock Analysis Pro v3.0</b> · Money Financial Services ·
  Data via Yahoo Finance · Piotroski F-Score + Graham/DCF Intrinsic Value + AI Verdict ·
  <br>For research & educational purposes only · Not SEBI registered investment advice
</div>
""", unsafe_allow_html=True)
