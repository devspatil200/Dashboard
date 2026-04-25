"""
Stock Analysis Pro — v4.3
Author : Money Financial Services
UI     : Pure Native Streamlit — No broken HTML — TradingView-style
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3, datetime, math

# ── PAGE CONFIG ────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Analysis Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── MINIMAL CLEAN CSS ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: #ffffff !important;
}
.stApp { background: #ffffff !important; }
section[data-testid="stSidebar"] { display: none !important; }
button[data-testid="collapsedControl"] { display: none !important; }
.stApp > header { display: none !important; }
#MainMenu, footer { display: none !important; }
.block-container { padding: 1rem 1.5rem 4rem !important; max-width: 100% !important; }

/* Watchlist row separator */
.wl-divider { border: none; border-top: 1px solid #f0f0f0; margin: 0; }

/* Stock ticker bold */
.ticker-bold { font-weight: 700; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; color: #0f172a; }
.ticker-name { font-size: 0.68rem; color: #94a3b8; margin-top: 1px; }
.price-val   { font-weight: 600; font-size: 0.82rem; font-family: 'JetBrains Mono', monospace; text-align: right; }
.chg-green   { color: #16a34a; font-weight: 700; font-size: 0.75rem; text-align: right; }
.chg-red     { color: #dc2626; font-weight: 700; font-size: 0.75rem; text-align: right; }

/* Section header */
.sec-hdr { font-size: 0.8rem; font-weight: 700; color: #0f172a; border-left: 2px solid #2563eb; padding-left: 8px; margin: 1.25rem 0 0.6rem; }

/* Metric mini card */
.mini-card { background: #fafafa; border: 1px solid #e4e4e7; border-radius: 8px; padding: 0.75rem 0.9rem; }
.mini-label { font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: #71717a; margin-bottom: 3px; }
.mini-val   { font-size: 1.25rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; line-height: 1.1; }
.mini-sub   { font-size: 0.65rem; color: #a1a1aa; margin-top: 2px; }

/* Stock header */
.stock-hdr { background: #fff; border: 1px solid #e4e4e7; border-radius: 10px; padding: 0.9rem 1.1rem; margin-bottom: 0.9rem; }

/* Alert overrides */
div[data-testid="stAlert"] { border-radius: 8px !important; font-size: 0.82rem !important; }

/* Button overrides */
[data-testid="stButton"] > button {
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    padding: 0.3rem 0.75rem !important;
}

/* Tab font */
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div { border-radius: 6px !important; font-size: 0.8rem !important; }

/* Input */
[data-testid="stTextInput"] input {
    border-radius: 6px !important;
    font-size: 0.8rem !important;
    padding: 0.35rem 0.65rem !important;
}

/* Progress bar */
.stProgress > div > div { border-radius: 999px !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 8px !important; overflow: hidden; }

/* Plotly chart */
.js-plotly-plot { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════
STOCK_DB = {
    "Reliance Industries": "RELIANCE.NS", "TCS": "TCS.NS",
    "Infosys": "INFY.NS", "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS", "Kotak Bank": "KOTAKBANK.NS",
    "Axis Bank": "AXISBANK.NS", "SBI": "SBIN.NS",
    "Bajaj Finance": "BAJFINANCE.NS", "Bajaj Finserv": "BAJAJFINSV.NS",
    "Wipro": "WIPRO.NS", "HCL Tech": "HCLTECH.NS",
    "Tech Mahindra": "TECHM.NS", "L&T": "LT.NS", "ITC": "ITC.NS",
    "HUL": "HINDUNILVR.NS", "Nestle India": "NESTLEIND.NS",
    "Asian Paints": "ASIANPAINT.NS", "Maruti Suzuki": "MARUTI.NS",
    "Tata Motors": "TATAMOTORS.NS", "Mahindra M&M": "M&M.NS",
    "Sun Pharma": "SUNPHARMA.NS", "Dr Reddys": "DRREDDY.NS",
    "Cipla": "CIPLA.NS", "Divis Lab": "DIVISLAB.NS",
    "Apollo Hospitals": "APOLLOHOSP.NS", "ONGC": "ONGC.NS",
    "Power Grid": "POWERGRID.NS", "NTPC": "NTPC.NS",
    "Coal India": "COALINDIA.NS", "Titan": "TITAN.NS",
    "Tata Steel": "TATASTEEL.NS", "JSW Steel": "JSWSTEEL.NS",
    "Hindalco": "HINDALCO.NS", "UltraTech Cement": "ULTRACEMCO.NS",
    "Adani Ports": "ADANIPORTS.NS", "Adani Enterprises": "ADANIENT.NS",
    "Shriram Finance": "SHRIRAMFIN.NS", "Muthoot Finance": "MUTHOOTFIN.NS",
    "IDFC First Bank": "IDFCFIRSTB.NS", "IndusInd Bank": "INDUSINDBK.NS",
    "Bank of Baroda": "BANKBARODA.NS", "PNB": "PNB.NS",
    "Canara Bank": "CANBK.NS", "Federal Bank": "FEDERALBNK.NS",
    "Yes Bank": "YESBANK.NS", "Paytm": "PAYTM.NS",
    "Zomato": "ZOMATO.NS", "Nykaa": "NYKAA.NS",
    "Tata Power": "TATAPOWER.NS", "Tata Consumer": "TATACONSUM.NS",
    "Godrej Consumer": "GODREJCP.NS", "Pidilite": "PIDILITIND.NS",
    "Berger Paints": "BERGEPAINT.NS", "Dabur": "DABUR.NS",
    "Marico": "MARICO.NS", "Britannia": "BRITANNIA.NS",
    "Havells": "HAVELLS.NS", "Dixon Tech": "DIXON.NS",
    "Hero MotoCorp": "HEROMOTOCO.NS", "Bajaj Auto": "BAJAJ-AUTO.NS",
    "Eicher Motors": "EICHERMOT.NS", "Ashok Leyland": "ASHOKLEY.NS",
    "IndiGo": "INDIGO.NS", "Lupin": "LUPIN.NS",
    "Biocon": "BIOCON.NS", "Torrent Pharma": "TORNTPHARM.NS",
    "Aurobindo Pharma": "AUROPHARMA.NS", "Mankind Pharma": "MANKIND.NS",
    "DLF": "DLF.NS", "Lodha": "LODHA.NS", "Varun Beverages": "VBL.NS",
    "Mphasis": "MPHASIS.NS", "LTIMindtree": "LTIM.NS",
    "Persistent Systems": "PERSISTENT.NS", "Coforge": "COFORGE.NS",
    "BSE": "BSE.NS", "MCX": "MCX.NS", "Angel One": "ANGELONE.NS",
    "CDSL": "CDSL.NS", "Polycab": "POLYCAB.NS",
    "Siemens India": "SIEMENS.NS", "ABB India": "ABB.NS",
    "BEL": "BEL.NS", "HAL": "HAL.NS", "IRCTC": "IRCTC.NS",
    "IRFC": "IRFC.NS", "RVNL": "RVNL.NS",
    "Max Healthcare": "MAXHEALTH.NS", "NHPC": "NHPC.NS",
    "Torrent Power": "TORNTPOWER.NS", "Grasim": "GRASIM.NS",
}

DEFAULT_GROUPS = {
    "Watchlist": ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","SBIN.NS"],
    "Banking":   ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS"],
    "IT Sector": ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Pharma":    ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","DIVISLAB.NS"],
}

# ══════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════
DB = "stock_v43.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS grp_tickers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grp TEXT NOT NULL, ticker TEXT NOT NULL, added_at TEXT,
        UNIQUE(grp, ticker))""")
    c.execute("""CREATE TABLE IF NOT EXISTS notes (
        ticker TEXT PRIMARY KEY, content TEXT, updated_at TEXT)""")
    conn.commit()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    for grp, tickers in DEFAULT_GROUPS.items():
        for t in tickers:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO grp_tickers (grp,ticker,added_at) VALUES (?,?,?)",
                    (grp, t, now))
            except Exception:
                pass
    conn.commit()
    conn.close()

def dbq(sql, p=()):
    conn = sqlite3.connect(DB)
    rows = conn.execute(sql, p).fetchall()
    conn.close()
    return rows

def dbx(sql, p=()):
    conn = sqlite3.connect(DB)
    conn.execute(sql, p)
    conn.commit()
    conn.close()

def get_groups():
    return [r[0] for r in dbq("SELECT DISTINCT grp FROM grp_tickers ORDER BY grp")]

def get_tickers(grp):
    return [r[0] for r in dbq(
        "SELECT ticker FROM grp_tickers WHERE grp=? AND ticker!='__init__' ORDER BY added_at",
        (grp,))]

