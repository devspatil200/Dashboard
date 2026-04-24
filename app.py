"""
Stock Analysis Pro — v4.2
Author  : Money Financial Services
UI      : TradingView-style Institutional Watchlist
Features: Compact list · Hover trash · Right-click menu · Logo · VPA · Trends · Piotroski · AI Score
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3, datetime, math, urllib.parse
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── PAGE CONFIG ────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Analysis Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── GLOBAL CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:    #ffffff;
  --bg1:   #fafafa;
  --bg2:   #f4f4f5;
  --line:  #e4e4e7;
  --line2: #d1d5db;
  --t1:    #09090b;
  --t2:    #3f3f46;
  --t3:    #71717a;
  --t4:    #a1a1aa;
  --green: #16a34a;
  --red:   #dc2626;
  --blue:  #2563eb;
  --blue2: #eff6ff;
  --r:     8px;
  --sh:    0 1px 2px rgba(0,0,0,.05);
  --sh2:   0 4px 16px rgba(0,0,0,.08);
}

html,body,[class*="css"] {
  font-family: 'Inter', sans-serif !important;
  background: var(--bg) !important;
  color: var(--t1) !important;
}

/* ── Hide Streamlit chrome ── */
section[data-testid="stSidebar"]   { display:none!important; }
button[data-testid="collapsedControl"] { display:none!important; }
.stApp > header                     { display:none!important; }
#MainMenu, footer                   { display:none!important; }
.block-container { padding:.5rem 1rem 4rem!important; max-width:100%!important; }

/* ── Top nav ── */
.topnav {
  position:sticky; top:0; z-index:900;
  background:rgba(255,255,255,.95);
  backdrop-filter:blur(12px);
  border-bottom:1px solid var(--line);
  display:flex; align-items:center;
  justify-content:space-between;
  padding:.6rem 1.25rem;
  margin-bottom:.75rem;
}
.brand { font-size:.95rem; font-weight:700; color:var(--t1); display:flex; align-items:center; gap:.4rem; }
.brand-v { font-size:.58rem; font-weight:700; background:var(--blue); color:#fff; padding:.1rem .35rem; border-radius:3px; }

/* ── Layout ── */
.layout { display:grid; grid-template-columns:280px 1fr; gap:0; min-height:calc(100vh - 56px); }

/* ── LEFT PANEL ── */
.lp {
  background:var(--bg);
  border-right:1px solid var(--line);
  display:flex; flex-direction:column;
  overflow:hidden;
}
.lp-head {
  padding:.65rem 1rem .5rem;
  border-bottom:1px solid var(--line);
  display:flex; align-items:center;
  justify-content:space-between;
}
.lp-title { font-size:.72rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:var(--t3); }

/* ── Group tab strip ── */
.gtabs {
  display:flex; overflow-x:auto; border-bottom:1px solid var(--line);
  padding:0 .75rem; gap:.1rem; scrollbar-width:none;
}
.gtabs::-webkit-scrollbar { display:none; }
.gtab {
  padding:.5rem .75rem; font-size:.76rem; font-weight:600;
  color:var(--t3); border-bottom:2px solid transparent;
  cursor:pointer; white-space:nowrap; transition:all .15s;
}
.gtab:hover { color:var(--t1); }
.gtab.on { color:var(--blue); border-bottom-color:var(--blue); }

/* ── Watchlist rows ── */
.wl { overflow-y:auto; flex:1; }

.wrow {
  display:flex; align-items:center; gap:.65rem;
  padding:.55rem .9rem;
  border-bottom:1px solid var(--line);
  cursor:pointer;
  position:relative;
  transition:background .1s;
  user-select:none;
}
.wrow:hover { background:var(--bg1); }
.wrow.sel   { background:var(--blue2); }
.wrow.sel::before {
  content:''; position:absolute; left:0; top:0; bottom:0;
  width:2px; background:var(--blue);
}

/* Logo */
.wlogo {
  width:28px; height:28px; border-radius:6px;
  object-fit:contain; border:1px solid var(--line);
  background:var(--bg1); flex-shrink:0;
}
.wlogo-placeholder {
  width:28px; height:28px; border-radius:6px;
  background:var(--bg2); border:1px solid var(--line);
  display:flex; align-items:center; justify-content:center;
  font-size:.6rem; font-weight:700; color:var(--t3); flex-shrink:0;
}

/* Stock info */
.winfo { flex:1; min-width:0; }
.wticker { font-size:.78rem; font-weight:700; color:var(--t1); font-family:'JetBrains Mono',monospace; }
.wname   { font-size:.66rem; color:var(--t3); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:120px; }

/* Price */
.wprice-wrap { text-align:right; flex-shrink:0; }
.wprice { font-size:.8rem; font-weight:600; color:var(--t1); font-family:'JetBrains Mono',monospace; }
.wchg   { font-size:.66rem; font-weight:600; padding:.05rem .3rem; border-radius:3px; display:inline-block; }
.wchg.up   { color:var(--green); background:#f0fdf4; }
.wchg.down { color:var(--red);   background:#fef2f2; }
.wchg.flat { color:var(--t3);    background:var(--bg2); }

/* Hover trash icon */
.wtrash {
  opacity:0; transition:opacity .15s;
  font-size:.78rem; color:var(--t3); cursor:pointer;
  padding:.2rem .3rem; border-radius:4px;
  flex-shrink:0;
}
.wrow:hover .wtrash { opacity:1; }
.wtrash:hover { background:var(--bg2); color:var(--red); }

/* ── Right-click context menu ── */
.ctx-menu {
  display:none; position:fixed; z-index:9999;
  background:var(--bg); border:1px solid var(--line);
  border-radius:var(--r); box-shadow:var(--sh2);
  padding:.3rem 0; min-width:170px;
  font-size:.8rem;
}
.ctx-menu.show { display:block; }
.ctx-item {
  padding:.45rem .9rem; cursor:pointer; display:flex;
  align-items:center; gap:.55rem; color:var(--t1);
  transition:background .1s;
}
.ctx-item:hover { background:var(--bg1); }
.ctx-item.danger { color:var(--red); }
.ctx-sep { border:none; border-top:1px solid var(--line); margin:.3rem 0; }

/* ── Add bar at bottom ── */
.add-bar {
  padding:.65rem .9rem;
  border-top:1px solid var(--line);
  background:var(--bg);
}

/* ── RIGHT PANEL ── */
.rp { background:var(--bg1); padding:1.25rem 1.5rem 3rem; overflow-y:auto; }

/* ── Stock header ── */
.shead {
  background:var(--bg); border:1px solid var(--line);
  border-radius:var(--r); padding:1rem 1.25rem;
  margin-bottom:1rem; display:flex;
  justify-content:space-between; align-items:flex-start;
  flex-wrap:wrap; gap:.75rem;
  box-shadow:var(--sh);
}
.sname { font-size:1.2rem; font-weight:700; color:var(--t1); line-height:1.2; }
.smeta { font-size:.72rem; color:var(--t3); margin-top:.25rem; display:flex; gap:.35rem; flex-wrap:wrap; align-items:center; }
.sprice { font-size:1.7rem; font-weight:800; color:var(--t1); font-family:'JetBrains Mono',monospace; line-height:1; }
.schg   { font-size:.82rem; font-weight:600; margin-top:.15rem; }

/* ── Metric cards ── */
.mc {
  background:var(--bg); border:1px solid var(--line);
  border-radius:var(--r); padding:.9rem 1rem;
  box-shadow:var(--sh); margin-bottom:.7rem;
}
.mc-l { font-size:.62rem; font-weight:700; text-transform:uppercase; letter-spacing:.07em; color:var(--t3); margin-bottom:.2rem; }
.mc-v { font-size:1.3rem; font-weight:700; color:var(--t1); font-family:'JetBrains Mono',monospace; line-height:1.1; }
.mc-s { font-size:.68rem; color:var(--t3); margin-top:.12rem; }

/* ── Section head ── */
.sec { font-size:.82rem; font-weight:700; color:var(--t1); border-left:2px solid var(--blue); padding-left:.55rem; margin:1.5rem 0 .75rem; }

/* ── Badges ── */
.bx { display:inline-block; padding:.15rem .5rem; border-radius:999px; font-size:.66rem; font-weight:700; }
.b-green  { background:#dcfce7; color:#15803d; }
.b-yellow { background:#fef9c3; color:#854d0e; }
.b-red    { background:#fee2e2; color:#b91c1c; }
.b-blue   { background:#dbeafe; color:#1d4ed8; }
.b-gray   { background:#f1f5f9; color:#475569; }
.b-purple { background:#ede9fe; color:#6d28d9; }

/* ── Progress ── */
.pb-w { background:#e4e4e7; border-radius:999px; height:5px; width:100%; margin:.3rem 0; }
.pb-f { height:5px; border-radius:999px; }

/* ── Checklist ── */
.ck { display:flex; align-items:flex-start; gap:.45rem; padding:.35rem .65rem; border-radius:6px; margin-bottom:.22rem; }
.ck-n { font-size:.76rem; font-weight:600; }
.ck-s { font-size:.66rem; color:var(--t3); }

/* ── Alerts ── */
.alert { border-radius:var(--r); padding:.65rem .9rem; font-size:.78rem; margin:.35rem 0; line-height:1.55; }
.a-info   { background:#eff6ff; border:1px solid #bfdbfe; color:#1e40af; }
.a-ok     { background:#f0fdf4; border:1px solid #bbf7d0; color:#15803d; }
.a-warn   { background:#fffbeb; border:1px solid #fde68a; color:#92400e; }
.a-danger { background:#fef2f2; border:1px solid #fecaca; color:#991b1b; }
.a-purple { background:#ede9fe; border:1px solid #c4b5fd; color:#5b21b6; }

/* ── Accum zone ── */
.accum {
  background:linear-gradient(135deg,#fefce8,#fef9c3);
  border:2px solid #f59e0b; border-radius:var(--r);
  padding:.9rem 1.1rem; margin:.6rem 0; text-align:center;
}

/* ── Landing ── */
.landing {
  display:flex; flex-direction:column; align-items:center;
  justify-content:center; min-height:55vh;
  text-align:center; padding:3rem 2rem;
}

/* ── Widget overrides ── */
[data-testid="stButton"]>button {
  border-radius:6px!important; font-family:'Inter',sans-serif!important;
  font-weight:600!important; font-size:.78rem!important;
}
[data-testid="stTextInput"] input {
  border-radius:6px!important; font-family:'Inter',sans-serif!important;
  font-size:.8rem!important; border:1px solid var(--line2)!important;
  padding:.4rem .65rem!important;
}
[data-testid="stTabs"] [role="tab"] {
  font-family:'Inter',sans-serif!important; font-weight:600!important; font-size:.78rem!important;
}
[data-testid="stSelectbox"]>div { border-radius:6px!important; font-size:.8rem!important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# STOCK DB
# ══════════════════════════════════════════════════════════
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
    "Watchlist":["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","SBIN.NS"],
    "Banking":["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS"],
    "IT Sector":["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Pharma":["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","DIVISLAB.NS"],
}

# ══════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════
DB = "stock_v42.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS grp_tickers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grp TEXT NOT NULL, ticker TEXT NOT NULL, added_at TEXT,
        UNIQUE(grp,ticker))""")
    c.execute("""CREATE TABLE IF NOT EXISTS notes (
        ticker TEXT PRIMARY KEY, content TEXT, updated_at TEXT)""")
    conn.commit()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    for grp, tickers in DEFAULT_GROUPS.items():
        for t in tickers:
            try:
                conn.execute("INSERT OR IGNORE INTO grp_tickers (grp,ticker,added_at) VALUES (?,?,?)",
                             (grp, t, now))
            except Exception: pass
    conn.commit(); conn.close()

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
        "SELECT ticker FROM grp_tickers WHERE grp=? AND ticker!='__init__' ORDER BY added_at",(grp,))]

