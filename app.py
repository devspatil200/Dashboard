"""
Stock Analysis Pro — v4.1
Author  : Money Financial Services
Features: Google Trends · VPA · Promoter Activity · Special Picks · Piotroski · Graham DCF
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3, datetime, math, time
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
  --border:#e6e9f0; --text1:#0b1120; --text2:#3d4a63; --text3:#7b8599;
  --green:#0ea371; --green-bg:#edfbf4;
  --red:#e53935;   --red-bg:#fef2f2;
  --blue:#2563eb;  --blue-bg:#eff6ff;
  --gold:#d97706;  --purple:#7c3aed;
  --radius:8px; --radius2:12px;
  --shadow:0 1px 4px rgba(11,17,32,.06),0 4px 20px rgba(11,17,32,.04);
}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background:var(--bg1)!important;color:var(--text1)!important;}
section[data-testid="stSidebar"]{display:none!important;}
button[data-testid="collapsedControl"]{display:none!important;}
.block-container{padding:0.5rem 1rem 3rem 1rem!important;max-width:100%!important;}
.card{background:var(--bg0);border:1px solid var(--border);border-radius:var(--radius2);padding:1.1rem 1.25rem;box-shadow:var(--shadow);margin-bottom:0.8rem;}
.m-label{font-size:.68rem;font-weight:600;text-transform:uppercase;letter-spacing:.07em;color:var(--text3);margin-bottom:.25rem;}
.m-value{font-size:1.4rem;font-weight:700;color:var(--text1);line-height:1.1;font-family:'JetBrains Mono',monospace;}
.m-sub{font-size:.72rem;color:var(--text3);margin-top:.15rem;}
.sec{font-size:.88rem;font-weight:700;color:var(--text1);border-left:3px solid var(--blue);padding-left:.6rem;margin:1.5rem 0 .8rem;}
.badge{display:inline-block;padding:.2rem .55rem;border-radius:999px;font-size:.7rem;font-weight:700;}
.bg{background:#dcfce7;color:#15803d;} .by{background:#fef9c3;color:#854d0e;}
.br{background:#fee2e2;color:#b91c1c;} .bb{background:#dbeafe;color:#1d4ed8;}
.bn{background:#f1f5f9;color:#475569;} .bpu{background:#ede9fe;color:#6d28d9;}
.pb-w{background:#e9ecf3;border-radius:999px;height:6px;width:100%;margin:.35rem 0;}
.pb-f{height:6px;border-radius:999px;}
.ck{display:flex;align-items:flex-start;gap:.5rem;padding:.4rem .7rem;border-radius:7px;margin-bottom:.25rem;}
.ck-n{font-size:.8rem;font-weight:600;} .ck-s{font-size:.7rem;color:var(--text3);}
.alert{border-radius:var(--radius);padding:.7rem 1rem;font-size:.82rem;margin:.4rem 0;line-height:1.55;}
.a-info{background:#eff6ff;border:1px solid #bfdbfe;color:#1e40af;}
.a-ok{background:#ecfdf5;border:1px solid #6ee7b7;color:#065f46;}
.a-warn{background:#fffbeb;border:1px solid #fcd34d;color:#92400e;}
.a-danger{background:#fef2f2;border:1px solid #fca5a5;color:#991b1b;}
.a-purple{background:#ede9fe;border:1px solid #c4b5fd;color:#5b21b6;}
.accum{background:linear-gradient(135deg,#fef3c7,#fde68a);border:2px solid #f59e0b;
       border-radius:10px;padding:1rem 1.25rem;margin:.75rem 0;text-align:center;}
.special-card{background:var(--bg0);border:2px solid var(--green);border-radius:var(--radius2);
              padding:1rem 1.25rem;box-shadow:0 0 0 4px #dcfce7;margin-bottom:.8rem;}
.logo-wrap{width:40px;height:40px;border-radius:8px;overflow:hidden;border:1px solid var(--border);
           display:flex;align-items:center;justify-content:center;background:var(--bg1);}
[data-testid="stButton"]>button{border-radius:7px!important;font-family:'Inter',sans-serif!important;font-weight:600!important;font-size:.82rem!important;}
[data-testid="stTextInput"] input{border-radius:7px!important;font-family:'Inter',sans-serif!important;}
[data-testid="stTabs"] [role="tab"]{font-family:'Inter',sans-serif!important;font-weight:600!important;font-size:.82rem!important;}
.stApp>header{display:none!important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# STOCK DATABASE
# ══════════════════════════════════════════════════════════════
STOCK_DB = {
    "Reliance Industries":"RELIANCE.NS","TCS":"TCS.NS","Infosys":"INFY.NS",
    "HDFC Bank":"HDFCBANK.NS","ICICI Bank":"ICICIBANK.NS","Kotak Bank":"KOTAKBANK.NS",
    "Axis Bank":"AXISBANK.NS","SBI":"SBIN.NS","Bajaj Finance":"BAJFINANCE.NS",
    "Bajaj Finserv":"BAJAJFINSV.NS","Wipro":"WIPRO.NS","HCL Tech":"HCLTECH.NS",
    "Tech Mahindra":"TECHM.NS","L&T":"LT.NS","ITC":"ITC.NS",
    "HUL":"HINDUNILVR.NS","Nestle India":"NESTLEIND.NS","Asian Paints":"ASIANPAINT.NS",
    "Maruti Suzuki":"MARUTI.NS","Tata Motors":"TATAMOTORS.NS","Mahindra M&M":"M&M.NS",
    "Sun Pharma":"SUNPHARMA.NS","Dr Reddys":"DRREDDY.NS","Cipla":"CIPLA.NS",
    "Divis Lab":"DIVISLAB.NS","Apollo Hospitals":"APOLLOHOSP.NS","ONGC":"ONGC.NS",
    "Power Grid":"POWERGRID.NS","NTPC":"NTPC.NS","Coal India":"COALINDIA.NS",
    "Titan":"TITAN.NS","Tata Steel":"TATASTEEL.NS","JSW Steel":"JSWSTEEL.NS",
    "Hindalco":"HINDALCO.NS","UltraTech Cement":"ULTRACEMCO.NS",
    "Adani Ports":"ADANIPORTS.NS","Adani Enterprises":"ADANIENT.NS",
    "Shriram Finance":"SHRIRAMFIN.NS","Muthoot Finance":"MUTHOOTFIN.NS",
    "IDFC First Bank":"IDFCFIRSTB.NS","IndusInd Bank":"INDUSINDBK.NS",
    "Bank of Baroda":"BANKBARODA.NS","PNB":"PNB.NS","Canara Bank":"CANBK.NS",
    "Federal Bank":"FEDERALBNK.NS","Yes Bank":"YESBANK.NS","Paytm":"PAYTM.NS",
    "Zomato":"ZOMATO.NS","Nykaa":"NYKAA.NS","Tata Power":"TATAPOWER.NS",
    "Tata Consumer":"TATACONSUM.NS","Godrej Consumer":"GODREJCP.NS",
    "Pidilite":"PIDILITIND.NS","Berger Paints":"BERGEPAINT.NS","Dabur":"DABUR.NS",
    "Marico":"MARICO.NS","Britannia":"BRITANNIA.NS","Havells":"HAVELLS.NS",
    "Dixon Tech":"DIXON.NS","Hero MotoCorp":"HEROMOTOCO.NS","Bajaj Auto":"BAJAJ-AUTO.NS",
    "Eicher Motors":"EICHERMOT.NS","Ashok Leyland":"ASHOKLEY.NS","IndiGo":"INDIGO.NS",
    "Lupin":"LUPIN.NS","Biocon":"BIOCON.NS","Torrent Pharma":"TORNTPHARM.NS",
    "Aurobindo Pharma":"AUROPHARMA.NS","Mankind Pharma":"MANKIND.NS","DLF":"DLF.NS",
    "Lodha":"LODHA.NS","Varun Beverages":"VBL.NS","Mphasis":"MPHASIS.NS",
    "LTIMindtree":"LTIM.NS","Persistent Systems":"PERSISTENT.NS","Coforge":"COFORGE.NS",
    "BSE":"BSE.NS","MCX":"MCX.NS","Angel One":"ANGELONE.NS","CDSL":"CDSL.NS",
    "Polycab":"POLYCAB.NS","Siemens India":"SIEMENS.NS","ABB India":"ABB.NS",
    "BEL":"BEL.NS","HAL":"HAL.NS","IRCTC":"IRCTC.NS","IRFC":"IRFC.NS",
    "RVNL":"RVNL.NS","Max Healthcare":"MAXHEALTH.NS","NHPC":"NHPC.NS",
    "Torrent Power":"TORNTPOWER.NS","Grasim":"GRASIM.NS",
}

DEFAULT_GROUPS = {
    "Watchlist":["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS"],
    "Banking":["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS"],
    "IT Sector":["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Pharma":["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","DIVISLAB.NS"],
    "Special Picks":["RELIANCE.NS","TCS.NS","INFY.NS"],
}

# ══════════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════════
DB = "stock_v41.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS grp_tickers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grp TEXT NOT NULL, ticker TEXT NOT NULL, added_at TEXT,
        UNIQUE(grp, ticker))""")
    c.execute("""CREATE TABLE IF NOT EXISTS notes (
        ticker TEXT PRIMARY KEY, content TEXT, updated_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS special_picks (
        ticker TEXT PRIMARY KEY, added_at TEXT)""")
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