def add_ticker(grp, ticker):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    dbx("INSERT OR IGNORE INTO grp_tickers (grp,ticker,added_at) VALUES (?,?,?)",
        (grp, ticker.upper().strip(), now))

def del_ticker(grp, ticker):
    dbx("DELETE FROM grp_tickers WHERE grp=? AND ticker=?", (grp, ticker))

def del_group(name):
    dbx("DELETE FROM grp_tickers WHERE grp=?", (name,))

def save_note(ticker, content):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    dbx("INSERT OR REPLACE INTO notes VALUES (?,?,?)", (ticker.upper(), content, now))

def load_note(ticker):
    rows = dbq("SELECT content,updated_at FROM notes WHERE ticker=?", (ticker.upper(),))
    return (rows[0][0], rows[0][1]) if rows else ("", "")

# ══════════════════════════════════════════════════════════
# DATA FETCHERS  (cache_resource = Python 3.14 compatible)
# ══════════════════════════════════════════════════════════
@st.cache_resource
def _price_cache():
    return {}

@st.cache_resource
def _data_cache():
    return {}

def fetch_price(ticker):
    cache = _price_cache()
    key = f"{ticker}_{datetime.datetime.now().strftime('%Y%m%d%H%M') // 2}"
    if key in cache:
        return cache[key]
    try:
        info = yf.Ticker(ticker).info or {}
        result = {
            "price":   info.get("regularMarketPrice") or info.get("currentPrice"),
            "prev":    info.get("regularMarketPreviousClose"),
            "name":    info.get("shortName") or info.get("longName") or ticker,
            "website": info.get("website", ""),
        }
    except Exception:
        result = {"price": None, "prev": None, "name": ticker, "website": ""}
    cache[key] = result
    return result

def fetch_full(ticker):
    """Full data fetch with global error protection."""
    try:
        stk  = yf.Ticker(ticker)
        info = stk.info or {}
        hist = stk.history(period="1y")
        try:    fin = stk.financials
        except: fin = pd.DataFrame()
        try:    bs  = stk.balance_sheet
        except: bs  = pd.DataFrame()
        try:    cf  = stk.cashflow
        except: cf  = pd.DataFrame()
        try:    mh  = stk.major_holders
        except: mh  = pd.DataFrame()
        try:    ih  = stk.institutional_holders
        except: ih  = pd.DataFrame()
        return {"ok": True, "info": info, "hist": hist,
                "fin": fin, "bs": bs, "cf": cf,
                "major_holders": mh, "inst_holders": ih}
    except Exception as e:
        return {"ok": False, "error": str(e), "info": {}, "hist": pd.DataFrame(),
                "fin": pd.DataFrame(), "bs": pd.DataFrame(), "cf": pd.DataFrame(),
                "major_holders": pd.DataFrame(), "inst_holders": pd.DataFrame()}

# ══════════════════════════════════════════════════════════
# SAFE HELPERS
# ══════════════════════════════════════════════════════════
def _v(d, *keys, default=None):
    for k in keys:
        try:
            val = d.get(k) if isinstance(d, dict) else None
            if val is not None and not (isinstance(val, float) and math.isnan(val)):
                return val
        except Exception:
            pass
    return default

def _row(df, *names):
    try:
        if df is None or df.empty:
            return None
        for name in names:
            for idx in df.index:
                if name.lower() in str(idx).lower():
                    s = df.loc[idx].dropna()
                    if not s.empty:
                        return s
    except Exception:
        pass
    return None

def _latest(s):
    try:
        if s is None:
            return None
        s2 = s.dropna()
        return float(s2.iloc[0]) if not s2.empty else None
    except Exception:
        return None

def sdiv(a, b, default=None):
    try:
        if b is None or b == 0:
            return default
        return a / b
    except Exception:
        return default

def fc(v):
    if v is None: return "N/A"
    try:
        v = float(v)
        if abs(v) >= 1e12: return f"₹{v/1e12:.2f}T"
        if abs(v) >= 1e7:  return f"₹{v/1e7:.2f}Cr"
        if abs(v) >= 1e5:  return f"₹{v/1e5:.2f}L"
        return f"₹{v:,.0f}"
    except: return "N/A"

def fp(v, d=1):
    if v is None: return "N/A"
    try: return f"{float(v)*100:.{d}f}%"
    except: return "N/A"

def fn(v, d=2):
    if v is None: return "N/A"
    try: return f"{float(v):,.{d}f}"
    except: return "N/A"

def logo_url(website):
    try:
        if not website: return None
        domain = website.replace("https://","").replace("http://","").split("/")[0]
        return f"https://logo.clearbit.com/{domain}" if domain else None
    except: return None

# ══════════════════════════════════════════════════════════
# METRICS BUILDER
# ══════════════════════════════════════════════════════════
def build_metrics(data):
    info, fin, bs, cf, hist = (
        data["info"], data["fin"], data["bs"], data["cf"], data["hist"])
    m = {}

    # Identity
    m["name"]     = _v(info, "longName", "shortName", default=None)
    m["sector"]   = _v(info, "sector",   default="—")
    m["industry"] = _v(info, "industry", default="—")
    m["exchange"] = _v(info, "exchange", default="—")
    m["currency"] = _v(info, "currency", default="INR")
    m["website"]  = _v(info, "website",  default="")
    m["price"]    = _v(info, "regularMarketPrice", "currentPrice")
    m["prev"]     = _v(info, "regularMarketPreviousClose")
    m["mktcap"]   = _v(info, "marketCap")
    m["beta"]     = _v(info, "beta")
    m["target"]   = _v(info, "targetMeanPrice")

    # Valuation
    m["pe"]  = _v(info, "trailingPE")
    m["fpe"] = _v(info, "forwardPE")
    m["pb"]  = _v(info, "priceToBook")
    m["ps"]  = _v(info, "priceToSalesTrailing12Months")
    m["peg"] = _v(info, "pegRatio")

    # Profitability
    m["roe"] = _v(info, "returnOnEquity")
    m["roa"] = _v(info, "returnOnAssets")
    m["pm"]  = _v(info, "profitMargins")
    m["gm"]  = _v(info, "grossMargins")
    m["om"]  = _v(info, "operatingMargins")

    # Debt & Liquidity
    m["de"]  = _v(info, "debtToEquity")
    m["cr"]  = _v(info, "currentRatio")
    m["qr"]  = _v(info, "quickRatio")
    m["fcf"] = _v(info, "freeCashflow")
    m["ocf"] = _v(info, "operatingCashflow")

    # Growth
    m["rg"]   = _v(info, "revenueGrowth")
    m["eg"]   = _v(info, "earningsGrowth")
    m["eps"]  = _v(info, "trailingEps")
    m["feps"] = _v(info, "forwardEps")
    m["dy"]   = _v(info, "dividendYield")

    # ── Fallbacks ──
    if m["roe"] is None:
        ni = _latest(_row(fin, "Net Income"))
        eq = _latest(_row(bs, "Stockholders Equity", "Total Stockholder Equity"))
        m["roe"] = sdiv(ni, abs(eq)) if ni and eq else None

    if m["roa"] is None:
        ni = _latest(_row(fin, "Net Income"))
        ta = _latest(_row(bs, "Total Assets"))
        m["roa"] = sdiv(ni, abs(ta)) if ni and ta else None

    if m["pm"] is None:
        ni  = _latest(_row(fin, "Net Income"))
        rev = _latest(_row(fin, "Total Revenue"))
        m["pm"] = sdiv(ni, abs(rev)) if ni and rev else None

    if m["de"] is None:
        td = _latest(_row(bs, "Total Debt", "Long Term Debt"))
        eq = _latest(_row(bs, "Stockholders Equity", "Total Stockholder Equity"))
        if td is not None and eq:
            v = sdiv(td, abs(eq))
            m["de"] = v * 100 if v is not None else None

    if m["fcf"] is None:
        ocf  = _latest(_row(cf, "Operating Cash Flow", "Cash From Operations"))
        capx = _latest(_row(cf, "Capital Expenditure",
                            "Purchases Of Property Plant And Equipment"))
        if ocf is not None:
            m["ocf"] = ocf
            m["fcf"] = ocf + (capx if capx else 0)

    # ── Technicals ──
    if not hist.empty:
        try:
            close = hist["Close"]
            m["ph"]   = float(close.iloc[-1])
            m["vol"]  = float(hist["Volume"].iloc[-1])
            m["v20"]  = float(hist["Volume"].rolling(20).mean().iloc[-1]) if len(hist) >= 20 else None
            m["d50"]  = float(close.rolling(50).mean().iloc[-1])  if len(close) >= 50  else None
            m["d200"] = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None
            m["h52"]  = float(close.rolling(252).max().iloc[-1])  if len(close) >= 252 else float(close.max())
            m["l52"]  = float(close.rolling(252).min().iloc[-1])  if len(close) >= 252 else float(close.min())

            # RSI
            delta = close.diff()
            gain  = delta.clip(lower=0).rolling(14).mean()
            loss  = (-delta.clip(upper=0)).rolling(14).mean()
            rs    = gain / loss.replace(0, float("nan"))
            rsi   = 100 - (100 / (1 + rs))
            m["rsi"] = float(rsi.iloc[-1]) if not rsi.empty else None

            # MACD
            e12 = close.ewm(span=12).mean(); e26 = close.ewm(span=26).mean()
            macd = e12 - e26; sig = macd.ewm(span=9).mean()
            m["macd"] = float(macd.iloc[-1])
            m["msig"] = float(sig.iloc[-1])
            m["mh"]   = float((macd - sig).iloc[-1])

            # Volatility
            m["vol_pct"] = float(close.pct_change().rolling(20).std().iloc[-1] * 100) \
                           if len(close) >= 20 else None

            # VPA — Institutional Buying
            if m["v20"] and m["v20"] > 0:
                mask = (hist["Close"] > hist["Close"].shift(1)) & \
                       (hist["Volume"] > 2 * hist["Volume"].rolling(20).mean())
                m["vpa_dates"] = list(hist.index[mask])
            else:
                m["vpa_dates"] = []

        except Exception:
            for k in ["ph","vol","v20","d50","d200","h52","l52",
                      "rsi","macd","msig","mh","vol_pct","vpa_dates"]:
                m[k] = None
    else:
        for k in ["ph","vol","v20","d50","d200","h52","l52",
                  "rsi","macd","msig","mh","vol_pct","vpa_dates"]:
            m[k] = None

    return m