def add_t(grp, ticker):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    dbx("INSERT OR IGNORE INTO grp_tickers (grp,ticker,added_at) VALUES (?,?,?)",
        (grp, ticker.upper().strip(), now))

def del_t(grp, ticker):
    dbx("DELETE FROM grp_tickers WHERE grp=? AND ticker=?",(grp,ticker))

def del_grp(name):
    dbx("DELETE FROM grp_tickers WHERE grp=?",(name,))

def save_note(ticker, content):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    dbx("INSERT OR REPLACE INTO notes VALUES (?,?,?)",(ticker.upper(),content,now))

def load_note(ticker):
    rows = dbq("SELECT content,updated_at FROM notes WHERE ticker=?",(ticker.upper(),))
    return (rows[0][0], rows[0][1]) if rows else ("","")

# ══════════════════════════════════════════════════════════
# DATA FETCHER
# ══════════════════════════════════════════════════════════
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
    except Exception:
        return {"info":{},"hist":pd.DataFrame(),"fin":pd.DataFrame(),
                "bs":pd.DataFrame(),"cf":pd.DataFrame(),
                "major_holders":pd.DataFrame(),"inst_holders":pd.DataFrame()}

@st.cache_data(ttl=90, show_spinner=False)
def fetch_price(ticker):
    try:
        info = yf.Ticker(ticker).info or {}
        return {
            "price": info.get("regularMarketPrice") or info.get("currentPrice"),
            "prev":  info.get("regularMarketPreviousClose"),
            "name":  info.get("shortName") or info.get("longName") or ticker,
            "website": info.get("website",""),
        }
    except Exception:
        return {"price":None,"prev":None,"name":ticker,"website":""}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_trends(keyword):
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
    except Exception:
        return None, "Trends data not available for this ticker"

# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════
def _v(d, *keys, default=None):
    for k in keys:
        try:
            val = d.get(k) if isinstance(d,dict) else None
            if val is not None and not(isinstance(val,float) and math.isnan(val)):
                return val
        except Exception: pass
    return default

def _row(df, *names):
    try:
        if df is None or df.empty: return None
        for name in names:
            for idx in df.index:
                if name.lower() in str(idx).lower():
                    s = df.loc[idx].dropna()
                    if not s.empty: return s
    except Exception: pass
    return None

def _latest(s):
    try:
        if s is None: return None
        s2 = s.dropna()
        return float(s2.iloc[0]) if not s2.empty else None
    except Exception: return None

def sdiv(a, b, default=None):
    try:
        if b is None or b==0: return default
        return a/b
    except Exception: return default

def get_logo(website):
    try:
        if not website: return None
        domain = website.replace("https://","").replace("http://","").split("/")[0]
        return f"https://logo.clearbit.com/{domain}"
    except Exception: return None

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

def mc(lbl,val,sub="",vc="#09090b"):
    return (f"<div class='mc'><div class='mc-l'>{lbl}</div>"
            f"<div class='mc-v' style='color:{vc};'>{val}</div>"
            +(f"<div class='mc-s'>{sub}</div>" if sub else "")+"</div>")

def pb(pct,color="#2563eb"):
    pct=max(0,min(100,pct))
    return (f"<div class='pb-w'><div class='pb-f' "
            f"style='width:{pct}%;background:{color};'></div></div>")