# ══════════════════════════════════════════════════════════════
# DATA FETCHER  (fully try-except protected)
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def fetch_all(ticker):
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
        return {"info":info,"hist":hist,"fin":fin,"bs":bs,"cf":cf,
                "major_holders":mh,"inst_holders":ih}
    except Exception as e:
        return {"info":{},"hist":pd.DataFrame(),"fin":pd.DataFrame(),
                "bs":pd.DataFrame(),"cf":pd.DataFrame(),
                "major_holders":pd.DataFrame(),"inst_holders":pd.DataFrame()}

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

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_trends(keyword):
    """Google Trends via pytrends — returns (interest_df, error_str)"""
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl='en-IN', tz=330, timeout=(10,25))
        kw = keyword.replace(".NS","").replace(".BO","")
        pt.build_payload([kw], cat=0, timeframe='today 1-m', geo='IN')
        df = pt.interest_over_time()
        if df.empty or kw not in df.columns:
            return None, "Trends data not available for this ticker"
        return df[[kw]], None
    except ImportError:
        return None, "pytrends not installed"
    except Exception as e:
        return None, f"Trends data not available for this ticker"

# ══════════════════════════════════════════════════════════════
# SAFE HELPERS
# ══════════════════════════════════════════════════════════════
def _v(d, *keys, default=None):
    for k in keys:
        try:
            val = d.get(k) if isinstance(d,dict) else None
            if val is not None and not(isinstance(val,float) and math.isnan(val)):
                return val
        except Exception:
            pass
    return default

def _row(df, *names):
    try:
        if df is None or df.empty: return None
        for name in names:
            for idx in df.index:
                if name.lower() in str(idx).lower():
                    s = df.loc[idx].dropna()
                    if not s.empty: return s
    except Exception:
        pass
    return None

def _latest(s):
    try:
        if s is None: return None
        s2 = s.dropna()
        return float(s2.iloc[0]) if not s2.empty else None
    except Exception:
        return None

def safe_div(a, b, default=None):
    try:
        if b is None or b == 0: return default
        return a / b
    except Exception:
        return default

# ══════════════════════════════════════════════════════════════
# METRICS BUILDER  (with fallbacks + zero-division protection)
# ══════════════════════════════════════════════════════════════
def build_m(data):
    info,fin,bs,cf,hist = (data["info"],data["fin"],data["bs"],
                           data["cf"],data["hist"])
    m = {}
    # Identity
    m["name"]    = _v(info,"longName","shortName",default=None)
    m["sector"]  = _v(info,"sector",default="—")
    m["industry"]= _v(info,"industry",default="—")
    m["exchange"]= _v(info,"exchange",default="—")
    m["currency"]= _v(info,"currency",default="INR")
    m["website"] = _v(info,"website",default=None)
    # Price
    m["price"]   = _v(info,"regularMarketPrice","currentPrice",default=None)
    m["prev"]    = _v(info,"regularMarketPreviousClose",default=None)
    m["mktcap"]  = _v(info,"marketCap",default=None)
    m["beta"]    = _v(info,"beta",default=None)
    m["target"]  = _v(info,"targetMeanPrice",default=None)
    # Valuation
    m["pe"]      = _v(info,"trailingPE",default=None)
    m["fpe"]     = _v(info,"forwardPE",default=None)
    m["pb"]      = _v(info,"priceToBook",default=None)
    m["ps"]      = _v(info,"priceToSalesTrailing12Months",default=None)
    m["peg"]     = _v(info,"pegRatio",default=None)
    # Profitability
    m["roe"]     = _v(info,"returnOnEquity",default=None)
    m["roa"]     = _v(info,"returnOnAssets",default=None)
    m["pm"]      = _v(info,"profitMargins",default=None)
    m["gm"]      = _v(info,"grossMargins",default=None)
    m["om"]      = _v(info,"operatingMargins",default=None)
    # Debt
    m["de"]      = _v(info,"debtToEquity",default=None)
    m["cr"]      = _v(info,"currentRatio",default=None)
    m["qr"]      = _v(info,"quickRatio",default=None)
    # Cash Flow
    m["fcf"]     = _v(info,"freeCashflow",default=None)
    m["ocf"]     = _v(info,"operatingCashflow",default=None)
    # Growth
    m["rg"]      = _v(info,"revenueGrowth",default=None)
    m["eg"]      = _v(info,"earningsGrowth",default=None)
    m["eps"]     = _v(info,"trailingEps",default=None)
    m["feps"]    = _v(info,"forwardEps",default=None)
    m["dy"]      = _v(info,"dividendYield",default=None)

    # ── Fallback ROE ──
    if m["roe"] is None:
        ni = _latest(_row(fin,"Net Income"))
        eq = _latest(_row(bs,"Stockholders Equity","Total Stockholder Equity"))
        m["roe"] = safe_div(ni, abs(eq)) if ni else None

    # ── Fallback ROA ──
    if m["roa"] is None:
        ni = _latest(_row(fin,"Net Income"))
        ta = _latest(_row(bs,"Total Assets"))
        m["roa"] = safe_div(ni, abs(ta)) if ni else None

    # ── Fallback PM ──
    if m["pm"] is None:
        ni  = _latest(_row(fin,"Net Income"))
        rev = _latest(_row(fin,"Total Revenue"))
        m["pm"] = safe_div(ni, abs(rev)) if ni else None

    # ── Fallback D/E ──
    if m["de"] is None:
        td = _latest(_row(bs,"Total Debt","Long Term Debt"))
        eq = _latest(_row(bs,"Stockholders Equity","Total Stockholder Equity"))
        if td is not None and eq:
            m["de"] = safe_div(td, abs(eq), default=None)
            if m["de"] is not None: m["de"] *= 100

    # ── Fallback FCF ──
    if m["fcf"] is None:
        ocf  = _latest(_row(cf,"Operating Cash Flow","Cash From Operations"))
        capx = _latest(_row(cf,"Capital Expenditure","Purchases Of Property Plant And Equipment"))
        if ocf is not None:
            m["ocf"] = ocf
            m["fcf"] = ocf + (capx if capx else 0)

    # ── Technical from hist ──
    if not hist.empty:
        try:
            close = hist["Close"]
            m["ph"]    = float(close.iloc[-1])
            m["vol"]   = float(hist["Volume"].iloc[-1])
            m["v20"]   = float(hist["Volume"].rolling(20).mean().iloc[-1]) if len(hist)>=20 else None
            m["d50"]   = float(close.rolling(50).mean().iloc[-1])  if len(close)>=50  else None
            m["d200"]  = float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else None
            m["h52"]   = float(close.rolling(252).max().iloc[-1])  if len(close)>=252 else float(close.max())
            m["l52"]   = float(close.rolling(252).min().iloc[-1])  if len(close)>=252 else float(close.min())
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
            m["macd"]  = float(macd.iloc[-1])
            m["msig"]  = float(sig.iloc[-1])
            m["mh"]    = float((macd - sig).iloc[-1])
            # Volatility (20-day std / mean)
            m["vol_pct"] = float(close.pct_change().rolling(20).std().iloc[-1] * 100) if len(close)>=20 else None
            # VPA — Institutional buying detection
            m["vpa_dates"] = []
            if m["v20"] and m["v20"] > 0:
                vpa_mask = (hist["Close"] > hist["Close"].shift(1)) & (hist["Volume"] > 2 * hist["Volume"].rolling(20).mean())
                m["vpa_dates"] = list(hist.index[vpa_mask])
        except Exception:
            for k in ["ph","vol","v20","d50","d200","h52","l52","rsi","macd","msig","mh","vol_pct","vpa_dates"]:
                m[k] = None
    else:
        for k in ["ph","vol","v20","d50","d200","h52","l52","rsi","macd","msig","mh","vol_pct","vpa_dates"]:
            m[k] = None

    return m