# ══════════════════════════════════════════════════════════
# PIOTROSKI F-SCORE  (0–9)
# ══════════════════════════════════════════════════════════
def calc_piotroski(data):
    info, fin, bs, cf = data["info"], data["fin"], data["bs"], data["cf"]
    C = []

    def _l(df, *n):  return _latest(_row(df, *n))
    def _lp(df, *n):
        r = _row(df, *n)
        if r is None or len(r.dropna()) < 2: return None
        return float(r.dropna().iloc[1])

    ni_c  = _l(fin, "Net Income");    ni_p  = _lp(fin, "Net Income")
    rev_c = _l(fin, "Total Revenue"); rev_p = _lp(fin, "Total Revenue")
    ta_c  = _l(bs,  "Total Assets");  ta_p  = _lp(bs,  "Total Assets")
    ocf   = _l(cf, "Operating Cash Flow", "Cash From Operations")
    roa   = _v(info, "returnOnAssets")
    if roa is None and ni_c and ta_c and ta_c != 0:
        roa = sdiv(ni_c, ta_c)

    def A(g, n, p, note): C.append({"g": g, "n": n, "p": p, "note": note})

    A("P","F1 — ROA Positive",
      roa is not None and roa > 0, f"ROA={roa*100:.1f}%" if roa else "N/A")
    A("P","F2 — OCF Positive",
      ocf is not None and ocf > 0, f"OCF=₹{ocf/1e7:.1f}Cr" if ocf else "N/A")
    if roa is not None and ta_p and ni_p and ta_p != 0:
        rp = sdiv(ni_p, ta_p, 0)
        A("P","F3 — ROA Improving", roa > rp,
          f"Curr {roa*100:.1f}% vs Prev {rp*100:.1f}%")
    else:
        A("P","F3 — ROA Improving", False, "Insufficient data")

    if ocf and ta_c and ta_c != 0 and roa is not None:
        A("P","F4 — Cash > Paper", sdiv(ocf, ta_c, 0) > roa,
          f"OCF/TA={sdiv(ocf,ta_c,0)*100:.1f}% vs ROA={roa*100:.1f}%")
    else:
        A("P","F4 — Cash > Paper", False, "N/A")

    ltd_r = _row(bs, "Long Term Debt")
    if ltd_r is not None and len(ltd_r.dropna()) >= 2 and ta_c and ta_p:
        lv = ltd_r.dropna()
        rc = sdiv(float(lv.iloc[0]), ta_c, 0)
        rp = sdiv(float(lv.iloc[1]), ta_p, 0)
        A("L","F5 — Debt Decreasing", rc < rp,
          f"Curr {rc*100:.1f}% vs Prev {rp*100:.1f}%")
    else:
        A("L","F5 — Debt Decreasing", False, "N/A")

    ca_r = _row(bs, "Current Assets"); cl_r = _row(bs, "Current Liabilities")
    if ca_r is not None and cl_r is not None and len(ca_r.dropna()) >= 2:
        cav = ca_r.dropna(); clv = cl_r.dropna()
        cc  = sdiv(float(cav.iloc[0]), float(clv.iloc[0]))
        cp  = sdiv(float(cav.iloc[1]), float(clv.iloc[1]))
        A("L","F6 — CR Improving", bool(cc and cp and cc > cp),
          f"Curr {cc:.2f} vs Prev {cp:.2f}" if cc and cp else "N/A")
    else:
        cr_i = _v(info, "currentRatio")
        A("L","F6 — CR > 1.5",
          cr_i is not None and cr_i > 1.5,
          f"CR={cr_i:.2f}" if cr_i else "N/A")

    sh_r = _row(bs, "Ordinary Shares Number", "Common Stock Shares Outstanding")
    if sh_r is not None and len(sh_r.dropna()) >= 2:
        sv = sh_r.dropna()
        A("L","F7 — No Dilution", float(sv.iloc[0]) <= float(sv.iloc[1]),
          f"Curr {float(sv.iloc[0])/1e7:.2f}Cr vs Prev {float(sv.iloc[1])/1e7:.2f}Cr")
    else:
        A("L","F7 — No Dilution", False, "N/A")

    gp_r = _row(fin, "Gross Profit")
    if gp_r is not None and len(gp_r.dropna()) >= 2 and rev_c and rev_p:
        gv = gp_r.dropna()
        gmc = sdiv(float(gv.iloc[0]), rev_c, 0)
        gmp = sdiv(float(gv.iloc[1]), rev_p, 0)
        A("E","F8 — GM Improving", gmc > gmp,
          f"Curr {gmc*100:.1f}% vs Prev {gmp*100:.1f}%")
    else:
        gm_i = _v(info, "grossMargins")
        A("E","F8 — GM > 20%",
          gm_i is not None and gm_i > 0.20,
          f"GM={gm_i*100:.1f}%" if gm_i else "N/A")

    if rev_c and rev_p and ta_c and ta_p:
        A("E","F9 — AT Improving",
          sdiv(rev_c, ta_c, 0) > sdiv(rev_p, ta_p, 0),
          f"Curr {sdiv(rev_c,ta_c,0):.2f}x vs Prev {sdiv(rev_p,ta_p,0):.2f}x")
    else:
        A("E","F9 — AT Improving", False, "Insufficient data")

    return sum(1 for c in C if c["p"]), C

# ══════════════════════════════════════════════════════════
# INTRINSIC VALUE
# ══════════════════════════════════════════════════════════
def calc_iv(m):
    r = {}
    eps   = m.get("eps")
    pb    = m.get("pb")
    price = m.get("price") or m.get("ph")
    bvps  = sdiv(price, pb) if (pb and pb > 0 and price) else None

    r["graham"] = math.sqrt(22.5 * eps * bvps) \
                  if (eps and eps > 0 and bvps and bvps > 0) else None

    g = m.get("eg") or m.get("rg")
    if eps and eps > 0 and g is not None:
        g2 = max(-20, min(50, g * 100))
        dcf = eps * (8.5 + 2 * g2) * 4.4 / 7.5
        r["dcf"] = dcf if dcf > 0 else None
    else:
        r["dcf"] = None

    target = m.get("target")
    r["analyst_up"]     = sdiv(target - price, price, 0) * 100 if target and price else None
    r["analyst_target"] = target

    valid = [v for v in [r.get("graham"), r.get("dcf")] if v]
    if valid and price:
        avg      = sum(valid) / len(valid)
        r["avg"] = avg
        r["mos"] = sdiv(avg - price, avg, 0) * 100
        r["up"]  = sdiv(avg - price, price, 0) * 100
    else:
        r["avg"] = r["mos"] = r["up"] = None
    return r