# ══════════════════════════════════════════════════════════
# METRICS BUILDER
# ══════════════════════════════════════════════════════════
def build_m(data):
    info,fin,bs,cf,hist = data["info"],data["fin"],data["bs"],data["cf"],data["hist"]
    m = {}
    m["name"]    = _v(info,"longName","shortName")
    m["sector"]  = _v(info,"sector",default="—")
    m["industry"]= _v(info,"industry",default="—")
    m["exchange"]= _v(info,"exchange",default="—")
    m["currency"]= _v(info,"currency",default="INR")
    m["website"] = _v(info,"website",default="")
    m["price"]   = _v(info,"regularMarketPrice","currentPrice")
    m["prev"]    = _v(info,"regularMarketPreviousClose")
    m["mktcap"]  = _v(info,"marketCap")
    m["beta"]    = _v(info,"beta")
    m["target"]  = _v(info,"targetMeanPrice")
    m["pe"]      = _v(info,"trailingPE")
    m["fpe"]     = _v(info,"forwardPE")
    m["pb2"]     = _v(info,"priceToBook")
    m["ps"]      = _v(info,"priceToSalesTrailing12Months")
    m["peg"]     = _v(info,"pegRatio")
    m["roe"]     = _v(info,"returnOnEquity")
    m["roa"]     = _v(info,"returnOnAssets")
    m["pm"]      = _v(info,"profitMargins")
    m["gm"]      = _v(info,"grossMargins")
    m["om"]      = _v(info,"operatingMargins")
    m["de"]      = _v(info,"debtToEquity")
    m["cr"]      = _v(info,"currentRatio")
    m["qr"]      = _v(info,"quickRatio")
    m["fcf"]     = _v(info,"freeCashflow")
    m["ocf"]     = _v(info,"operatingCashflow")
    m["rg"]      = _v(info,"revenueGrowth")
    m["eg"]      = _v(info,"earningsGrowth")
    m["eps"]     = _v(info,"trailingEps")
    m["feps"]    = _v(info,"forwardEps")
    m["dy"]      = _v(info,"dividendYield")

    # Fallbacks
    if m["roe"] is None:
        ni=_latest(_row(fin,"Net Income")); eq=_latest(_row(bs,"Stockholders Equity","Total Stockholder Equity"))
        m["roe"] = sdiv(ni,abs(eq)) if ni else None
    if m["roa"] is None:
        ni=_latest(_row(fin,"Net Income")); ta=_latest(_row(bs,"Total Assets"))
        m["roa"] = sdiv(ni,abs(ta)) if ni else None
    if m["pm"] is None:
        ni=_latest(_row(fin,"Net Income")); rev=_latest(_row(fin,"Total Revenue"))
        m["pm"] = sdiv(ni,abs(rev)) if ni else None
    if m["de"] is None:
        td=_latest(_row(bs,"Total Debt","Long Term Debt")); eq=_latest(_row(bs,"Stockholders Equity","Total Stockholder Equity"))
        if td is not None and eq:
            m["de"] = sdiv(td,abs(eq),None)
            if m["de"] is not None: m["de"]*=100
    if m["fcf"] is None:
        ocf=_latest(_row(cf,"Operating Cash Flow","Cash From Operations"))
        capx=_latest(_row(cf,"Capital Expenditure","Purchases Of Property Plant And Equipment"))
        if ocf is not None: m["ocf"]=ocf; m["fcf"]=ocf+(capx if capx else 0)

    if not hist.empty:
        try:
            close=hist["Close"]
            m["ph"]    = float(close.iloc[-1])
            m["vol"]   = float(hist["Volume"].iloc[-1])
            m["v20"]   = float(hist["Volume"].rolling(20).mean().iloc[-1]) if len(hist)>=20 else None
            m["d50"]   = float(close.rolling(50).mean().iloc[-1]) if len(close)>=50 else None
            m["d200"]  = float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else None
            m["h52"]   = float(close.rolling(252).max().iloc[-1]) if len(close)>=252 else float(close.max())
            m["l52"]   = float(close.rolling(252).min().iloc[-1]) if len(close)>=252 else float(close.min())
            delta=close.diff(); gain=delta.clip(lower=0).rolling(14).mean()
            loss=(-delta.clip(upper=0)).rolling(14).mean(); rs=gain/loss.replace(0,float("nan"))
            rsi=100-(100/(1+rs)); m["rsi"]=float(rsi.iloc[-1]) if not rsi.empty else None
            e12=close.ewm(span=12).mean(); e26=close.ewm(span=26).mean()
            macd=e12-e26; sig=macd.ewm(span=9).mean()
            m["macd"]=float(macd.iloc[-1]); m["msig"]=float(sig.iloc[-1]); m["mh"]=float((macd-sig).iloc[-1])
            m["vol_pct"] = float(close.pct_change().rolling(20).std().iloc[-1]*100) if len(close)>=20 else None
            if m["v20"] and m["v20"]>0:
                mask=(hist["Close"]>hist["Close"].shift(1))&(hist["Volume"]>2*hist["Volume"].rolling(20).mean())
                m["vpa_dates"]=list(hist.index[mask])
            else: m["vpa_dates"]=[]
        except Exception:
            for k in ["ph","vol","v20","d50","d200","h52","l52","rsi","macd","msig","mh","vol_pct","vpa_dates"]: m[k]=None
    else:
        for k in ["ph","vol","v20","d50","d200","h52","l52","rsi","macd","msig","mh","vol_pct","vpa_dates"]: m[k]=None
    return m

# ══════════════════════════════════════════════════════════
# PIOTROSKI
# ══════════════════════════════════════════════════════════
def piotroski(data):
    info,fin,bs,cf = data["info"],data["fin"],data["bs"],data["cf"]
    C=[]
    def _l(df,*n): return _latest(_row(df,*n))
    def _lp(df,*n):
        r=_row(df,*n)
        if r is None or len(r.dropna())<2: return None
        return float(r.dropna().iloc[1])
    ni_c=_l(fin,"Net Income"); ni_p=_lp(fin,"Net Income")
    rev_c=_l(fin,"Total Revenue"); rev_p=_lp(fin,"Total Revenue")
    ta_c=_l(bs,"Total Assets"); ta_p=_lp(bs,"Total Assets")
    ocf=_l(cf,"Operating Cash Flow","Cash From Operations")
    roa=_v(info,"returnOnAssets")
    if roa is None and ni_c and ta_c and ta_c!=0: roa=sdiv(ni_c,ta_c)
    def add(g,n,p,note): C.append({"g":g,"n":n,"p":p,"note":note})
    add("P","F1 — ROA Positive", roa is not None and roa>0, f"ROA={roa*100:.1f}%" if roa else "N/A")
    add("P","F2 — OCF Positive", ocf is not None and ocf>0, f"OCF=₹{ocf/1e7:.1f}Cr" if ocf else "N/A")
    if roa is not None and ta_p and ni_p and ta_p!=0:
        rp=sdiv(ni_p,ta_p,0)
        add("P","F3 — ROA Improving", roa>rp, f"Curr {roa*100:.1f}% vs Prev {rp*100:.1f}%")
    else: add("P","F3 — ROA Improving",False,"Insufficient data")
    if ocf and ta_c and ta_c!=0 and roa is not None:
        add("P","F4 — Cash>Paper", sdiv(ocf,ta_c,0)>roa, f"OCF/TA={sdiv(ocf,ta_c,0)*100:.1f}% vs ROA={roa*100:.1f}%")
    else: add("P","F4 — Cash>Paper",False,"N/A")
    ltd_r=_row(bs,"Long Term Debt")
    if ltd_r is not None and len(ltd_r.dropna())>=2 and ta_c and ta_p:
        lv=ltd_r.dropna(); rc_=sdiv(float(lv.iloc[0]),ta_c,0); rp_=sdiv(float(lv.iloc[1]),ta_p,0)
        add("L","F5 — Debt Decreasing", rc_<rp_, f"Curr {rc_*100:.1f}% vs Prev {rp_*100:.1f}%")
    else: add("L","F5 — Debt Decreasing",False,"N/A")
    ca_r=_row(bs,"Current Assets"); cl_r=_row(bs,"Current Liabilities")
    if ca_r is not None and cl_r is not None and len(ca_r.dropna())>=2:
        cav=ca_r.dropna(); clv=cl_r.dropna()
        cc=sdiv(float(cav.iloc[0]),float(clv.iloc[0])); cp_=sdiv(float(cav.iloc[1]),float(clv.iloc[1]))
        add("L","F6 — CR Improving", bool(cc and cp_ and cc>cp_), f"Curr {cc:.2f} vs Prev {cp_:.2f}" if cc and cp_ else "N/A")
    else:
        cr_i=_v(info,"currentRatio")
        add("L","F6 — CR > 1.5", cr_i is not None and cr_i>1.5, f"CR={cr_i:.2f}" if cr_i else "N/A")
    sh_r=_row(bs,"Ordinary Shares Number","Common Stock Shares Outstanding")
    if sh_r is not None and len(sh_r.dropna())>=2:
        sv=sh_r.dropna()
        add("L","F7 — No Dilution", float(sv.iloc[0])<=float(sv.iloc[1]),
            f"Curr {float(sv.iloc[0])/1e7:.2f}Cr vs Prev {float(sv.iloc[1])/1e7:.2f}Cr")
    else: add("L","F7 — No Dilution",False,"N/A")
    gp_r=_row(fin,"Gross Profit")
    if gp_r is not None and len(gp_r.dropna())>=2 and rev_c and rev_p:
        gv=gp_r.dropna(); gmc=sdiv(float(gv.iloc[0]),rev_c,0); gmp=sdiv(float(gv.iloc[1]),rev_p,0)
        add("E","F8 — GM Improving", gmc>gmp, f"Curr {gmc*100:.1f}% vs Prev {gmp*100:.1f}%")
    else:
        gm_i=_v(info,"grossMargins")
        add("E","F8 — GM > 20%", gm_i is not None and gm_i>0.20, f"GM={gm_i*100:.1f}%" if gm_i else "N/A")
    if rev_c and rev_p and ta_c and ta_p:
        add("E","F9 — AT Improving", sdiv(rev_c,ta_c,0)>sdiv(rev_p,ta_p,0),
            f"Curr {sdiv(rev_c,ta_c,0):.2f}x vs Prev {sdiv(rev_p,ta_p,0):.2f}x")
    else: add("E","F9 — AT Improving",False,"Insufficient data")
    return sum(1 for c in C if c["p"]), C

def iv_calc(m):
    r={}; eps=m.get("eps"); pb2=m.get("pb2"); price=m.get("price") or m.get("ph")
    bvps=sdiv(price,pb2) if (pb2 and pb2>0 and price) else None
    r["graham"]=math.sqrt(22.5*eps*bvps) if(eps and eps>0 and bvps and bvps>0) else None
    g=m.get("eg") or m.get("rg")
    if eps and eps>0 and g is not None:
        g2=max(-20,min(50,g*100)); dcf=eps*(8.5+2*g2)*4.4/7.5
        r["dcf"]=dcf if dcf>0 else None
    else: r["dcf"]=None
    target=m.get("target")
    r["analyst_upside"]=sdiv(target-price,price,0)*100 if target and price and price>0 else None
    r["analyst_target"]=target
    valid=[v for v in [r.get("graham"),r.get("dcf")] if v]
    if valid and price:
        avg=sum(valid)/len(valid); r["avg"]=avg
        r["mos"]=sdiv(avg-price,avg,0)*100; r["up"]=sdiv(avg-price,price,0)*100
    else: r["avg"]=r["mos"]=r["up"]=None
    return r

