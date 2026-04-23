"""
Stock Analysis Pro — v4.0 Fixed
Author  : Money Financial Services
UI Style: TradingView-inspired clean light theme
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3, datetime, math
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── PAGE CONFIG ────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Analysis Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg0:#ffffff; --bg1:#f8f9fc; --bg2:#f1f3f8;
  --border:#e6e9f0; --border2:#d0d5e5;
  --text1:#0b1120; --text2:#3d4a63; --text3:#7b8599;
  --green:#0ea371; --green-bg:#edfbf4;
  --red:#e53935;   --red-bg:#fef2f2;
  --blue:#2563eb;  --blue-bg:#eff6ff;
  --radius:8px; --radius2:12px;
  --shadow:0 1px 4px rgba(11,17,32,.06),0 4px 20px rgba(11,17,32,.04);
}

html, body, [class*="css"] {
  font-family: 'Inter', sans-serif !important;
  background: var(--bg1) !important;
  color: var(--text1) !important;
}

/* Hide sidebar completely */
section[data-testid="stSidebar"] { display: none !important; }
button[data-testid="collapsedControl"] { display: none !important; }

/* Remove default padding */
.block-container {
  padding: 0.5rem 1rem 3rem 1rem !important;
  max-width: 100% !important;
}

/* Cards */
.card {
  background: var(--bg0);
  border: 1px solid var(--border);
  border-radius: var(--radius2);
  padding: 1.1rem 1.25rem;
  box-shadow: var(--shadow);
  margin-bottom: 0.8rem;
}
.m-label {
  font-size: .68rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: .07em;
  color: var(--text3); margin-bottom: .25rem;
}
.m-value {
  font-size: 1.45rem; font-weight: 700;
  color: var(--text1); line-height: 1.1;
  font-family: 'JetBrains Mono', monospace;
}
.m-sub { font-size: .72rem; color: var(--text3); margin-top: .15rem; }

/* Section header */
.sec {
  font-size: .88rem; font-weight: 700;
  color: var(--text1);
  border-left: 3px solid var(--blue);
  padding-left: .6rem;
  margin: 1.5rem 0 .8rem;
}

/* Badges */
.badge {
  display: inline-block; padding: .2rem .55rem;
  border-radius: 999px; font-size: .7rem; font-weight: 700;
}
.bg { background:#dcfce7; color:#15803d; }
.by { background:#fef9c3; color:#854d0e; }
.br { background:#fee2e2; color:#b91c1c; }
.bb { background:#dbeafe; color:#1d4ed8; }
.bn { background:#f1f5f9; color:#475569; }

/* Progress bar */
.pb-w { background:#e9ecf3; border-radius:999px; height:6px; width:100%; margin:.35rem 0; }
.pb-f { height:6px; border-radius:999px; }

/* Checklist */
.ck {
  display:flex; align-items:flex-start; gap:.5rem;
  padding:.4rem .7rem; border-radius:7px; margin-bottom:.25rem;
}
.ck-n { font-size:.8rem; font-weight:600; }
.ck-s { font-size:.7rem; color:var(--text3); }

/* Alert boxes */
.alert { border-radius:var(--radius); padding:.7rem 1rem; font-size:.82rem; margin:.4rem 0; line-height:1.55; }
.a-info    { background:#eff6ff; border:1px solid #bfdbfe; color:#1e40af; }
.a-ok      { background:#ecfdf5; border:1px solid #6ee7b7; color:#065f46; }
.a-warn    { background:#fffbeb; border:1px solid #fcd34d; color:#92400e; }
.a-danger  { background:#fef2f2; border:1px solid #fca5a5; color:#991b1b; }

/* Stock list panel */
.slist-wrap {
  background: var(--bg0);
  border: 1px solid var(--border);
  border-radius: var(--radius2);
  overflow: hidden;
  box-shadow: var(--shadow);
}
.slist-header {
  padding: .75rem 1rem;
  border-bottom: 1px solid var(--border);
  font-size: .82rem; font-weight: 700;
  color: var(--text2);
  background: var(--bg1);
}
.stock-header {
  background: var(--bg0);
  border: 1px solid var(--border);
  border-radius: var(--radius2);
  padding: 1rem 1.25rem;
  box-shadow: var(--shadow);
  margin-bottom: 1rem;
}

/* Override buttons */
[data-testid="stButton"] > button {
  border-radius: 7px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: .82rem !important;
}
[data-testid="stTextInput"] input {
  border-radius: 7px !important;
  font-family: 'Inter', sans-serif !important;
}
[data-testid="stTabs"] [role="tab"] {
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: .82rem !important;
}
.stApp > header { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── STOCK DATABASE ──────────────────────────────────────────
STOCK_DB = {
    "Reliance Industries": "RELIANCE.NS",
    "TCS":                 "TCS.NS",
    "Infosys":             "INFY.NS",
    "HDFC Bank":           "HDFCBANK.NS",
    "ICICI Bank":          "ICICIBANK.NS",
    "Kotak Bank":          "KOTAKBANK.NS",
    "Axis Bank":           "AXISBANK.NS",
    "SBI":                 "SBIN.NS",
    "Bajaj Finance":       "BAJFINANCE.NS",
    "Bajaj Finserv":       "BAJAJFINSV.NS",
    "Wipro":               "WIPRO.NS",
    "HCL Tech":            "HCLTECH.NS",
    "Tech Mahindra":       "TECHM.NS",
    "L&T":                 "LT.NS",
    "ITC":                 "ITC.NS",
    "HUL":                 "HINDUNILVR.NS",
    "Nestle India":        "NESTLEIND.NS",
    "Asian Paints":        "ASIANPAINT.NS",
    "Maruti Suzuki":       "MARUTI.NS",
    "Tata Motors":         "TATAMOTORS.NS",
    "Mahindra M&M":        "M&M.NS",
    "Sun Pharma":          "SUNPHARMA.NS",
    "Dr Reddys":           "DRREDDY.NS",
    "Cipla":               "CIPLA.NS",
    "Divis Lab":           "DIVISLAB.NS",
    "Apollo Hospitals":    "APOLLOHOSP.NS",
    "ONGC":                "ONGC.NS",
    "Power Grid":          "POWERGRID.NS",
    "NTPC":                "NTPC.NS",
    "Coal India":          "COALINDIA.NS",
    "Titan":               "TITAN.NS",
    "Tata Steel":          "TATASTEEL.NS",
    "JSW Steel":           "JSWSTEEL.NS",
    "Hindalco":            "HINDALCO.NS",
    "UltraTech Cement":    "ULTRACEMCO.NS",
    "Adani Ports":         "ADANIPORTS.NS",
    "Adani Enterprises":   "ADANIENT.NS",
    "Shriram Finance":     "SHRIRAMFIN.NS",
    "Muthoot Finance":     "MUTHOOTFIN.NS",
    "Cholamandalam":       "CHOLAFIN.NS",
    "IDFC First Bank":     "IDFCFIRSTB.NS",
    "IndusInd Bank":       "INDUSINDBK.NS",
    "Bank of Baroda":      "BANKBARODA.NS",
    "PNB":                 "PNB.NS",
    "Canara Bank":         "CANBK.NS",
    "Federal Bank":        "FEDERALBNK.NS",
    "Yes Bank":            "YESBANK.NS",
    "Paytm":               "PAYTM.NS",
    "Zomato":              "ZOMATO.NS",
    "Nykaa":               "NYKAA.NS",
    "Tata Power":          "TATAPOWER.NS",
    "Tata Consumer":       "TATACONSUM.NS",
    "Godrej Consumer":     "GODREJCP.NS",
    "Pidilite":            "PIDILITIND.NS",
    "Berger Paints":       "BERGEPAINT.NS",
    "Dabur":               "DABUR.NS",
    "Marico":              "MARICO.NS",
    "Britannia":           "BRITANNIA.NS",
    "Havells":             "HAVELLS.NS",
    "Dixon Tech":          "DIXON.NS",
    "Hero MotoCorp":       "HEROMOTOCO.NS",
    "Bajaj Auto":          "BAJAJ-AUTO.NS",
    "Eicher Motors":       "EICHERMOT.NS",
    "Ashok Leyland":       "ASHOKLEY.NS",
    "IndiGo":              "INDIGO.NS",
    "Lupin":               "LUPIN.NS",
    "Biocon":              "BIOCON.NS",
    "Torrent Pharma":      "TORNTPHARM.NS",
    "Aurobindo Pharma":    "AUROPHARMA.NS",
    "Mankind Pharma":      "MANKIND.NS",
    "DLF":                 "DLF.NS",
    "Lodha":               "LODHA.NS",
    "Varun Beverages":     "VBL.NS",
    "Mphasis":             "MPHASIS.NS",
    "LTIMindtree":         "LTIM.NS",
    "Persistent Systems":  "PERSISTENT.NS",
    "Coforge":             "COFORGE.NS",
    "BSE":                 "BSE.NS",
    "MCX":                 "MCX.NS",
    "Angel One":           "ANGELONE.NS",
    "CDSL":                "CDSL.NS",
    "Polycab":             "POLYCAB.NS",
    "Siemens India":       "SIEMENS.NS",
    "ABB India":           "ABB.NS",
    "BEL":                 "BEL.NS",
    "HAL":                 "HAL.NS",
    "IRCTC":               "IRCTC.NS",
    "IRFC":                "IRFC.NS",
    "RVNL":                "RVNL.NS",
    "Max Healthcare":      "MAXHEALTH.NS",
    "NHPC":                "NHPC.NS",
    "Torrent Power":       "TORNTPOWER.NS",
    "Grasim":              "GRASIM.NS",
}

DEFAULT_GROUPS = {
    "Watchlist":  ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS"],
    "Banking":    ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS"],
    "IT Sector":  ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Pharma":     ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","DIVISLAB.NS"],
}

# ── DATABASE ────────────────────────────────────────────────
DB = "stock_v4.db"

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
    conn.close(); return rows

def dbx(sql, p=()):
    conn = sqlite3.connect(DB)
    conn.execute(sql, p)
    conn.commit(); conn.close()

def get_groups():
    return [r[0] for r in dbq("SELECT DISTINCT grp FROM grp_tickers ORDER BY grp")]

def get_tickers(grp):
    return [r[0] for r in dbq(
        "SELECT ticker FROM grp_tickers WHERE grp=? ORDER BY added_at",(grp,))]

def add_t(grp, ticker):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    dbx("INSERT OR IGNORE INTO grp_tickers (grp,ticker,added_at) VALUES (?,?,?)",
        (grp, ticker.upper().strip(), now))

def del_t(grp, ticker):
    dbx("DELETE FROM grp_tickers WHERE grp=? AND ticker=?",(grp, ticker))

def del_grp(name):
    dbx("DELETE FROM grp_tickers WHERE grp=?",(name,))

def save_note(ticker, content):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    dbx("INSERT OR REPLACE INTO notes VALUES (?,?,?)",(ticker.upper(),content,now))

def load_note(ticker):
    rows = dbq("SELECT content,updated_at FROM notes WHERE ticker=?",(ticker.upper(),))
    return (rows[0][0], rows[0][1]) if rows else ("","")

# ── DATA FETCHER ────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_all(ticker):
    try:
        stk = yf.Ticker(ticker)
        info = stk.info or {}
        hist = stk.history(period="1y")
        try:    fin = stk.financials
        except: fin = pd.DataFrame()
        try:    bs  = stk.balance_sheet
        except: bs  = pd.DataFrame()
        try:    cf  = stk.cashflow
        except: cf  = pd.DataFrame()
        return {"info":info,"hist":hist,"fin":fin,"bs":bs,"cf":cf}
    except Exception:
        return {"info":{},"hist":pd.DataFrame(),
                "fin":pd.DataFrame(),"bs":pd.DataFrame(),"cf":pd.DataFrame()}

@st.cache_data(ttl=120, show_spinner=False)
def fetch_price(ticker):
    try:
        info = yf.Ticker(ticker).info or {}
        return {
            "price": info.get("regularMarketPrice") or info.get("currentPrice"),
            "prev":  info.get("regularMarketPreviousClose"),
            "name":  info.get("shortName") or info.get("longName") or ticker,
        }
    except Exception:
        return {"price":None,"prev":None,"name":ticker}

def _v(d, *keys, default=None):
    for k in keys:
        val = d.get(k) if isinstance(d,dict) else None
        if val is not None and not(isinstance(val,float) and math.isnan(val)):
            return val
    return default

def _row(df, *names):
    if df is None or df.empty: return None
    for name in names:
        for idx in df.index:
            if name.lower() in str(idx).lower():
                s = df.loc[idx].dropna()
                if not s.empty: return s
    return None

def _latest(s):
    if s is None: return None
    s2 = s.dropna()
    return float(s2.iloc[0]) if not s2.empty else None

def build_m(data):
    info,fin,bs,cf,hist = data["info"],data["fin"],data["bs"],data["cf"],data["hist"]
    m = {}
    m["name"]      = _v(info,"longName","shortName",default=None)
    m["sector"]    = _v(info,"sector",default="—")
    m["industry"]  = _v(info,"industry",default="—")
    m["exchange"]  = _v(info,"exchange",default="—")
    m["currency"]  = _v(info,"currency",default="INR")
    m["price"]     = _v(info,"regularMarketPrice","currentPrice",default=None)
    m["prev"]      = _v(info,"regularMarketPreviousClose",default=None)
    m["mktcap"]    = _v(info,"marketCap",default=None)
    m["beta"]      = _v(info,"beta",default=None)
    m["pe"]        = _v(info,"trailingPE",default=None)
    m["fpe"]       = _v(info,"forwardPE",default=None)
    m["pb"]        = _v(info,"priceToBook",default=None)
    m["ps"]        = _v(info,"priceToSalesTrailing12Months",default=None)
    m["peg"]       = _v(info,"pegRatio",default=None)
    m["roe"]       = _v(info,"returnOnEquity",default=None)
    m["roa"]       = _v(info,"returnOnAssets",default=None)
    m["pm"]        = _v(info,"profitMargins",default=None)
    m["gm"]        = _v(info,"grossMargins",default=None)
    m["om"]        = _v(info,"operatingMargins",default=None)
    m["de"]        = _v(info,"debtToEquity",default=None)
    m["cr"]        = _v(info,"currentRatio",default=None)
    m["qr"]        = _v(info,"quickRatio",default=None)
    m["fcf"]       = _v(info,"freeCashflow",default=None)
    m["ocf"]       = _v(info,"operatingCashflow",default=None)
    m["rg"]        = _v(info,"revenueGrowth",default=None)
    m["eg"]        = _v(info,"earningsGrowth",default=None)
    m["eps"]       = _v(info,"trailingEps",default=None)
    m["feps"]      = _v(info,"forwardEps",default=None)
    m["dy"]        = _v(info,"dividendYield",default=None)

    # Fallbacks
    if m["roe"] is None:
        ni = _latest(_row(fin,"Net Income"))
        eq = _latest(_row(bs,"Stockholders Equity","Total Stockholder Equity"))
        if ni and eq and eq!=0: m["roe"] = ni/abs(eq)
    if m["roa"] is None:
        ni = _latest(_row(fin,"Net Income"))
        ta = _latest(_row(bs,"Total Assets"))
        if ni and ta and ta!=0: m["roa"] = ni/abs(ta)
    if m["pm"] is None:
        ni  = _latest(_row(fin,"Net Income"))
        rev = _latest(_row(fin,"Total Revenue"))
        if ni and rev and rev!=0: m["pm"] = ni/abs(rev)
    if m["de"] is None:
        td = _latest(_row(bs,"Total Debt","Long Term Debt"))
        eq = _latest(_row(bs,"Stockholders Equity","Total Stockholder Equity"))
        if td is not None and eq and eq!=0: m["de"] = (td/abs(eq))*100
    if m["fcf"] is None:
        ocf  = _latest(_row(cf,"Operating Cash Flow","Cash From Operations"))
        capx = _latest(_row(cf,"Capital Expenditure","Purchases Of Property Plant And Equipment"))
        if ocf is not None:
            m["ocf"] = ocf
            m["fcf"] = ocf + (capx if capx else 0)

    if not hist.empty:
        close = hist["Close"]
        m["ph"]    = float(close.iloc[-1])
        m["vol"]   = float(hist["Volume"].iloc[-1])
        m["v20"]   = float(hist["Volume"].rolling(20).mean().iloc[-1]) if len(hist)>=20 else None
        m["d50"]   = float(close.rolling(50).mean().iloc[-1])  if len(close)>=50  else None
        m["d200"]  = float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else None
        m["h52"]   = float(close.rolling(252).max().iloc[-1])  if len(close)>=252 else float(close.max())
        m["l52"]   = float(close.rolling(252).min().iloc[-1])  if len(close)>=252 else float(close.min())
        delta = close.diff()
        gain  = delta.clip(lower=0).rolling(14).mean()
        loss  = (-delta.clip(upper=0)).rolling(14).mean()
        rs    = gain/loss.replace(0,float("nan"))
        rsi   = 100-(100/(1+rs))
        m["rsi"]   = float(rsi.iloc[-1]) if not rsi.empty else None
        e12 = close.ewm(span=12).mean(); e26 = close.ewm(span=26).mean()
        macd = e12-e26; sig = macd.ewm(span=9).mean()
        m["macd"]  = float(macd.iloc[-1])
        m["msig"]  = float(sig.iloc[-1])
        m["mh"]    = float((macd-sig).iloc[-1])
    else:
        for k in ["ph","vol","v20","d50","d200","h52","l52","rsi","macd","msig","mh"]:
            m[k] = None
    return m

# ── PIOTROSKI ───────────────────────────────────────────────
def piotroski(data):
    info,fin,bs,cf = data["info"],data["fin"],data["bs"],data["cf"]
    C = []

    def _v2(df, *n): return _latest(_row(df,*n))
    def _v2prev(df, *n):
        r = _row(df,*n)
        if r is None or len(r.dropna())<2: return None
        return float(r.dropna().iloc[1])

    ni_c  = _v2(fin,"Net Income");    ni_p  = _v2prev(fin,"Net Income")
    rev_c = _v2(fin,"Total Revenue"); rev_p = _v2prev(fin,"Total Revenue")
    ta_c  = _v2(bs,"Total Assets");   ta_p  = _v2prev(bs,"Total Assets")
    ocf   = _v2(cf,"Operating Cash Flow","Cash From Operations")
    roa   = _v(info,"returnOnAssets",default=None)
    if roa is None and ni_c and ta_c and ta_c!=0: roa = ni_c/ta_c

    def add(grp,name,p,note): C.append({"g":grp,"n":name,"p":p,"note":note})

    add("Profitability","F1 — ROA Positive",
        roa is not None and roa>0, f"ROA={roa*100:.1f}%" if roa else "N/A")
    add("Profitability","F2 — Operating Cash Flow > 0",
        ocf is not None and ocf>0, f"OCF=₹{ocf/1e7:.1f}Cr" if ocf else "N/A")
    if roa is not None and ta_p and ni_p and ta_p!=0:
        rp = ni_p/ta_p
        add("Profitability","F3 — ROA Improving YoY", roa>rp,
            f"Curr {roa*100:.1f}% vs Prev {rp*100:.1f}%")
    else:
        add("Profitability","F3 — ROA Improving YoY", False, "Insufficient data")
    if ocf and ta_c and ta_c!=0 and roa is not None:
        add("Profitability","F4 — Cash > Paper Earnings",
            ocf/ta_c>roa, f"OCF/TA={ocf/ta_c*100:.1f}% vs ROA={roa*100:.1f}%")
    else:
        add("Profitability","F4 — Cash > Paper Earnings", False, "N/A")

    ltd_r = _row(bs,"Long Term Debt")
    if ltd_r is not None and len(ltd_r.dropna())>=2 and ta_c and ta_p:
        lv = ltd_r.dropna()
        rc_ = float(lv.iloc[0])/ta_c; rp_ = float(lv.iloc[1])/ta_p
        add("Leverage","F5 — Debt Ratio Decreasing", rc_<rp_,
            f"Curr {rc_*100:.1f}% vs Prev {rp_*100:.1f}%")
    else:
        add("Leverage","F5 — Debt Ratio Decreasing", False, "N/A")

    ca_r = _row(bs,"Current Assets"); cl_r = _row(bs,"Current Liabilities")
    if ca_r is not None and cl_r is not None and len(ca_r.dropna())>=2:
        cav=ca_r.dropna(); clv=cl_r.dropna()
        cc=float(cav.iloc[0])/float(clv.iloc[0]) if float(clv.iloc[0])!=0 else None
        cp_=float(cav.iloc[1])/float(clv.iloc[1]) if float(clv.iloc[1])!=0 else None
        add("Leverage","F6 — Current Ratio Improving",
            bool(cc and cp_ and cc>cp_),
            f"Curr {cc:.2f} vs Prev {cp_:.2f}" if cc and cp_ else "N/A")
    else:
        cr_i = _v(info,"currentRatio",default=None)
        add("Leverage","F6 — Current Ratio > 1.5",
            cr_i is not None and cr_i>1.5,
            f"CR={cr_i:.2f}" if cr_i else "N/A")

    sh_r = _row(bs,"Ordinary Shares Number","Common Stock Shares Outstanding")
    if sh_r is not None and len(sh_r.dropna())>=2:
        sv = sh_r.dropna()
        add("Leverage","F7 — No Dilution",
            float(sv.iloc[0])<=float(sv.iloc[1]),
            f"Curr {float(sv.iloc[0])/1e7:.2f}Cr vs Prev {float(sv.iloc[1])/1e7:.2f}Cr")
    else:
        add("Leverage","F7 — No Dilution", False, "N/A")

    gp_r = _row(fin,"Gross Profit")
    if gp_r is not None and len(gp_r.dropna())>=2 and rev_c and rev_p:
        gv = gp_r.dropna()
        gmc = float(gv.iloc[0])/rev_c; gmp = float(gv.iloc[1])/rev_p
        add("Efficiency","F8 — Gross Margin Improving", gmc>gmp,
            f"Curr {gmc*100:.1f}% vs Prev {gmp*100:.1f}%")
    else:
        gm_i = _v(info,"grossMargins",default=None)
        add("Efficiency","F8 — Gross Margin > 20%",
            gm_i is not None and gm_i>0.20,
            f"GM={gm_i*100:.1f}%" if gm_i else "N/A")

    if rev_c and rev_p and ta_c and ta_p:
        add("Efficiency","F9 — Asset Turnover Improving",
            rev_c/ta_c>rev_p/ta_p,
            f"Curr {rev_c/ta_c:.2f}x vs Prev {rev_p/ta_p:.2f}x")
    else:
        add("Efficiency","F9 — Asset Turnover Improving", False, "Insufficient data")

    return sum(1 for c in C if c["p"]), C

# ── INTRINSIC VALUE ─────────────────────────────────────────
def iv_calc(m):
    r = {}
    eps=m.get("eps"); pb=m.get("pb")
    price = m.get("price") or m.get("ph")
    bvps = (price/pb) if(pb and pb>0 and price) else None
    r["graham"] = math.sqrt(22.5*eps*bvps) if(eps and eps>0 and bvps and bvps>0) else None
    g = m.get("eg") or m.get("rg")
    if eps and eps>0 and g is not None:
        g2 = max(-20,min(50,g*100))
        dcf = eps*(8.5+2*g2)*4.4/7.5
        r["dcf"] = dcf if dcf>0 else None
    else:
        r["dcf"] = None
    valid = [v for v in [r.get("graham"),r.get("dcf")] if v]
    if valid and price:
        avg = sum(valid)/len(valid)
        r["avg"] = avg
        r["mos"] = (avg-price)/avg*100
        r["up"]  = (avg-price)/price*100
    else:
        r["avg"]=r["mos"]=r["up"]=None
    return r

# ── AI SCORE ────────────────────────────────────────────────
def ai_score(m, pio, iv):
    bd = {}
    price = m.get("price") or m.get("ph") or 0

    v=0
    pe=m.get("pe")
    if pe: v += 10 if pe<15 else(7 if pe<25 else(4 if pe<40 else 0))
    pb=m.get("pb")
    if pb: v += 10 if pb<1.5 else(7 if pb<3 else(3 if pb<5 else 0))
    bd["Valuation"]=min(v,20)

    p=0
    roe=m.get("roe")
    if roe: p += 8 if roe>0.25 else(5 if roe>0.15 else(2 if roe>0 else 0))
    pm=m.get("pm")
    if pm: p += 7 if pm>0.20 else(4 if pm>0.10 else(1 if pm>0 else 0))
    fcf=m.get("fcf")
    if fcf and fcf>0: p+=5
    bd["Profitability"]=min(p,20)

    h=0
    de=m.get("de")
    if de is not None:
        dr=de/100
        h += 8 if dr<0.3 else(5 if dr<0.7 else(2 if dr<1 else 0))
    cr=m.get("cr")
    if cr: h += 7 if cr>2 else(4 if cr>1.5 else(1 if cr>1 else 0))
    h += min(pio,5)
    bd["Financial Health"]=min(h,20)

    t=0
    d200=m.get("d200"); d50=m.get("d50"); rsi=m.get("rsi")
    if price and d200:
        pct=(price-d200)/d200*100
        t += 8 if 0<pct<20 else(4 if pct>=20 else(3 if pct>-10 else 0))
    if price and d50 and price>d50: t+=5
    if rsi:
        t += 7 if 40<=rsi<=65 else(4 if(30<=rsi<40 or 65<rsi<=70) else(2 if rsi<30 else 0))
    bd["Technical"]=min(t,20)

    g=0
    rg=m.get("rg")
    if rg: g += 7 if rg>0.20 else(4 if rg>0.10 else(1 if rg>0 else 0))
    eg=m.get("eg")
    if eg: g += 7 if eg>0.20 else(4 if eg>0.10 else(1 if eg>0 else 0))
    up=iv.get("up")
    if up: g += 6 if up>30 else(3 if up>10 else(1 if up>0 else 0))
    bd["Growth"]=min(g,20)

    total=sum(bd.values())
    if total>=75:   grade,color="Excellent — Strong Buy","#059669"
    elif total>=60: grade,color="Good — Buy","#2563eb"
    elif total>=45: grade,color="Average — Watch","#d97706"
    elif total>=30: grade,color="Weak — Caution","#ea580c"
    else:           grade,color="Poor — Avoid","#dc2626"
    return total, bd, grade, color

# ── FORMATTERS ──────────────────────────────────────────────
def fc(v):
    if v is None: return "N/A"
    try:
        v=float(v)
        if abs(v)>=1e12: return f"₹{v/1e12:.2f}T"
        if abs(v)>=1e7:  return f"₹{v/1e7:.2f}Cr"
        if abs(v)>=1e5:  return f"₹{v/1e5:.2f}L"
        return f"₹{v:,.0f}"
    except: return "N/A"

def fp(v,d=1):
    if v is None: return "N/A"
    try: return f"{float(v)*100:.{d}f}%"
    except: return "N/A"

def fn(v,d=2):
    if v is None: return "N/A"
    try: return f"{float(v):,.{d}f}"
    except: return "N/A"

def card(lbl,val,sub="",vc="#0b1120"):
    s = f"<div class='card'><div class='m-label'>{lbl}</div>"
    s += f"<div class='m-value' style='color:{vc};'>{val}</div>"
    if sub: s += f"<div class='m-sub'>{sub}</div>"
    return s+"</div>"

def pb_bar(pct, color="#2563eb"):
    pct=max(0,min(100,pct))
    return (f"<div class='pb-w'><div class='pb-f' "
            f"style='width:{pct}%;background:{color};'></div></div>")

# ── CHARTS ──────────────────────────────────────────────────
def candle_chart(hist, d50, d200):
    if hist.empty: return None
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, row_heights=[0.75,0.25])
    fig.add_trace(go.Candlestick(
        x=hist.index, open=hist["Open"], high=hist["High"],
        low=hist["Low"], close=hist["Close"], name="Price",
        increasing_line_color="#0ea371", decreasing_line_color="#e53935",
        increasing_fillcolor="#0ea371", decreasing_fillcolor="#e53935",
    ), row=1, col=1)
    if d50 is not None:
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist["Close"].rolling(50).mean(),
            name="50 DMA", line=dict(color="#2563eb",width=1.5),
        ), row=1, col=1)
    if d200 is not None:
        fig.add_trace(go.Scatter(
            x=hist.index, y=hist["Close"].rolling(200).mean(),
            name="200 DMA", line=dict(color="#d97706",width=1.5,dash="dot"),
        ), row=1, col=1)
    colors = ["#0ea371" if c>=o else "#e53935"
              for c,o in zip(hist["Close"],hist["Open"])]
    fig.add_trace(go.Bar(
        x=hist.index, y=hist["Volume"], name="Volume",
        marker_color=colors, opacity=0.55, showlegend=False
    ), row=2, col=1)
    fig.update_layout(
        height=440, margin=dict(l=0,r=0,t=24,b=0),
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        font=dict(family="Inter",size=11,color="#3d4a63"),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h",yanchor="bottom",y=1.01,
                    xanchor="right",x=1,bgcolor="rgba(0,0,0,0)",
                    font=dict(size=10)),
        yaxis=dict(showgrid=True,gridcolor="#f1f3f8",side="right",
                   tickfont=dict(size=10),zeroline=False),
        yaxis2=dict(showgrid=False,side="right",tickfont=dict(size=9),zeroline=False),
        xaxis2=dict(showgrid=True,gridcolor="#f1f3f8",tickfont=dict(size=10)),
    )
    return fig

def gauge_chart(score, grade, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"font":{"size":38,"family":"JetBrains Mono","color":color}},
        gauge=dict(
            axis=dict(range=[0,100],tickwidth=1,tickcolor="#e6e9f0",
                      tickfont=dict(size=10,color="#7b8599"),nticks=6),
            bar=dict(color=color,thickness=0.25),
            bgcolor="white", borderwidth=0,
            steps=[
                dict(range=[0,30],  color="#fef2f2"),
                dict(range=[30,45], color="#fff7ed"),
                dict(range=[45,60], color="#fffbeb"),
                dict(range=[60,75], color="#eff6ff"),
                dict(range=[75,100],color="#ecfdf5"),
            ],
            threshold=dict(line=dict(color=color,width=3),
                           thickness=0.75,value=score)
        ),
        domain={"x":[0,1],"y":[0,1]},
        title={"text":grade,"font":{"size":11,"family":"Inter","color":"#3d4a63"}}
    ))
    fig.update_layout(
        height=210, margin=dict(l=20,r=20,t=30,b=0),
        paper_bgcolor="#ffffff", font=dict(family="Inter"),
    )
    return fig

# ── FULL ANALYSIS ───────────────────────────────────────────
def render_analysis(ticker):
    with st.spinner(f"Loading {ticker}…"):
        data = fetch_all(ticker)
        m    = build_m(data)

    price = m.get("price") or m.get("ph")
    if not price:
        st.markdown(
            f"<div class='alert a-danger'>❌ Could not fetch <b>{ticker}</b>. "
            "Check symbol. NSE → add .NS (e.g. SBIN.NS)</div>",
            unsafe_allow_html=True)
        return

    pio_s, pio_c = piotroski(data)
    iv           = iv_calc(m)
    total, bd, grade, color = ai_score(m, pio_s, iv)
    hist = data.get("hist", pd.DataFrame())

    prev  = m.get("prev")
    chg   = price-prev if prev else 0
    chgp  = chg/prev*100 if prev else 0
    cc    = "#0ea371" if chg>=0 else "#e53935"
    arr   = "▲" if chg>=0 else "▼"
    curr  = m.get("currency","INR")

    # Header
    st.markdown(f"""
    <div class='stock-header'>
      <div style='display:flex;justify-content:space-between;
                  align-items:flex-start;flex-wrap:wrap;gap:.75rem;'>
        <div>
          <div style='font-size:1.3rem;font-weight:700;color:#0b1120;line-height:1.2;'>
            {m.get("name") or ticker}
          </div>
          <div style='font-size:.75rem;color:#7b8599;margin-top:.3rem;
                      display:flex;gap:.4rem;flex-wrap:wrap;align-items:center;'>
            <span class='badge bb'>{ticker}</span>
            <span class='badge bn'>{m.get("exchange","—")}</span>
            <span>{m.get("sector","—")} · {m.get("industry","—")}</span>
          </div>
        </div>
        <div style='text-align:right;'>
          <div style='font-size:1.75rem;font-weight:800;color:#0b1120;
                      font-family:"JetBrains Mono",monospace;line-height:1;'>
            {curr} {price:,.2f}
          </div>
          <div style='font-size:.85rem;font-weight:600;color:{cc};margin-top:.15rem;'>
            {arr} {abs(chg):,.2f} ({chgp:+.2f}%)
          </div>
          <div style='font-size:.7rem;color:#94a3b8;margin-top:.1rem;'>
            Mkt Cap: {fc(m.get("mktcap"))} &nbsp;|&nbsp; Beta: {fn(m.get("beta"))}
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    T1,T2,T3,T4,T5 = st.tabs([
        "📋 Fundamentals","📡 Technicals",
        "🏆 Piotroski","💎 Intrinsic Value","🤖 AI Verdict"])

    # ── TAB 1 ──
    with T1:
        st.markdown("<div class='sec'>Valuation</div>", unsafe_allow_html=True)
        pe_v=m.get("pe")
        pe_c = ("#059669" if pe_v and pe_v<25 else
                "#d97706" if pe_v and pe_v<40 else "#e53935") if pe_v else "#7b8599"
        c1,c2,c3,c4,c5 = st.columns(5)
        for col,(l,v,s,vc) in zip([c1,c2,c3,c4,c5],[
            ("Trailing PE",fn(m.get("pe"),1),"< 25 ideal",pe_c),
            ("Forward PE",fn(m.get("fpe"),1),"Estimated","#0b1120"),
            ("Price/Book",fn(m.get("pb"),2),"< 3 ideal","#0b1120"),
            ("Price/Sales",fn(m.get("ps"),2),"Revenue multiple","#0b1120"),
            ("PEG Ratio",fn(m.get("peg"),2),"< 1 undervalued","#0b1120"),
        ]):
            col.markdown(card(l,v,s,vc),unsafe_allow_html=True)

        st.markdown("<div class='sec'>Profitability</div>", unsafe_allow_html=True)
        c1,c2,c3,c4,c5 = st.columns(5)
        roe_v=m.get("roe"); pm_v=m.get("pm")
        for col,(l,v,s,vc) in zip([c1,c2,c3,c4,c5],[
            ("ROE",fp(roe_v),"> 15% ideal",
             "#059669" if roe_v and roe_v>0.15 else "#e53935" if roe_v else "#7b8599"),
            ("ROA",fp(m.get("roa")),"Asset efficiency","#0b1120"),
            ("Net Margin",fp(pm_v),"> 10% ideal",
             "#059669" if pm_v and pm_v>0.10 else "#e53935" if pm_v else "#7b8599"),
            ("Gross Margin",fp(m.get("gm")),"Revenue quality","#0b1120"),
            ("Oper. Margin",fp(m.get("om")),"Operating eff.","#0b1120"),
        ]):
            col.markdown(card(l,v,s,vc),unsafe_allow_html=True)

        st.markdown("<div class='sec'>Balance Sheet & Cash Flow</div>", unsafe_allow_html=True)
        c1,c2,c3,c4,c5 = st.columns(5)
        de_v=m.get("de"); cr_v=m.get("cr"); fcf_v=m.get("fcf")
        de_r=de_v/100 if de_v is not None else None
        for col,(l,v,s,vc) in zip([c1,c2,c3,c4,c5],[
            ("Debt/Equity",
             f"{de_r:.2f}x" if de_r is not None else "N/A","< 1x ideal",
             "#059669" if de_r is not None and de_r<1 else "#e53935" if de_r is not None else "#7b8599"),
            ("Current Ratio",fn(cr_v,2),"> 1.5 ideal",
             "#059669" if cr_v and cr_v>1.5 else "#e53935" if cr_v else "#7b8599"),
            ("Quick Ratio",fn(m.get("qr"),2),"Acid test","#0b1120"),
            ("Free Cash Flow",fc(fcf_v),"Positive = healthy",
             "#059669" if fcf_v and fcf_v>0 else "#e53935" if fcf_v else "#7b8599"),
            ("Oper. Cash Flow",fc(m.get("ocf")),"Generated cash","#0b1120"),
        ]):
            col.markdown(card(l,v,s,vc),unsafe_allow_html=True)

        st.markdown("<div class='sec'>Growth & EPS</div>", unsafe_allow_html=True)
        c1,c2,c3,c4,c5 = st.columns(5)
        rg_v=m.get("rg"); eg_v=m.get("eg")
        for col,(l,v,s,vc) in zip([c1,c2,c3,c4,c5],[
            ("Revenue Growth",fp(rg_v),"YoY",
             "#059669" if rg_v and rg_v>0 else "#e53935" if rg_v else "#7b8599"),
            ("Earnings Growth",fp(eg_v),"YoY",
             "#059669" if eg_v and eg_v>0 else "#e53935" if eg_v else "#7b8599"),
            ("Trailing EPS",fn(m.get("eps"),2),"Per share","#0b1120"),
            ("Forward EPS",fn(m.get("feps"),2),"Estimated","#0b1120"),
            ("Dividend Yield",fp(m.get("dy"),2),"Annual","#0b1120"),
        ]):
            col.markdown(card(l,v,s,vc),unsafe_allow_html=True)

        desc = _v(data["info"],"longBusinessSummary",default="")
        if desc:
            with st.expander("📖 About the Company"):
                st.markdown(
                    f"<p style='font-size:.86rem;line-height:1.8;color:#3d4a63;'>"
                    f"{desc[:1200]}{'…' if len(desc)>1200 else ''}</p>",
                    unsafe_allow_html=True)

    # ── TAB 2 ──
    with T2:
        st.markdown("<div class='sec'>Candlestick Chart (1 Year)</div>", unsafe_allow_html=True)
        fig_c = candle_chart(hist, m.get("d50"), m.get("d200"))
        if fig_c:
            st.plotly_chart(fig_c, use_container_width=True,
                            config={"displayModeBar":False})
        else:
            st.info("Chart data not available.")

        st.markdown("<div class='sec'>Moving Averages & Trend</div>", unsafe_allow_html=True)
        ph = m.get("ph") or price
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            st.markdown(card("Current Price",f"₹{ph:,.2f}","Latest close"),
                        unsafe_allow_html=True)
        with c2:
            d50=m.get("d50")
            if d50:
                p50=(ph-d50)/d50*100
                st.markdown(card("50-Day DMA",f"₹{d50:,.2f}",
                    f"{p50:+.1f}% from price",
                    "#059669" if ph>d50 else "#e53935"),unsafe_allow_html=True)
            else:
                st.markdown(card("50-Day DMA","N/A","Insufficient history"),
                            unsafe_allow_html=True)
        with c3:
            d200=m.get("d200")
            if d200:
                p200=(ph-d200)/d200*100
                st.markdown(card("200-Day DMA",f"₹{d200:,.2f}",
                    f"{p200:+.1f}% from price",
                    "#059669" if ph>d200 else "#e53935"),unsafe_allow_html=True)
            else:
                st.markdown(card("200-Day DMA","N/A","Insufficient history"),
                            unsafe_allow_html=True)
        with c4:
            rsi_v=m.get("rsi")
            if rsi_v:
                rl="Overbought ⚠️" if rsi_v>70 else("Oversold 🔎" if rsi_v<30 else "Neutral ✅")
                rc="#e53935" if rsi_v>70 else("#d97706" if rsi_v<30 else "#059669")
                st.markdown(card("RSI (14-day)",f"{rsi_v:.1f}",rl,rc),
                            unsafe_allow_html=True)
            else:
                st.markdown(card("RSI (14-day)","N/A",""),unsafe_allow_html=True)

        if d200:
            cl2=max(-50,min(50,p200))
            fp200=(cl2+50)/100*100
            fc200="#059669" if p200>=0 else "#e53935"
            if p200>20:    trap,tc="⚠️ <b>Overextended</b> above 200 DMA — Pullback risk.","a-warn"
            elif p200>0:   trap,tc="✅ <b>Healthy uptrend</b> — Price above 200 DMA.","a-ok"
            elif p200>-15: trap,tc="🔎 <b>Near 200 DMA</b> — Wait for recovery.","a-warn"
            else:          trap,tc="🚨 <b>Below 200 DMA</b> — Downtrend. Avoid.","a-danger"
            st.markdown(f"""
            <div class='card' style='margin-top:.5rem;'>
              <div style='display:flex;justify-content:space-between;margin-bottom:.3rem;'>
                <span style='font-size:.7rem;color:#94a3b8;'>−50%</span>
                <span style='font-size:.84rem;font-weight:700;color:{fc200};'>{p200:+.1f}% from 200 DMA</span>
                <span style='font-size:.7rem;color:#94a3b8;'>+50%</span>
              </div>
              {pb_bar(fp200,fc200)}
            </div>
            <div class='alert {tc}'>{trap}</div>
            """,unsafe_allow_html=True)

        h52=m.get("h52"); l52=m.get("l52")
        if h52 and l52 and h52!=l52:
            st.markdown("<div class='sec'>52-Week Range</div>",unsafe_allow_html=True)
            pos=(ph-l52)/(h52-l52)*100; pfh=(ph-h52)/h52*100
            ca,cb=st.columns([3,1])
            with ca:
                st.markdown(f"""
                <div class='card'>
                  <div style='display:flex;justify-content:space-between;margin-bottom:.3rem;'>
                    <span style='font-size:.7rem;color:#7b8599;'>52W Low ₹{l52:,.0f}</span>
                    <span style='font-size:.8rem;font-weight:700;'>📍 ₹{ph:,.1f} ({pos:.0f}th%ile)</span>
                    <span style='font-size:.7rem;color:#7b8599;'>52W High ₹{h52:,.0f}</span>
                  </div>
                  {pb_bar(pos,"linear-gradient(90deg,#e53935 0%,#f59e0b 50%,#0ea371 100%)")}
                </div>""",unsafe_allow_html=True)
            with cb:
                st.markdown(card("From 52W High",f"{pfh:+.1f}%","",
                    "#059669" if pfh>-5 else "#e53935"),unsafe_allow_html=True)

        st.markdown("<div class='sec'>Volume Analysis</div>",unsafe_allow_html=True)
        cv=m.get("vol"); v20=m.get("v20")
        c1,c2,c3,c4=st.columns(4)
        with c1:
            st.markdown(card("Today's Volume",f"{cv:,.0f}" if cv else "N/A","Shares"),
                        unsafe_allow_html=True)
        with c2:
            st.markdown(card("20-Day Avg Vol",f"{v20:,.0f}" if v20 else "N/A","Rolling avg"),
                        unsafe_allow_html=True)
        with c3:
            if cv and v20 and v20>0:
                vr=cv/v20
                vc2="#059669" if vr>1.5 else("#e53935" if vr<0.5 else "#d97706")
                vl="📈 High" if vr>1.5 else("📉 Dry" if vr<0.5 else "➡️ Normal")
                st.markdown(card("Vol vs 20D Avg",f"{vr:.2f}×",vl,vc2),
                            unsafe_allow_html=True)
            else:
                st.markdown(card("Vol vs 20D Avg","N/A",""),unsafe_allow_html=True)
        with c4:
            mh=m.get("mh")
            if mh:
                st.markdown(card("MACD Histogram",f"{mh:.2f}",
                    "Bullish 🟢" if mh>0 else "Bearish 🔴",
                    "#059669" if mh>0 else "#e53935"),unsafe_allow_html=True)
            else:
                st.markdown(card("MACD","N/A",""),unsafe_allow_html=True)

    # ── TAB 3 ──
    with T3:
        pc2="#059669" if pio_s>=7 else("#d97706" if pio_s>=5 else "#e53935")
        pc3="bg" if pio_s>=7 else("by" if pio_s>=5 else "br")
        pt="Strong 💪" if pio_s>=7 else("Moderate — Monitor" if pio_s>=5 else "Weak ⚠️")
        ca,cb=st.columns([1,2])
        with ca:
            st.markdown(f"""
            <div class='card' style='text-align:center;padding:1.75rem 1rem;'>
              <div style='font-size:.66rem;font-weight:700;text-transform:uppercase;
                          letter-spacing:.07em;color:#7b8599;margin-bottom:.4rem;'>
                PIOTROSKI F-SCORE</div>
              <div style='font-size:5rem;font-weight:800;color:{pc2};line-height:1;
                          font-family:"JetBrains Mono",monospace;'>{pio_s}</div>
              <div style='font-size:.76rem;color:#7b8599;margin:.2rem 0 .6rem;'>out of 9</div>
              {pb_bar(pio_s/9*100,pc2)}
              <div style='margin-top:.7rem;'>
                <span class='badge {pc3}' style='font-size:.76rem;padding:.28rem .8rem;'>{pt}</span>
              </div>
            </div>
            """,unsafe_allow_html=True)
        with cb:
            st.markdown("<div class='sec' style='margin-top:0;'>F-Score Breakdown</div>",
                        unsafe_allow_html=True)
            grps_p = {}
            for c in pio_c: grps_p.setdefault(c["g"],[]).append(c)
            for grp,items in grps_p.items():
                gs=sum(1 for x in items if x["p"])
                st.markdown(f"<div style='font-size:.68rem;font-weight:700;text-transform:uppercase;"
                            f"letter-spacing:.05em;color:#94a3b8;margin:.65rem 0 .3rem;'>"
                            f"{grp} ({gs}/{len(items)})</div>",unsafe_allow_html=True)
                for item in items:
                    ic="✅" if item["p"] else "❌"
                    bg="#f0fdf4" if item["p"] else "#fef2f2"
                    tc="#065f46" if item["p"] else "#991b1b"
                    st.markdown(f"""<div class='ck' style='background:{bg};'>
                      <span style='font-size:.9rem;'>{ic}</span>
                      <div><div class='ck-n' style='color:{tc};'>{item["n"]}</div>
                      <div class='ck-s'>{item["note"]}</div></div>
                    </div>""",unsafe_allow_html=True)
        st.markdown("<div class='alert a-info' style='margin-top:.75rem;'>"
                    "ℹ️ <b>Piotroski:</b> 7–9 = Strong · 4–6 = Moderate · 0–3 = Weak</div>",
                    unsafe_allow_html=True)

    # ── TAB 4 ──
    with T4:
        curr_p = m.get("price") or m.get("ph")
        st.markdown("<div class='sec'>Intrinsic Value Estimates</div>",unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1:
            gv=iv.get("graham")
            if gv and curr_p:
                diff=(curr_p-gv)/gv*100
                cg="#059669" if curr_p<gv else "#e53935"
                st.markdown(card("Graham Number",f"₹{gv:,.1f}",
                    f"{'Under' if curr_p<gv else 'Over'}valued {abs(diff):.1f}%",cg),
                    unsafe_allow_html=True)
            else:
                st.markdown(card("Graham Number","N/A","EPS/BVPS unavailable"),
                            unsafe_allow_html=True)
        with c2:
            dv=iv.get("dcf")
            if dv and curr_p:
                diff2=(curr_p-dv)/dv*100
                cd="#059669" if curr_p<dv else "#e53935"
                st.markdown(card("Graham DCF",f"₹{dv:,.1f}",
                    f"{'Under' if curr_p<dv else 'Over'}valued {abs(diff2):.1f}%",cd),
                    unsafe_allow_html=True)
            else:
                st.markdown(card("Graham DCF","N/A","EPS/Growth unavailable"),
                            unsafe_allow_html=True)
        with c3:
            avg_iv=iv.get("avg"); up_v=iv.get("up"); mos_v=iv.get("mos")
            if avg_iv and curr_p:
                ca2="#059669" if up_v and up_v>0 else "#e53935"
                st.markdown(card("Blended IV",f"₹{avg_iv:,.1f}",
                    f"{'↑' if up_v and up_v>0 else '↓'} {abs(up_v):.1f}% | MOS: {mos_v:.1f}%",ca2),
                    unsafe_allow_html=True)
            else:
                st.markdown(card("Blended IV","N/A","Insufficient data"),
                            unsafe_allow_html=True)

        if avg_iv and curr_p:
            if mos_v>0:
                st.markdown(f"<div class='alert a-ok'>✅ <b>MOS: {mos_v:.1f}%</b> — Undervalued. Upside: {up_v:.1f}%</div>",unsafe_allow_html=True)
            elif mos_v>-20:
                st.markdown(f"<div class='alert a-warn'>⚠️ Near fair value. Overvalued by {abs(mos_v):.1f}%.</div>",unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='alert a-danger'>🚨 Overvalued by {abs(mos_v):.1f}%. Downside: {abs(up_v):.1f}%.</div>",unsafe_allow_html=True)

        st.markdown("<div class='alert a-info'>ℹ️ Graham Number = √(22.5 × EPS × BVPS). "
                    "DCF uses India bond yield ~7.5%. Estimates only.</div>",unsafe_allow_html=True)

        st.markdown("<hr style='border:none;border-top:1px solid #e6e9f0;margin:1.25rem 0 1rem;'>",
                    unsafe_allow_html=True)
        st.markdown("<div class='sec' style='margin-top:0;'>📝 Research Notes</div>",
                    unsafe_allow_html=True)
        existing,last_upd=load_note(ticker)
        tmpl=(f"📌 {ticker}  |  📅 {datetime.date.today()}\n\n"
              "🎯 THESIS:\n\n📊 KEY METRICS:\n- PE: \n- ROE: \n- D/E: \n- FCF: \n"
              "- Piotroski: /9\n- AI Score: /100\n- IV: ₹\n\n"
              "⚠️ RISKS:\n\n🎯 TRADE PLAN:\n- Entry: ₹  Stop: ₹  Target: ₹\n\n✅ DECISION:")
        if st.button("📋 Template",key=f"t_{ticker}"):
            existing=tmpl
        note_txt=st.text_area("",value=existing,height=280,
                              key=f"n_{ticker}",label_visibility="collapsed")
        c1x,c2x=st.columns([3,1])
        with c1x:
            if st.button("💾 Save",key=f"s_{ticker}",
                         use_container_width=True,type="primary"):
                save_note(ticker,note_txt)
                st.success("✅ Saved!")
        with c2x:
            if last_upd:
                st.markdown(f"<div style='font-size:.7rem;color:#94a3b8;padding-top:.5rem;'>"
                            f"Saved: {last_upd}</div>",unsafe_allow_html=True)

    # ── TAB 5 ──
    with T5:
        ca,cb=st.columns([1,2])
        with ca:
            fig_g=gauge_chart(total,grade,color)
            st.plotly_chart(fig_g,use_container_width=True,
                            config={"displayModeBar":False})
        with cb:
            st.markdown("<div class='sec' style='margin-top:0;'>Score by Pillar</div>",
                        unsafe_allow_html=True)
            pillar_colors={
                "Valuation":"#2563eb","Profitability":"#059669",
                "Financial Health":"#7c3aed","Technical":"#d97706","Growth":"#0891b2"
            }
            for pillar,pts in bd.items():
                pc=pillar_colors.get(pillar,"#64748b")
                bc2="bg" if pts>=15 else("by" if pts>=10 else "br")
                st.markdown(f"""
                <div style='background:#fff;border:1px solid #e6e9f0;border-radius:8px;
                            padding:.65rem .9rem;margin-bottom:.4rem;'>
                  <div style='display:flex;justify-content:space-between;
                              align-items:center;margin-bottom:.25rem;'>
                    <div style='font-size:.82rem;font-weight:600;'>{pillar}</div>
                    <span class='badge {bc2}'>{pts}/20</span>
                  </div>
                  {pb_bar(pts/20*100,pc)}
                </div>""",unsafe_allow_html=True)

        st.markdown("<div class='sec'>Investment Summary</div>",unsafe_allow_html=True)
        ab="above" if price>(m.get("d200") or 0) else "below"
        if total>=75:
            st.markdown(f"<div class='alert a-ok'><b>{ticker}</b> scores <b>{total}/100 — {grade}</b>. "
                        f"ROE {fp(m.get('roe'))}, D/E {fn(m.get('de') and m.get('de')/100,2)}x. "
                        f"Piotroski {pio_s}/9. Trading {ab} 200 DMA. "
                        + (f"IV upside: {up_v:.1f}%." if iv.get('up') else "")+"</div>",
                        unsafe_allow_html=True)
        elif total>=45:
            st.markdown(f"<div class='alert a-warn'><b>{ticker}</b> scores <b>{total}/100 — {grade}</b>. "
                        f"Mixed signals. Piotroski {pio_s}/9. Use strict stop-loss.</div>",
                        unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='alert a-danger'><b>{ticker}</b> scores <b>{total}/100 — {grade}</b>. "
                        f"Multiple red flags. Piotroski {pio_s}/9. High risk.</div>",
                        unsafe_allow_html=True)
        st.markdown("<div class='alert a-info'>⚠️ Quantitative research tool only. "
                    "Not SEBI registered advice.</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════
init_db()

# Session state
for k,v in [("sel_grp","Watchlist"),("sel_ticker",None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# Top bar
st.markdown("""
<div style='background:#fff;border-bottom:1px solid #e6e9f0;
            padding:.7rem 1.5rem;display:flex;align-items:center;
            justify-content:space-between;margin-bottom:.75rem;'>
  <div style='font-size:1rem;font-weight:700;color:#0b1120;display:flex;
              align-items:center;gap:.5rem;'>
    📈 Stock Analysis Pro
    <span style='background:#2563eb;color:#fff;font-size:.6rem;font-weight:700;
                 padding:.1rem .4rem;border-radius:4px;'>v4.0</span>
  </div>
  <div style='font-size:.72rem;color:#7b8599;'>Money Financial Services</div>
</div>
""", unsafe_allow_html=True)

# Two-column layout
left_col, right_col = st.columns([1, 3], gap="medium")

# ══ LEFT PANEL ═══════════════════════════════════════════════
with left_col:
    groups = get_groups()

    # Group selector
    if groups:
        if st.session_state.sel_grp not in groups:
            st.session_state.sel_grp = groups[0]
        sel_grp = st.selectbox(
            "📁 Group",
            groups,
            index=groups.index(st.session_state.sel_grp),
            key="grp_sel",
            label_visibility="visible"
        )
        if sel_grp != st.session_state.sel_grp:
            st.session_state.sel_grp = sel_grp
            st.session_state.sel_ticker = None
            st.rerun()
    else:
        sel_grp = "Watchlist"

    # Create new group
    with st.expander("➕ New Group"):
        ng = st.text_input("Group name",placeholder="e.g. Swing Trades",
                           key="ng",label_visibility="collapsed")
        if st.button("Create",use_container_width=True,key="create_g"):
            if ng.strip():
                add_t(ng.strip(),"__init__")
                st.session_state.sel_grp = ng.strip()
                st.rerun()

    # Delete group
    if sel_grp and sel_grp in groups:
        if st.button(f"🗑️ Delete '{sel_grp}'",use_container_width=True,
                     key="del_g"):
            del_grp(sel_grp)
            st.session_state.sel_grp = groups[0] if len(groups)>1 else "Watchlist"
            st.session_state.sel_ticker = None
            st.rerun()

    st.markdown("---")

    # Add stock
    with st.expander("🔍 Add Stock"):
        sq = st.text_input("",placeholder="Search: SBI, Bajaj…",
                           key="sq",label_visibility="collapsed")
        tickers_now = [t for t in get_tickers(sel_grp) if t!="__init__"]
        if sq:
            ql=sq.lower(); hits={}; seen=set()
            for name,t in STOCK_DB.items():
                if(ql in name.lower() or ql in t.lower()) and t not in seen:
                    seen.add(t); hits[name]=t
            if hits:
                for name,t in list(hits.items())[:6]:
                    already = t in tickers_now
                    ca2,cb2=st.columns([5,1])
                    with ca2:
                        st.markdown(
                            f"<div style='font-size:.74rem;padding:.1rem 0;'>"
                            f"<b>{t}</b><br>"
                            f"<span style='color:#94a3b8;font-size:.66rem;'>{name}</span></div>",
                            unsafe_allow_html=True)
                    with cb2:
                        if already:
                            st.markdown("<div style='padding-top:.3rem;'>✅</div>",
                                        unsafe_allow_html=True)
                        elif st.button("＋",key=f"h_{t}_{sel_grp}"):
                            add_t(sel_grp,t)
                            st.success(f"Added {t}")
                            st.rerun()
            else:
                st.caption("Not found in DB.")
        mt=st.text_input("",placeholder="Manual: SBIN.NS",
                         key="mt",label_visibility="collapsed")
        if st.button("Add ticker",use_container_width=True,key="mt_btn"):
            t=mt.strip().upper()
            if t and t not in tickers_now:
                add_t(sel_grp,t)
                st.success(f"Added {t}!")
                st.rerun()
            elif t in tickers_now:
                st.warning("Already in list.")

    st.markdown("---")

    # Stock list
    tickers_list = [t for t in get_tickers(sel_grp) if t!="__init__"]
    if not tickers_list:
        st.caption("No stocks. Add above ↑")
    else:
        st.markdown(f"<div style='font-size:.75rem;font-weight:600;color:#7b8599;"
                    f"margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.06em;'>"
                    f"{sel_grp} · {len(tickers_list)} stocks</div>",
                    unsafe_allow_html=True)

        for t in tickers_list:
            is_sel = st.session_state.sel_ticker == t
            pd_data = fetch_price(t)
            p   = pd_data["price"]
            pr  = pd_data["prev"]
            nm  = pd_data["name"]

            if p and pr and pr>0:
                chgp_l = (p-pr)/pr*100
                cc2    = "#0ea371" if chgp_l>=0 else "#e53935"
                bg_c2  = "#edfbf4" if chgp_l>=0 else "#fef2f2"
                arr2   = "▲" if chgp_l>=0 else "▼"
                chg_s  = f"{arr2}{abs(chgp_l):.2f}%"
                p_s    = f"{p:,.1f}"
            else:
                cc2,bg_c2,chg_s = "#7b8599","#f8f9fc","—"
                p_s = f"{p:,.1f}" if p else "—"

            sel_bg = "#eff6ff" if is_sel else "white"
            sel_bdr = "2px solid #2563eb" if is_sel else "1px solid #e6e9f0"

            st.markdown(f"""
            <div style='background:{sel_bg};border:{sel_bdr};border-radius:8px;
                        padding:.6rem .8rem;margin-bottom:.35rem;'>
              <div style='display:flex;justify-content:space-between;align-items:center;'>
                <div>
                  <div style='font-size:.8rem;font-weight:700;color:#0b1120;
                              font-family:"JetBrains Mono",monospace;'>{t}</div>
                  <div style='font-size:.68rem;color:#7b8599;max-width:120px;
                              overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'>{nm[:20]}</div>
                </div>
                <div style='text-align:right;'>
                  <div style='font-size:.8rem;font-weight:600;color:#0b1120;
                              font-family:"JetBrains Mono",monospace;'>{p_s}</div>
                  <div style='font-size:.68rem;font-weight:600;color:{cc2};
                              background:{bg_c2};padding:.05rem .3rem;
                              border-radius:4px;'>{chg_s}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            ba,bb2 = st.columns([3,1])
            with ba:
                if st.button(
                    f"{'▶' if is_sel else '▷'} Analyse {t}",
                    key=f"sel_{t}_{sel_grp}",
                    use_container_width=True,
                    type="primary" if is_sel else "secondary"
                ):
                    st.session_state.sel_ticker = t
                    st.rerun()
            with bb2:
                if st.button("✕",key=f"rm_{t}_{sel_grp}",help=f"Remove {t}"):
                    del_t(sel_grp,t)
                    if st.session_state.sel_ticker==t:
                        st.session_state.sel_ticker=None
                    st.success(f"Removed {t}")
                    st.rerun()

# ══ RIGHT PANEL ══════════════════════════════════════════════
with right_col:
    sel = st.session_state.sel_ticker

    if not sel:
        st.markdown("""
        <div style='display:flex;flex-direction:column;align-items:center;
                    justify-content:center;min-height:55vh;text-align:center;
                    padding:3rem 2rem;'>
          <div style='font-size:3rem;margin-bottom:1rem;'>📊</div>
          <div style='font-size:1.4rem;font-weight:700;color:#0b1120;margin-bottom:.5rem;'>
            Stock Analysis Pro v4.0
          </div>
          <div style='font-size:.9rem;color:#64748b;max-width:440px;line-height:1.75;'>
            Select any stock from the left panel to view its complete analysis.
          </div>
          <div style='margin-top:1.5rem;display:flex;gap:.6rem;flex-wrap:wrap;justify-content:center;'>
            <span class='badge bb'>📈 Candlestick</span>
            <span class='badge bg'>Graham/DCF IV</span>
            <span class='badge by'>Piotroski F-Score</span>
            <span class='badge bn'>AI Score 0–100</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        render_analysis(sel)

# Footer
st.markdown("""
<div style='text-align:center;font-size:.68rem;color:#94a3b8;
            padding:.75rem 0 1.5rem;border-top:1px solid #e6e9f0;margin-top:1rem;'>
  📊 Stock Analysis Pro v4.0 · Money Financial Services ·
  Data: Yahoo Finance · Educational use only · Not SEBI advice
</div>
""", unsafe_allow_html=True)