# ══════════════════════════════════════════════════════════
# AI SCORE  (0–100)
# ══════════════════════════════════════════════════════════
def calc_ai(m, pio, iv):
    bd = {}
    price = m.get("price") or m.get("ph") or 0

    v = 0
    pe = m.get("pe")
    if pe: v += 10 if pe < 15 else (7 if pe < 25 else (4 if pe < 40 else 0))
    pb = m.get("pb")
    if pb: v += 10 if pb < 1.5 else (7 if pb < 3 else (3 if pb < 5 else 0))
    bd["Valuation"] = min(v, 20)

    p = 0
    roe = m.get("roe"); pm = m.get("pm"); fcf = m.get("fcf")
    if roe: p += 8 if roe > 0.25 else (5 if roe > 0.15 else (2 if roe > 0 else 0))
    if pm:  p += 7 if pm  > 0.20 else (4 if pm  > 0.10 else (1 if pm  > 0 else 0))
    if fcf and fcf > 0: p += 5
    bd["Profitability"] = min(p, 20)

    h = 0
    de = m.get("de"); cr = m.get("cr")
    if de is not None:
        dr = de / 100
        h += 8 if dr < 0.3 else (5 if dr < 0.7 else (2 if dr < 1 else 0))
    if cr: h += 7 if cr > 2 else (4 if cr > 1.5 else (1 if cr > 1 else 0))
    h += min(pio, 5)
    bd["Fin. Health"] = min(h, 20)

    t = 0
    d200 = m.get("d200"); d50 = m.get("d50"); rsi = m.get("rsi")
    if price and d200:
        pct = sdiv(price - d200, d200, 0) * 100
        t += 8 if 0 < pct < 20 else (4 if pct >= 20 else (3 if pct > -10 else 0))
    if price and d50 and price > d50: t += 5
    if rsi:
        t += 7 if 40 <= rsi <= 65 else (4 if (30 <= rsi < 40 or 65 < rsi <= 70) else (2 if rsi < 30 else 0))
    bd["Technical"] = min(t, 20)

    g = 0
    rg = m.get("rg"); eg = m.get("eg"); up = iv.get("up")
    if rg: g += 7 if rg > 0.20 else (4 if rg > 0.10 else (1 if rg > 0 else 0))
    if eg: g += 7 if eg > 0.20 else (4 if eg > 0.10 else (1 if eg > 0 else 0))
    if up: g += 6 if up > 30 else (3 if up > 10 else (1 if up > 0 else 0))
    bd["Growth"] = min(g, 20)

    total = sum(bd.values())
    if total >= 75:   grade, col = "Excellent — Strong Buy", "#16a34a"
    elif total >= 60: grade, col = "Good — Buy",            "#2563eb"
    elif total >= 45: grade, col = "Average — Watch",       "#d97706"
    elif total >= 30: grade, col = "Weak — Caution",        "#ea580c"
    else:             grade, col = "Poor — Avoid",          "#dc2626"
    return total, bd, grade, col

# ══════════════════════════════════════════════════════════
# CHARTS  (Plotly — plotly_white template)
# ══════════════════════════════════════════════════════════
def make_candle(hist, d50, d200, vpa_dates=None):
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        if hist.empty: return None
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            vertical_spacing=0.03, row_heights=[0.75, 0.25])
        fig.add_trace(go.Candlestick(
            x=hist.index, open=hist["Open"], high=hist["High"],
            low=hist["Low"], close=hist["Close"], name="Price",
            increasing_line_color="#16a34a", decreasing_line_color="#dc2626",
            increasing_fillcolor="#16a34a", decreasing_fillcolor="#dc2626",
        ), row=1, col=1)
        if d50:
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"].rolling(50).mean(),
                name="50 DMA", line=dict(color="#2563eb", width=1.5)), row=1, col=1)
        if d200:
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"].rolling(200).mean(),
                name="200 DMA", line=dict(color="#d97706", width=1.5, dash="dot")),
                row=1, col=1)
        if vpa_dates:
            vd = [d for d in vpa_dates if d in hist.index]
            vp = [hist.loc[d, "High"] * 1.01 for d in vd]
            if vd:
                fig.add_trace(go.Scatter(
                    x=vd, y=vp, mode="markers", name="🏦 Inst.Buy",
                    marker=dict(symbol="triangle-up", size=10, color="#7c3aed",
                                line=dict(color="#fff", width=1.5))), row=1, col=1)
        colors = ["#16a34a" if c >= o else "#dc2626"
                  for c, o in zip(hist["Close"], hist["Open"])]
        fig.add_trace(go.Bar(
            x=hist.index, y=hist["Volume"], name="Volume",
            marker_color=colors, opacity=0.5, showlegend=False), row=2, col=1)
        fig.update_layout(
            height=430, margin=dict(l=0, r=0, t=16, b=0),
            paper_bgcolor="#fff", plot_bgcolor="#fff",
            template="plotly_white",
            font=dict(family="Inter", size=11, color="#3f3f46"),
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.01,
                        xanchor="right", x=1, bgcolor="rgba(0,0,0,0)",
                        font=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor="#f4f4f5", side="right",
                       zeroline=False, tickfont=dict(size=10)),
            yaxis2=dict(showgrid=False, side="right", zeroline=False,
                        tickfont=dict(size=9)),
            xaxis2=dict(showgrid=True, gridcolor="#f4f4f5", tickfont=dict(size=10)),
        )
        return fig
    except Exception:
        return None

def make_gauge(score, grade, color):
    try:
        import plotly.graph_objects as go
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=score,
            number={"font": {"size": 34, "family": "JetBrains Mono", "color": color}},
            gauge=dict(
                axis=dict(range=[0, 100], tickfont=dict(size=9, color="#71717a"), nticks=6),
                bar=dict(color=color, thickness=0.25),
                bgcolor="white", borderwidth=0,
                steps=[dict(range=[0,  30], color="#fef2f2"),
                       dict(range=[30, 45], color="#fff7ed"),
                       dict(range=[45, 60], color="#fffbeb"),
                       dict(range=[60, 75], color="#eff6ff"),
                       dict(range=[75,100], color="#f0fdf4")],
                threshold=dict(line=dict(color=color, width=3),
                               thickness=0.75, value=score)),
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": grade, "font": {"size": 10, "family": "Inter", "color": "#3f3f46"}}))
        fig.update_layout(
            height=195, margin=dict(l=10, r=10, t=25, b=0),
            paper_bgcolor="#fff", template="plotly_white",
            font=dict(family="Inter"))
        return fig
    except Exception:
        return None

# ══════════════════════════════════════════════════════════
# GOOGLE TRENDS  (safe — won't crash app)
# ══════════════════════════════════════════════════════════
def get_trends(keyword):
    """Returns (df_or_None, error_str_or_None)"""
    try:
        from pytrends.request import TrendReq
        kw = keyword.replace(".NS","").replace(".BO","")
        pt = TrendReq(hl="en-IN", tz=330, timeout=(10, 25))
        pt.build_payload([kw], cat=0, timeframe="today 1-m", geo="IN")
        df = pt.interest_over_time()
        if df.empty or kw not in df.columns:
            return None, "Trends data not available for this ticker"
        return df[[kw]], None
    except ImportError:
        return None, "pytrends not installed — add to requirements.txt"
    except Exception:
        return None, "Trends data not available for this ticker"

# ══════════════════════════════════════════════════════════
# MINI METRIC CARD  (native Streamlit + styled HTML)
# ══════════════════════════════════════════════════════════
def metric_card(label, value, sub="", color="#0f172a"):
    st.markdown(
        f"<div class='mini-card'>"
        f"<div class='mini-label'>{label}</div>"
        f"<div class='mini-val' style='color:{color};'>{value}</div>"
        + (f"<div class='mini-sub'>{sub}</div>" if sub else "")
        + "</div>",
        unsafe_allow_html=True)