# ══════════════════════════════════════════════════════════════
# PIOTROSKI F-SCORE
# ══════════════════════════════════════════════════════════════
def piotroski(data):
    info,fin,bs,cf = data["info"],data["fin"],data["bs"],data["cf"]
    C = []

    def _l(df, *n): return _latest(_row(df,*n))
    def _lp(df, *n):
        r = _row(df,*n)
        if r is None or len(r.dropna())<2: return None
        return float(r.dropna().iloc[1])

    ni_c=_l(fin,"Net Income"); ni_p=_lp(fin,"Net Income")
    rev_c=_l(fin,"Total Revenue"); rev_p=_lp(fin,"Total Revenue")
    ta_c=_l(bs,"Total Assets"); ta_p=_lp(bs,"Total Assets")
    ocf=_l(cf,"Operating Cash Flow","Cash From Operations")
    roa=_v(info,"returnOnAssets",default=None)
    if roa is None and ni_c and ta_c and ta_c!=0:
        roa = safe_div(ni_c, ta_c)

    def add(g,n,p,note): C.append({"g":g,"n":n,"p":p,"note":note})

    add("Profitability","F1 — ROA Positive",
        roa is not None and roa>0, f"ROA={roa*100:.1f}%" if roa else "N/A")
    add("Profitability","F2 — OCF Positive",
        ocf is not None and ocf>0, f"OCF=₹{ocf/1e7:.1f}Cr" if ocf else "N/A")
    if roa is not None and ta_p and ni_p and ta_p!=0:
        rp = safe_div(ni_p, ta_p, 0)
        add("Profitability","F3 — ROA Improving YoY", roa>rp,
            f"Curr {roa*100:.1f}% vs Prev {rp*100:.1f}%" if rp else "N/A")
    else:
        add("Profitability","F3 — ROA Improving YoY",False,"Insufficient data")

    if ocf and ta_c and ta_c!=0 and roa is not None:
        accrual = safe_div(ocf, ta_c, 0)
        add("Profitability","F4 — Cash > Paper Earnings",
            accrual > roa, f"OCF/TA={accrual*100:.1f}% vs ROA={roa*100:.1f}%" if accrual else "N/A")
    else:
        add("Profitability","F4 — Cash > Paper Earnings",False,"N/A")

    ltd_r = _row(bs,"Long Term Debt")
    if ltd_r is not None and len(ltd_r.dropna())>=2 and ta_c and ta_p:
        lv = ltd_r.dropna()
        rc_ = safe_div(float(lv.iloc[0]), ta_c, 0)
        rp_ = safe_div(float(lv.iloc[1]), ta_p, 0)
        add("Leverage","F5 — Debt Ratio Decreasing", rc_<rp_,
            f"Curr {rc_*100:.1f}% vs Prev {rp_*100:.1f}%")
    else:
        add("Leverage","F5 — Debt Ratio Decreasing",False,"N/A")

    ca_r=_row(bs,"Current Assets"); cl_r=_row(bs,"Current Liabilities")
    if ca_r is not None and cl_r is not None and len(ca_r.dropna())>=2:
        cav=ca_r.dropna(); clv=cl_r.dropna()
        cc = safe_div(float(cav.iloc[0]), float(clv.iloc[0]))
        cp_ = safe_div(float(cav.iloc[1]), float(clv.iloc[1]))
        add("Leverage","F6 — Current Ratio Improving",
            bool(cc and cp_ and cc>cp_),
            f"Curr {cc:.2f} vs Prev {cp_:.2f}" if cc and cp_ else "N/A")
    else:
        cr_i=_v(info,"currentRatio",default=None)
        add("Leverage","F6 — Current Ratio > 1.5",
            cr_i is not None and cr_i>1.5,
            f"CR={cr_i:.2f}" if cr_i else "N/A")

    sh_r=_row(bs,"Ordinary Shares Number","Common Stock Shares Outstanding")
    if sh_r is not None and len(sh_r.dropna())>=2:
        sv=sh_r.dropna()
        add("Leverage","F7 — No Dilution",float(sv.iloc[0])<=float(sv.iloc[1]),
            f"Curr {float(sv.iloc[0])/1e7:.2f}Cr vs Prev {float(sv.iloc[1])/1e7:.2f}Cr")
    else:
        add("Leverage","F7 — No Dilution",False,"N/A")

    gp_r=_row(fin,"Gross Profit")
    if gp_r is not None and len(gp_r.dropna())>=2 and rev_c and rev_p:
        gv=gp_r.dropna()
        gmc=safe_div(float(gv.iloc[0]),rev_c,0); gmp=safe_div(float(gv.iloc[1]),rev_p,0)
        add("Efficiency","F8 — Gross Margin Improving",gmc>gmp,
            f"Curr {gmc*100:.1f}% vs Prev {gmp*100:.1f}%")
    else:
        gm_i=_v(info,"grossMargins",default=None)
        add("Efficiency","F8 — Gross Margin > 20%",
            gm_i is not None and gm_i>0.20,
            f"GM={gm_i*100:.1f}%" if gm_i else "N/A")

    if rev_c and rev_p and ta_c and ta_p:
        at_c=safe_div(rev_c,ta_c,0); at_p=safe_div(rev_p,ta_p,0)
        add("Efficiency","F9 — Asset Turnover Improving",at_c>at_p,
            f"Curr {at_c:.2f}x vs Prev {at_p:.2f}x")
    else:
        add("Efficiency","F9 — Asset Turnover Improving",False,"Insufficient data")

    return sum(1 for c in C if c["p"]), C

# ══════════════════════════════════════════════════════════════
# INTRINSIC VALUE
# ══════════════════════════════════════════════════════════════
def iv_calc(m):
    r = {}
    eps=m.get("eps"); pb=m.get("pb"); price=m.get("price") or m.get("ph")
    bvps = safe_div(price, pb) if (pb and pb>0 and price) else None
    r["graham"] = math.sqrt(22.5*eps*bvps) if(eps and eps>0 and bvps and bvps>0) else None
    g=m.get("eg") or m.get("rg")
    if eps and eps>0 and g is not None:
        g2=max(-20,min(50,g*100))
        dcf=eps*(8.5+2*g2)*4.4/7.5
        r["dcf"] = dcf if dcf>0 else None
    else:
        r["dcf"] = None
    # Analyst target upside
    target = m.get("target")
    if target and price and price>0:
        r["analyst_upside"] = safe_div(target-price, price, 0)*100
        r["analyst_target"] = target
    else:
        r["analyst_upside"] = None; r["analyst_target"] = None

    valid=[v for v in [r.get("graham"),r.get("dcf")] if v]
    if valid and price:
        avg=sum(valid)/len(valid)
        r["avg"]=avg; r["mos"]=safe_div(avg-price,avg,0)*100
        r["up"]=safe_div(avg-price,price,0)*100
    else:
        r["avg"]=r["mos"]=r["up"]=None
    return r

# ══════════════════════════════════════════════════════════════
# AI SCORE  (0-100)
# ══════════════════════════════════════════════════════════════
def ai_score(m, pio, iv):
    bd={}; price=m.get("price") or m.get("ph") or 0
    v=0
    pe=m.get("pe")
    if pe: v+=10 if pe<15 else(7 if pe<25 else(4 if pe<40 else 0))
    pb=m.get("pb")
    if pb: v+=10 if pb<1.5 else(7 if pb<3 else(3 if pb<5 else 0))
    bd["Valuation"]=min(v,20)

    p=0
    roe=m.get("roe")
    if roe: p+=8 if roe>0.25 else(5 if roe>0.15 else(2 if roe>0 else 0))
    pm=m.get("pm")
    if pm: p+=7 if pm>0.20 else(4 if pm>0.10 else(1 if pm>0 else 0))
    fcf=m.get("fcf")
    if fcf and fcf>0: p+=5
    bd["Profitability"]=min(p,20)

    h=0
    de=m.get("de")
    if de is not None:
        dr=de/100
        h+=8 if dr<0.3 else(5 if dr<0.7 else(2 if dr<1 else 0))
    cr=m.get("cr")
    if cr: h+=7 if cr>2 else(4 if cr>1.5 else(1 if cr>1 else 0))
    h+=min(pio,5)
    bd["Financial Health"]=min(h,20)

    t=0
    d200=m.get("d200"); d50=m.get("d50"); rsi=m.get("rsi")
    if price and d200:
        pct=safe_div(price-d200,d200,0)*100
        t+=8 if 0<pct<20 else(4 if pct>=20 else(3 if pct>-10 else 0))
    if price and d50 and price>d50: t+=5
    if rsi:
        t+=7 if 40<=rsi<=65 else(4 if(30<=rsi<40 or 65<rsi<=70) else(2 if rsi<30 else 0))
    bd["Technical"]=min(t,20)

    g=0
    rg=m.get("rg")
    if rg: g+=7 if rg>0.20 else(4 if rg>0.10 else(1 if rg>0 else 0))
    eg=m.get("eg")
    if eg: g+=7 if eg>0.20 else(4 if eg>0.10 else(1 if eg>0 else 0))
    up=iv.get("up")
    if up: g+=6 if up>30 else(3 if up>10 else(1 if up>0 else 0))
    bd["Growth"]=min(g,20)

    total=sum(bd.values())
    if total>=75:   grade,color="Excellent — Strong Buy","#059669"
    elif total>=60: grade,color="Good — Buy","#2563eb"
    elif total>=45: grade,color="Average — Watch","#d97706"
    elif total>=30: grade,color="Weak — Caution","#ea580c"
    else:           grade,color="Poor — Avoid","#dc2626"
    return total, bd, grade, color