def ai_score(m, pio, iv):
    bd={}; price=m.get("price") or m.get("ph") or 0
    v=0; pe=m.get("pe")
    if pe: v+=10 if pe<15 else(7 if pe<25 else(4 if pe<40 else 0))
    pb2=m.get("pb2")
    if pb2: v+=10 if pb2<1.5 else(7 if pb2<3 else(3 if pb2<5 else 0))
    bd["Valuation"]=min(v,20)
    p=0; roe=m.get("roe"); pm_v=m.get("pm"); fcf=m.get("fcf")
    if roe: p+=8 if roe>0.25 else(5 if roe>0.15 else(2 if roe>0 else 0))
    if pm_v: p+=7 if pm_v>0.20 else(4 if pm_v>0.10 else(1 if pm_v>0 else 0))
    if fcf and fcf>0: p+=5
    bd["Profitability"]=min(p,20)
    h=0; de=m.get("de"); cr=m.get("cr")
    if de is not None:
        dr=de/100; h+=8 if dr<0.3 else(5 if dr<0.7 else(2 if dr<1 else 0))
    if cr: h+=7 if cr>2 else(4 if cr>1.5 else(1 if cr>1 else 0))
    h+=min(pio,5); bd["Financial Health"]=min(h,20)
    t=0; d200=m.get("d200"); d50=m.get("d50"); rsi=m.get("rsi")
    if price and d200:
        pct=sdiv(price-d200,d200,0)*100
        t+=8 if 0<pct<20 else(4 if pct>=20 else(3 if pct>-10 else 0))
    if price and d50 and price>d50: t+=5
    if rsi: t+=7 if 40<=rsi<=65 else(4 if(30<=rsi<40 or 65<rsi<=70) else(2 if rsi<30 else 0))
    bd["Technical"]=min(t,20)
    g=0; rg=m.get("rg"); eg=m.get("eg"); up=iv.get("up")
    if rg: g+=7 if rg>0.20 else(4 if rg>0.10 else(1 if rg>0 else 0))
    if eg: g+=7 if eg>0.20 else(4 if eg>0.10 else(1 if eg>0 else 0))
    if up: g+=6 if up>30 else(3 if up>10 else(1 if up>0 else 0))
    bd["Growth"]=min(g,20)
    total=sum(bd.values())
    if total>=75: grade,color="Excellent — Strong Buy","#16a34a"
    elif total>=60: grade,color="Good — Buy","#2563eb"
    elif total>=45: grade,color="Average — Watch","#d97706"
    elif total>=30: grade,color="Weak — Caution","#ea580c"
    else: grade,color="Poor — Avoid","#dc2626"
    return total, bd, grade, color

# ══════════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════════
def candle_chart(hist, d50, d200, vpa_dates=None):
    if hist.empty: return None
    fig=make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=0.03,row_heights=[0.75,0.25])
    fig.add_trace(go.Candlestick(
        x=hist.index,open=hist["Open"],high=hist["High"],low=hist["Low"],close=hist["Close"],
        name="Price",increasing_line_color="#16a34a",decreasing_line_color="#dc2626",
        increasing_fillcolor="#16a34a",decreasing_fillcolor="#dc2626",
    ),row=1,col=1)
    if d50: fig.add_trace(go.Scatter(x=hist.index,y=hist["Close"].rolling(50).mean(),
        name="50 DMA",line=dict(color="#2563eb",width=1.5)),row=1,col=1)
    if d200: fig.add_trace(go.Scatter(x=hist.index,y=hist["Close"].rolling(200).mean(),
        name="200 DMA",line=dict(color="#d97706",width=1.5,dash="dot")),row=1,col=1)
    if vpa_dates:
        vpa_p=[hist.loc[d,"High"]*1.01 for d in vpa_dates if d in hist.index]
        vpa_d=[d for d in vpa_dates if d in hist.index]
        if vpa_d:
            fig.add_trace(go.Scatter(x=vpa_d,y=vpa_p,mode="markers",name="🏦 Inst.Buy",
                marker=dict(symbol="triangle-up",size=11,color="#7c3aed",
                            line=dict(color="#fff",width=1.5))),row=1,col=1)
    colors=["#16a34a" if c>=o else "#dc2626" for c,o in zip(hist["Close"],hist["Open"])]
    fig.add_trace(go.Bar(x=hist.index,y=hist["Volume"],name="Volume",
        marker_color=colors,opacity=0.5,showlegend=False),row=2,col=1)
    fig.update_layout(
        height=440,margin=dict(l=0,r=0,t=20,b=0),
        paper_bgcolor="#fff",plot_bgcolor="#fff",template="plotly_white",
        font=dict(family="Inter",size=11,color="#3f3f46"),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=1,
                    bgcolor="rgba(0,0,0,0)",font=dict(size=10)),
        yaxis=dict(showgrid=True,gridcolor="#f4f4f5",side="right",tickfont=dict(size=10),zeroline=False),
        yaxis2=dict(showgrid=False,side="right",tickfont=dict(size=9),zeroline=False),
        xaxis2=dict(showgrid=True,gridcolor="#f4f4f5",tickfont=dict(size=10)),
    )
    return fig

def gauge_chart(score, grade, color):
    fig=go.Figure(go.Indicator(
        mode="gauge+number",value=score,
        number={"font":{"size":36,"family":"JetBrains Mono","color":color}},
        gauge=dict(
            axis=dict(range=[0,100],tickfont=dict(size=10,color="#71717a"),nticks=6),
            bar=dict(color=color,thickness=0.25),bgcolor="white",borderwidth=0,
            steps=[dict(range=[0,30],color="#fef2f2"),dict(range=[30,45],color="#fff7ed"),
                   dict(range=[45,60],color="#fffbeb"),dict(range=[60,75],color="#eff6ff"),
                   dict(range=[75,100],color="#f0fdf4")],
            threshold=dict(line=dict(color=color,width=3),thickness=0.75,value=score)),
        domain={"x":[0,1],"y":[0,1]},
        title={"text":grade,"font":{"size":10,"family":"Inter","color":"#3f3f46"}}))
    fig.update_layout(height=200,margin=dict(l=15,r=15,t=25,b=0),
                      paper_bgcolor="#fff",template="plotly_white",font=dict(family="Inter"))
    return fig