def sec(title):
    st.markdown(f"<div class='sec-hdr'>{title}</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# WATCHLIST ROW  (native st.columns — no HTML rendering issues)
# ══════════════════════════════════════════════════════════
def render_watchlist_row(ticker, grp, is_selected):
    pd_data = fetch_price(ticker)
    p  = pd_data["price"]
    pr = pd_data["prev"]
    nm = pd_data["name"]
    ws = pd_data.get("website","")

    # Price / Change
    if p and pr and pr > 0:
        chg_pct = (p - pr) / pr * 100
        chg_str = f"{'▲' if chg_pct >= 0 else '▼'}{abs(chg_pct):.2f}%"
        p_str   = f"{p:,.2f}"
        is_up   = chg_pct >= 0
    else:
        chg_str = "—"; p_str = f"{p:,.2f}" if p else "—"; is_up = None

    # Cols: logo | ticker+name | price | change | delete
    c0, c1, c2, c3, c4 = st.columns([0.5, 3, 1.2, 1.2, 0.5])

    # Logo
    lurl = logo_url(ws)
    tabbr = ticker.replace(".NS","").replace(".BO","")[:2].upper()
    with c0:
        if lurl:
            st.markdown(
                f'<img src="{lurl}" width="26" height="26" '
                f'style="border-radius:5px;object-fit:contain;border:1px solid #e4e4e7;'
                f'margin-top:4px;" onerror="this.style.display=\'none\'">',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div style="width:26px;height:26px;border-radius:5px;'
                f'background:#e4e4e7;display:flex;align-items:center;justify-content:center;'
                f'font-size:0.6rem;font-weight:700;color:#71717a;margin-top:4px;">'
                f'{tabbr}</div>',
                unsafe_allow_html=True)

    # Ticker + Name
    with c1:
        label = f"**{'▶ ' if is_selected else ''}{ticker.replace('.NS','').replace('.BO','')}**"
        if st.button(label, key=f"sel_{ticker}_{grp}",
                     use_container_width=True,
                     type="primary" if is_selected else "secondary"):
            st.session_state.selected_stock = ticker
            st.rerun()
        st.caption(nm[:28] if nm else ticker)

    # Price
    with c2:
        st.markdown(
            f"<div style='text-align:right;padding-top:6px;'>"
            f"<div style='font-size:0.82rem;font-weight:600;font-family:JetBrains Mono,monospace;color:#0f172a;'>{p_str}</div>"
            f"</div>",
            unsafe_allow_html=True)

    # Change
    with c3:
        chg_color = "#16a34a" if is_up else ("#dc2626" if is_up is False else "#71717a")
        chg_bg    = "#f0fdf4" if is_up else ("#fef2f2" if is_up is False else "#fafafa")
        st.markdown(
            f"<div style='text-align:right;padding-top:8px;'>"
            f"<span style='font-size:0.75rem;font-weight:700;color:{chg_color};"
            f"background:{chg_bg};padding:2px 6px;border-radius:4px;'>{chg_str}</span>"
            f"</div>",
            unsafe_allow_html=True)

    # Delete button
    with c4:
        if st.button("🗑️", key=f"del_{ticker}_{grp}", help=f"Remove {ticker}"):
            del_ticker(grp, ticker)
            if st.session_state.get("selected_stock") == ticker:
                st.session_state.selected_stock = None
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid #f0f0f0;margin:2px 0;'>",
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# FULL ANALYSIS  (right panel)
# ══════════════════════════════════════════════════════════
def render_analysis(ticker):
    with st.spinner(f"Loading {ticker}…"):
        data = fetch_full(ticker)

    if not data["ok"]:
        st.error(f"Failed to fetch data for **{ticker}**: {data.get('error','Unknown error')}")
        return

    m       = build_metrics(data)
    price   = m.get("price") or m.get("ph")
    hist    = data.get("hist", pd.DataFrame())

    if not price:
        st.warning(f"Price data unavailable for **{ticker}**. Verify ticker symbol.")
        return

    pio_s, pio_c = calc_piotroski(data)
    iv           = calc_iv(m)
    total, bd, grade, color = calc_ai(m, pio_s, iv)

    prev    = m.get("prev")
    chg     = price - prev if prev else 0
    chg_pct = sdiv(chg, prev, 0) * 100
    chg_col = "#16a34a" if chg >= 0 else "#dc2626"
    arr     = "▲" if chg >= 0 else "▼"
    curr    = m.get("currency","INR")
    lurl    = logo_url(m.get("website",""))

    # ── Stock Header ──
    h1, h2 = st.columns([3, 2])
    with h1:
        logo_html = ""
        if lurl:
            logo_html = (f'<img src="{lurl}" width="36" height="36" '
                         f'style="border-radius:7px;object-fit:contain;'
                         f'border:1px solid #e4e4e7;margin-right:8px;vertical-align:middle;" '
                         f'onerror="this.style.display=\'none\'">')
        st.markdown(
            f"{logo_html}"
            f"<span style='font-size:1.25rem;font-weight:800;color:#0f172a;vertical-align:middle;'>"
            f"{m.get('name') or ticker}</span>",
            unsafe_allow_html=True)
        st.caption(f"{ticker} · {m.get('exchange','—')} · {m.get('sector','—')} · {m.get('industry','—')}")
    with h2:
        st.markdown(
            f"<div style='text-align:right;'>"
            f"<div style='font-size:1.7rem;font-weight:800;font-family:JetBrains Mono,monospace;color:#0f172a;line-height:1;'>"
            f"{curr} {price:,.2f}</div>"
            f"<div style='font-size:0.85rem;font-weight:600;color:{chg_col};margin-top:3px;'>"
            f"{arr} {abs(chg):,.2f} ({chg_pct:+.2f}%)</div>"
            f"<div style='font-size:0.68rem;color:#a1a1aa;margin-top:2px;'>"
            f"Cap: {fc(m.get('mktcap'))} · Beta: {fn(m.get('beta'))} · Target: {fn(m.get('target'))}</div>"
            f"</div>",
            unsafe_allow_html=True)

    st.markdown("---")

    T1,T2,T3,T4,T5,T6 = st.tabs([
        "📋 Fundamentals","📡 Technicals","📈 Trends",
        "🏦 Holders","🏆 Piotroski + IV","🤖 AI Verdict"])

    # ── TAB 1: FUNDAMENTALS ──
    with T1:
        sec("Valuation")
        pe_v = m.get("pe")
        pe_c = ("#16a34a" if pe_v and pe_v < 25 else
                "#d97706" if pe_v and pe_v < 40 else "#dc2626") if pe_v else "#71717a"
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: metric_card("Trailing PE", fn(m.get("pe"),1), "< 25 ideal", pe_c)
        with c2: metric_card("Forward PE",  fn(m.get("fpe"),1),"Estimated")
        with c3: metric_card("Price/Book",  fn(m.get("pb"),2), "< 3 ideal")
        with c4: metric_card("Price/Sales", fn(m.get("ps"),2), "Revenue mult.")
        with c5: metric_card("PEG",         fn(m.get("peg"),2),"< 1 cheap")

        sec("Profitability")
        roe_v = m.get("roe"); pm_v = m.get("pm")
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: metric_card("ROE", fp(roe_v), "> 15%",
                             "#16a34a" if roe_v and roe_v>0.15 else "#dc2626" if roe_v else "#71717a")
        with c2: metric_card("ROA", fp(m.get("roa")), "Asset return")
        with c3: metric_card("Net Margin", fp(pm_v), "> 10%",
                             "#16a34a" if pm_v and pm_v>0.10 else "#dc2626" if pm_v else "#71717a")
        with c4: metric_card("Gross Margin", fp(m.get("gm")), "Quality")
        with c5: metric_card("Oper. Margin", fp(m.get("om")), "Efficiency")

        sec("Balance Sheet & Cash Flow")
        de_v = m.get("de"); cr_v = m.get("cr"); fcf_v = m.get("fcf")
        de_r = de_v/100 if de_v is not None else None
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: metric_card("Debt/Equity",
                             f"{de_r:.2f}x" if de_r is not None else "N/A", "< 1x",
                             "#16a34a" if de_r is not None and de_r<1 else "#dc2626" if de_r is not None else "#71717a")
        with c2: metric_card("Current Ratio", fn(cr_v,2), "> 1.5",
                             "#16a34a" if cr_v and cr_v>1.5 else "#dc2626" if cr_v else "#71717a")
        with c3: metric_card("Quick Ratio",   fn(m.get("qr"),2), "Acid test")
        with c4: metric_card("Free CF",  fc(fcf_v), "Positive=healthy",
                             "#16a34a" if fcf_v and fcf_v>0 else "#dc2626" if fcf_v else "#71717a")
        with c5: metric_card("Oper. CF", fc(m.get("ocf")), "Generated")

        sec("Growth & EPS")
        rg_v = m.get("rg"); eg_v = m.get("eg")
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: metric_card("Revenue Growth", fp(rg_v), "YoY",
                             "#16a34a" if rg_v and rg_v>0 else "#dc2626" if rg_v else "#71717a")
        with c2: metric_card("Earnings Growth", fp(eg_v), "YoY",
                             "#16a34a" if eg_v and eg_v>0 else "#dc2626" if eg_v else "#71717a")
        with c3: metric_card("Trailing EPS",  fn(m.get("eps"),2),  "Per share")
        with c4: metric_card("Forward EPS",   fn(m.get("feps"),2), "Estimated")
        with c5: metric_card("Dividend Yield", fp(m.get("dy"),2),  "Annual")

        desc = _v(data["info"], "longBusinessSummary", default="")
        if desc:
            with st.expander("📖 About the Company"):
                st.markdown(f"<p style='font-size:0.84rem;line-height:1.8;color:#3f3f46;'>"
                            f"{desc[:1200]}{'…' if len(desc)>1200 else ''}</p>",
                            unsafe_allow_html=True)

    # ── TAB 2: TECHNICALS ──
    with T2:
        sec("Candlestick Chart — 1 Year")
        fig_c = make_candle(hist, m.get("d50"), m.get("d200"), m.get("vpa_dates") or [])
        if fig_c:
            st.plotly_chart(fig_c, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Chart data not available.")

        vpa_d = m.get("vpa_dates") or []
        if vpa_d:
            st.success(f"🏦 **Institutional Buying Detected** — {len(vpa_d)} signal(s). "
                       f"Price↑ + Volume > 2× 20-day average. "
                       f"Last: **{str(vpa_d[-1])[:10]}**")
        else:
            st.info("ℹ️ No institutional buying signals detected in last 1 year.")

        sec("Key Levels")
        ph = m.get("ph") or price
        c1,c2,c3,c4 = st.columns(4)
        with c1: metric_card("Price", f"₹{ph:,.2f}", "Current")
        with c2:
            d50 = m.get("d50")
            if d50:
                p50 = sdiv(ph-d50, d50, 0)*100
                metric_card("50 DMA", f"₹{d50:,.2f}", f"{p50:+.1f}%",
                            "#16a34a" if ph>d50 else "#dc2626")
            else: metric_card("50 DMA","N/A","—")
        with c3:
            d200 = m.get("d200")
            if d200:
                p200 = sdiv(ph-d200, d200, 0)*100
                metric_card("200 DMA", f"₹{d200:,.2f}", f"{p200:+.1f}%",
                            "#16a34a" if ph>d200 else "#dc2626")
            else: metric_card("200 DMA","N/A","—")
        with c4:
            rsi_v = m.get("rsi")
            if rsi_v:
                rl = "Overbought ⚠️" if rsi_v>70 else ("Oversold 🔎" if rsi_v<30 else "Neutral ✅")
                rc = "#dc2626" if rsi_v>70 else ("#d97706" if rsi_v<30 else "#16a34a")
                metric_card("RSI (14)", f"{rsi_v:.1f}", rl, rc)
            else: metric_card("RSI","N/A","—")

        h52 = m.get("h52"); l52 = m.get("l52")
        if h52 and l52 and h52 != l52:
            sec("52-Week Range")
            pos = sdiv(ph-l52, h52-l52, 0)*100
            pfh = sdiv(ph-h52, h52, 0)*100
            st.markdown(
                f"<div style='background:#fafafa;border:1px solid #e4e4e7;border-radius:8px;"
                f"padding:0.75rem 1rem;margin-bottom:0.5rem;'>"
                f"<div style='display:flex;justify-content:space-between;margin-bottom:6px;'>"
                f"<span style='font-size:0.7rem;color:#71717a;'>52W Low ₹{l52:,.0f}</span>"
                f"<span style='font-size:0.78rem;font-weight:700;'>📍 ₹{ph:,.1f} ({pos:.0f}th%ile)</span>"
                f"<span style='font-size:0.7rem;color:#71717a;'>52W High ₹{h52:,.0f}</span>"
                f"</div>"
                f"<div style='background:#e4e4e7;border-radius:999px;height:5px;width:100%;'>"
                f"<div style='width:{pos:.1f}%;height:5px;border-radius:999px;"
                f"background:linear-gradient(90deg,#dc2626 0%,#f59e0b 50%,#16a34a 100%);'>"
                f"</div></div></div>",
                unsafe_allow_html=True)
            st.caption(f"From 52W High: {pfh:+.1f}%")

        sec("Volume Analysis")
        cv = m.get("vol"); v20 = m.get("v20")
        c1,c2,c3,c4 = st.columns(4)
        with c1: metric_card("Today Volume", f"{cv:,.0f}" if cv else "N/A","Shares")
        with c2: metric_card("20D Avg Vol",  f"{v20:,.0f}" if v20 else "N/A","Rolling avg")
        with c3:
            if cv and v20 and v20>0:
                vr = cv/v20
                vc2 = "#16a34a" if vr>1.5 else ("#dc2626" if vr<0.5 else "#d97706")
                vl  = "📈 Spike" if vr>1.5 else ("📉 Dry" if vr<0.5 else "➡️ Normal")
                metric_card("Vol Ratio", f"{vr:.2f}×", vl, vc2)
            else: metric_card("Vol Ratio","N/A","—")
        with c4:
            mh_v = m.get("mh")
            if mh_v:
                metric_card("MACD Hist", f"{mh_v:.2f}",
                           "Bullish 🟢" if mh_v>0 else "Bearish 🔴",
                           "#16a34a" if mh_v>0 else "#dc2626")
            else: metric_card("MACD","N/A","—")

    # ── TAB 3: TRENDS ──
    with T3:
        sec("Google Trends — India Search Interest (30 Days)")
        kw = ticker.replace(".NS","").replace(".BO","")
        with st.spinner("Fetching trends…"):
            tdf, terr = get_trends(kw)

        if terr:
            st.warning(f"⚠️ {terr}")
        elif tdf is not None and not tdf.empty:
            try:
                import plotly.graph_objects as go
                half  = len(tdf) // 2
                f1    = tdf[kw].iloc[:half].mean()
                f2    = tdf[kw].iloc[half:].mean()
                growth = sdiv(f2-f1, f1, 0)*100
                vol_pct = m.get("vol_pct") or 999

                fig_t = go.Figure()
                fig_t.add_trace(go.Scatter(
                    x=tdf.index, y=tdf[kw],
                    line=dict(color="#7c3aed", width=2),
                    fill="tozeroy", fillcolor="rgba(124,58,237,0.08)"))
                fig_t.update_layout(
                    height=180, margin=dict(l=0,r=0,t=10,b=0),
                    paper_bgcolor="#fff", plot_bgcolor="#fff",
                    template="plotly_white", showlegend=False,
                    yaxis=dict(range=[0,105], gridcolor="#f4f4f5", tickfont=dict(size=10)),
                    xaxis=dict(gridcolor="#f4f4f5", tickfont=dict(size=10)))
                st.plotly_chart(fig_t, use_container_width=True,
                                config={"displayModeBar": False})

                c1,c2,c3 = st.columns(3)
                with c1: metric_card("Current Interest", f"{tdf[kw].iloc[-1]:.0f}/100","Google scale")
                with c2: metric_card("30-Day Growth", f"{growth:+.1f}%","Search trend",
                                    "#16a34a" if growth>15 else "#71717a")
                with c3: metric_card("Volatility (20D)", f"{vol_pct:.1f}%" if vol_pct!=999 else "N/A",
                                    "Price std dev",
                                    "#16a34a" if vol_pct<5 else "#d97706")

                # Accumulation Zone ONLY if both conditions met
                if growth > 15 and vol_pct < 5:
                    st.markdown(
                        f"<div style='background:linear-gradient(135deg,#fefce8,#fef9c3);"
                        f"border:2px solid #f59e0b;border-radius:10px;"
                        f"padding:1rem 1.25rem;margin:.75rem 0;text-align:center;'>"
                        f"<div style='font-size:1.4rem;'>🚨</div>"
                        f"<div style='font-size:1rem;font-weight:800;color:#92400e;margin:.2rem 0;'>"
                        f"ACCUMULATION ZONE DETECTED</div>"
                        f"<div style='font-size:0.82rem;color:#78350f;line-height:1.6;'>"
                        f"Search interest ↑<b>{growth:+.1f}%</b> · "
                        f"Price volatility only <b>{vol_pct:.1f}%</b><br>"
                        f"Quiet accumulation — institutions may be buying before breakout."
                        f"</div></div>",
                        unsafe_allow_html=True)
                elif growth > 15:
                    st.success(f"📈 Rising interest ({growth:+.1f}%) — Watch for breakout confirmation.")
                elif growth < -15:
                    st.warning(f"📉 Declining interest ({growth:+.1f}%) — Caution.")
                else:
                    st.info("ℹ️ Stable interest — No extreme signals.")
            except Exception as e:
                st.warning(f"Could not render trends chart: {e}")
        else:
            st.warning("⚠️ Trends data not available for this ticker.")

    # ── TAB 4: HOLDERS ──
    with T4:
        sec("Major Holders")
        mh_df = data.get("major_holders", pd.DataFrame())
        if mh_df is not None and not mh_df.empty:
            try:
                st.dataframe(mh_df, use_container_width=True, hide_index=True)
            except Exception:
                st.warning("Could not display major holders.")
        else:
            st.info("Major holders data not available.")

        sec("Institutional Holders (Top 10)")
        ih_df = data.get("inst_holders", pd.DataFrame())
        if ih_df is not None and not ih_df.empty:
            try:
                d = ih_df.head(10).copy()
                if "Value" in d.columns:
                    d["Value"] = d["Value"].apply(
                        lambda x: f"₹{x/1e7:.1f}Cr"
                        if isinstance(x,(int,float)) and not math.isnan(float(x)) else "N/A")
                if "% Out" in d.columns:
                    d["% Out"] = d["% Out"].apply(
                        lambda x: f"{float(x)*100:.2f}%" if isinstance(x,(int,float)) else str(x))
                st.dataframe(d, use_container_width=True, hide_index=True)
                st.info("🟢 Increasing institutional holding = positive signal. "
                        "Track quarterly changes for conviction.")
            except Exception:
                st.warning("Could not display institutional holders.")
        else:
            st.info("Institutional holders data not available.")

    # ── TAB 5: PIOTROSKI + IV ──
    with T5:
        pc = "#16a34a" if pio_s>=7 else ("#d97706" if pio_s>=5 else "#dc2626")
        pt = "Strong 💪" if pio_s>=7 else ("Moderate" if pio_s>=5 else "Weak ⚠️")
        badge_txt = "High Conviction ⭐" if pio_s >= 7 else pt

        ca, cb = st.columns([1, 2])
        with ca:
            st.markdown(
                f"<div style='background:#fafafa;border:1px solid #e4e4e7;border-radius:10px;"
                f"text-align:center;padding:1.75rem 1rem;'>"
                f"<div style='font-size:0.62rem;font-weight:700;text-transform:uppercase;"
                f"letter-spacing:0.07em;color:#71717a;margin-bottom:4px;'>PIOTROSKI F-SCORE</div>"
                f"<div style='font-size:5rem;font-weight:800;color:{pc};line-height:1;"
                f"font-family:JetBrains Mono,monospace;'>{pio_s}</div>"
                f"<div style='font-size:0.72rem;color:#71717a;margin:3px 0 8px;'>out of 9</div>"
                f"<div style='background:#e4e4e7;border-radius:999px;height:5px;width:100%;'>"
                f"<div style='width:{pio_s/9*100:.0f}%;height:5px;border-radius:999px;"
                f"background:{pc};'></div></div>"
                f"<div style='margin-top:10px;font-size:0.76rem;font-weight:700;"
                f"color:{pc};'>{badge_txt}</div>"
                f"</div>",
                unsafe_allow_html=True)

        with cb:
            sec("F-Score Breakdown")
            g_names = {"P": "Profitability", "L": "Leverage", "E": "Efficiency"}
            grps_p = {}
            for c in pio_c: grps_p.setdefault(c["g"], []).append(c)
            for grp_k, items in grps_p.items():
                gs = sum(1 for x in items if x["p"])
                st.markdown(f"<div style='font-size:0.64rem;font-weight:700;text-transform:uppercase;"
                            f"letter-spacing:0.05em;color:#a1a1aa;margin:10px 0 4px;'>"
                            f"{g_names.get(grp_k,grp_k)} ({gs}/{len(items)})</div>",
                            unsafe_allow_html=True)
                for item in items:
                    ic = "✅" if item["p"] else "❌"
                    bg = "#f0fdf4" if item["p"] else "#fef2f2"
                    tc = "#15803d" if item["p"] else "#b91c1c"
                    st.markdown(
                        f"<div style='background:{bg};border-radius:6px;"
                        f"padding:5px 10px;margin-bottom:3px;display:flex;gap:8px;align-items:flex-start;'>"
                        f"<span style='font-size:0.85rem;'>{ic}</span>"
                        f"<div><div style='font-size:0.76rem;font-weight:600;color:{tc};'>{item['n']}</div>"
                        f"<div style='font-size:0.66rem;color:#71717a;'>{item['note']}</div></div>"
                        f"</div>",
                        unsafe_allow_html=True)

        st.divider()
        sec("Intrinsic Value")
        curr_p = m.get("price") or m.get("ph")
        c1,c2,c3,c4 = st.columns(4)
        gv = iv.get("graham"); dv = iv.get("dcf")
        avg_iv = iv.get("avg"); up_v = iv.get("up"); mos_v = iv.get("mos")
        with c1:
            if gv and curr_p:
                diff = sdiv(curr_p-gv, gv, 0)*100
                metric_card("Graham Number", f"₹{gv:,.1f}",
                           f"{'Under' if curr_p<gv else 'Over'}valued {abs(diff):.1f}%",
                           "#16a34a" if curr_p<gv else "#dc2626")
            else: metric_card("Graham Number","N/A","EPS/BVPS N/A")
        with c2:
            if dv and curr_p:
                diff2 = sdiv(curr_p-dv, dv, 0)*100
                metric_card("Graham DCF", f"₹{dv:,.1f}",
                           f"{'Under' if curr_p<dv else 'Over'}valued {abs(diff2):.1f}%",
                           "#16a34a" if curr_p<dv else "#dc2626")
            else: metric_card("Graham DCF","N/A","EPS/Growth N/A")
        with c3:
            if avg_iv and curr_p:
                metric_card("Blended IV", f"₹{avg_iv:,.1f}",
                           f"{'↑' if up_v and up_v>0 else '↓'} {abs(up_v):.1f}% | MOS: {mos_v:.1f}%",
                           "#16a34a" if up_v and up_v>0 else "#dc2626")
            else: metric_card("Blended IV","N/A","Insufficient data")
        with c4:
            at = iv.get("analyst_target"); au = iv.get("analyst_up")
            if at and au is not None:
                metric_card("Analyst Target", f"₹{at:,.1f}",
                           f"Upside: {au:+.1f}%",
                           "#16a34a" if au>0 else "#dc2626")
            else: metric_card("Analyst Target","N/A","Not available")

        if avg_iv and curr_p:
            if mos_v > 20:    st.success(f"✅ **MOS: {mos_v:.1f}%** — Significantly undervalued. Upside: {up_v:.1f}%")
            elif mos_v > 0:   st.success(f"✅ Marginally undervalued. MOS: {mos_v:.1f}%")
            elif mos_v > -20: st.warning(f"⚠️ Near fair value. Overvalued by {abs(mos_v):.1f}%.")
            else:             st.error(f"🚨 Overvalued {abs(mos_v):.1f}%. Downside: {abs(up_v):.1f}%.")

        st.divider()
        sec("📝 Research Notes")
        existing, last_upd = load_note(ticker)
        if st.button("📋 Load Template", key=f"tmpl_{ticker}"):
            existing = (f"📌 {ticker}  |  📅 {datetime.date.today()}\n\n"
                       f"🎯 THESIS:\n\n📊 METRICS:\n- PE:\n- ROE:\n- D/E:\n- FCF:\n"
                       f"- Piotroski: /9\n- AI Score: /100\n- IV: ₹\n\n"
                       f"⚠️ RISKS:\n\n🎯 TRADE:\n- Entry: ₹  Stop: ₹  Target: ₹\n\n✅ DECISION:")
        note_txt = st.text_area("", value=existing, height=260,
                                key=f"note_{ticker}", label_visibility="collapsed")
        c1x, c2x = st.columns([3,1])
        with c1x:
            if st.button("💾 Save Note", key=f"save_{ticker}",
                         use_container_width=True, type="primary"):
                save_note(ticker, note_txt)
                st.success("✅ Note saved!")
        with c2x:
            if last_upd:
                st.caption(f"Saved: {last_upd}")

    # ── TAB 6: AI VERDICT ──
    with T6:
        ca, cb = st.columns([1,2])
        with ca:
            fig_g = make_gauge(total, grade, color)
            if fig_g:
                st.plotly_chart(fig_g, use_container_width=True,
                                config={"displayModeBar": False})
        with cb:
            sec("Score by Pillar")
            pc_map = {"Valuation":"#2563eb","Profitability":"#16a34a",
                      "Fin. Health":"#7c3aed","Technical":"#d97706","Growth":"#0891b2"}
            for pillar, pts in bd.items():
                pc2 = pc_map.get(pillar,"#71717a")
                bc_txt = "🟢" if pts>=15 else ("🟡" if pts>=10 else "🔴")
                st.markdown(
                    f"<div style='background:#fafafa;border:1px solid #e4e4e7;"
                    f"border-radius:6px;padding:0.55rem 0.85rem;margin-bottom:0.3rem;'>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;'>"
                    f"<div style='font-size:0.78rem;font-weight:600;'>{pillar}</div>"
                    f"<div style='font-size:0.72rem;font-weight:700;color:{pc2};'>{bc_txt} {pts}/20</div>"
                    f"</div>"
                    f"<div style='background:#e4e4e7;border-radius:999px;height:4px;width:100%;'>"
                    f"<div style='width:{pts/20*100:.0f}%;height:4px;border-radius:999px;background:{pc2};'>"
                    f"</div></div></div>",
                    unsafe_allow_html=True)

        sec("Investment Summary")
        ab = "above" if price > (m.get("d200") or 0) else "below"
        roe_str = fp(m.get("roe"))
        de_str  = f"{sdiv(m.get('de'),100,0):.2f}x" if m.get("de") else "N/A"
        if total >= 75:
            st.success(f"**{ticker}** → **{total}/100 — {grade}**. "
                       f"ROE {roe_str}, D/E {de_str}. "
                       f"Piotroski {pio_s}/9. Trading {ab} 200 DMA."
                       + (f" IV upside: {iv.get('up'):.1f}%." if iv.get('up') else ""))
        elif total >= 45:
            st.warning(f"**{ticker}** → **{total}/100 — {grade}**. "
                       f"Mixed signals. Piotroski {pio_s}/9. Use strict stop-loss.")
        else:
            st.error(f"**{ticker}** → **{total}/100 — {grade}**. "
                     f"Multiple red flags. Piotroski {pio_s}/9. High risk.")
        st.info("⚠️ Research tool only — Not SEBI registered investment advice.")

# ══════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════
init_db()

# Session defaults
for k, v in [("selected_stock", None), ("sel_grp", "Watchlist")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── TOP NAV BAR ──
c_nav1, c_nav2 = st.columns([3,2])
with c_nav1:
    st.markdown(
        "<div style='font-size:1rem;font-weight:800;color:#0f172a;padding:0.5rem 0 0.25rem;'>"
        "📈 Stock Analysis Pro "
        "<span style='font-size:0.6rem;font-weight:700;background:#2563eb;color:#fff;"
        "padding:2px 6px;border-radius:3px;vertical-align:middle;'>v4.3</span>"
        "</div>",
        unsafe_allow_html=True)
    st.caption("Money Financial Services · TradingView UI · VPA · Google Trends · Piotroski · AI Score")
with c_nav2:
    st.markdown("") # spacer

st.markdown("---")

# ── TWO COLUMN LAYOUT ──
left, right = st.columns([1, 3], gap="medium")

# ══ LEFT PANEL ══════════════════════════════════════════════
with left:
    groups = get_groups()
    if not groups:
        groups = ["Watchlist"]
    if st.session_state.sel_grp not in groups:
        st.session_state.sel_grp = groups[0]

    # Group selector
    sel_grp = st.selectbox(
        "📁 Select Group", groups,
        index=groups.index(st.session_state.sel_grp),
        key="grp_sel", label_visibility="visible")
    if sel_grp != st.session_state.sel_grp:
        st.session_state.sel_grp  = sel_grp
        st.session_state.selected_stock = None
        st.rerun()

    # Group management
    with st.expander("⚙️ Manage Groups"):
        ng = st.text_input("New group name", placeholder="e.g. Swing Trades",
                           key="ng", label_visibility="visible")
        if st.button("➕ Create Group", use_container_width=True, key="cg"):
            if ng.strip() and ng.strip() not in groups:
                add_ticker(ng.strip(), "__init__")
                st.session_state.sel_grp = ng.strip()
                st.rerun()
        if st.button(f"🗑️ Delete '{sel_grp}'", use_container_width=True,
                     key="del_g", type="secondary"):
            del_group(sel_grp)
            st.session_state.sel_grp = groups[0] if len(groups) > 1 else "Watchlist"
            st.session_state.selected_stock = None
            st.rerun()

    # Add stock
    with st.expander("🔍 Add Stock to Group"):
        sq = st.text_input("Search company / ticker",
                           placeholder="HDFC, Wipro, SBIN.NS…",
                           key="sq", label_visibility="collapsed")
        tickers_now = get_tickers(sel_grp)
        if sq:
            ql   = sq.lower()
            hits = {}; seen = set()
            for name, t in STOCK_DB.items():
                if (ql in name.lower() or ql in t.lower()) and t not in seen:
                    seen.add(t); hits[name] = t
            if hits:
                for name, t in list(hits.items())[:6]:
                    ca2, cb2 = st.columns([5,1])
                    with ca2:
                        st.markdown(
                            f"<div style='font-size:0.72rem;padding:2px 0;'>"
                            f"<b>{t}</b> <span style='color:#94a3b8;font-size:0.62rem;'>{name}</span></div>",
                            unsafe_allow_html=True)
                    with cb2:
                        if t in tickers_now:
                            st.markdown("✅")
                        elif st.button("＋", key=f"add_{t}_{sel_grp}"):
                            add_ticker(sel_grp, t)
                            st.success(f"✅ Added {t}")
                            st.rerun()
            else:
                st.caption("Not found. Try manual add below.")

        mt = st.text_input("Manual ticker (e.g. SBIN.NS)",
                           key="mt", label_visibility="collapsed",
                           placeholder="SBIN.NS")
        if st.button("Add Manually", use_container_width=True, key="mt_btn"):
            t = mt.strip().upper()
            if t and t not in tickers_now:
                add_ticker(sel_grp, t)
                st.success(f"✅ Added {t}!")
                st.rerun()
            elif t in tickers_now:
                st.warning("Already in list.")

    st.markdown("---")

    # ── INSTITUTIONAL WATCHLIST ──────────────────────────
    tickers_list = get_tickers(sel_grp)
    if not tickers_list:
        st.caption("No stocks yet. Use Add Stock above ↑")
    else:
        st.markdown(
            f"<div style='font-size:0.64rem;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.08em;color:#a1a1aa;margin-bottom:6px;'>"
            f"{sel_grp.upper()} · {len(tickers_list)} STOCKS</div>",
            unsafe_allow_html=True)

        for t in tickers_list:
            is_sel = st.session_state.selected_stock == t
            render_watchlist_row(t, sel_grp, is_sel)

    # ── High Conviction sidebar section ──
    st.markdown("---")
    with st.expander("⭐ High Conviction Picks (Pio ≥ 7)"):
        if not tickers_list:
            st.caption("Add stocks first.")
        else:
            st.caption("Screening… (may take a moment)")
            hc_picks = []
            for t in tickers_list[:8]:  # limit to 8 for speed
                try:
                    d = fetch_full(t)
                    if d["ok"]:
                        ps, _ = calc_piotroski(d)
                        if ps >= 7:
                            hc_picks.append((t, ps))
                except Exception:
                    pass
            if hc_picks:
                for t, ps in sorted(hc_picks, key=lambda x: -x[1]):
                    ca2, cb2 = st.columns([4,1])
                    with ca2:
                        if st.button(f"⭐ {t}", key=f"hc_{t}",
                                     use_container_width=True):
                            st.session_state.selected_stock = t
                            st.rerun()
                    with cb2:
                        st.markdown(
                            f"<div style='font-size:0.72rem;font-weight:700;color:#16a34a;"
                            f"padding-top:6px;text-align:right;'>{ps}/9</div>",
                            unsafe_allow_html=True)
            else:
                st.caption("No high conviction picks found in this group.")

# ══ RIGHT PANEL ══════════════════════════════════════════════
with right:
    sel = st.session_state.selected_stock
    if not sel:
        st.markdown(
            "<div style='display:flex;flex-direction:column;align-items:center;"
            "justify-content:center;min-height:55vh;text-align:center;padding:3rem 2rem;'>"
            "<div style='font-size:2.5rem;margin-bottom:0.9rem;'>📊</div>"
            "<div style='font-size:1.3rem;font-weight:800;color:#0f172a;margin-bottom:0.4rem;'>"
            "Stock Analysis Pro v4.3</div>"
            "<div style='font-size:0.85rem;color:#71717a;max-width:380px;line-height:1.75;'>"
            "Click any stock from the left panel to see full analysis —<br>"
            "Fundamentals · Technicals · VPA · Trends · Piotroski · AI Score"
            "</div></div>",
            unsafe_allow_html=True)
    else:
        render_analysis(sel)

st.markdown(
    "<div style='text-align:center;font-size:0.65rem;color:#a1a1aa;"
    "padding:0.6rem 0 1.5rem;border-top:1px solid #e4e4e7;margin-top:0.75rem;'>"
    "📊 Stock Analysis Pro v4.3 · Money Financial Services · "
    "Yahoo Finance + Google Trends · Educational only · Not SEBI advice"
    "</div>",
    unsafe_allow_html=True)