# ══════════════════════════════════════════════════════════════
# FORMATTERS
# ══════════════════════════════════════════════════════════════
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
    return (f"<div class='card'><div class='m-label'>{lbl}</div>"
            f"<div class='m-value' style='color:{vc};'>{val}</div>"
            + (f"<div class='m-sub'>{sub}</div>" if sub else "")
            + "</div>")

def pb_bar(pct,color="#2563eb"):
    pct=max(0,min(100,pct))
    return (f"<div class='pb-w'><div class='pb-f' "
            f"style='width:{pct}%;background:{color};'></div></div>")

# ══════════════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════════════
def candle_chart(hist, d50, d200, vpa_dates=None):
    if hist.empty: return None
    fig = make_subplots(rows=2,cols=1,shared_xaxes=True,
                        vertical_spacing=0.03,row_heights=[0.75,0.25])
    fig.add_trace(go.Candlestick(
        x=hist.index,open=hist["Open"],high=hist["High"],
        low=hist["Low"],close=hist["Close"],name="Price",
        increasing_line_color="#0ea371",decreasing_line_color="#e53935",
        increasing_fillcolor="#0ea371",decreasing_fillcolor="#e53935",
    ),row=1,col=1)
    if d50 is not None:
        fig.add_trace(go.Scatter(
            x=hist.index,y=hist["Close"].rolling(50).mean(),
            name="50 DMA",line=dict(color="#2563eb",width=1.5),
        ),row=1,col=1)
    if d200 is not None:
        fig.add_trace(go.Scatter(
            x=hist.index,y=hist["Close"].rolling(200).mean(),
            name="200 DMA",line=dict(color="#d97706",width=1.5,dash="dot"),
        ),row=1,col=1)
    # VPA markers — institutional buying
    if vpa_dates:
        vpa_prices = [hist.loc[d,"High"]*1.01 if d in hist.index else None for d in vpa_dates]
        vpa_prices = [p for p in vpa_prices if p is not None]
        vpa_dates2 = [d for d,p in zip(vpa_dates,[hist.loc[d,"High"]*1.01 if d in hist.index else None for d in vpa_dates]) if p is not None]
        if vpa_dates2:
            fig.add_trace(go.Scatter(
                x=vpa_dates2, y=vpa_prices,
                mode="markers", name="🏦 Inst. Buying",
                marker=dict(symbol="triangle-up",size=12,color="#7c3aed",
                            line=dict(color="#ffffff",width=1.5)),
            ),row=1,col=1)
    colors=["#0ea371" if c>=o else "#e53935"
            for c,o in zip(hist["Close"],hist["Open"])]
    fig.add_trace(go.Bar(
        x=hist.index,y=hist["Volume"],name="Volume",
        marker_color=colors,opacity=0.55,showlegend=False),row=2,col=1)
    fig.update_layout(
        height=460,margin=dict(l=0,r=0,t=24,b=0),
        paper_bgcolor="#ffffff",plot_bgcolor="#ffffff",
        template="plotly_white",
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
    fig=go.Figure(go.Indicator(
        mode="gauge+number",value=score,
        number={"font":{"size":38,"family":"JetBrains Mono","color":color}},
        gauge=dict(
            axis=dict(range=[0,100],tickfont=dict(size=10,color="#7b8599"),nticks=6),
            bar=dict(color=color,thickness=0.25),
            bgcolor="white",borderwidth=0,
            steps=[
                dict(range=[0,30],color="#fef2f2"),dict(range=[30,45],color="#fff7ed"),
                dict(range=[45,60],color="#fffbeb"),dict(range=[60,75],color="#eff6ff"),
                dict(range=[75,100],color="#ecfdf5"),
            ],
            threshold=dict(line=dict(color=color,width=3),thickness=0.75,value=score)
        ),
        domain={"x":[0,1],"y":[0,1]},
        title={"text":grade,"font":{"size":11,"family":"Inter","color":"#3d4a63"}}
    ))
    fig.update_layout(height=210,margin=dict(l=20,r=20,t=30,b=0),
                      paper_bgcolor="#ffffff",template="plotly_white",
                      font=dict(family="Inter"))
    return fig

def trends_chart(df, kw):
    fig=go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,y=df[kw],name="Search Interest",
        line=dict(color="#7c3aed",width=2),fill="tozeroy",
        fillcolor="rgba(124,58,237,0.08)"
    ))
    fig.update_layout(
        height=200,margin=dict(l=0,r=0,t=20,b=0),
        paper_bgcolor="#ffffff",plot_bgcolor="#ffffff",
        template="plotly_white",
        font=dict(family="Inter",size=11,color="#3d4a63"),
        showlegend=False,
        yaxis=dict(range=[0,105],tickfont=dict(size=10),gridcolor="#f1f3f8"),
        xaxis=dict(tickfont=dict(size=10),gridcolor="#f1f3f8"),
    )
    return fig

# ══════════════════════════════════════════════════════════════
# LOGO HELPER
# ══════════════════════════════════════════════════════════════
def get_logo_url(website):
    try:
        if not website: return None
        domain = website.replace("https://","").replace("http://","").split("/")[0]
        return f"https://logo.clearbit.com/{domain}"
    except Exception:
        return None