# ══════════════════════════════════════════════════════════
# FULL ANALYSIS
# ══════════════════════════════════════════════════════════
def render_analysis(ticker):
    with st.spinner(f"Loading {ticker}…"):
        data=fetch_all(ticker); m=build_m(data)
    price=m.get("price") or m.get("ph")
    if not price:
        st.markdown(f"<div class='alert a-danger'>❌ Cannot fetch <b>{ticker}</b>. "
                    "Verify ticker — NSE: add .NS</div>",unsafe_allow_html=True); return
    pio_s,pio_c=piotroski(data); iv=iv_calc(m)
    total,bd,grade,color=ai_score(m,pio_s,iv)
    hist=data.get("hist",pd.DataFrame())
    prev=m.get("prev"); chg=price-prev if prev else 0
    chgp=sdiv(chg,prev,0)*100; cc="#16a34a" if chg>=0 else "#dc2626"; arr="▲" if chg>=0 else "▼"
    curr=m.get("currency","INR")
    logo_url=get_logo(m.get("website",""))
    logo_html=(f'<img src="{logo_url}" width="32" height="32" '
               f'style="border-radius:6px;object-fit:contain;border:1px solid #e4e4e7;" '
               f'onerror="this.style.display=\'none\'"> ') if logo_url else ""

    # Header
    st.markdown(f"""
    <div class='shead'>
      <div style='display:flex;align-items:center;gap:.75rem;'>
        {logo_html}
        <div>
          <div class='sname'>{m.get("name") or ticker}</div>
          <div class='smeta'>
            <span class='bx b-blue'>{ticker}</span>
            <span class='bx b-gray'>{m.get("exchange","—")}</span>
            <span>{m.get("sector","—")} · {m.get("industry","—")}</span>
          </div>
        </div>
      </div>
      <div style='text-align:right;'>
        <div class='sprice'>{curr} {price:,.2f}</div>
        <div class='schg' style='color:{cc};'>{arr} {abs(chg):,.2f} ({chgp:+.2f}%)</div>
        <div style='font-size:.68rem;color:#a1a1aa;margin-top:.1rem;'>
          Cap: {fc(m.get("mktcap"))} · Beta: {fn(m.get("beta"))} · Target: {fn(m.get("target"))}
        </div>
      </div>
    </div>
    """,unsafe_allow_html=True)

    T1,T2,T3,T4,T5,T6=st.tabs(["📋 Fundamentals","📡 Technicals","📈 Trends",
                                 "🏦 Holders","🏆 Piotroski + IV","🤖 AI Verdict"])

    # TAB 1
    with T1:
        st.markdown("<div class='sec'>Valuation</div>",unsafe_allow_html=True)
        pe_v=m.get("pe")
        pe_c=("#16a34a" if pe_v and pe_v<25 else "#d97706" if pe_v and pe_v<40 else "#dc2626") if pe_v else "#71717a"
        c1,c2,c3,c4,c5=st.columns(5)
        for col,(l,v,s,vc) in zip([c1,c2,c3,c4,c5],[
            ("Trailing PE",fn(m.get("pe"),1),"< 25 ideal",pe_c),
            ("Forward PE",fn(m.get("fpe"),1),"Estimated","#09090b"),
            ("Price/Book",fn(m.get("pb2"),2),"< 3 ideal","#09090b"),
            ("Price/Sales",fn(m.get("ps"),2),"Revenue mult.","#09090b"),
            ("PEG",fn(m.get("peg"),2),"< 1 cheap","#09090b"),
        ]): col.markdown(mc(l,v,s,vc),unsafe_allow_html=True)

        st.markdown("<div class='sec'>Profitability</div>",unsafe_allow_html=True)
        c1,c2,c3,c4,c5=st.columns(5)
        roe_v=m.get("roe"); pm_v2=m.get("pm")
        for col,(l,v,s,vc) in zip([c1,c2,c3,c4,c5],[
            ("ROE",fp(roe_v),"> 15%","#16a34a" if roe_v and roe_v>0.15 else "#dc2626" if roe_v else "#71717a"),
            ("ROA",fp(m.get("roa")),"Asset return","#09090b"),
            ("Net Margin",fp(pm_v2),"> 10%","#16a34a" if pm_v2 and pm_v2>0.10 else "#dc2626" if pm_v2 else "#71717a"),
            ("Gross Margin",fp(m.get("gm")),"Revenue quality","#09090b"),
            ("Oper. Margin",fp(m.get("om")),"Oper. efficiency","#09090b"),
        ]): col.markdown(mc(l,v,s,vc),unsafe_allow_html=True)

        st.markdown("<div class='sec'>Balance Sheet & Cash Flow</div>",unsafe_allow_html=True)
        c1,c2,c3,c4,c5=st.columns(5)
        de_v=m.get("de"); cr_v=m.get("cr"); fcf_v=m.get("fcf"); de_r=de_v/100 if de_v is not None else None
        for col,(l,v,s,vc) in zip([c1,c2,c3,c4,c5],[
            ("Debt/Equity",f"{de_r:.2f}x" if de_r is not None else "N/A","< 1x",
             "#16a34a" if de_r is not None and de_r<1 else "#dc2626" if de_r is not None else "#71717a"),
            ("Current Ratio",fn(cr_v,2),"> 1.5","#16a34a" if cr_v and cr_v>1.5 else "#dc2626" if cr_v else "#71717a"),
            ("Quick Ratio",fn(m.get("qr"),2),"Acid test","#09090b"),
            ("Free Cash Flow",fc(fcf_v),"Positive = healthy","#16a34a" if fcf_v and fcf_v>0 else "#dc2626" if fcf_v else "#71717a"),
            ("Oper. Cash Flow",fc(m.get("ocf")),"Generated","#09090b"),
        ]): col.markdown(mc(l,v,s,vc),unsafe_allow_html=True)

        st.markdown("<div class='sec'>Growth & EPS</div>",unsafe_allow_html=True)
        c1,c2,c3,c4,c5=st.columns(5)
        rg_v=m.get("rg"); eg_v=m.get("eg")
        for col,(l,v,s,vc) in zip([c1,c2,c3,c4,c5],[
            ("Revenue Growth",fp(rg_v),"YoY","#16a34a" if rg_v and rg_v>0 else "#dc2626" if rg_v else "#71717a"),
            ("Earnings Growth",fp(eg_v),"YoY","#16a34a" if eg_v and eg_v>0 else "#dc2626" if eg_v else "#71717a"),
            ("Trailing EPS",fn(m.get("eps"),2),"Per share","#09090b"),
            ("Forward EPS",fn(m.get("feps"),2),"Estimated","#09090b"),
            ("Dividend Yield",fp(m.get("dy"),2),"Annual","#09090b"),
        ]): col.markdown(mc(l,v,s,vc),unsafe_allow_html=True)
        desc=_v(data["info"],"longBusinessSummary",default="")
        if desc:
            with st.expander("📖 About"):
                st.markdown(f"<p style='font-size:.84rem;line-height:1.8;color:#3f3f46;'>{desc[:1200]}{'…' if len(desc)>1200 else ''}</p>",unsafe_allow_html=True)

    # TAB 2
    with T2:
        st.markdown("<div class='sec'>Candlestick + VPA Signals</div>",unsafe_allow_html=True)
        fig_c=candle_chart(hist,m.get("d50"),m.get("d200"),m.get("vpa_dates"))
        if fig_c: st.plotly_chart(fig_c,use_container_width=True,config={"displayModeBar":False})
        vpa_d=m.get("vpa_dates") or []
        if vpa_d: st.markdown(f"<div class='alert a-purple'>🏦 <b>Institutional Buying — {len(vpa_d)} signals</b> (Price↑ + Vol > 2× avg). Last: {str(vpa_d[-1])[:10]}</div>",unsafe_allow_html=True)
        else: st.markdown("<div class='alert a-info'>ℹ️ No institutional buying signals in last 1 year.</div>",unsafe_allow_html=True)

        st.markdown("<div class='sec'>Key Levels</div>",unsafe_allow_html=True)
        ph=m.get("ph") or price
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(mc("Price",f"₹{ph:,.2f}","Current close"),unsafe_allow_html=True)
        with c2:
            d50=m.get("d50")
            if d50: p50=sdiv(ph-d50,d50,0)*100; st.markdown(mc("50 DMA",f"₹{d50:,.2f}",f"{p50:+.1f}%","#16a34a" if ph>d50 else "#dc2626"),unsafe_allow_html=True)
            else: st.markdown(mc("50 DMA","N/A","—"),unsafe_allow_html=True)
        with c3:
            d200=m.get("d200")
            if d200: p200=sdiv(ph-d200,d200,0)*100; st.markdown(mc("200 DMA",f"₹{d200:,.2f}",f"{p200:+.1f}%","#16a34a" if ph>d200 else "#dc2626"),unsafe_allow_html=True)
            else: st.markdown(mc("200 DMA","N/A","—"),unsafe_allow_html=True)
        with c4:
            rsi_v=m.get("rsi")
            if rsi_v:
                rl="Overbought ⚠️" if rsi_v>70 else("Oversold 🔎" if rsi_v<30 else "Neutral ✅")
                rc="#dc2626" if rsi_v>70 else("#d97706" if rsi_v<30 else "#16a34a")
                st.markdown(mc("RSI (14)",f"{rsi_v:.1f}",rl,rc),unsafe_allow_html=True)
            else: st.markdown(mc("RSI (14)","N/A",""),unsafe_allow_html=True)

        h52=m.get("h52"); l52=m.get("l52")
        if h52 and l52 and h52!=l52:
            pos=sdiv(ph-l52,h52-l52,0)*100; pfh=sdiv(ph-h52,h52,0)*100
            ca,cb=st.columns([3,1])
            with ca:
                st.markdown(f"""<div class='mc'>
                  <div style='display:flex;justify-content:space-between;margin-bottom:.3rem;'>
                    <span style='font-size:.66rem;color:#71717a;'>52W Low ₹{l52:,.0f}</span>
                    <span style='font-size:.76rem;font-weight:700;'>📍 ₹{ph:,.1f} ({pos:.0f}th%ile)</span>
                    <span style='font-size:.66rem;color:#71717a;'>52W High ₹{h52:,.0f}</span>
                  </div>
                  {pb(pos,"linear-gradient(90deg,#dc2626 0%,#f59e0b 50%,#16a34a 100%)")}
                </div>""",unsafe_allow_html=True)
            with cb: st.markdown(mc("From 52W High",f"{pfh:+.1f}%","","#16a34a" if pfh>-5 else "#dc2626"),unsafe_allow_html=True)

        cv=m.get("vol"); v20=m.get("v20")
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(mc("Today Vol",f"{cv:,.0f}" if cv else "N/A","Shares traded"),unsafe_allow_html=True)
        with c2: st.markdown(mc("20D Avg Vol",f"{v20:,.0f}" if v20 else "N/A","Rolling avg"),unsafe_allow_html=True)
        with c3:
            if cv and v20 and v20>0:
                vr=cv/v20; vc2="#16a34a" if vr>1.5 else("#dc2626" if vr<0.5 else "#d97706")
                vl="📈 Spike" if vr>1.5 else("📉 Dry" if vr<0.5 else "➡️ Normal")
                st.markdown(mc("Vol Ratio",f"{vr:.2f}×",vl,vc2),unsafe_allow_html=True)
            else: st.markdown(mc("Vol Ratio","N/A",""),unsafe_allow_html=True)
        with c4:
            mh2=m.get("mh")
            if mh2: st.markdown(mc("MACD Hist",f"{mh2:.2f}","Bullish 🟢" if mh2>0 else "Bearish 🔴","#16a34a" if mh2>0 else "#dc2626"),unsafe_allow_html=True)
            else: st.markdown(mc("MACD","N/A",""),unsafe_allow_html=True)

    # TAB 3
    with T3:
        st.markdown("<div class='sec'>Google Trends — India Search Interest (30 Days)</div>",unsafe_allow_html=True)
        kw=ticker.replace(".NS","").replace(".BO","")
        with st.spinner("Fetching trends…"):
            tdf,terr=fetch_trends(kw)
        if terr:
            st.markdown(f"<div class='alert a-warn'>⚠️ {terr}</div>",unsafe_allow_html=True)
        elif tdf is not None and not tdf.empty:
            half=len(tdf)//2; f1=tdf[kw].iloc[:half].mean(); f2=tdf[kw].iloc[half:].mean()
            growth=sdiv(f2-f1,f1,0)*100; vol_pct=m.get("vol_pct") or 999
            fig_t=go.Figure(); fig_t.add_trace(go.Scatter(x=tdf.index,y=tdf[kw],
                line=dict(color="#7c3aed",width=2),fill="tozeroy",fillcolor="rgba(124,58,237,.08)"))
            fig_t.update_layout(height=190,margin=dict(l=0,r=0,t=15,b=0),
                paper_bgcolor="#fff",plot_bgcolor="#fff",template="plotly_white",
                showlegend=False,yaxis=dict(range=[0,105],gridcolor="#f4f4f5",tickfont=dict(size=10)),
                xaxis=dict(gridcolor="#f4f4f5",tickfont=dict(size=10)))
            st.plotly_chart(fig_t,use_container_width=True,config={"displayModeBar":False})
            c1,c2,c3=st.columns(3)
            with c1: st.markdown(mc("Current Interest",f"{tdf[kw].iloc[-1]:.0f}/100","Google scale"),unsafe_allow_html=True)
            with c2: st.markdown(mc("30-Day Growth",f"{growth:+.1f}%","Search trend","#16a34a" if growth>15 else "#71717a"),unsafe_allow_html=True)
            with c3: st.markdown(mc("Price Volatility",f"{vol_pct:.1f}%" if vol_pct!=999 else "N/A","20-day std","#16a34a" if vol_pct<5 else "#d97706"),unsafe_allow_html=True)
            if growth>15 and vol_pct<5:
                st.markdown(f"""<div class='accum'>
                  <div style='font-size:1.4rem;'>🚨</div>
                  <div style='font-size:1rem;font-weight:800;color:#92400e;margin:.25rem 0;'>ACCUMULATION ZONE DETECTED</div>
                  <div style='font-size:.8rem;color:#78350f;line-height:1.6;'>
                    Search interest ↑<b>{growth:+.1f}%</b> · Volatility only <b>{vol_pct:.1f}%</b><br>
                    Quiet accumulation pattern — institutions may be buying before breakout.
                  </div>
                </div>""",unsafe_allow_html=True)
            elif growth>15: st.markdown(f"<div class='alert a-ok'>📈 Rising interest ({growth:+.1f}%) — Watch for breakout.</div>",unsafe_allow_html=True)
            elif growth<-15: st.markdown(f"<div class='alert a-warn'>📉 Declining interest ({growth:+.1f}%) — Caution.</div>",unsafe_allow_html=True)
            else: st.markdown("<div class='alert a-info'>ℹ️ Stable interest — No extreme signals.</div>",unsafe_allow_html=True)
        else: st.markdown("<div class='alert a-warn'>⚠️ Trends data not available for this ticker.</div>",unsafe_allow_html=True)

    # TAB 4
    with T4:
        st.markdown("<div class='sec'>Major Holders</div>",unsafe_allow_html=True)
        mh_df=data.get("major_holders",pd.DataFrame())
        if mh_df is not None and not mh_df.empty:
            try:
                rows_html=""
                for _,row in mh_df.iterrows():
                    val=str(row.iloc[0]); cat=str(row.iloc[1])
                    hl="background:#f0fdf4;" if "insider" in cat.lower() or "Insider" in cat else ""
                    rows_html+=f"<tr style='{hl}'><td style='padding:.45rem .75rem;font-weight:600;font-family:JetBrains Mono,monospace;font-size:.8rem;'>{val}</td><td style='padding:.45rem .75rem;color:#3f3f46;font-size:.8rem;'>{cat}</td></tr>"
                st.markdown(f"""<div class='mc'><table style='width:100%;border-collapse:collapse;'>
                  <thead><tr style='background:#fafafa;border-bottom:1px solid #e4e4e7;'>
                    <th style='text-align:left;padding:.4rem .75rem;font-size:.66rem;text-transform:uppercase;letter-spacing:.07em;color:#71717a;'>%</th>
                    <th style='text-align:left;padding:.4rem .75rem;font-size:.66rem;text-transform:uppercase;letter-spacing:.07em;color:#71717a;'>Category</th>
                  </tr></thead><tbody>{rows_html}</tbody></table></div>""",unsafe_allow_html=True)
            except Exception: st.markdown("<div class='alert a-warn'>Could not parse holders data.</div>",unsafe_allow_html=True)
        else: st.markdown("<div class='alert a-info'>Major holders data not available.</div>",unsafe_allow_html=True)
        st.markdown("<div class='sec'>Institutional Holders (Top 10)</div>",unsafe_allow_html=True)
        ih_df=data.get("inst_holders",pd.DataFrame())
        if ih_df is not None and not ih_df.empty:
            try:
                d=ih_df.head(10).copy()
                if "Value" in d.columns: d["Value"]=d["Value"].apply(lambda x: f"₹{x/1e7:.1f}Cr" if isinstance(x,(int,float)) and not math.isnan(float(x)) else "N/A")
                if "% Out" in d.columns: d["% Out"]=d["% Out"].apply(lambda x: f"{float(x)*100:.2f}%" if isinstance(x,(int,float)) else str(x))
                st.dataframe(d,use_container_width=True,hide_index=True)
            except Exception: st.markdown("<div class='alert a-warn'>Could not parse institutional holders.</div>",unsafe_allow_html=True)
        else: st.markdown("<div class='alert a-info'>Institutional holders data not available.</div>",unsafe_allow_html=True)

    # TAB 5
    with T5:
        pc="#16a34a" if pio_s>=7 else("#d97706" if pio_s>=5 else "#dc2626")
        pt="Strong 💪" if pio_s>=7 else("Moderate" if pio_s>=5 else "Weak ⚠️")
        ca,cb=st.columns([1,2])
        with ca:
            st.markdown(f"""<div class='mc' style='text-align:center;padding:1.75rem 1rem;'>
              <div style='font-size:.6rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:#71717a;margin-bottom:.35rem;'>PIOTROSKI F-SCORE</div>
              <div style='font-size:5rem;font-weight:800;color:{pc};line-height:1;font-family:"JetBrains Mono",monospace;'>{pio_s}</div>
              <div style='font-size:.72rem;color:#71717a;margin:.2rem 0 .55rem;'>out of 9</div>
              {pb(pio_s/9*100,pc)}
              <span class='bx {"b-green" if pio_s>=7 else "b-yellow" if pio_s>=5 else "b-red"}' style='margin-top:.65rem;font-size:.72rem;padding:.25rem .75rem;'>{pt}</span>
            </div>""",unsafe_allow_html=True)
        with cb:
            st.markdown("<div class='sec' style='margin-top:0;'>Breakdown</div>",unsafe_allow_html=True)
            grps_p={}
            for c in pio_c: grps_p.setdefault(c["g"],[]).append(c)
            for grp,items in grps_p.items():
                gs=sum(1 for x in items if x["p"])
                g_names={"P":"Profitability","L":"Leverage","E":"Efficiency"}
                st.markdown(f"<div style='font-size:.64rem;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#a1a1aa;margin:.6rem 0 .28rem;'>{g_names.get(grp,grp)} ({gs}/{len(items)})</div>",unsafe_allow_html=True)
                for item in items:
                    ic="✅" if item["p"] else "❌"; bg="#f0fdf4" if item["p"] else "#fef2f2"; tc="#15803d" if item["p"] else "#b91c1c"
                    st.markdown(f"""<div class='ck' style='background:{bg};'>
                      <span style='font-size:.85rem;'>{ic}</span>
                      <div><div class='ck-n' style='color:{tc};'>{item["n"]}</div>
                      <div class='ck-s'>{item["note"]}</div></div>
                    </div>""",unsafe_allow_html=True)
        st.markdown("<hr style='border:none;border-top:1px solid #e4e4e7;margin:1.25rem 0;'>",unsafe_allow_html=True)
        st.markdown("<div class='sec'>Intrinsic Value</div>",unsafe_allow_html=True)
        curr_p=m.get("price") or m.get("ph")
        c1,c2,c3,c4=st.columns(4)
        gv=iv.get("graham"); dv=iv.get("dcf"); avg_iv=iv.get("avg"); up_v=iv.get("up"); mos_v=iv.get("mos")
        with c1:
            if gv and curr_p: diff=sdiv(curr_p-gv,gv,0)*100; st.markdown(mc("Graham Number",f"₹{gv:,.1f}",f"{'Under' if curr_p<gv else 'Over'}valued {abs(diff):.1f}%","#16a34a" if curr_p<gv else "#dc2626"),unsafe_allow_html=True)
            else: st.markdown(mc("Graham Number","N/A","EPS/BVPS N/A"),unsafe_allow_html=True)
        with c2:
            if dv and curr_p: diff2=sdiv(curr_p-dv,dv,0)*100; st.markdown(mc("Graham DCF",f"₹{dv:,.1f}",f"{'Under' if curr_p<dv else 'Over'}valued {abs(diff2):.1f}%","#16a34a" if curr_p<dv else "#dc2626"),unsafe_allow_html=True)
            else: st.markdown(mc("Graham DCF","N/A","EPS/Growth N/A"),unsafe_allow_html=True)
        with c3:
            if avg_iv and curr_p: st.markdown(mc("Blended IV",f"₹{avg_iv:,.1f}",f"{'↑' if up_v and up_v>0 else '↓'} {abs(up_v):.1f}% | MOS: {mos_v:.1f}%","#16a34a" if up_v and up_v>0 else "#dc2626"),unsafe_allow_html=True)
            else: st.markdown(mc("Blended IV","N/A","Insufficient data"),unsafe_allow_html=True)
        with c4:
            at=iv.get("analyst_target"); au=iv.get("analyst_upside")
            if at and au is not None: st.markdown(mc("Analyst Target",f"₹{at:,.1f}",f"Upside: {au:+.1f}%","#16a34a" if au>0 else "#dc2626"),unsafe_allow_html=True)
            else: st.markdown(mc("Analyst Target","N/A","Not available"),unsafe_allow_html=True)
        if avg_iv and curr_p:
            if mos_v>20: st.markdown(f"<div class='alert a-ok'>✅ <b>MOS: {mos_v:.1f}%</b> — Significantly undervalued. Upside: {up_v:.1f}%</div>",unsafe_allow_html=True)
            elif mos_v>0: st.markdown(f"<div class='alert a-ok'>✅ Marginally undervalued. MOS: {mos_v:.1f}%</div>",unsafe_allow_html=True)
            elif mos_v>-20: st.markdown(f"<div class='alert a-warn'>⚠️ Near fair value. Overvalued by {abs(mos_v):.1f}%.</div>",unsafe_allow_html=True)
            else: st.markdown(f"<div class='alert a-danger'>🚨 Overvalued {abs(mos_v):.1f}%. Downside: {abs(up_v):.1f}%.</div>",unsafe_allow_html=True)
        st.markdown("<hr style='border:none;border-top:1px solid #e4e4e7;margin:1.25rem 0;'>",unsafe_allow_html=True)
        st.markdown("<div class='sec' style='margin-top:0;'>📝 Research Notes</div>",unsafe_allow_html=True)
        existing,last_upd=load_note(ticker)
        if st.button("📋 Template",key=f"tmpl_{ticker}"):
            existing=(f"📌 {ticker}  |  📅 {datetime.date.today()}\n\n🎯 THESIS:\n\n"
                      "📊 METRICS:\n- PE:\n- ROE:\n- D/E:\n- FCF:\n- Piotroski: /9\n- AI: /100\n- IV: ₹\n\n"
                      "⚠️ RISKS:\n\n🎯 TRADE:\n- Entry: ₹  Stop: ₹  Target: ₹\n\n✅ DECISION:")
        note_txt=st.text_area("",value=existing,height=260,key=f"note_{ticker}",label_visibility="collapsed")
        c1x,c2x=st.columns([3,1])
        with c1x:
            if st.button("💾 Save",key=f"save_{ticker}",use_container_width=True,type="primary"):
                save_note(ticker,note_txt); st.success("✅ Saved!")
        with c2x:
            if last_upd: st.markdown(f"<div style='font-size:.68rem;color:#a1a1aa;padding-top:.5rem;'>Saved: {last_upd}</div>",unsafe_allow_html=True)

    # TAB 6
    with T6:
        ca,cb=st.columns([1,2])
        with ca:
            fig_g=gauge_chart(total,grade,color)
            st.plotly_chart(fig_g,use_container_width=True,config={"displayModeBar":False})
        with cb:
            st.markdown("<div class='sec' style='margin-top:0;'>Score by Pillar</div>",unsafe_allow_html=True)
            pc_map={"Valuation":"#2563eb","Profitability":"#16a34a","Financial Health":"#7c3aed","Technical":"#d97706","Growth":"#0891b2"}
            for pillar,pts in bd.items():
                pc2=pc_map.get(pillar,"#71717a"); bc2="b-green" if pts>=15 else("b-yellow" if pts>=10 else "b-red")
                st.markdown(f"""<div style='background:#fff;border:1px solid #e4e4e7;border-radius:6px;padding:.6rem .85rem;margin-bottom:.35rem;'>
                  <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:.22rem;'>
                    <div style='font-size:.78rem;font-weight:600;'>{pillar}</div>
                    <span class='bx {bc2}'>{pts}/20</span>
                  </div>{pb(pts/20*100,pc2)}</div>""",unsafe_allow_html=True)
        st.markdown("<div class='sec'>Summary</div>",unsafe_allow_html=True)
        ab="above" if price>(m.get("d200") or 0) else "below"
        if total>=75: st.markdown(f"<div class='alert a-ok'><b>{ticker}</b> → <b>{total}/100 — {grade}</b>. ROE {fp(m.get('roe'))}, D/E {fn(sdiv(m.get('de'),100),2) if m.get('de') else 'N/A'}x. Piotroski {pio_s}/9. {ab.title()} 200 DMA."+(f" IV ↑{iv.get('up'):.1f}%." if iv.get('up') else "")+"</div>",unsafe_allow_html=True)
        elif total>=45: st.markdown(f"<div class='alert a-warn'><b>{ticker}</b> → <b>{total}/100 — {grade}</b>. Mixed signals. Piotroski {pio_s}/9.</div>",unsafe_allow_html=True)
        else: st.markdown(f"<div class='alert a-danger'><b>{ticker}</b> → <b>{total}/100 — {grade}</b>. High risk. Piotroski {pio_s}/9.</div>",unsafe_allow_html=True)
        st.markdown("<div class='alert a-info'>⚠️ Research tool only — Not SEBI registered advice.</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════
init_db()

# Session defaults
for k,v in [("sel_grp","Watchlist"),("sel_ticker",None),("del_req",None),("alert_req",None)]:
    if k not in st.session_state: st.session_state[k]=v

# Process query params (from JS right-click actions)
qp = st.query_params
if "action" in qp:
    action = qp.get("action","")
    t_param = qp.get("t","")
    g_param = qp.get("g","")
    if action == "select" and t_param:
        st.session_state.sel_ticker = t_param
    elif action == "delete" and t_param and g_param:
        del_t(g_param, t_param)
        if st.session_state.sel_ticker == t_param:
            st.session_state.sel_ticker = None
    st.query_params.clear()
    st.rerun()

# Top nav
st.markdown("""
<div class='topnav'>
  <div class='brand'>
    📈 Stock Analysis Pro <span class='brand-v'>v4.2</span>
  </div>
  <div style='font-size:.68rem;color:#71717a;'>Money Financial Services · TradingView UI · VPA · Trends · AI</div>
</div>
""",unsafe_allow_html=True)

left_col, right_col = st.columns([1,3], gap="small")

# ══ LEFT PANEL ══════════════════════════════════════════════
with left_col:
    groups = get_groups()
    if st.session_state.sel_grp not in groups and groups:
        st.session_state.sel_grp = groups[0]
    sel_grp = st.session_state.sel_grp

    # Group selector
    if groups:
        new_grp = st.selectbox("",groups,
            index=groups.index(sel_grp) if sel_grp in groups else 0,
            key="grp_dd",label_visibility="collapsed")
        if new_grp != sel_grp:
            st.session_state.sel_grp = new_grp
            st.session_state.sel_ticker = None
            st.rerun()
        sel_grp = new_grp

    # Group actions
    ca_g, cb_g = st.columns([3,1])
    with ca_g:
        with st.expander("➕ New Group"):
            ng=st.text_input("",placeholder="Group name…",key="ng",label_visibility="collapsed")
            if st.button("Create",use_container_width=True,key="cg"):
                if ng.strip():
                    add_t(ng.strip(),"__init__"); st.session_state.sel_grp=ng.strip(); st.rerun()
    with cb_g:
        if st.button("🗑️",key="del_g",help=f"Delete {sel_grp}"):
            del_grp(sel_grp)
            st.session_state.sel_grp=groups[0] if len(groups)>1 else "Watchlist"
            st.session_state.sel_ticker=None; st.rerun()

    # Add stock
    with st.expander("🔍 Add Stock"):
        sq=st.text_input("",placeholder="Search: HDFC, Wipro…",key="sq",label_visibility="collapsed")
        tickers_now=[t for t in get_tickers(sel_grp)]
        if sq:
            ql=sq.lower(); hits={}; seen=set()
            for name,t in STOCK_DB.items():
                if(ql in name.lower() or ql in t.lower()) and t not in seen:
                    seen.add(t); hits[name]=t
            for name,t in list(hits.items())[:5]:
                already=t in tickers_now
                ca2,cb2=st.columns([5,1])
                with ca2: st.markdown(f"<div style='font-size:.72rem;padding:.1rem 0;'><b>{t}</b><br><span style='color:#a1a1aa;font-size:.64rem;'>{name}</span></div>",unsafe_allow_html=True)
                with cb2:
                    if already: st.markdown("<div style='padding-top:.3rem;font-size:.8rem;'>✅</div>",unsafe_allow_html=True)
                    elif st.button("＋",key=f"h_{t}_{sel_grp}"): add_t(sel_grp,t); st.success(f"✅ {t}"); st.rerun()
        mt=st.text_input("",placeholder="Manual: SBIN.NS",key="mt",label_visibility="collapsed")
        if st.button("Add",use_container_width=True,key="mt_btn"):
            t=mt.strip().upper()
            if t and t not in tickers_now: add_t(sel_grp,t); st.success(f"✅ {t}"); st.rerun()
            elif t: st.warning("Already exists.")

    st.markdown("<hr style='border:none;border-top:1px solid #e4e4e7;margin:.5rem 0;'>",unsafe_allow_html=True)

    # ── INSTITUTIONAL LIST VIEW ──────────────────────────
    tickers_list=[t for t in get_tickers(sel_grp)]
    if not tickers_list:
        st.markdown("<div style='padding:1.5rem 1rem;font-size:.78rem;color:#a1a1aa;text-align:center;'>No stocks yet.<br>Use Add Stock above ↑</div>",unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size:.64rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#a1a1aa;padding:.3rem .5rem .4rem;'>{sel_grp.upper()} · {len(tickers_list)}</div>",unsafe_allow_html=True)

        # Right-click context menu JS
        st.markdown("""
        <div id="ctx" class="ctx-menu">
          <div class="ctx-item" id="ctx-view">📈 View Analysis</div>
          <div class="ctx-item" id="ctx-alert">🔔 Add Alert (coming soon)</div>
          <hr class="ctx-sep">
          <div class="ctx-item danger" id="ctx-del">🗑️ Delete from Watchlist</div>
        </div>
        <script>
        (function(){
          var ctx=document.getElementById('ctx');
          var ctxTicker=''; var ctxGrp='';
          function hide(){ctx.classList.remove('show');}
          document.addEventListener('click',hide);
          document.addEventListener('scroll',hide);
          window.openCtx=function(e,ticker,grp){
            e.preventDefault(); e.stopPropagation();
            ctxTicker=ticker; ctxGrp=grp;
            ctx.style.left=e.clientX+'px';
            ctx.style.top=e.clientY+'px';
            ctx.classList.add('show');
          };
          document.getElementById('ctx-view').onclick=function(){
            window.location.href='?action=select&t='+encodeURIComponent(ctxTicker)+'&g='+encodeURIComponent(ctxGrp);
            hide();
          };
          document.getElementById('ctx-alert').onclick=function(){
            alert('Alert feature coming in v5.0!'); hide();
          };
          document.getElementById('ctx-del').onclick=function(){
            if(confirm('Remove '+ctxTicker+' from '+ctxGrp+'?')){
              window.location.href='?action=delete&t='+encodeURIComponent(ctxTicker)+'&g='+encodeURIComponent(ctxGrp);
            }
            hide();
          };
        })();
        </script>
        """,unsafe_allow_html=True)

        for t in tickers_list:
            is_sel = st.session_state.sel_ticker == t
            pd_data = fetch_price(t)
            p=pd_data["price"]; pr=pd_data["prev"]; nm=pd_data["name"]
            logo_url=get_logo(pd_data.get("website",""))

            if p and pr and pr>0:
                chgp_l=sdiv(p-pr,pr,0)*100
                cc2="#16a34a" if chgp_l>=0 else "#dc2626"
                bg_c="#f0fdf4" if chgp_l>=0 else "#fef2f2"
                arr2="▲" if chgp_l>=0 else "▼"
                chg_s=f"{arr2}{abs(chgp_l):.2f}%"; p_s=f"{p:,.1f}"
            else:
                cc2,bg_c,chg_s="#71717a","#fafafa","—"
                p_s=f"{p:,.1f}" if p else "—"

            sel_bg="#eff6ff" if is_sel else "#fff"
            sel_bdr="1px solid #bfdbfe" if is_sel else "1px solid transparent"
            ticker_abbr=t.replace(".NS","").replace(".BO","")[:3]

            if logo_url:
                logo_html=f'<img src="{logo_url}" class="wlogo" onerror="this.outerHTML=\'<div class=\\"wlogo-placeholder\\">{ticker_abbr}</div>\'">'
            else:
                logo_html=f'<div class="wlogo-placeholder">{ticker_abbr}</div>'

            # Compact TradingView-style row
            st.markdown(f"""
            <div class="wrow {'sel' if is_sel else ''}"
                 style="background:{sel_bg};border-bottom:1px solid #f4f4f5;{sel_bdr}"
                 oncontextmenu="openCtx(event,'{t}','{sel_grp}');return false;"
                 onclick="window.location.href='?action=select&t={urllib.parse.quote(t)}&g={urllib.parse.quote(sel_grp)}'">
              {logo_html}
              <div class="winfo">
                <div class="wticker">{t.replace('.NS','').replace('.BO','')}</div>
                <div class="wname">{nm[:22]}</div>
              </div>
              <div class="wprice-wrap">
                <div class="wprice">{p_s}</div>
                <div class="wchg {'up' if chgp_l>=0 else 'down' if p and pr else 'flat'}" style="background:{bg_c};color:{cc2};">{chg_s}</div>
              </div>
              <div class="wtrash" onclick="event.stopPropagation();if(confirm('Remove {t}?'))window.location.href='?action=delete&t={urllib.parse.quote(t)}&g={urllib.parse.quote(sel_grp)}'">🗑</div>
            </div>
            """,unsafe_allow_html=True)

# ══ RIGHT PANEL ══════════════════════════════════════════════
with right_col:
    sel=st.session_state.sel_ticker
    if not sel:
        st.markdown("""
        <div class='landing'>
          <div style='font-size:2.5rem;margin-bottom:.9rem;'>📊</div>
          <div style='font-size:1.35rem;font-weight:700;color:#09090b;margin-bottom:.45rem;'>Stock Analysis Pro v4.2</div>
          <div style='font-size:.85rem;color:#71717a;max-width:420px;line-height:1.75;'>
            Click any stock from the list — or <b>right-click</b> for more options.
          </div>
          <div style='margin-top:1.25rem;display:flex;gap:.5rem;flex-wrap:wrap;justify-content:center;'>
            <span class='bx b-blue'>Candlestick + VPA</span>
            <span class='bx b-purple'>Google Trends</span>
            <span class='bx b-green'>Graham / DCF</span>
            <span class='bx b-yellow'>Piotroski</span>
            <span class='bx b-gray'>AI Score 0–100</span>
          </div>
        </div>
        """,unsafe_allow_html=True)
    else:
        render_analysis(sel)

st.markdown("""
<div style='text-align:center;font-size:.64rem;color:#a1a1aa;padding:.6rem 0 1.5rem;border-top:1px solid #e4e4e7;margin-top:.75rem;'>
  📊 Stock Analysis Pro v4.2 · Money Financial Services · Yahoo Finance + Google Trends · Educational only · Not SEBI advice
</div>
""",unsafe_allow_html=True)