# ══════════════════════════════════════════════════════════════
# FULL ANALYSIS RENDERER
# ══════════════════════════════════════════════════════════════
def render_analysis(ticker):
    with st.spinner(f"Loading {ticker}…"):
        data = fetch_all(ticker)
        m    = build_m(data)

    price = m.get("price") or m.get("ph")
    if not price:
        st.markdown(
            f"<div class='alert a-danger'>❌ Could not fetch <b>{ticker}</b>. "
            "Verify ticker — NSE: add .NS · BSE: add .BO</div>",
            unsafe_allow_html=True)
        return

    pio_s, pio_c = piotroski(data)
    iv            = iv_calc(m)
    total, bd, grade, color = ai_score(m, pio_s, iv)
    hist          = data.get("hist", pd.DataFrame())

    prev=m.get("prev"); chg=price-prev if prev else 0
    chgp=safe_div(chg,prev,0)*100
    cc="#0ea371" if chg>=0 else "#e53935"; arr="▲" if chg>=0 else "▼"
    curr=m.get("currency","INR")

    # ── Logo + Header ──
    logo_url = get_logo_url(m.get("website"))
    logo_html = (f'<img src="{logo_url}" width="36" height="36" '
                 f'style="border-radius:8px;object-fit:contain;border:1px solid #e6e9f0;" '
                 f'onerror="this.style.display=\'none\'"> ')  if logo_url else ""

    st.markdown(f"""
    <div class='card' style='margin-bottom:1rem;'>
      <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:.75rem;'>
        <div style='display:flex;align-items:center;gap:.75rem;'>
          {logo_html}
          <div>
            <div style='font-size:1.3rem;font-weight:700;color:#0b1120;line-height:1.2;'>
              {m.get("name") or ticker}
            </div>
            <div style='font-size:.75rem;color:#7b8599;margin-top:.3rem;display:flex;gap:.4rem;flex-wrap:wrap;align-items:center;'>
              <span class='badge bb'>{ticker}</span>
              <span class='badge bn'>{m.get("exchange","—")}</span>
              <span>{m.get("sector","—")} · {m.get("industry","—")}</span>
            </div>
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
            &nbsp;|&nbsp; Target: {fn(m.get("target"))}
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──
    T1,T2,T3,T4,T5,T6 = st.tabs([
        "📋 Fundamentals","📡 Technicals + VPA",
        "📈 Google Trends","🏦 Promoter Activity",
        "🏆 Piotroski + IV","🤖 AI Verdict"
    ])

    # ════ TAB 1 — FUNDAMENTALS ════
    with T1:
        st.markdown("<div class='sec'>Valuation</div>", unsafe_allow_html=True)
        pe_v=m.get("pe")
        pe_c=("#059669" if pe_v and pe_v<25 else "#d97706" if pe_v and pe_v<40 else "#e53935") if pe_v else "#7b8599"
        c1,c2,c3,c4,c5=st.columns(5)
        for col,(l,v,s,vc) in zip([c1,c2,c3,c4,c5],[
            ("Trailing PE",fn(m.get("pe"),1),"< 25 ideal",pe_c),
            ("Forward PE",fn(m.get("fpe"),1),"Estimated","#0b1120"),
            ("Price/Book",fn(m.get("pb"),2),"< 3 ideal","#0b1120"),
            ("Price/Sales",fn(m.get("ps"),2),"Revenue multiple","#0b1120"),
            ("PEG Ratio",fn(m.get("peg"),2),"< 1 undervalued","#0b1120"),
        ]):
            col.markdown(card(l,v,s,vc),unsafe_allow_html=True)

        st.markdown("<div class='sec'>Profitability</div>", unsafe_allow_html=True)
        c1,c2,c3,c4,c5=st.columns(5)
        roe_v=m.get("roe"); pm_v=m.get("pm")
        for col,(l,v,s,vc) in zip([c1,c2,c3,c4,c5],[
            ("ROE",fp(roe_v),"> 15% ideal",
             "#059669" if roe_v and roe_v>0.15 else "#e53935" if roe_v else "#7b8599"),
            ("ROA",fp(m.get("roa")),"Asset return","#0b1120"),
            ("Net Margin",fp(pm_v),"> 10% ideal",
             "#059669" if pm_v and pm_v>0.10 else "#e53935" if pm_v else "#7b8599"),
            ("Gross Margin",fp(m.get("gm")),"Revenue quality","#0b1120"),
            ("Oper. Margin",fp(m.get("om")),"Operating eff.","#0b1120"),
        ]):
            col.markdown(card(l,v,s,vc),unsafe_allow_html=True)

        st.markdown("<div class='sec'>Balance Sheet & Cash Flow</div>", unsafe_allow_html=True)
        c1,c2,c3,c4,c5=st.columns(5)
        de_v=m.get("de"); cr_v=m.get("cr"); fcf_v=m.get("fcf")
        de_r=de_v/100 if de_v is not None else None
        for col,(l,v,s,vc) in zip([c1,c2,c3,c4,c5],[
            ("Debt/Equity",f"{de_r:.2f}x" if de_r is not None else "N/A","< 1x ideal",
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
        c1,c2,c3,c4,c5=st.columns(5)
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

        desc=_v(data["info"],"longBusinessSummary",default="")
        if desc:
            with st.expander("📖 About the Company"):
                st.markdown(f"<p style='font-size:.86rem;line-height:1.8;color:#3d4a63;'>{desc[:1200]}{'…' if len(desc)>1200 else ''}</p>",
                            unsafe_allow_html=True)

    # ════ TAB 2 — TECHNICALS + VPA ════
    with T2:
        st.markdown("<div class='sec'>Candlestick Chart with VPA Signals</div>", unsafe_allow_html=True)
        vpa_dates=m.get("vpa_dates") or []
        fig_c=candle_chart(hist,m.get("d50"),m.get("d200"),vpa_dates)
        if fig_c:
            st.plotly_chart(fig_c,use_container_width=True,config={"displayModeBar":False})
        if vpa_dates:
            st.markdown(f"""<div class='alert a-purple'>
            🏦 <b>Institutional Buying Detected on {len(vpa_dates)} occasions</b><br>
            Price moved UP with Volume > 2× the 20-day average — a classic institutional accumulation signal.
            Last occurrence: <b>{str(vpa_dates[-1])[:10]}</b>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<div class='alert a-info'>ℹ️ No institutional buying signals detected in last 1 year.</div>",
                        unsafe_allow_html=True)

        st.markdown("<div class='sec'>Moving Averages</div>", unsafe_allow_html=True)
        ph=m.get("ph") or price
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(card("Current Price",f"₹{ph:,.2f}","Latest"),unsafe_allow_html=True)
        with c2:
            d50=m.get("d50")
            if d50:
                p50=safe_div(ph-d50,d50,0)*100
                st.markdown(card("50-Day DMA",f"₹{d50:,.2f}",f"{p50:+.1f}%",
                    "#059669" if ph>d50 else "#e53935"),unsafe_allow_html=True)
            else: st.markdown(card("50-Day DMA","N/A","Insufficient"),unsafe_allow_html=True)
        with c3:
            d200=m.get("d200")
            if d200:
                p200=safe_div(ph-d200,d200,0)*100
                st.markdown(card("200-Day DMA",f"₹{d200:,.2f}",f"{p200:+.1f}%",
                    "#059669" if ph>d200 else "#e53935"),unsafe_allow_html=True)
            else: st.markdown(card("200-Day DMA","N/A","Insufficient"),unsafe_allow_html=True)
        with c4:
            rsi_v=m.get("rsi")
            if rsi_v:
                rl="Overbought ⚠️" if rsi_v>70 else("Oversold 🔎" if rsi_v<30 else "Neutral ✅")
                rc="#e53935" if rsi_v>70 else("#d97706" if rsi_v<30 else "#059669")
                st.markdown(card("RSI (14)",f"{rsi_v:.1f}",rl,rc),unsafe_allow_html=True)
            else: st.markdown(card("RSI (14)","N/A",""),unsafe_allow_html=True)

        st.markdown("<div class='sec'>Volume Analysis</div>", unsafe_allow_html=True)
        cv=m.get("vol"); v20=m.get("v20")
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(card("Today's Volume",f"{cv:,.0f}" if cv else "N/A","Shares"),unsafe_allow_html=True)
        with c2: st.markdown(card("20-Day Avg Vol",f"{v20:,.0f}" if v20 else "N/A","Rolling avg"),unsafe_allow_html=True)
        with c3:
            if cv and v20 and v20>0:
                vr=cv/v20
                vc2="#059669" if vr>1.5 else("#e53935" if vr<0.5 else "#d97706")
                vl="📈 High" if vr>1.5 else("📉 Dry" if vr<0.5 else "➡️ Normal")
                st.markdown(card("Vol vs 20D Avg",f"{vr:.2f}×",vl,vc2),unsafe_allow_html=True)
            else: st.markdown(card("Vol vs 20D Avg","N/A",""),unsafe_allow_html=True)
        with c4:
            vol_pct=m.get("vol_pct")
            vc_p="#059669" if vol_pct and vol_pct<3 else("#d97706" if vol_pct and vol_pct<7 else "#e53935")
            st.markdown(card("Price Volatility (20D)",f"{vol_pct:.1f}%" if vol_pct else "N/A",
                "< 5% = stable",vc_p if vol_pct else "#7b8599"),unsafe_allow_html=True)

        h52=m.get("h52"); l52=m.get("l52")
        if h52 and l52 and h52!=l52:
            st.markdown("<div class='sec'>52-Week Range</div>", unsafe_allow_html=True)
            pos=safe_div(ph-l52,h52-l52,0)*100; pfh=safe_div(ph-h52,h52,0)*100
            ca,cb=st.columns([3,1])
            with ca:
                st.markdown(f"""<div class='card'>
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

    # ════ TAB 3 — GOOGLE TRENDS ════
    with T3:
        st.markdown("<div class='sec'>Google Trends — Search Interest (Last 30 Days)</div>",
                    unsafe_allow_html=True)
        kw = ticker.replace(".NS","").replace(".BO","")
        with st.spinner("Fetching Google Trends data…"):
            trends_df, trends_err = fetch_trends(kw)

        if trends_err:
            st.markdown(f"<div class='alert a-warn'>⚠️ {trends_err}</div>",
                        unsafe_allow_html=True)
        elif trends_df is not None and not trends_df.empty:
            # Growth calculation
            half = len(trends_df)//2
            first_half  = trends_df[kw].iloc[:half].mean()
            second_half = trends_df[kw].iloc[half:].mean()
            growth = safe_div(second_half - first_half, first_half, 0) * 100
            vol_pct = m.get("vol_pct") or 999

            # Show chart
            fig_t = trends_chart(trends_df, kw)
            st.plotly_chart(fig_t, use_container_width=True,
                            config={"displayModeBar":False})

            # Metrics
            c1,c2,c3 = st.columns(3)
            with c1: st.markdown(card("Current Interest",f"{trends_df[kw].iloc[-1]:.0f}/100","Google scale"),unsafe_allow_html=True)
            with c2: st.markdown(card("30-Day Growth",f"{growth:+.1f}%","Search trend",
                "#059669" if growth>15 else "#7b8599"),unsafe_allow_html=True)
            with c3: st.markdown(card("Price Volatility",f"{vol_pct:.1f}%" if vol_pct!=999 else "N/A","20-day std",
                "#059669" if vol_pct<5 else "#d97706"),unsafe_allow_html=True)

            # 🚨 Accumulation Zone Detection
            if growth > 15 and vol_pct < 5:
                st.markdown(f"""
                <div class='accum'>
                  <div style='font-size:1.5rem;'>🚨</div>
                  <div style='font-size:1.1rem;font-weight:800;color:#92400e;margin:.3rem 0;'>
                    ACCUMULATION ZONE DETECTED
                  </div>
                  <div style='font-size:.88rem;color:#78350f;line-height:1.6;'>
                    Search interest grew <b>{growth:+.1f}%</b> while price volatility is only <b>{vol_pct:.1f}%</b>.<br>
                    This pattern suggests <b>quiet accumulation</b> — institutions may be buying
                    before a breakout. Monitor closely.
                  </div>
                </div>
                """, unsafe_allow_html=True)
            elif growth > 15:
                st.markdown(f"<div class='alert a-ok'>📈 <b>High search interest growth ({growth:+.1f}%)</b> — "
                            "Rising retail interest. Watch for breakout confirmation.</div>",
                            unsafe_allow_html=True)
            elif growth < -15:
                st.markdown(f"<div class='alert a-warn'>📉 <b>Declining search interest ({growth:+.1f}%)</b> — "
                            "Fading interest. Caution advised.</div>",
                            unsafe_allow_html=True)
            else:
                st.markdown("<div class='alert a-info'>ℹ️ Search interest is stable. No extreme signals detected.</div>",
                            unsafe_allow_html=True)
        else:
            st.markdown("<div class='alert a-warn'>⚠️ Trends data not available for this ticker.</div>",
                        unsafe_allow_html=True)

    # ════ TAB 4 — PROMOTER ACTIVITY ════
    with T4:
        st.markdown("<div class='sec'>Major Holders</div>", unsafe_allow_html=True)
        mh_df = data.get("major_holders", pd.DataFrame())
        if mh_df is not None and not mh_df.empty:
            try:
                # Format major holders
                mh_display = mh_df.copy()
                mh_display.columns = ["Value","Category"]
                styled_rows = ""
                for _, row in mh_display.iterrows():
                    val = str(row.iloc[0])
                    cat = str(row.iloc[1])
                    highlight = "background:#ecfdf5;" if "Insider" in cat or "insider" in cat.lower() else ""
                    styled_rows += f"<tr style='{highlight}'><td style='padding:.5rem .75rem;font-weight:600;font-family:JetBrains Mono,monospace;'>{val}</td><td style='padding:.5rem .75rem;color:#3d4a63;'>{cat}</td></tr>"
                st.markdown(f"""
                <div class='card'>
                <table style='width:100%;border-collapse:collapse;'>
                  <thead>
                    <tr style='background:#f8f9fc;border-bottom:2px solid #e6e9f0;'>
                      <th style='text-align:left;padding:.5rem .75rem;font-size:.75rem;
                                 text-transform:uppercase;letter-spacing:.05em;color:#7b8599;'>%</th>
                      <th style='text-align:left;padding:.5rem .75rem;font-size:.75rem;
                                 text-transform:uppercase;letter-spacing:.05em;color:#7b8599;'>Category</th>
                    </tr>
                  </thead>
                  <tbody>{styled_rows}</tbody>
                </table>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                st.markdown("<div class='alert a-warn'>Could not parse major holders data.</div>",
                            unsafe_allow_html=True)
        else:
            st.markdown("<div class='alert a-info'>Major holders data not available for this ticker.</div>",
                        unsafe_allow_html=True)

        st.markdown("<div class='sec'>Institutional Holders (Top 10)</div>", unsafe_allow_html=True)
        ih_df = data.get("inst_holders", pd.DataFrame())
        if ih_df is not None and not ih_df.empty:
            try:
                display_df = ih_df.head(10).copy()
                # Highlight positive change
                if "Value" in display_df.columns:
                    display_df["Value"] = display_df["Value"].apply(
                        lambda x: f"₹{x/1e7:.1f}Cr" if isinstance(x,(int,float)) and not math.isnan(float(x)) else "N/A")
                if "% Out" in display_df.columns:
                    display_df["% Out"] = display_df["% Out"].apply(
                        lambda x: f"{float(x)*100:.2f}%" if isinstance(x,(int,float)) else str(x))
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                st.markdown("<div class='alert a-info'>🟢 Green rows indicate insider/promoter holdings. "
                            "Rising institutional holding = positive signal.</div>",
                            unsafe_allow_html=True)
            except Exception:
                st.markdown("<div class='alert a-warn'>Could not parse institutional holders.</div>",
                            unsafe_allow_html=True)
        else:
            st.markdown("<div class='alert a-info'>Institutional holders data not available.</div>",
                        unsafe_allow_html=True)

    # ════ TAB 5 — PIOTROSKI + IV ════
    with T5:
        pc="#059669" if pio_s>=7 else("#d97706" if pio_s>=5 else "#e53935")
        pt="Strong 💪" if pio_s>=7 else("Moderate — Monitor" if pio_s>=5 else "Weak ⚠️")
        ca,cb=st.columns([1,2])
        with ca:
            st.markdown(f"""
            <div class='card' style='text-align:center;padding:1.75rem 1rem;'>
              <div style='font-size:.66rem;font-weight:700;text-transform:uppercase;
                          letter-spacing:.07em;color:#7b8599;margin-bottom:.4rem;'>
                PIOTROSKI F-SCORE</div>
              <div style='font-size:5rem;font-weight:800;color:{pc};line-height:1;
                          font-family:"JetBrains Mono",monospace;'>{pio_s}</div>
              <div style='font-size:.76rem;color:#7b8599;margin:.2rem 0 .6rem;'>out of 9</div>
              {pb_bar(pio_s/9*100,pc)}
              <span class='badge {"bg" if pio_s>=7 else "by" if pio_s>=5 else "br"}' style='margin-top:.7rem;font-size:.76rem;padding:.28rem .8rem;'>{pt}</span>
            </div>
            """,unsafe_allow_html=True)
        with cb:
            st.markdown("<div class='sec' style='margin-top:0;'>F-Score Breakdown</div>",
                        unsafe_allow_html=True)
            grps_p={}
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

        st.markdown("<hr style='border:none;border-top:1px solid #e6e9f0;margin:1.25rem 0;'>",
                    unsafe_allow_html=True)
        st.markdown("<div class='sec'>Intrinsic Value</div>", unsafe_allow_html=True)
        curr_p=m.get("price") or m.get("ph")
        c1,c2,c3,c4=st.columns(4)
        with c1:
            gv=iv.get("graham")
            if gv and curr_p:
                diff=safe_div(curr_p-gv,gv,0)*100
                st.markdown(card("Graham Number",f"₹{gv:,.1f}",
                    f"{'Under' if curr_p<gv else 'Over'}valued {abs(diff):.1f}%",
                    "#059669" if curr_p<gv else "#e53935"),unsafe_allow_html=True)
            else: st.markdown(card("Graham Number","N/A","EPS/BVPS unavailable"),unsafe_allow_html=True)
        with c2:
            dv=iv.get("dcf")
            if dv and curr_p:
                diff2=safe_div(curr_p-dv,dv,0)*100
                st.markdown(card("Graham DCF",f"₹{dv:,.1f}",
                    f"{'Under' if curr_p<dv else 'Over'}valued {abs(diff2):.1f}%",
                    "#059669" if curr_p<dv else "#e53935"),unsafe_allow_html=True)
            else: st.markdown(card("Graham DCF","N/A","EPS/Growth unavailable"),unsafe_allow_html=True)
        with c3:
            avg_iv=iv.get("avg"); up_v=iv.get("up"); mos_v=iv.get("mos")
            if avg_iv and curr_p:
                st.markdown(card("Blended IV",f"₹{avg_iv:,.1f}",
                    f"{'↑' if up_v and up_v>0 else '↓'} {abs(up_v):.1f}% | MOS: {mos_v:.1f}%",
                    "#059669" if up_v and up_v>0 else "#e53935"),unsafe_allow_html=True)
            else: st.markdown(card("Blended IV","N/A","Insufficient data"),unsafe_allow_html=True)
        with c4:
            at=iv.get("analyst_target"); au=iv.get("analyst_upside")
            if at and au is not None:
                st.markdown(card("Analyst Target",f"₹{at:,.1f}",
                    f"Upside: {au:+.1f}%",
                    "#059669" if au>0 else "#e53935"),unsafe_allow_html=True)
            else: st.markdown(card("Analyst Target","N/A","Not available"),unsafe_allow_html=True)

        if avg_iv and curr_p:
            if mos_v>20: st.markdown(f"<div class='alert a-ok'>✅ <b>MOS: {mos_v:.1f}%</b> — Significantly undervalued. Upside: {up_v:.1f}%</div>",unsafe_allow_html=True)
            elif mos_v>0: st.markdown(f"<div class='alert a-ok'>✅ <b>MOS: {mos_v:.1f}%</b> — Marginally undervalued. Upside: {up_v:.1f}%</div>",unsafe_allow_html=True)
            elif mos_v>-20: st.markdown(f"<div class='alert a-warn'>⚠️ Near fair value. Overvalued by {abs(mos_v):.1f}%.</div>",unsafe_allow_html=True)
            else: st.markdown(f"<div class='alert a-danger'>🚨 Overvalued by {abs(mos_v):.1f}%. Downside risk: {abs(up_v):.1f}%.</div>",unsafe_allow_html=True)

        # Research notes
        st.markdown("<hr style='border:none;border-top:1px solid #e6e9f0;margin:1.25rem 0;'>",
                    unsafe_allow_html=True)
        st.markdown("<div class='sec' style='margin-top:0;'>📝 Research Notes</div>",
                    unsafe_allow_html=True)
        existing,last_upd=load_note(ticker)
        tmpl=(f"📌 {ticker}  |  📅 {datetime.date.today()}\n\n"
              "🎯 THESIS:\n\n📊 KEY METRICS:\n- PE: \n- ROE: \n- D/E: \n- FCF: \n"
              "- Piotroski: /9\n- AI Score: /100\n- IV: ₹\n- Analyst Target: ₹\n\n"
              "⚠️ RISKS:\n\n🎯 TRADE PLAN:\n- Entry: ₹  Stop: ₹  Target: ₹\n\n✅ DECISION:")
        if st.button("📋 Template",key=f"tmpl_{ticker}"):
            existing=tmpl
        note_txt=st.text_area("",value=existing,height=280,
                              key=f"note_{ticker}",label_visibility="collapsed")
        c1x,c2x=st.columns([3,1])
        with c1x:
            if st.button("💾 Save",key=f"save_{ticker}",
                         use_container_width=True,type="primary"):
                save_note(ticker,note_txt)
                st.success("✅ Saved!")
        with c2x:
            if last_upd:
                st.markdown(f"<div style='font-size:.7rem;color:#94a3b8;padding-top:.5rem;'>Saved: {last_upd}</div>",
                            unsafe_allow_html=True)

    # ════ TAB 6 — AI VERDICT ════
    with T6:
        ca,cb=st.columns([1,2])
        with ca:
            fig_g=gauge_chart(total,grade,color)
            st.plotly_chart(fig_g,use_container_width=True,config={"displayModeBar":False})
        with cb:
            st.markdown("<div class='sec' style='margin-top:0;'>Score by Pillar</div>",
                        unsafe_allow_html=True)
            pcolors={"Valuation":"#2563eb","Profitability":"#059669",
                     "Financial Health":"#7c3aed","Technical":"#d97706","Growth":"#0891b2"}
            for pillar,pts in bd.items():
                pc2=pcolors.get(pillar,"#64748b")
                bc2="bg" if pts>=15 else("by" if pts>=10 else "br")
                st.markdown(f"""
                <div style='background:#fff;border:1px solid #e6e9f0;border-radius:8px;
                            padding:.65rem .9rem;margin-bottom:.4rem;'>
                  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:.25rem;'>
                    <div style='font-size:.82rem;font-weight:600;'>{pillar}</div>
                    <span class='badge {bc2}'>{pts}/20</span>
                  </div>
                  {pb_bar(pts/20*100,pc2)}
                </div>""",unsafe_allow_html=True)

        st.markdown("<div class='sec'>Investment Summary</div>", unsafe_allow_html=True)
        ab="above" if price>(m.get("d200") or 0) else "below"
        if total>=75:
            st.markdown(f"<div class='alert a-ok'><b>{ticker}</b> scores <b>{total}/100 — {grade}</b>. ROE {fp(m.get('roe'))}, D/E {fn(safe_div(m.get('de'),100),2) if m.get('de') else 'N/A'}x. Piotroski {pio_s}/9. Trading {ab} 200 DMA."+(f" IV upside: {iv.get('up'):.1f}%." if iv.get('up') else "")+"</div>",unsafe_allow_html=True)
        elif total>=45:
            st.markdown(f"<div class='alert a-warn'><b>{ticker}</b> scores <b>{total}/100 — {grade}</b>. Mixed signals. Piotroski {pio_s}/9. Use strict stop-loss.</div>",unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='alert a-danger'><b>{ticker}</b> scores <b>{total}/100 — {grade}</b>. Multiple red flags. Piotroski {pio_s}/9. High risk.</div>",unsafe_allow_html=True)
        st.markdown("<div class='alert a-info'>⚠️ Research tool only. Not SEBI registered advice.</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SPECIAL PICKS TAB (standalone section)
# ══════════════════════════════════════════════════════════════
def render_special_picks(tickers_list):
    st.markdown("""
    <div style='background:linear-gradient(135deg,#ecfdf5,#d1fae5);
                border:1px solid #6ee7b7;border-radius:12px;
                padding:1rem 1.25rem;margin-bottom:1rem;'>
      <div style='font-size:1.1rem;font-weight:700;color:#065f46;'>
        ⭐ Special Picks — Auto Screener
      </div>
      <div style='font-size:.82rem;color:#047857;margin-top:.2rem;'>
        Stocks with Piotroski F-Score ≥ 7 AND Undervalued by ≥ 20% (Intrinsic Value)
      </div>
    </div>
    """, unsafe_allow_html=True)

    picks = []
    progress = st.progress(0, text="Screening stocks…")
    total_t = len(tickers_list)

    for i, ticker in enumerate(tickers_list):
        try:
            progress.progress((i+1)/total_t, text=f"Screening {ticker}…")
            data = fetch_all(ticker)
            m    = build_m(data)
            pio_s, _ = piotroski(data)
            iv   = iv_calc(m)

            price = m.get("price") or m.get("ph")
            mos   = iv.get("mos")
            up    = iv.get("up")

            if pio_s >= 7 and mos is not None and mos > 20:
                picks.append({
                    "ticker": ticker,
                    "name":   m.get("name") or ticker,
                    "price":  price,
                    "pio":    pio_s,
                    "iv":     iv.get("avg"),
                    "mos":    mos,
                    "up":     up,
                    "pe":     m.get("pe"),
                    "roe":    m.get("roe"),
                    "website":m.get("website"),
                })
        except Exception:
            pass

    progress.empty()

    if not picks:
        st.markdown("<div class='alert a-warn'>No stocks matched the criteria (Piotroski ≥ 7 AND undervalued ≥ 20%) in the current group. Try adding more stocks or lowering criteria.</div>",
                    unsafe_allow_html=True)
        return

    st.markdown(f"<div style='font-size:.82rem;color:#065f46;font-weight:600;margin-bottom:.75rem;'>"
                f"✅ {len(picks)} stock(s) matched</div>", unsafe_allow_html=True)

    cols = st.columns(min(len(picks), 3))
    for i, pick in enumerate(picks):
        logo_url = get_logo_url(pick["website"])
        logo_html = (f'<img src="{logo_url}" width="32" height="32" '
                     f'style="border-radius:6px;object-fit:contain;border:1px solid #e6e9f0;margin-bottom:.5rem;" '
                     f'onerror="this.style.display=\'none\'">') if logo_url else "⭐"

        with cols[i % 3]:
            st.markdown(f"""
            <div class='special-card'>
              <div style='text-align:center;margin-bottom:.5rem;'>{logo_html}</div>
              <div style='font-size:.8rem;font-weight:700;color:#0b1120;text-align:center;'>{pick["ticker"]}</div>
              <div style='font-size:.7rem;color:#7b8599;text-align:center;margin-bottom:.6rem;'>{(pick["name"] or "")[:22]}</div>
              <div style='display:flex;justify-content:space-between;margin-bottom:.25rem;'>
                <span style='font-size:.72rem;color:#475569;'>Price</span>
                <span style='font-size:.78rem;font-weight:700;font-family:"JetBrains Mono",monospace;'>₹{pick["price"]:,.1f}</span>
              </div>
              <div style='display:flex;justify-content:space-between;margin-bottom:.25rem;'>
                <span style='font-size:.72rem;color:#475569;'>Intrinsic Value</span>
                <span style='font-size:.78rem;font-weight:700;color:#059669;'>₹{pick["iv"]:,.1f}</span>
              </div>
              <div style='display:flex;justify-content:space-between;margin-bottom:.25rem;'>
                <span style='font-size:.72rem;color:#475569;'>Margin of Safety</span>
                <span style='font-size:.78rem;font-weight:700;color:#059669;'>{pick["mos"]:.1f}%</span>
              </div>
              <div style='display:flex;justify-content:space-between;margin-bottom:.25rem;'>
                <span style='font-size:.72rem;color:#475569;'>Upside</span>
                <span style='font-size:.78rem;font-weight:700;color:#059669;'>↑ {pick["up"]:.1f}%</span>
              </div>
              <div style='display:flex;justify-content:space-between;margin-bottom:.25rem;'>
                <span style='font-size:.72rem;color:#475569;'>Piotroski</span>
                <span class='badge bg'>{pick["pio"]}/9</span>
              </div>
              <div style='display:flex;justify-content:space-between;'>
                <span style='font-size:.72rem;color:#475569;'>PE / ROE</span>
                <span style='font-size:.75rem;color:#3d4a63;'>{fn(pick["pe"],1)} / {fp(pick["roe"])}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔍 Analyse {pick['ticker']}",
                         key=f"sp_{pick['ticker']}", use_container_width=True):
                st.session_state.sel_ticker = pick["ticker"]
                st.rerun()

# ══════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════
init_db()

for k,v in [("sel_grp","Watchlist"),("sel_ticker",None),("show_special",False)]:
    if k not in st.session_state:
        st.session_state[k] = v

# Top bar
st.markdown("""
<div style='background:#fff;border-bottom:1px solid #e6e9f0;
            padding:.65rem 1.5rem;display:flex;align-items:center;
            justify-content:space-between;margin-bottom:.75rem;'>
  <div style='font-size:1rem;font-weight:700;color:#0b1120;display:flex;align-items:center;gap:.5rem;'>
    📈 Stock Analysis Pro
    <span style='background:#2563eb;color:#fff;font-size:.6rem;font-weight:700;
                 padding:.1rem .4rem;border-radius:4px;'>v4.1</span>
  </div>
  <div style='font-size:.72rem;color:#7b8599;'>Money Financial Services · Piotroski · VPA · Trends · AI Score</div>
</div>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([1, 3], gap="medium")

# ══ LEFT PANEL ═══════════════════════════════════════════════
with left_col:
    groups = get_groups()
    if st.session_state.sel_grp not in groups and groups:
        st.session_state.sel_grp = groups[0]
    sel_grp = st.session_state.sel_grp

    # Group selector
    if groups:
        sel_grp = st.selectbox("📁 Group", groups,
                               index=groups.index(st.session_state.sel_grp) if st.session_state.sel_grp in groups else 0,
                               key="grp_sel", label_visibility="visible")
        if sel_grp != st.session_state.sel_grp:
            st.session_state.sel_grp = sel_grp
            st.session_state.sel_ticker = None
            st.session_state.show_special = False
            st.rerun()

    # Special Picks button
    if st.button("⭐ Special Picks Screen", use_container_width=True, key="sp_btn"):
        st.session_state.show_special = not st.session_state.show_special
        st.session_state.sel_ticker = None
        st.rerun()

    # Create new group
    with st.expander("➕ New Group"):
        ng = st.text_input("",placeholder="e.g. Swing Trades",key="ng",label_visibility="collapsed")
        if st.button("Create",use_container_width=True,key="create_g"):
            if ng.strip():
                add_t(ng.strip(),"__init__")
                st.session_state.sel_grp=ng.strip()
                st.rerun()

    if sel_grp and sel_grp in groups:
        if st.button(f"🗑️ Delete '{sel_grp}'",use_container_width=True,key="del_g"):
            del_grp(sel_grp)
            st.session_state.sel_grp=groups[0] if len(groups)>1 else "Watchlist"
            st.session_state.sel_ticker=None
            st.rerun()

    st.markdown("---")

    # Add stock
    with st.expander("🔍 Add Stock"):
        sq=st.text_input("",placeholder="Search: SBI, Bajaj…",key="sq",label_visibility="collapsed")
        tickers_now=[t for t in get_tickers(sel_grp) if t!="__init__"]
        if sq:
            ql=sq.lower(); hits={}; seen=set()
            for name,t in STOCK_DB.items():
                if(ql in name.lower() or ql in t.lower()) and t not in seen:
                    seen.add(t); hits[name]=t
            for name,t in list(hits.items())[:6]:
                already=t in tickers_now
                ca2,cb2=st.columns([5,1])
                with ca2:
                    st.markdown(f"<div style='font-size:.74rem;padding:.1rem 0;'>"
                                f"<b>{t}</b><br><span style='color:#94a3b8;font-size:.66rem;'>{name}</span></div>",
                                unsafe_allow_html=True)
                with cb2:
                    if already:
                        st.markdown("<div style='padding-top:.3rem;'>✅</div>",unsafe_allow_html=True)
                    elif st.button("＋",key=f"h_{t}_{sel_grp}"):
                        add_t(sel_grp,t); st.success(f"Added {t}"); st.rerun()
        mt=st.text_input("",placeholder="Manual: SBIN.NS",key="mt",label_visibility="collapsed")
        if st.button("Add ticker",use_container_width=True,key="mt_btn"):
            t=mt.strip().upper()
            if t and t not in tickers_now: add_t(sel_grp,t); st.success(f"Added {t}!"); st.rerun()
            elif t in tickers_now: st.warning("Already in list.")

    st.markdown("---")

    # Stock list
    tickers_list=[t for t in get_tickers(sel_grp) if t!="__init__"]
    if not tickers_list:
        st.caption("No stocks. Add above ↑")
    else:
        st.markdown(f"<div style='font-size:.75rem;font-weight:600;color:#7b8599;"
                    f"margin-bottom:.5rem;text-transform:uppercase;letter-spacing:.06em;'>"
                    f"{sel_grp} · {len(tickers_list)} stocks</div>",unsafe_allow_html=True)

        for t in tickers_list:
            is_sel = st.session_state.sel_ticker == t
            pd_data = fetch_price(t)
            p=pd_data["price"]; pr=pd_data["prev"]; nm=pd_data["name"]

            if p and pr and pr>0:
                chgp_l=safe_div(p-pr,pr,0)*100
                cc2="#0ea371" if chgp_l>=0 else "#e53935"
                bg_c="#edfbf4" if chgp_l>=0 else "#fef2f2"
                arr2="▲" if chgp_l>=0 else "▼"
                chg_s=f"{arr2}{abs(chgp_l):.2f}%"
                p_s=f"{p:,.1f}"
            else:
                cc2,bg_c,chg_s="#7b8599","#f8f9fc","—"
                p_s=f"{p:,.1f}" if p else "—"

            sel_bdr="2px solid #2563eb" if is_sel else "1px solid #e6e9f0"
            sel_bg="#eff6ff" if is_sel else "white"

            st.markdown(f"""
            <div style='background:{sel_bg};border:{sel_bdr};border-radius:8px;
                        padding:.55rem .75rem;margin-bottom:.3rem;'>
              <div style='display:flex;justify-content:space-between;align-items:center;'>
                <div>
                  <div style='font-size:.8rem;font-weight:700;color:#0b1120;
                              font-family:"JetBrains Mono",monospace;'>{t}</div>
                  <div style='font-size:.66rem;color:#7b8599;max-width:120px;overflow:hidden;
                              text-overflow:ellipsis;white-space:nowrap;'>{nm[:20]}</div>
                </div>
                <div style='text-align:right;'>
                  <div style='font-size:.8rem;font-weight:600;color:#0b1120;
                              font-family:"JetBrains Mono",monospace;'>{p_s}</div>
                  <div style='font-size:.66rem;font-weight:600;color:{cc2};
                              background:{bg_c};padding:.05rem .28rem;border-radius:4px;'>{chg_s}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            ba,bb2=st.columns([3,1])
            with ba:
                if st.button(f"{'▶' if is_sel else '▷'} {t}",
                             key=f"sel_{t}_{sel_grp}",
                             use_container_width=True,
                             type="primary" if is_sel else "secondary"):
                    st.session_state.sel_ticker=t
                    st.session_state.show_special=False
                    st.rerun()
            with bb2:
                if st.button("✕",key=f"rm_{t}_{sel_grp}",help=f"Remove {t}"):
                    del_t(sel_grp,t)
                    if st.session_state.sel_ticker==t:
                        st.session_state.sel_ticker=None
                    st.rerun()

# ══ RIGHT PANEL ══════════════════════════════════════════════
with right_col:
    if st.session_state.show_special:
        tickers_list2=[t for t in get_tickers(st.session_state.sel_grp) if t!="__init__"]
        render_special_picks(tickers_list2)
    elif st.session_state.sel_ticker:
        render_analysis(st.session_state.sel_ticker)
    else:
        st.markdown("""
        <div style='display:flex;flex-direction:column;align-items:center;
                    justify-content:center;min-height:55vh;text-align:center;padding:3rem 2rem;'>
          <div style='font-size:3rem;margin-bottom:1rem;'>📊</div>
          <div style='font-size:1.4rem;font-weight:700;color:#0b1120;margin-bottom:.5rem;'>
            Stock Analysis Pro v4.1
          </div>
          <div style='font-size:.9rem;color:#64748b;max-width:460px;line-height:1.75;'>
            Select any stock from the left panel for full analysis,
            or click <b>⭐ Special Picks</b> to auto-screen for undervalued gems.
          </div>
          <div style='margin-top:1.5rem;display:flex;gap:.6rem;flex-wrap:wrap;justify-content:center;'>
            <span class='badge bb'>📈 Candlestick + VPA</span>
            <span class='badge bpu'>📊 Google Trends</span>
            <span class='badge bg'>Graham/DCF IV</span>
            <span class='badge by'>Piotroski F-Score</span>
            <span class='badge bn'>AI Score 0–100</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center;font-size:.68rem;color:#94a3b8;
            padding:.75rem 0 1.5rem;border-top:1px solid #e6e9f0;margin-top:1rem;'>
  📊 Stock Analysis Pro v4.1 · Money Financial Services ·
  Data: Yahoo Finance + Google Trends · Educational use only · Not SEBI advice
</div>
""", unsafe_allow_html=True)
