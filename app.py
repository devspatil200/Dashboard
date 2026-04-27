"""
Stock Analysis Pro — v6.0
Author  : Money Financial Services
Pages   : Discovery Hub · Pro Watchlist · Deep Dive · AI Verdict & Strategy
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3, datetime, math

# ══════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Stock Analysis Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: #f8fafc !important;
}
.stApp { background: #f8fafc !important; }
.stApp > header { display: none !important; }
#MainMenu, footer { display: none !important; }

/* ── Fix top padding cutoff ── */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1440px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 0.85rem !important;
    border-radius: 8px !important;
    display: block !important;
    transition: background .15s !important;
    color: #cbd5e1 !important;
}
[data-testid="stSidebar"] .stRadio label:hover { background: rgba(255,255,255,.08) !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.1) !important; }

/* ── Cards ── */
.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.05), 0 4px 16px rgba(0,0,0,.04);
    transition: box-shadow .2s;
}
.card:hover { box-shadow: 0 4px 20px rgba(0,0,0,.1); }

/* ── Page header ── */
.page-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    border-radius: 14px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    color: #fff;
}
.ph-title { font-size: 1.45rem; font-weight: 800; color: #fff; }
.ph-sub   { font-size: 0.82rem; color: #94a3b8; margin-top: 3px; }

/* ── Section header ── */
.sec {
    font-size: 0.82rem;
    font-weight: 700;
    color: #0f172a;
    border-left: 3px solid #3b82f6;
    padding-left: 9px;
    margin: 1.4rem 0 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Metric card ── */
.mc {
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.65rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.ml { font-size: 0.6rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 3px; }
.mv { font-size: 1.25rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; line-height: 1.1; }
.ms { font-size: 0.64rem; color: #94a3b8; margin-top: 2px; }

/* ── Score badge ── */
.score-badge {
    display: inline-block; border-radius: 999px;
    font-size: 0.72rem; font-weight: 700; padding: 0.22rem 0.65rem;
}
.s-green  { background: #dcfce7; color: #15803d; }
.s-yellow { background: #fef9c3; color: #854d0e; }
.s-red    { background: #fee2e2; color: #b91c1c; }
.s-blue   { background: #dbeafe; color: #1d4ed8; }
.s-purple { background: #ede9fe; color: #6d28d9; }
.s-gray   { background: #f1f5f9; color: #475569; }

/* ── Progress bar ── */
.pb { background: #e2e8f0; border-radius: 999px; height: 5px; }
.pbf { height: 5px; border-radius: 999px; }

/* ── Alerts ── */
.al { border-radius: 10px; padding: 0.8rem 1rem; font-size: 0.83rem; margin: 0.5rem 0; line-height: 1.55; }
.al-ok     { background: #f0fdf4; border: 1px solid #86efac; color: #15803d; }
.al-warn   { background: #fffbeb; border: 1px solid #fcd34d; color: #92400e; }
.al-danger { background: #fef2f2; border: 1px solid #fca5a5; color: #991b1b; }
.al-info   { background: #eff6ff; border: 1px solid #93c5fd; color: #1d4ed8; }
.al-purple { background: #ede9fe; border: 1px solid #c4b5fd; color: #5b21b6; }
.al-gold   { background: linear-gradient(135deg,#fefce8,#fef9c3); border: 2px solid #f59e0b; }

/* ── Watchlist row ── */
.wl-header {
    font-size: 0.62rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #94a3b8; padding-bottom: 4px;
}
.wl-row-border { border-top: 1px solid #f1f5f9; margin: 3px 0; }

/* ── Trap cards ── */
.trap-card {
    border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 0.75rem;
}
.trap-danger { background: linear-gradient(135deg,#fef2f2,#fee2e2); border: 2px solid #f87171; }
.trap-ok     { background: linear-gradient(135deg,#f0fdf4,#dcfce7); border: 2px solid #4ade80; }
.trap-warn   { background: linear-gradient(135deg,#fffbeb,#fef3c7); border: 2px solid #fbbf24; }

/* ── Buttons ── */
[data-testid="stButton"] > button {
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    transition: all 0.15s !important;
}
/* ── Inputs ── */
[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    border: 1.5px solid #e2e8f0 !important;
    padding: 0.5rem 0.85rem !important;
    background: #fff !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,.12) !important;
}
/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
}
/* ── Metric override ── */
[data-testid="stMetric"] {
    background: #fff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 0.85rem 1rem !important;
}
[data-testid="stMetric"] label {
    font-size: 0.62rem !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 0.08em !important;
    color: #94a3b8 !important;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.2rem !important; font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
}
hr { border-color: #e2e8f0 !important; margin: 1rem 0 !important; }
div[data-testid="stAlert"] { border-radius: 10px !important; font-size: 0.83rem !important; }
[data-testid="stDataFrame"] { border-radius: 10px !important; }
[data-testid="stExpander"] { border: 1px solid #e2e8f0 !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# DATABASE
# ══════════════════════════════════════════════════════════
DB = "sap_v6.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS watchlist (
        ticker TEXT PRIMARY KEY, name TEXT, added_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS notes (
        ticker TEXT PRIMARY KEY, content TEXT, updated_at TEXT)""")
    conn.commit(); conn.close()

def db_wl():
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT ticker,name FROM watchlist ORDER BY added_at DESC").fetchall()
    conn.close(); return rows

def db_add(ticker, name=""):
    conn = sqlite3.connect(DB)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute("INSERT OR IGNORE INTO watchlist VALUES (?,?,?)", (ticker.upper().strip(), name, now))
    conn.commit(); conn.close()

def db_del(ticker):
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM watchlist WHERE ticker=?", (ticker,))
    conn.commit(); conn.close()

def db_note_save(ticker, content):
    conn = sqlite3.connect(DB)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute("INSERT OR REPLACE INTO notes VALUES (?,?,?)", (ticker.upper(), content, now))
    conn.commit(); conn.close()

def db_note_load(ticker):
    conn = sqlite3.connect(DB)
    r = conn.execute("SELECT content,updated_at FROM notes WHERE ticker=?", (ticker.upper(),)).fetchall()
    conn.close(); return (r[0][0], r[0][1]) if r else ("", "")

# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
init_db()
for k, v in [
    ("page",            "🔍 Discovery Hub"),
    ("watchlist",       None),
    ("analyse_ticker",  None),
    ("search_ticker",   None),
    ("search_data",     None),
]:
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state.watchlist is None:
    rows = db_wl()
    st.session_state.watchlist = [r[0] for r in rows]

# ══════════════════════════════════════════════════════════
# DATA LAYER
# ══════════════════════════════════════════════════════════
@st.cache_resource
def _cache(): return {}

def safe_info(ticker):
    cache = _cache(); key = f"info_{ticker}_{datetime.datetime.now().strftime('%Y%m%d%H')}"
    if key in cache: return cache[key]
    try:
        info = yf.Ticker(ticker).info or {}
        cache[key] = info; return info
    except: return {}

def safe_hist(ticker, period="1y"):
    cache = _cache(); key = f"hist_{ticker}_{period}_{datetime.datetime.now().strftime('%Y%m%d%H')}"
    if key in cache: return cache[key]
    try:
        h = yf.Ticker(ticker).history(period=period); cache[key] = h; return h
    except: return pd.DataFrame()

def safe_full(ticker):
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
        try:    mh  = stk.major_holders
        except: mh  = pd.DataFrame()
        try:    ih  = stk.institutional_holders
        except: ih  = pd.DataFrame()
        return {"ok":True,"info":info,"hist":hist,"fin":fin,"bs":bs,"cf":cf,"mh":mh,"ih":ih}
    except Exception as e:
        return {"ok":False,"error":str(e),"info":{},"hist":pd.DataFrame(),
                "fin":pd.DataFrame(),"bs":pd.DataFrame(),"cf":pd.DataFrame(),
                "mh":pd.DataFrame(),"ih":pd.DataFrame()}

# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════
def _v(d, *keys, default=None):
    for k in keys:
        try:
            v = d.get(k) if isinstance(d, dict) else None
            if v is not None and not (isinstance(v, float) and math.isnan(v)): return v
        except: pass
    return default

def _row(df, *names):
    try:
        if df is None or df.empty: return None
        for n in names:
            for idx in df.index:
                if n.lower() in str(idx).lower():
                    s = df.loc[idx].dropna()
                    if not s.empty: return s
    except: pass
    return None

def _lat(s):
    try:
        if s is None: return None
        s2 = s.dropna(); return float(s2.iloc[0]) if not s2.empty else None
    except: return None

def sdiv(a, b, default=None):
    try:
        if b is None or b == 0: return default
        return a / b
    except: return default

def sf(v):
    try:
        if v is None: return None
        f = float(v); return None if math.isnan(f) else f
    except: return None

def fc(v):
    if v is None: return "—"
    try:
        v = float(v)
        if abs(v) >= 1e12: return f"₹{v/1e12:.2f}T"
        if abs(v) >= 1e7:  return f"₹{v/1e7:.2f}Cr"
        if abs(v) >= 1e5:  return f"₹{v/1e5:.2f}L"
        return f"₹{v:,.0f}"
    except: return "—"

def fp(v, d=1):
    if v is None: return "—"
    try: return f"{float(v)*100:.{d}f}%"
    except: return "—"

def fn(v, d=2):
    if v is None: return "—"
    try: return f"{float(v):,.{d}f}"
    except: return "—"

def logo_url(w):
    try:
        if not w: return None
        d = w.replace("https://","").replace("http://","").split("/")[0]
        return f"https://logo.clearbit.com/{d}" if d else None
    except: return None

def mc(lbl, val, sub="", vc="#0f172a"):
    st.markdown(
        f"<div class='mc'><div class='ml'>{lbl}</div>"
        f"<div class='mv' style='color:{vc};'>{val}</div>"
        + (f"<div class='ms'>{sub}</div>" if sub else "") + "</div>",
        unsafe_allow_html=True)

def sec(t):
    st.markdown(f"<div class='sec'>{t}</div>", unsafe_allow_html=True)

def badge(txt, cls="s-gray"):
    return f"<span class='score-badge {cls}'>{txt}</span>"

def pb_bar(pct, color="#3b82f6"):
    pct = max(0, min(100, pct))
    return (f"<div class='pb'><div class='pbf' style='width:{pct}%;background:{color};'></div></div>")

# ══════════════════════════════════════════════════════════
# METRICS BUILDER  (with fallbacks for N/A)
# ══════════════════════════════════════════════════════════
def build_m(data):
    info, fin, bs, cf, hist = (
        data["info"], data["fin"], data["bs"], data["cf"], data["hist"])
    m = {}
    # Identity
    m["name"]   = _v(info, "longName", "shortName", default=ticker_name(data))
    m["sector"] = _v(info, "sector",   default="—")
    m["ind"]    = _v(info, "industry", default="—")
    m["exch"]   = _v(info, "exchange", default="—")
    m["curr"]   = _v(info, "currency", default="INR")
    m["web"]    = _v(info, "website",  default="")
    # Price
    m["price"]  = _v(info, "regularMarketPrice", "currentPrice")
    m["prev"]   = _v(info, "regularMarketPreviousClose")
    m["mktcap"] = _v(info, "marketCap")
    m["beta"]   = _v(info, "beta")
    m["target"] = _v(info, "targetMeanPrice")
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
    # Balance
    m["de"]  = _v(info, "debtToEquity")
    m["cr"]  = _v(info, "currentRatio")
    m["qr"]  = _v(info, "quickRatio")
    m["fcf"] = _v(info, "freeCashflow")
    m["ocf"] = _v(info, "operatingCashflow")
    # Growth
    m["rg"]  = _v(info, "revenueGrowth")
    m["eg"]  = _v(info, "earningsGrowth")
    m["eps"] = _v(info, "trailingEps")
    m["feps"]= _v(info, "forwardEps")
    m["dy"]  = _v(info, "dividendYield")
    m["h52"] = _v(info, "fiftyTwoWeekHigh")
    m["l52"] = _v(info, "fiftyTwoWeekLow")
    # Fallback ROE
    if m["roe"] is None:
        ni = _lat(_row(fin, "Net Income"))
        eq = _lat(_row(bs,  "Stockholders Equity", "Total Stockholder Equity"))
        m["roe"] = sdiv(ni, abs(eq)) if ni and eq else None
    # Fallback ROA
    if m["roa"] is None:
        ni = _lat(_row(fin, "Net Income"))
        ta = _lat(_row(bs,  "Total Assets"))
        m["roa"] = sdiv(ni, abs(ta)) if ni and ta else None
    # Fallback PM
    if m["pm"] is None:
        ni  = _lat(_row(fin, "Net Income"))
        rev = _lat(_row(fin, "Total Revenue"))
        m["pm"] = sdiv(ni, abs(rev)) if ni and rev else None
    # Fallback D/E
    if m["de"] is None:
        td = _lat(_row(bs, "Total Debt", "Long Term Debt"))
        eq = _lat(_row(bs, "Stockholders Equity", "Total Stockholder Equity"))
        if td is not None and eq:
            v = sdiv(td, abs(eq)); m["de"] = v * 100 if v is not None else None
    # Fallback FCF
    if m["fcf"] is None:
        ocf  = _lat(_row(cf, "Operating Cash Flow", "Cash From Operations"))
        capx = _lat(_row(cf, "Capital Expenditure",
                         "Purchases Of Property Plant And Equipment"))
        if ocf is not None:
            m["ocf"] = ocf; m["fcf"] = ocf + (capx if capx else 0)
    # Technicals
    if not hist.empty:
        try:
            close = hist["Close"]
            m["ph"]   = float(close.iloc[-1])
            m["vol"]  = float(hist["Volume"].iloc[-1])
            m["v20"]  = float(hist["Volume"].rolling(20).mean().iloc[-1]) if len(hist) >= 20 else None
            m["d50"]  = float(close.rolling(50).mean().iloc[-1])  if len(close) >= 50  else None
            m["d200"] = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None
            delta = close.diff()
            gain  = delta.clip(lower=0).rolling(14).mean()
            loss  = (-delta.clip(upper=0)).rolling(14).mean()
            rs    = gain / loss.replace(0, float("nan"))
            rsi   = 100 - (100 / (1 + rs))
            m["rsi"] = float(rsi.iloc[-1]) if not rsi.empty else None
            e12 = close.ewm(span=12).mean(); e26 = close.ewm(span=26).mean()
            macd = e12 - e26; sig = macd.ewm(span=9).mean()
            m["macd"] = float(macd.iloc[-1]); m["msig"] = float(sig.iloc[-1])
            m["mh"]   = float((macd - sig).iloc[-1])
            m["vp"]   = float(close.pct_change().rolling(20).std().iloc[-1] * 100) if len(close) >= 20 else None
            if m["v20"] and m["v20"] > 0:
                mask = ((hist["Close"] > hist["Close"].shift(1)) &
                        (hist["Volume"] > 2 * hist["Volume"].rolling(20).mean()))
                m["vpa"] = list(hist.index[mask])
            else:
                m["vpa"] = []
        except:
            for k in ["ph","vol","v20","d50","d200","rsi","macd","msig","mh","vp","vpa"]:
                m[k] = None
    else:
        for k in ["ph","vol","v20","d50","d200","rsi","macd","msig","mh","vp","vpa"]:
            m[k] = None
    return m

def ticker_name(data):
    return _v(data.get("info",{}), "shortName", "longName", default="")

# ══════════════════════════════════════════════════════════
# PIOTROSKI F-SCORE
# ══════════════════════════════════════════════════════════
def piotroski(data):
    info, fin, bs, cf = data["info"], data["fin"], data["bs"], data["cf"]
    C = []

    def _l(df, *n): return _lat(_row(df, *n))
    def _lp(df, *n):
        r = _row(df, *n)
        if r is None or len(r.dropna()) < 2: return None
        return float(r.dropna().iloc[1])

    ni_c = _l(fin, "Net Income");    ni_p  = _lp(fin, "Net Income")
    rv_c = _l(fin, "Total Revenue"); rv_p  = _lp(fin, "Total Revenue")
    ta_c = _l(bs,  "Total Assets");  ta_p  = _lp(bs,  "Total Assets")
    ocf  = _l(cf, "Operating Cash Flow", "Cash From Operations")
    roa  = _v(info, "returnOnAssets")
    if roa is None and ni_c and ta_c and ta_c != 0:
        roa = sdiv(ni_c, ta_c)

    def A(g, n, p, note): C.append({"g": g, "n": n, "p": p, "note": note})

    A("Profitability", "F1 — ROA Positive",
      roa is not None and roa > 0, f"ROA = {roa*100:.1f}%" if roa else "N/A")
    A("Profitability", "F2 — OCF Positive",
      ocf is not None and ocf > 0, f"₹{ocf/1e7:.1f} Cr" if ocf else "N/A")
    if roa is not None and ta_p and ni_p and ta_p != 0:
        rp = sdiv(ni_p, ta_p, 0)
        A("Profitability", "F3 — ROA Improving YoY", roa > rp,
          f"Curr {roa*100:.1f}% vs Prev {rp*100:.1f}%")
    else:
        A("Profitability", "F3 — ROA Improving YoY", False, "Insufficient data")
    if ocf and ta_c and ta_c != 0 and roa is not None:
        A("Profitability", "F4 — Cash Earnings > Paper",
          sdiv(ocf, ta_c, 0) > roa,
          f"OCF/TA={sdiv(ocf,ta_c,0)*100:.1f}% vs ROA={roa*100:.1f}%")
    else:
        A("Profitability", "F4 — Cash Earnings > Paper", False, "N/A")

    ltd = _row(bs, "Long Term Debt")
    if ltd is not None and len(ltd.dropna()) >= 2 and ta_c and ta_p:
        lv = ltd.dropna()
        rc = sdiv(float(lv.iloc[0]), ta_c, 0); rp2 = sdiv(float(lv.iloc[1]), ta_p, 0)
        A("Leverage", "F5 — Debt Ratio Decreasing", rc < rp2,
          f"Curr {rc*100:.1f}% vs Prev {rp2*100:.1f}%")
    else:
        A("Leverage", "F5 — Debt Ratio Decreasing", False, "N/A")

    ca = _row(bs, "Current Assets"); cl = _row(bs, "Current Liabilities")
    if ca is not None and cl is not None and len(ca.dropna()) >= 2:
        cav = ca.dropna(); clv = cl.dropna()
        cc  = sdiv(float(cav.iloc[0]), float(clv.iloc[0]))
        cp  = sdiv(float(cav.iloc[1]), float(clv.iloc[1]))
        A("Leverage", "F6 — Current Ratio Improving",
          bool(cc and cp and cc > cp),
          f"Curr {cc:.2f} vs Prev {cp:.2f}" if cc and cp else "N/A")
    else:
        cr_i = _v(info, "currentRatio")
        A("Leverage", "F6 — Current Ratio > 1.5",
          cr_i is not None and cr_i > 1.5,
          f"CR = {cr_i:.2f}" if cr_i else "N/A")

    sh = _row(bs, "Ordinary Shares Number", "Common Stock Shares Outstanding")
    if sh is not None and len(sh.dropna()) >= 2:
        sv = sh.dropna()
        A("Leverage", "F7 — No Share Dilution",
          float(sv.iloc[0]) <= float(sv.iloc[1]),
          f"Curr {float(sv.iloc[0])/1e7:.2f}Cr vs Prev {float(sv.iloc[1])/1e7:.2f}Cr")
    else:
        A("Leverage", "F7 — No Share Dilution", False, "N/A")

    gp = _row(fin, "Gross Profit")
    if gp is not None and len(gp.dropna()) >= 2 and rv_c and rv_p:
        gv = gp.dropna()
        gmc = sdiv(float(gv.iloc[0]), rv_c, 0)
        gmp = sdiv(float(gv.iloc[1]), rv_p, 0)
        A("Efficiency", "F8 — Gross Margin Improving", gmc > gmp,
          f"Curr {gmc*100:.1f}% vs Prev {gmp*100:.1f}%")
    else:
        gm_i = _v(info, "grossMargins")
        A("Efficiency", "F8 — Gross Margin > 20%",
          gm_i is not None and gm_i > 0.20,
          f"GM = {gm_i*100:.1f}%" if gm_i else "N/A")

    if rv_c and rv_p and ta_c and ta_p:
        A("Efficiency", "F9 — Asset Turnover Improving",
          sdiv(rv_c, ta_c, 0) > sdiv(rv_p, ta_p, 0),
          f"Curr {sdiv(rv_c,ta_c,0):.2f}x vs Prev {sdiv(rv_p,ta_p,0):.2f}x")
    else:
        A("Efficiency", "F9 — Asset Turnover Improving", False, "Insufficient data")

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

    r["graham"] = math.sqrt(22.5 * eps * bvps) if (
        eps and eps > 0 and bvps and bvps > 0) else None

    g = m.get("eg") or m.get("rg")
    if eps and eps > 0 and g is not None:
        g2 = max(-20, min(50, g * 100))
        dcf = eps * (8.5 + 2 * g2) * 4.4 / 7.5
        r["dcf"] = dcf if dcf > 0 else None
    else:
        r["dcf"] = None

    tg = m.get("target")
    r["at"] = tg
    r["au"] = sdiv(tg - price, price, 0) * 100 if tg and price else None

    valid = [v for v in [r.get("graham"), r.get("dcf")] if v]
    if valid and price:
        avg    = sum(valid) / len(valid)
        r["avg"] = avg
        r["mos"] = sdiv(avg - price, avg, 0) * 100
        r["up"]  = sdiv(avg - price, price, 0) * 100
    else:
        r["avg"] = r["mos"] = r["up"] = None
    return r

# ══════════════════════════════════════════════════════════
# AI SCORE  (0-100)
# ══════════════════════════════════════════════════════════
def calc_ai(m, pio, iv):
    bd = {}
    price = m.get("price") or m.get("ph") or 0

    v = 0
    pe = m.get("pe"); pb = m.get("pb")
    if pe: v += 10 if pe < 15 else (7 if pe < 25 else (4 if pe < 40 else 0))
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
    if total >= 75:   grade, col = "Excellent — Strong Buy",  "#16a34a"
    elif total >= 60: grade, col = "Good — Buy",              "#2563eb"
    elif total >= 45: grade, col = "Average — Watch",         "#d97706"
    elif total >= 30: grade, col = "Weak — Caution",          "#ea580c"
    else:             grade, col = "Poor — Avoid",            "#dc2626"
    return total, bd, grade, col

# ══════════════════════════════════════════════════════════
# TRAP DETECTOR LOGIC
# ══════════════════════════════════════════════════════════
def trap_detect(m, pio_s, total, iv):
    price = m.get("price") or m.get("ph") or 0
    mos   = iv.get("mos")
    pb    = m.get("pb") or 0
    pe    = m.get("pe") or 0
    rsi   = m.get("rsi") or 50
    de    = (m.get("de") or 0) / 100
    fcf   = m.get("fcf")

    alerts = []

    # Value Trap: Low score + Low Price from 52W High + Weak fundamentals
    h52 = m.get("h52") or price
    pct_from_high = sdiv(price - h52, h52, 0) * 100 if h52 else 0
    if total < 40 and pct_from_high < -30 and (pio_s < 4):
        alerts.append({
            "type": "VALUE_TRAP",
            "title": "🪤 Value Trap Detected",
            "desc": (f"Stock is down {abs(pct_from_high):.0f}% from 52W High, "
                     f"Piotroski {pio_s}/9, AI Score {total}/100. "
                     "This appears cheap but fundamentals are weak. "
                     "Cheap price ≠ good investment. Avoid."),
            "cls": "trap-danger"
        })

    # Debt Trap
    if de > 2 and (fcf is None or fcf < 0):
        alerts.append({
            "type": "DEBT_TRAP",
            "title": "💣 Debt Trap Warning",
            "desc": (f"Debt/Equity ratio is extremely high ({de:.1f}x) "
                     "with negative/no free cash flow. "
                     "Company may struggle to service debt in a downturn."),
            "cls": "trap-danger"
        })

    # Overbought + Overvalued
    if rsi > 72 and (mos is not None and mos < -25):
        alerts.append({
            "type": "OVERBOUGHT_OVERVALUED",
            "title": "🚨 Overbought + Overvalued",
            "desc": (f"RSI {rsi:.0f} (Overbought) AND stock is overvalued by "
                     f"{abs(mos):.0f}% above intrinsic value. "
                     "High risk of sharp correction. Do NOT chase."),
            "cls": "trap-danger"
        })

    # Quality Premium — High score, premium priced
    if total >= 70 and pio_s >= 7 and pb > 5:
        alerts.append({
            "type": "QUALITY_PREMIUM",
            "title": "⭐ Quality Premium Stock",
            "desc": (f"AI Score {total}/100, Piotroski {pio_s}/9 — Excellent fundamentals. "
                     f"P/B of {pb:.1f}x reflects quality premium. "
                     "Buy on dips. Suitable for long-term 8-10 year holding."),
            "cls": "trap-ok"
        })

    # Accumulation Zone
    vp = m.get("vp") or 999
    if vp < 5 and (mos is not None and mos > 20):
        alerts.append({
            "type": "ACCUMULATION",
            "title": "📦 Accumulation Zone",
            "desc": (f"Price volatility low ({vp:.1f}%) + undervalued by {mos:.0f}%. "
                     "Quiet accumulation pattern — institutions may be loading. "
                     "Good entry zone for patient investors."),
            "cls": "trap-warn"
        })

    # Oversold value play
    if rsi < 30 and total >= 55 and (mos is not None and mos > 10):
        alerts.append({
            "type": "OVERSOLD_VALUE",
            "title": "🔎 Oversold Value Play",
            "desc": (f"RSI {rsi:.0f} (Oversold) but fundamentals are solid (AI: {total}/100). "
                     f"Undervalued by {mos:.0f}%. "
                     "Could be an opportunity — wait for RSI > 35 confirmation."),
            "cls": "trap-ok"
        })

    # Nothing triggered
    if not alerts:
        alerts.append({
            "type": "NEUTRAL",
            "title": "✅ No Traps Detected",
            "desc": (f"No major red flags. AI Score {total}/100, Piotroski {pio_s}/9. "
                     "Continue standard due diligence before investing."),
            "cls": "trap-warn"
        })

    return alerts

# ══════════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════════
def chart_candle(hist, d50=None, d200=None, vpa=None):
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        if hist.empty: return None
        ema20 = hist["Close"].ewm(span=20).mean()
        ema50 = hist["Close"].ewm(span=50).mean()
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            vertical_spacing=0.03, row_heights=[0.75, 0.25])
        fig.add_trace(go.Candlestick(
            x=hist.index, open=hist["Open"], high=hist["High"],
            low=hist["Low"], close=hist["Close"], name="Price",
            increasing_line_color="#16a34a", decreasing_line_color="#ef4444",
            increasing_fillcolor="#16a34a", decreasing_fillcolor="#ef4444",
        ), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=ema20, name="EMA 20",
            line=dict(color="#3b82f6", width=1.6)), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=ema50, name="EMA 50",
            line=dict(color="#f59e0b", width=1.6, dash="dot")), row=1, col=1)
        if d200 is not None:
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Close"].rolling(200).mean(),
                name="200 DMA", line=dict(color="#8b5cf6", width=1.2, dash="dot")),
                row=1, col=1)
        if vpa:
            vd = [d for d in vpa if d in hist.index]
            vp = [hist.loc[d, "High"] * 1.01 for d in vd]
            if vd:
                fig.add_trace(go.Scatter(x=vd, y=vp, mode="markers",
                    name="🏦 Inst.Buy", marker=dict(symbol="triangle-up",
                    size=11, color="#7c3aed", line=dict(color="#fff", width=1.5))),
                    row=1, col=1)
        colors = ["#16a34a" if c >= o else "#ef4444"
                  for c, o in zip(hist["Close"], hist["Open"])]
        fig.add_trace(go.Bar(x=hist.index, y=hist["Volume"], name="Volume",
            marker_color=colors, opacity=0.5, showlegend=False), row=2, col=1)
        fig.update_layout(
            height=460, margin=dict(l=0, r=0, t=16, b=0),
            paper_bgcolor="#fff", plot_bgcolor="#fff", template="plotly_white",
            font=dict(family="Inter", size=11, color="#475569"),
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.01,
                        xanchor="right", x=1, bgcolor="rgba(0,0,0,0)",
                        font=dict(size=10)),
            yaxis=dict(showgrid=True, gridcolor="#f1f5f9", side="right",
                       zeroline=False, tickfont=dict(size=10)),
            yaxis2=dict(showgrid=False, side="right", zeroline=False, tickfont=dict(size=9)),
            xaxis2=dict(showgrid=True, gridcolor="#f1f5f9", tickfont=dict(size=10)))
        return fig
    except: return None

def chart_rsi(hist):
    try:
        import plotly.graph_objects as go
        if hist.empty: return None
        close = hist["Close"]; delta = close.diff()
        gain  = delta.clip(lower=0).rolling(14).mean()
        loss  = (-delta.clip(upper=0)).rolling(14).mean()
        rs    = gain / loss.replace(0, float("nan"))
        rsi   = 100 - (100 / (1 + rs))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=rsi, name="RSI(14)",
            line=dict(color="#7c3aed", width=2),
            fill="tozeroy", fillcolor="rgba(124,58,237,.06)"))
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(239,68,68,.07)", line_width=0,
            annotation_text="Overbought >70", annotation_position="top left",
            annotation=dict(font_size=10, font_color="#dc2626"))
        fig.add_hrect(y0=0, y1=30, fillcolor="rgba(22,163,74,.07)", line_width=0,
            annotation_text="Oversold <30", annotation_position="bottom left",
            annotation=dict(font_size=10, font_color="#16a34a"))
        fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", line_width=1, opacity=0.5)
        fig.add_hline(y=30, line_dash="dash", line_color="#16a34a", line_width=1, opacity=0.5)
        fig.add_hline(y=50, line_dash="dot",  line_color="#94a3b8", line_width=1, opacity=0.35)
        fig.update_layout(height=215, margin=dict(l=0, r=0, t=14, b=0),
            paper_bgcolor="#fff", plot_bgcolor="#fff", template="plotly_white",
            showlegend=False, font=dict(family="Inter", size=11),
            yaxis=dict(range=[0, 100], side="right", showgrid=True,
                       gridcolor="#f1f5f9", tickfont=dict(size=10), zeroline=False),
            xaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickfont=dict(size=10)))
        return fig
    except: return None

def chart_gauge(score, grade, color):
    try:
        import plotly.graph_objects as go
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=score,
            number={"font": {"size": 36, "family": "JetBrains Mono", "color": color}},
            gauge=dict(
                axis=dict(range=[0, 100], tickfont=dict(size=9, color="#94a3b8"), nticks=6),
                bar=dict(color=color, thickness=0.25), bgcolor="white", borderwidth=0,
                steps=[dict(range=[0,  30], color="#fef2f2"),
                       dict(range=[30, 45], color="#fff7ed"),
                       dict(range=[45, 60], color="#fffbeb"),
                       dict(range=[60, 75], color="#eff6ff"),
                       dict(range=[75,100], color="#f0fdf4")],
                threshold=dict(line=dict(color=color, width=3), thickness=0.75, value=score)),
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": grade, "font": {"size": 11, "family": "Inter", "color": "#64748b"}}))
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=28, b=0),
            paper_bgcolor="#fff", template="plotly_white", font=dict(family="Inter"))
        return fig
    except: return None

# ══════════════════════════════════════════════════════════
# AI STRATEGY GENERATOR
# ══════════════════════════════════════════════════════════
def ai_strategy(ticker, m, pio_s, iv, total, bd, grade, traps):
    price  = m.get("price") or m.get("ph") or 0
    rsi    = m.get("rsi") or 50
    pe     = m.get("pe") or 0
    roe    = m.get("roe") or 0
    de     = (m.get("de") or 0) / 100
    fcf    = m.get("fcf")
    mos    = iv.get("mos")
    up     = iv.get("up")
    avg_iv = iv.get("avg")
    h52    = m.get("h52") or price
    l52    = m.get("l52") or price
    vpa    = m.get("vpa") or []
    d200   = m.get("d200")

    # Determine overall stance
    if total >= 70 and pio_s >= 7:
        stance = "STRONG BUY"; s_col = "#16a34a"
    elif total >= 55 and pio_s >= 5:
        stance = "CAUTIOUS BUY"; s_col = "#2563eb"
    elif total >= 40:
        stance = "HOLD / WATCH"; s_col = "#d97706"
    else:
        stance = "AVOID"; s_col = "#dc2626"

    # Capital preservation zones
    above_200 = price > d200 if d200 else None
    pct_h = sdiv(price - h52, h52, 0) * 100

    # Suggested SL and Target
    sl  = round(price * 0.92, 2)
    tgt = round(price * 1.15, 2)
    if avg_iv and avg_iv > price:
        tgt = round(min(avg_iv, price * 1.25), 2)

    # Time horizon
    if pio_s >= 7 and total >= 65: horizon = "8–10 Years (SIP-friendly)"
    elif pio_s >= 5 and total >= 50: horizon = "3–5 Years"
    elif total >= 40: horizon = "6–12 Months (Swing)"
    else: horizon = "Not recommended"

    return {
        "stance":   stance,
        "s_col":    s_col,
        "sl":       sl,
        "target":   tgt,
        "horizon":  horizon,
        "above_200": above_200,
        "pct_from_h": pct_h,
        "mos":      mos,
        "up":       up,
        "avg_iv":   avg_iv,
        "vpa_count": len(vpa),
    }

# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        "<div style='padding:1rem 0.5rem 0.75rem;'>"
        "<div style='font-size:1.05rem;font-weight:800;color:#f1f5f9;letter-spacing:-0.02em;'>"
        "📈 Stock Analysis Pro</div>"
        "<div style='font-size:0.68rem;color:#64748b;margin-top:2px;'>Money Financial Services · v6.0</div>"
        "</div>", unsafe_allow_html=True)

    page = st.radio("", [
        "🔍 Discovery Hub",
        "📋 Pro Watchlist",
        "🛠️ Deep Dive Analysis",
        "🤖 AI Verdict & Strategy",
    ], index=["🔍 Discovery Hub","📋 Pro Watchlist",
              "🛠️ Deep Dive Analysis","🤖 AI Verdict & Strategy"].index(
                  st.session_state.page),
        label_visibility="collapsed", key="nav")

    if page != st.session_state.page:
        st.session_state.page = page; st.rerun()

    st.markdown("---")
    wl = st.session_state.watchlist
    st.markdown(
        f"<div style='font-size:0.68rem;color:#64748b;margin-bottom:5px;'>"
        f"📌 Watchlist — {len(wl)} stocks</div>", unsafe_allow_html=True)
    for t in wl[:8]:
        if st.button(t, key=f"sb_{t}", use_container_width=True):
            st.session_state.analyse_ticker = t
            st.session_state.page = "🛠️ Deep Dive Analysis"; st.rerun()
    if len(wl) > 8:
        st.caption(f"+ {len(wl)-8} more in watchlist")

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.64rem;color:#475569;line-height:1.7;'>"
        "NSE → NAME.NS<br>BSE → NAME.BO<br>US → AAPL, MSFT"
        "</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE 1 — DISCOVERY HUB
# ══════════════════════════════════════════════════════════
def page_discovery():
    st.markdown(
        "<div class='page-header'>"
        "<div class='ph-title'>🔍 Discovery Hub</div>"
        "<div class='ph-sub'>Search any NSE/BSE/US stock · Get instant snapshot · Add to Watchlist</div>"
        "</div>", unsafe_allow_html=True)

    ci, cb = st.columns([5, 1])
    with ci:
        t_in = st.text_input("", placeholder="Enter ticker — e.g. RELIANCE.NS · TCS.NS · HDFCBANK.NS · AAPL",
                             key="d_input", label_visibility="collapsed")
    with cb:
        go_btn = st.button("🔍 Search", use_container_width=True, type="primary", key="d_go")

    # Popular
    pop = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
           "SBIN.NS","BAJFINANCE.NS","WIPRO.NS","TITAN.NS","SUNPHARMA.NS",
           "MARUTI.NS","ONGC.NS","NTPC.NS","LT.NS","ADANIPORTS.NS"]
    st.caption("Quick search:")
    pc = st.columns(5)
    for i, ps in enumerate(pop):
        with pc[i % 5]:
            if st.button(ps.replace(".NS","").replace(".BO",""),
                         key=f"pop_{ps}", use_container_width=True):
                st.session_state.search_ticker = ps
                st.session_state.search_data   = None
                st.rerun()

    st.markdown("---")
    if go_btn and t_in.strip():
        st.session_state.search_ticker = t_in.strip().upper()
        st.session_state.search_data   = None

    q = st.session_state.search_ticker
    if not q: return

    # Fetch
    if st.session_state.search_data is None:
        with st.spinner(f"Fetching {q}…"):
            info = safe_info(q)
            hist = safe_hist(q, "6mo")
            st.session_state.search_data = {"info": info, "hist": hist}
    else:
        info = st.session_state.search_data["info"]
        hist = st.session_state.search_data["hist"]

    price = sf(_v(info, "regularMarketPrice", "currentPrice"))
    if not price:
        st.error(f"❌ **{q}** not found. Check ticker. NSE → .NS suffix  |  BSE → .BO")
        return

    prev  = sf(_v(info, "regularMarketPreviousClose"))
    chg   = price - prev if prev else 0
    chgp  = (chg / prev * 100) if prev and prev != 0 else 0
    cc    = "#16a34a" if chg >= 0 else "#dc2626"
    arr   = "▲" if chg >= 0 else "▼"
    name  = info.get("longName") or info.get("shortName") or q
    curr  = info.get("currency", "INR")
    lurl  = logo_url(info.get("website", ""))
    logo_html = (
        f'<img src="{lurl}" width="40" height="40" '
        f'style="border-radius:8px;object-fit:contain;border:1px solid #e2e8f0;'
        f'margin-right:12px;vertical-align:middle;" onerror="this.style.display=\'none\'"> '
    ) if lurl else ""

    # Header card
    st.markdown(
        f"<div class='card' style='display:flex;justify-content:space-between;"
        f"align-items:flex-start;flex-wrap:wrap;gap:0.75rem;'>"
        f"<div style='display:flex;align-items:center;'>{logo_html}"
        f"<div><div style='font-size:1.2rem;font-weight:800;color:#0f172a;'>{name}</div>"
        f"<div style='font-size:0.73rem;color:#64748b;margin-top:3px;'>"
        f"{q} · {info.get('exchange','—')} · {info.get('sector','—')} · {info.get('industry','—')}"
        f"</div></div></div>"
        f"<div style='text-align:right;'>"
        f"<div style='font-size:1.65rem;font-weight:800;color:#0f172a;font-family:JetBrains Mono,monospace;'>"
        f"{curr} {price:,.2f}</div>"
        f"<div style='font-size:0.86rem;font-weight:600;color:{cc};margin-top:3px;'>"
        f"{arr} {abs(chg):,.2f} ({chgp:+.2f}%)</div>"
        f"</div></div>", unsafe_allow_html=True)

    # Mini fundamental snapshot
    sec("Mini Fundamental Snapshot")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: st.metric("Market Cap",  fc(info.get("marketCap")))
    with c2: st.metric("P/E Ratio",   f"{sf(info.get('trailingPE')):.1f}"       if sf(info.get('trailingPE'))    else "—")
    with c3: st.metric("52W High",    f"₹{sf(info.get('fiftyTwoWeekHigh')):,.0f}" if sf(info.get('fiftyTwoWeekHigh')) else "—")
    with c4: st.metric("52W Low",     f"₹{sf(info.get('fiftyTwoWeekLow')):,.0f}"  if sf(info.get('fiftyTwoWeekLow'))  else "—")
    with c5: st.metric("Volume",      f"{info.get('regularMarketVolume',0):,.0f}"  if info.get('regularMarketVolume') else "—")
    with c6: st.metric("Avg Vol",     f"{info.get('averageVolume',0):,.0f}"         if info.get('averageVolume')        else "—")

    # Buttons
    already = q in st.session_state.watchlist
    ca, cb2, cc2 = st.columns([2, 2, 3])
    with ca:
        if already:
            st.success("✅ Already in watchlist")
        elif st.button("➕ Add to My Watchlist", type="primary",
                       use_container_width=True, key="add_wl"):
            db_add(q, name)
            st.session_state.watchlist = [r[0] for r in db_wl()]
            st.success(f"✅ **{q}** added to watchlist!")
            st.rerun()
    with cb2:
        if st.button("📊 Deep Dive Analysis", use_container_width=True, key="goto_dd"):
            st.session_state.analyse_ticker = q
            st.session_state.page = "🛠️ Deep Dive Analysis"; st.rerun()
    with cc2:
        if st.button("🤖 AI Verdict", use_container_width=True, key="goto_ai"):
            st.session_state.analyse_ticker = q
            st.session_state.page = "🤖 AI Verdict & Strategy"; st.rerun()

    # Chart
    if not hist.empty:
        st.markdown("---")
        sec("6-Month Price Chart")
        fig = chart_candle(hist)
        if fig: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    desc = info.get("longBusinessSummary", "")
    if desc:
        with st.expander("📖 About the Company"):
            st.markdown(
                f"<p style='font-size:0.83rem;line-height:1.8;color:#475569;'>"
                f"{desc[:1500]}{'…' if len(desc)>1500 else ''}</p>",
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# PAGE 2 — PRO WATCHLIST
# ══════════════════════════════════════════════════════════
def page_watchlist():
    st.markdown(
        "<div class='page-header'>"
        "<div class='ph-title'>📋 Pro Watchlist</div>"
        "<div class='ph-sub'>Real-time LTP · Change% · Volume · One-click Deep Dive</div>"
        "</div>", unsafe_allow_html=True)

    wl = st.session_state.watchlist
    if not wl:
        st.info("📭 Watchlist is empty. Go to 🔍 Discovery Hub to add stocks.")
        if st.button("🔍 Discovery Hub", type="primary"):
            st.session_state.page = "🔍 Discovery Hub"; st.rerun()
        return

    ca, cb = st.columns([5, 1])
    with cb:
        if st.button("🔄 Refresh", use_container_width=True):
            _cache().clear(); st.rerun()

    st.markdown("---")
    # Column headers
    hc = st.columns([0.4, 2.5, 1.4, 1.2, 1.3, 1.2, 1.2, 1.0])
    for col, h in zip(hc, ["", "Stock", "LTP (₹)", "Change%", "Volume", "Mkt Cap", "P/E", "Actions"]):
        col.markdown(
            f"<div class='wl-header'>{h}</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border:none;border-top:2px solid #e2e8f0;margin:2px 0 4px;'>",
                unsafe_allow_html=True)

    for ticker in wl:
        info   = safe_info(ticker)
        price  = sf(_v(info, "regularMarketPrice", "currentPrice"))
        prev   = sf(_v(info, "regularMarketPreviousClose"))
        chgp   = (price - prev) / prev * 100 if price and prev and prev != 0 else None
        name   = info.get("shortName") or info.get("longName") or ticker
        lurl   = logo_url(info.get("website", ""))
        tabbr  = ticker.replace(".NS","").replace(".BO","")[:2].upper()

        p_str = f"{price:,.2f}" if price else "—"
        if chgp is not None:
            cc  = "#16a34a" if chgp >= 0 else "#dc2626"
            cbg = "#f0fdf4" if chgp >= 0 else "#fef2f2"
            cs  = f"{'▲' if chgp>=0 else '▼'}{abs(chgp):.2f}%"
        else:
            cc = "#94a3b8"; cbg = "#f8fafc"; cs = "—"

        vol = info.get("regularMarketVolume")
        vol_str = f"{vol:,.0f}" if vol else "—"
        pe_v = sf(info.get("trailingPE"))

        rc = st.columns([0.4, 2.5, 1.4, 1.2, 1.3, 1.2, 1.2, 1.0])
        with rc[0]:
            if lurl:
                st.markdown(
                    f'<img src="{lurl}" width="24" height="24" '
                    f'style="border-radius:5px;object-fit:contain;border:1px solid #e2e8f0;'
                    f'margin-top:6px;" onerror="this.style.display=\'none\'">',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div style="width:24px;height:24px;border-radius:5px;background:#e2e8f0;'
                    f'display:flex;align-items:center;justify-content:center;font-size:0.55rem;'
                    f'font-weight:700;color:#64748b;margin-top:6px;">{tabbr}</div>',
                    unsafe_allow_html=True)
        with rc[1]:
            st.markdown(
                f"<div style='padding-top:3px;'>"
                f"<div style='font-size:0.82rem;font-weight:700;color:#0f172a;"
                f"font-family:JetBrains Mono,monospace;'>"
                f"{ticker.replace('.NS','').replace('.BO','')}</div>"
                f"<div style='font-size:0.66rem;color:#94a3b8;'>{name[:26]}</div></div>",
                unsafe_allow_html=True)
        with rc[2]:
            st.markdown(
                f"<div style='font-size:0.84rem;font-weight:600;color:#0f172a;"
                f"font-family:JetBrains Mono,monospace;padding-top:6px;'>{p_str}</div>",
                unsafe_allow_html=True)
        with rc[3]:
            st.markdown(
                f"<div style='padding-top:6px;'>"
                f"<span style='font-size:0.76rem;font-weight:700;color:{cc};"
                f"background:{cbg};padding:2px 7px;border-radius:4px;'>{cs}</span></div>",
                unsafe_allow_html=True)
        with rc[4]:
            st.markdown(
                f"<div style='font-size:0.76rem;color:#475569;padding-top:6px;'>{vol_str}</div>",
                unsafe_allow_html=True)
        with rc[5]:
            st.markdown(
                f"<div style='font-size:0.76rem;color:#475569;padding-top:6px;'>{fc(info.get('marketCap'))}</div>",
                unsafe_allow_html=True)
        with rc[6]:
            st.markdown(
                f"<div style='font-size:0.76rem;color:#475569;padding-top:6px;'>"
                f"{f'{pe_v:.1f}' if pe_v else '—'}</div>",
                unsafe_allow_html=True)
        with rc[7]:
            ba, bb = st.columns(2)
            with ba:
                if st.button("📊", key=f"v_{ticker}", help="Deep Dive"):
                    st.session_state.analyse_ticker = ticker
                    st.session_state.page = "🛠️ Deep Dive Analysis"; st.rerun()
            with bb:
                if st.button("🗑️", key=f"d_{ticker}", help=f"Remove {ticker}"):
                    db_del(ticker)
                    st.session_state.watchlist = [r[0] for r in db_wl()]; st.rerun()

        st.markdown("<div class='wl-row-border'></div>", unsafe_allow_html=True)

    st.caption(f"Yahoo Finance data · {len(wl)} stocks · Refreshes hourly")

# ══════════════════════════════════════════════════════════
# PAGE 3 — DEEP DIVE ANALYSIS
# ══════════════════════════════════════════════════════════
def page_deep_dive():
    st.markdown(
        "<div class='page-header'>"
        "<div class='ph-title'>🛠️ Deep Dive Analysis</div>"
        "<div class='ph-sub'>Technicals · Piotroski F-Score · Intrinsic Value · Trap Detector · Holders</div>"
        "</div>", unsafe_allow_html=True)

    wl = st.session_state.watchlist
    at = st.session_state.analyse_ticker
    options = ([at] + [x for x in wl if x != at]) if at else wl
    if not options:
        st.info("📭 No stocks. Go to 🔍 Discovery Hub first.")
        if st.button("🔍 Discovery Hub", type="primary"):
            st.session_state.page = "🔍 Discovery Hub"; st.rerun()
        return

    ca, cb, _ = st.columns([3, 1, 3])
    with ca:
        sel = st.selectbox("Select Stock", options,
            index=0, key="dd_sel", label_visibility="visible")
    with cb:
        period = st.selectbox("Period", ["1mo","3mo","6mo","1y","2y"],
            index=3, key="dd_per", label_visibility="visible")
    if sel != st.session_state.analyse_ticker:
        st.session_state.analyse_ticker = sel; st.rerun()

    ticker = sel
    with st.spinner(f"Loading full data for {ticker}…"):
        data = safe_full(ticker)
        if not data["hist"].empty and period != "1y":
            try: data["hist"] = yf.Ticker(ticker).history(period=period)
            except: pass

    if not data["ok"]:
        st.error(f"❌ Failed to load {ticker}: {data.get('error','')}"); return

    m    = build_m(data)
    hist = data["hist"]
    price = m.get("price") or m.get("ph")
    if not price:
        st.warning(f"Price data unavailable for {ticker}."); return

    pio_s, pio_c  = piotroski(data)
    iv             = calc_iv(m)
    total, bd, grade, color = calc_ai(m, pio_s, iv)
    traps          = trap_detect(m, pio_s, total, iv)

    prev  = m.get("prev"); chg = price - prev if prev else 0
    chgp  = (chg/prev*100) if prev and prev!=0 else 0
    cc    = "#16a34a" if chg >= 0 else "#dc2626"
    arr   = "▲" if chg >= 0 else "▼"
    curr  = m.get("curr","INR"); name = m.get("name") or ticker
    lurl  = logo_url(m.get("web",""))
    logo_html = (
        f'<img src="{lurl}" width="36" height="36" '
        f'style="border-radius:7px;object-fit:contain;border:1px solid #e2e8f0;'
        f'margin-right:12px;vertical-align:middle;" onerror="this.style.display=\'none\'">'
    ) if lurl else ""

    # Stock header
    h1, h2 = st.columns([3, 2])
    with h1:
        st.markdown(
            f"{logo_html}<span style='font-size:1.15rem;font-weight:800;color:#0f172a;"
            f"vertical-align:middle;'>{name}</span>", unsafe_allow_html=True)
        st.caption(f"{ticker} · {m.get('exch','—')} · {m.get('sector','—')} · {m.get('ind','—')}")
    with h2:
        st.markdown(
            f"<div style='text-align:right;'>"
            f"<div style='font-size:1.6rem;font-weight:800;color:#0f172a;"
            f"font-family:JetBrains Mono,monospace;line-height:1;'>{curr} {price:,.2f}</div>"
            f"<div style='font-size:0.84rem;font-weight:600;color:{cc};margin-top:3px;'>"
            f"{arr} {abs(chg):,.2f} ({chgp:+.2f}%)</div>"
            f"<div style='font-size:0.67rem;color:#94a3b8;margin-top:2px;'>"
            f"Cap: {fc(m.get('mktcap'))} · Beta: {fn(m.get('beta'))} · Target: {fn(m.get('target'))}"
            f"</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # RSI Trap Alert (top-level)
    rsi_v = m.get("rsi")
    if rsi_v is not None:
        if rsi_v > 70:
            st.markdown(
                f"<div class='al al-danger'><b>🚨 OVERBOUGHT TRAP — RSI: {rsi_v:.1f}</b><br>"
                f"RSI above 70 = overbought. High reversal risk. "
                f"<b>Avoid chasing. Wait for RSI to cool below 60.</b></div>",
                unsafe_allow_html=True)
        elif rsi_v < 30:
            st.markdown(
                f"<div class='al al-ok'><b>🔎 OVERSOLD OPPORTUNITY — RSI: {rsi_v:.1f}</b><br>"
                f"RSI below 30 = oversold. Potential bounce zone. "
                f"<b>Wait for RSI > 35 confirmation before entering.</b></div>",
                unsafe_allow_html=True)

    # Quick KPI bar
    k1,k2,k3,k4,k5,k6 = st.columns(6)
    with k1: st.metric("P/E",       f"{sf(m.get('pe')):.1f}"   if sf(m.get('pe'))  else "—")
    with k2: st.metric("ROE",       fp(m.get("roe")))
    with k3: st.metric("D/E",       f"{sf(m.get('de'))/100:.2f}x" if sf(m.get('de')) else "—")
    with k4: st.metric("RSI (14)",  f"{rsi_v:.1f}" if rsi_v else "—")
    with k5: st.metric("Piotroski", f"{pio_s}/9 {'⭐' if pio_s>=7 else '⚠️' if pio_s>=5 else '🔴'}")
    with k6: st.metric("AI Score",  f"{total}/100")

    st.markdown("---")

    # ── TABS ──
    T1, T2, T3, T4 = st.tabs([
        "📈 Technicals",
        "📊 Fundamental Health",
        "🪤 Trap Detector",
        "🏦 Holders & Notes",
    ])

    # ── TAB 1: TECHNICALS ──
    with T1:
        sec("Candlestick Chart — EMA 20/50 · 200 DMA · Volume · Institutional Buying")
        vpa_d = m.get("vpa") or []
        fig_c = chart_candle(hist, m.get("d50"), m.get("d200"), vpa_d)
        if fig_c:
            st.plotly_chart(fig_c, use_container_width=True, config={"displayModeBar": False})
        else:
            st.warning("Chart unavailable.")

        if vpa_d:
            st.markdown(
                f"<div class='al al-purple'>🏦 <b>Institutional Buying Detected</b> — "
                f"{len(vpa_d)} signal(s). Price↑ + Volume > 2× 20-day average. "
                f"Last: <b>{str(vpa_d[-1])[:10]}</b></div>",
                unsafe_allow_html=True)
        else:
            st.info("ℹ️ No institutional buying signals in last year.")

        sec("RSI (14) — Overbought / Oversold Zone")
        fig_r = chart_rsi(hist)
        if fig_r:
            st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar": False})

        sec("Key Technical Levels & Volume")
        ph = m.get("ph") or price
        c1,c2,c3,c4 = st.columns(4)
        with c1: mc("Current Price", f"₹{ph:,.2f}", "Latest close")
        with c2:
            d50 = m.get("d50")
            if d50: p50=sdiv(ph-d50,d50,0)*100; mc("EMA 50",f"₹{d50:,.2f}",f"{p50:+.1f}%","#16a34a" if ph>d50 else "#dc2626")
            else: mc("EMA 50","N/A","—")
        with c3:
            d200 = m.get("d200")
            if d200: p200=sdiv(ph-d200,d200,0)*100; mc("200 DMA",f"₹{d200:,.2f}",f"{p200:+.1f}%","#16a34a" if ph>d200 else "#dc2626")
            else: mc("200 DMA","N/A","—")
        with c4:
            mh2 = m.get("mh")
            mc("MACD Histogram", f"{mh2:.2f}" if mh2 else "N/A",
               "Bullish 🟢" if mh2 and mh2>0 else "Bearish 🔴",
               "#16a34a" if mh2 and mh2>0 else "#dc2626")

        h52 = m.get("h52"); l52 = m.get("l52")
        if h52 and l52 and h52 != l52:
            sec("52-Week Range")
            pos = sdiv(ph-l52, h52-l52, 0)*100; pfh = sdiv(ph-h52, h52, 0)*100
            ca2, cb2 = st.columns([3,1])
            with ca2:
                st.markdown(
                    f"<div class='mc'>"
                    f"<div style='display:flex;justify-content:space-between;margin-bottom:4px;'>"
                    f"<span style='font-size:0.68rem;color:#94a3b8;'>52W Low ₹{l52:,.0f}</span>"
                    f"<span style='font-size:0.76rem;font-weight:700;'>📍 ₹{ph:,.1f} ({pos:.0f}th%ile)</span>"
                    f"<span style='font-size:0.68rem;color:#94a3b8;'>52W High ₹{h52:,.0f}</span></div>"
                    f"{pb_bar(pos,'linear-gradient(90deg,#ef4444 0%,#f59e0b 50%,#16a34a 100%)')}"
                    f"</div>", unsafe_allow_html=True)
            with cb2: mc("From 52W High",f"{pfh:+.1f}%","","#16a34a" if pfh>-5 else "#dc2626")

        sec("Volume Analysis")
        cv = m.get("vol"); v20 = m.get("v20")
        c1,c2,c3,c4 = st.columns(4)
        with c1: mc("Today Volume", f"{cv:,.0f}" if cv else "N/A","Shares traded")
        with c2: mc("20D Avg Volume",f"{v20:,.0f}" if v20 else "N/A","Rolling avg")
        with c3:
            if cv and v20 and v20 > 0:
                vr = cv/v20; vc2="#16a34a" if vr>1.5 else("#dc2626" if vr<0.5 else "#d97706")
                vl = "📈 Spike" if vr>1.5 else("📉 Dry" if vr<0.5 else "➡️ Normal")
                mc("Vol vs 20D Avg", f"{vr:.2f}×", vl, vc2)
            else: mc("Vol vs 20D Avg","N/A","—")
        with c4:
            vp = m.get("vp")
            mc("Price Volatility (20D)", f"{vp:.1f}%" if vp else "N/A",
               "< 5% = stable", "#16a34a" if vp and vp<5 else "#d97706")

    # ── TAB 2: FUNDAMENTAL HEALTH ──
    with T2:
        sec("Valuation Ratios")
        pe_v = m.get("pe")
        pe_c = ("#16a34a" if pe_v and pe_v<25 else "#d97706" if pe_v and pe_v<40 else "#dc2626") if pe_v else "#94a3b8"
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: mc("Trailing P/E",  fn(m.get("pe"),1),  "< 25 = ideal", pe_c)
        with c2: mc("Forward P/E",   fn(m.get("fpe"),1), "Estimated")
        with c3: mc("Price/Book",    fn(m.get("pb"),2),  "< 3 = fair")
        with c4: mc("Price/Sales",   fn(m.get("ps"),2),  "Revenue multiple")
        with c5: mc("PEG Ratio",     fn(m.get("peg"),2), "< 1 = undervalued")

        sec("Profitability")
        roe_v = m.get("roe"); pm_v = m.get("pm")
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: mc("ROE", fp(roe_v), "> 15% ideal","#16a34a" if roe_v and roe_v>0.15 else "#dc2626" if roe_v else "#94a3b8")
        with c2: mc("ROA", fp(m.get("roa")), "Asset efficiency")
        with c3: mc("Net Margin", fp(pm_v), "> 10% ideal","#16a34a" if pm_v and pm_v>0.10 else "#dc2626" if pm_v else "#94a3b8")
        with c4: mc("Gross Margin", fp(m.get("gm")), "Revenue quality")
        with c5: mc("Oper. Margin", fp(m.get("om")), "Cost efficiency")

        sec("Balance Sheet & Cash Flow")
        de_v=m.get("de"); cr_v=m.get("cr"); fcf_v=m.get("fcf"); de_r=de_v/100 if de_v else None
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: mc("Debt/Equity",f"{de_r:.2f}x" if de_r else "N/A","< 1x ideal","#16a34a" if de_r and de_r<1 else "#dc2626" if de_r else "#94a3b8")
        with c2: mc("Current Ratio",fn(cr_v,2),"> 1.5 ideal","#16a34a" if cr_v and cr_v>1.5 else "#dc2626" if cr_v else "#94a3b8")
        with c3: mc("Quick Ratio",fn(m.get("qr"),2),"Acid test")
        with c4: mc("Free Cash Flow",fc(fcf_v),"Positive = healthy","#16a34a" if fcf_v and fcf_v>0 else "#dc2626" if fcf_v else "#94a3b8")
        with c5: mc("Oper. Cash Flow",fc(m.get("ocf")),"Generated cash")

        sec("Growth & EPS")
        rg_v=m.get("rg"); eg_v=m.get("eg")
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: mc("Revenue Growth",fp(rg_v),"YoY","#16a34a" if rg_v and rg_v>0 else "#dc2626" if rg_v else "#94a3b8")
        with c2: mc("Earnings Growth",fp(eg_v),"YoY","#16a34a" if eg_v and eg_v>0 else "#dc2626" if eg_v else "#94a3b8")
        with c3: mc("Trailing EPS",fn(m.get("eps"),2),"Per share")
        with c4: mc("Forward EPS",fn(m.get("feps"),2),"Estimated")
        with c5: mc("Dividend Yield",fp(m.get("dy"),2),"Annual")

        st.markdown("---")
        sec("Piotroski F-Score — 9-Point Financial Health Check")
        pc = "#16a34a" if pio_s>=7 else "#d97706" if pio_s>=5 else "#dc2626"
        pt = "Financially Strong 💪" if pio_s>=7 else ("Moderate — Monitor" if pio_s>=5 else "Weak — Distress Risk ⚠️")
        ca2, cb2 = st.columns([1,2])
        with ca2:
            st.markdown(
                f"<div class='card' style='text-align:center;padding:1.75rem 1rem;'>"
                f"<div style='font-size:0.6rem;font-weight:700;text-transform:uppercase;"
                f"letter-spacing:0.08em;color:#94a3b8;margin-bottom:4px;'>PIOTROSKI F-SCORE</div>"
                f"<div style='font-size:5rem;font-weight:800;color:{pc};line-height:1;"
                f"font-family:JetBrains Mono,monospace;'>{pio_s}</div>"
                f"<div style='font-size:0.7rem;color:#94a3b8;margin:3px 0 8px;'>out of 9</div>"
                f"{pb_bar(pio_s/9*100, pc)}"
                f"<div style='margin-top:10px;font-size:0.76rem;font-weight:700;color:{pc};'>{pt}</div>"
                f"</div>", unsafe_allow_html=True)
        with cb2:
            gn={"Profitability":"Profitability","Leverage":"Leverage","Efficiency":"Efficiency"}
            grps={}
            for c in pio_c: grps.setdefault(c["g"],[]).append(c)
            for gk, items in grps.items():
                gs = sum(1 for x in items if x["p"])
                st.markdown(
                    f"<div style='font-size:0.62rem;font-weight:700;text-transform:uppercase;"
                    f"letter-spacing:0.05em;color:#94a3b8;margin:10px 0 4px;'>{gk} ({gs}/{len(items)})</div>",
                    unsafe_allow_html=True)
                for item in items:
                    ic = "✅" if item["p"] else "❌"
                    bg = "#f0fdf4" if item["p"] else "#fef2f2"
                    tc = "#15803d" if item["p"] else "#b91c1c"
                    st.markdown(
                        f"<div style='background:{bg};border-radius:7px;padding:5px 10px;"
                        f"margin-bottom:3px;display:flex;gap:8px;align-items:flex-start;'>"
                        f"<span style='font-size:0.84rem;'>{ic}</span>"
                        f"<div><div style='font-size:0.76rem;font-weight:600;color:{tc};'>{item['n']}</div>"
                        f"<div style='font-size:0.65rem;color:#64748b;'>{item['note']}</div></div></div>",
                        unsafe_allow_html=True)
        st.info("ℹ️ Piotroski F-Score: 7–9 = Strong · 4–6 = Moderate · 0–3 = Weak")

        st.markdown("---")
        sec("Intrinsic Value — Graham Number & DCF")
        curr_p = m.get("price") or m.get("ph")
        c1,c2,c3,c4 = st.columns(4)
        gv=iv.get("graham"); dv=iv.get("dcf"); avg_iv=iv.get("avg"); up_v=iv.get("up"); mos_v=iv.get("mos")
        with c1:
            if gv and curr_p:
                d=sdiv(curr_p-gv,gv,0)*100
                mc("Graham Number",f"₹{gv:,.1f}",f"{'Under' if curr_p<gv else 'Over'}valued {abs(d):.1f}%","#16a34a" if curr_p<gv else "#dc2626")
            else: mc("Graham Number","N/A","EPS or BVPS unavailable")
        with c2:
            if dv and curr_p:
                d2=sdiv(curr_p-dv,dv,0)*100
                mc("Graham DCF",f"₹{dv:,.1f}",f"{'Under' if curr_p<dv else 'Over'}valued {abs(d2):.1f}%","#16a34a" if curr_p<dv else "#dc2626")
            else: mc("Graham DCF","N/A","EPS or Growth unavailable")
        with c3:
            if avg_iv and curr_p:
                mc("Blended IV",f"₹{avg_iv:,.1f}",f"{'↑' if up_v and up_v>0 else '↓'} {abs(up_v):.1f}% | MOS: {mos_v:.1f}%","#16a34a" if up_v and up_v>0 else "#dc2626")
            else: mc("Blended IV","N/A","Insufficient data")
        with c4:
            at=iv.get("at"); au=iv.get("au")
            if at and au is not None:
                mc("Analyst Target",f"₹{at:,.1f}",f"Upside: {au:+.1f}%","#16a34a" if au>0 else "#dc2626")
            else: mc("Analyst Target","N/A","Not available")

        if avg_iv and curr_p:
            if mos_v>20:   st.success(f"✅ **MOS: {mos_v:.1f}%** — Significantly undervalued. Potential upside: {up_v:.1f}%")
            elif mos_v>0:  st.success(f"✅ Marginally undervalued. MOS: {mos_v:.1f}%")
            elif mos_v>-20:st.warning(f"⚠️ Near fair value. Overvalued by {abs(mos_v):.1f}%")
            else:          st.error(  f"🚨 Overvalued by {abs(mos_v):.1f}%. Downside risk: {abs(up_v):.1f}%")

        desc = _v(data["info"],"longBusinessSummary",default="")
        if desc:
            with st.expander("📖 About the Company"):
                st.markdown(f"<p style='font-size:0.83rem;line-height:1.8;color:#475569;'>{desc[:1500]}{'…' if len(desc)>1500 else ''}</p>",unsafe_allow_html=True)

    # ── TAB 3: TRAP DETECTOR ──
    with T3:
        st.markdown(
            "<div class='al al-info'>🧠 <b>Trap Detector</b> automatically analyzes this stock "
            "across 6 trap patterns using fundamental, technical, and valuation data.</div>",
            unsafe_allow_html=True)

        for trap in traps:
            st.markdown(
                f"<div class='trap-card {trap['cls']}'>"
                f"<div style='font-size:1rem;font-weight:800;color:#0f172a;margin-bottom:6px;'>"
                f"{trap['title']}</div>"
                f"<div style='font-size:0.83rem;color:#374151;line-height:1.65;'>"
                f"{trap['desc']}</div></div>",
                unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("<div class='sec'>Trap Reference Table</div>", unsafe_allow_html=True)
        trap_df = pd.DataFrame({
            "Pattern":    ["Value Trap","Debt Trap","Overbought+Overvalued","Quality Premium","Accumulation Zone","Oversold Value"],
            "Trigger":    ["Low Score + Far from 52W High + Weak Piotroski",
                           "D/E > 2x + Negative FCF",
                           "RSI > 72 + Overvalued > 25%",
                           "AI ≥ 70 + Piotroski ≥ 7 + P/B > 5",
                           "Volatility < 5% + Undervalued > 20%",
                           "RSI < 30 + AI ≥ 55 + Undervalued > 10%"],
            "Action":     ["AVOID","AVOID","DO NOT CHASE","BUY ON DIPS","ACCUMULATE","WAIT FOR CONFIRM"],
            "Status":     [("🔴 ACTIVE" if any(t["type"]=="VALUE_TRAP" for t in traps) else "—"),
                           ("🔴 ACTIVE" if any(t["type"]=="DEBT_TRAP"  for t in traps) else "—"),
                           ("🔴 ACTIVE" if any(t["type"]=="OVERBOUGHT_OVERVALUED" for t in traps) else "—"),
                           ("🟢 ACTIVE" if any(t["type"]=="QUALITY_PREMIUM" for t in traps) else "—"),
                           ("🟡 ACTIVE" if any(t["type"]=="ACCUMULATION" for t in traps) else "—"),
                           ("🟢 ACTIVE" if any(t["type"]=="OVERSOLD_VALUE" for t in traps) else "—")],
        })
        st.dataframe(trap_df, use_container_width=True, hide_index=True)

    # ── TAB 4: HOLDERS & NOTES ──
    with T4:
        sec("Major Holders")
        mh_df = data.get("mh", pd.DataFrame())
        if mh_df is not None and not mh_df.empty:
            try: st.dataframe(mh_df, use_container_width=True, hide_index=True)
            except: st.warning("Could not display major holders.")
        else:
            st.info("Major holders data not available.")

        sec("Institutional Holders (Top 10)")
        ih_df = data.get("ih", pd.DataFrame())
        if ih_df is not None and not ih_df.empty:
            try:
                d = ih_df.head(10).copy()
                if "Value" in d.columns:
                    d["Value"] = d["Value"].apply(
                        lambda x: f"₹{x/1e7:.1f}Cr" if isinstance(x,(int,float)) and not math.isnan(float(x)) else "N/A")
                if "% Out" in d.columns:
                    d["% Out"] = d["% Out"].apply(
                        lambda x: f"{float(x)*100:.2f}%" if isinstance(x,(int,float)) else str(x))
                st.dataframe(d, use_container_width=True, hide_index=True)
                st.info("🟢 Rising institutional holding over quarters = strong conviction signal.")
            except: st.warning("Could not parse institutional holders.")
        else:
            st.info("Institutional holders data not available.")

        st.markdown("---")
        sec("📝 My Research Notes")
        existing, last_upd = db_note_load(ticker)
        if st.button("📋 Load Research Template", key=f"tmpl_{ticker}"):
            existing = (
                f"📌 {ticker}  |  📅 {datetime.date.today()}\n\n"
                f"🎯 INVESTMENT THESIS:\n\n"
                f"📊 KEY METRICS:\n"
                f"- P/E: {fn(m.get('pe'),1)}\n"
                f"- ROE: {fp(m.get('roe'))}\n"
                f"- D/E: {fn(m.get('de') and m.get('de')/100,2)}x\n"
                f"- FCF: {fc(m.get('fcf'))}\n"
                f"- Piotroski: {pio_s}/9\n"
                f"- AI Score: {total}/100\n"
                f"- Intrinsic Value: ₹{fn(iv.get('avg'),0) if iv.get('avg') else 'N/A'}\n\n"
                f"⚠️ KEY RISKS:\n\n"
                f"🎯 TRADE PLAN:\n"
                f"- Entry Price: ₹\n"
                f"- Stop Loss: ₹\n"
                f"- Target: ₹\n"
                f"- Time Horizon:\n\n"
                f"✅ FINAL DECISION (Buy / Hold / Avoid):")
        note = st.text_area("", value=existing, height=280,
                            key=f"note_{ticker}", label_visibility="collapsed",
                            placeholder="Write your research, thesis, trade plan…")
        nc1, nc2 = st.columns([3,1])
        with nc1:
            if st.button("💾 Save Note", key=f"save_{ticker}",
                         use_container_width=True, type="primary"):
                db_note_save(ticker, note); st.success("✅ Note saved!")
        with nc2:
            if last_upd: st.caption(f"Saved:\n{last_upd}")

# ══════════════════════════════════════════════════════════
# PAGE 4 — AI VERDICT & STRATEGY
# ══════════════════════════════════════════════════════════
def page_ai_verdict():
    st.markdown(
        "<div class='page-header'>"
        "<div class='ph-title'>🤖 AI Verdict & Strategy</div>"
        "<div class='ph-sub'>Logic-based AI summary · Insurance Advisor Strategy · Capital Preservation · 8–10 Year Vision</div>"
        "</div>", unsafe_allow_html=True)

    wl = st.session_state.watchlist
    at = st.session_state.analyse_ticker
    options = ([at] + [x for x in wl if x != at]) if at else wl
    if not options:
        st.info("📭 No stocks. Add stocks in 🔍 Discovery Hub first.")
        if st.button("🔍 Discovery Hub", type="primary"):
            st.session_state.page = "🔍 Discovery Hub"; st.rerun()
        return

    ca, _, _ = st.columns([3,1,3])
    with ca:
        sel = st.selectbox("Select Stock", options, index=0, key="ai_sel")
    if sel != st.session_state.analyse_ticker:
        st.session_state.analyse_ticker = sel; st.rerun()

    ticker = sel
    with st.spinner(f"Generating AI analysis for {ticker}…"):
        data = safe_full(ticker)

    if not data["ok"]:
        st.error(f"❌ Data unavailable: {data.get('error','')}"); return

    m    = build_m(data)
    price = m.get("price") or m.get("ph")
    if not price:
        st.warning("Price data unavailable."); return

    pio_s, pio_c  = piotroski(data)
    iv             = calc_iv(m)
    total, bd, grade, color = calc_ai(m, pio_s, iv)
    traps          = trap_detect(m, pio_s, total, iv)
    strat          = ai_strategy(ticker, m, pio_s, iv, total, bd, grade, traps)

    name  = m.get("name") or ticker
    curr  = m.get("curr","INR")
    rsi_v = m.get("rsi")
    de_r  = (m.get("de") or 0) / 100
    mos   = iv.get("mos")
    up    = iv.get("up")
    avg_iv= iv.get("avg")

    # ── AI VERDICT CARD ─────────────────────────────────────
    stance_bg = {
        "STRONG BUY":   "linear-gradient(135deg,#f0fdf4,#dcfce7)",
        "CAUTIOUS BUY": "linear-gradient(135deg,#eff6ff,#dbeafe)",
        "HOLD / WATCH": "linear-gradient(135deg,#fffbeb,#fef3c7)",
        "AVOID":        "linear-gradient(135deg,#fef2f2,#fee2e2)",
    }.get(strat["stance"],"#fafafa")

    st.markdown(
        f"<div style='background:{stance_bg};border:2px solid {strat['s_col']};"
        f"border-radius:14px;padding:1.5rem 1.75rem;margin-bottom:1rem;'>"
        f"<div style='font-size:0.68rem;font-weight:700;text-transform:uppercase;"
        f"letter-spacing:0.08em;color:{strat['s_col']};margin-bottom:4px;'>AI VERDICT</div>"
        f"<div style='font-size:1.6rem;font-weight:800;color:{strat['s_col']};margin-bottom:6px;'>"
        f"{strat['stance']} — {name}</div>"
        f"<div style='font-size:0.85rem;color:#374151;line-height:1.7;'>"
        f"<b>{ticker}</b> scores <b>{total}/100</b> (AI Score) and <b>{pio_s}/9</b> (Piotroski F-Score). "
        f"Grade: <b>{grade}</b>. "
        f"{'Stock is trading ABOVE 200 DMA — uptrend confirmed.' if strat['above_200'] else 'Stock is trading BELOW 200 DMA — caution advised.'} "
        f"{'Intrinsic Value suggests ' + f'<b>{abs(mos):.0f}%</b> ' + ('undervaluation — margin of safety exists.' if mos and mos>0 else 'overvaluation — limited margin of safety.') if mos else ''}"
        f"</div></div>",
        unsafe_allow_html=True)

    # AI Score Gauge + Pillar breakdown
    ca2, cb2 = st.columns([1,2])
    with ca2:
        fig_g = chart_gauge(total, grade, color)
        if fig_g: st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar":False})
    with cb2:
        sec("Score Breakdown")
        pc_map = {"Valuation":"#3b82f6","Profitability":"#16a34a",
                  "Fin. Health":"#8b5cf6","Technical":"#f59e0b","Growth":"#06b6d4"}
        for pillar, pts in bd.items():
            pc2 = pc_map.get(pillar,"#64748b")
            bc  = "s-green" if pts>=15 else("s-yellow" if pts>=10 else "s-red")
            st.markdown(
                f"<div style='background:#fff;border:1px solid #e2e8f0;border-radius:8px;"
                f"padding:0.55rem 0.9rem;margin-bottom:0.3rem;'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;'>"
                f"<div style='font-size:0.8rem;font-weight:600;'>{pillar}</div>"
                f"<div>{badge(f'{pts}/20',bc)}</div></div>"
                f"{pb_bar(pts/20*100,pc2)}</div>",
                unsafe_allow_html=True)

    st.markdown("---")

    # ── STRATEGY SECTION ────────────────────────────────────
    sec("📋 Investment Strategy — Insurance Advisor Framework (8–10 Year Vision)")

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        mc("AI Stance",      strat["stance"],    "Overall verdict", strat["s_col"])
    with s2:
        mc("Suggested SL",   f"₹{strat['sl']:,.2f}", "92% of current price", "#dc2626")
    with s3:
        mc("Target Price",   f"₹{strat['target']:,.2f}",
           f"Intrinsic or +15%" if not avg_iv else f"Based on IV ₹{avg_iv:,.0f}", "#16a34a")
    with s4:
        mc("Time Horizon",   strat["horizon"],    "Recommended holding")

    st.markdown("---")

    # ── INSURANCE ADVISOR STRATEGY ──────────────────────────
    # Capital Preservation framework — 8-10 year experience logic
    sec("🛡️ Capital Preservation Analysis — 8-10 Year Market Experience Logic")

    # Risk classification
    risk_score = 0
    if de_r > 1.5:    risk_score += 2
    elif de_r > 0.8:  risk_score += 1
    if m.get("fcf") and m["fcf"] < 0: risk_score += 2
    if pio_s < 4:     risk_score += 2
    elif pio_s < 6:   risk_score += 1
    if rsi_v and rsi_v > 72: risk_score += 1
    if total < 40:    risk_score += 2

    if risk_score <= 2:   risk_label, risk_col = "LOW RISK ✅",    "#16a34a"
    elif risk_score <= 4: risk_label, risk_col = "MODERATE RISK ⚠️","#d97706"
    elif risk_score <= 6: risk_label, risk_col = "HIGH RISK 🔴",    "#ea580c"
    else:                 risk_label, risk_col = "VERY HIGH RISK 🚨","#dc2626"

    # Position sizing
    if risk_score <= 2:   pos_pct = "5–10% of portfolio"
    elif risk_score <= 4: pos_pct = "3–5% of portfolio"
    elif risk_score <= 6: pos_pct = "1–3% of portfolio (Speculative)"
    else:                 pos_pct = "0% — Do not invest"

    # SIP suitability
    sip_ok = total >= 60 and pio_s >= 6 and de_r < 1
    sip_label = "✅ SIP-friendly (Consistent compounder)" if sip_ok else "⚠️ Not ideal for SIP — Wait for better entry"

    p1, p2, p3 = st.columns(3)
    with p1: mc("Risk Classification", risk_label, f"Risk Score: {risk_score}/10", risk_col)
    with p2: mc("Suggested Position",  pos_pct, "Capital allocation guideline")
    with p3: mc("SIP Suitability",     "YES ✅" if sip_ok else "NO ❌", sip_label, "#16a34a" if sip_ok else "#dc2626")

    st.markdown("---")

    # ── Detailed AI Narrative ──
    sec("🧠 AI Narrative — Complete Investment Summary")

    def gen_narrative():
        lines = []
        lines.append(f"**{name} ({ticker})** — AI Score: **{total}/100** | Piotroski: **{pio_s}/9** | Grade: **{grade}**")
        lines.append("")
        lines.append("---")

        # Fundamental summary
        roe_v = m.get("roe"); pm_v = m.get("pm"); fcf_v = m.get("fcf")
        lines.append("**📊 Fundamental Summary:**")
        if roe_v:
            lines.append(f"- **ROE: {roe_v*100:.1f}%** — {'Strong' if roe_v>0.20 else 'Adequate' if roe_v>0.12 else 'Weak'} return on shareholder equity.")
        if pm_v:
            lines.append(f"- **Net Margin: {pm_v*100:.1f}%** — {'Excellent' if pm_v>0.20 else 'Good' if pm_v>0.10 else 'Thin'} profitability.")
        if de_r:
            lines.append(f"- **Debt/Equity: {de_r:.2f}x** — {'Conservative' if de_r<0.3 else 'Manageable' if de_r<1 else 'High leverage — risk in rising rate environment'}.")
        if fcf_v:
            lines.append(f"- **Free Cash Flow: {fc(fcf_v)}** — {'Company generates real cash ✅' if fcf_v>0 else 'Negative FCF ⚠️ — burning cash'}.")

        lines.append("")
        lines.append("**📈 Technical Summary:**")
        if rsi_v:
            lines.append(f"- **RSI: {rsi_v:.1f}** — {'🚨 Overbought — pullback risk' if rsi_v>70 else '🔎 Oversold — potential bounce' if rsi_v<30 else '✅ Neutral zone — no extreme'}")
        d200 = m.get("d200")
        if d200:
            p200 = sdiv(price-d200,d200,0)*100
            lines.append(f"- **200 DMA:** {'✅ Trading above — uptrend' if price>d200 else '⚠️ Trading below — downtrend'} ({p200:+.1f}% from 200 DMA)")
        vpa_d = m.get("vpa") or []
        if vpa_d:
            lines.append(f"- **Institutional Buying:** {len(vpa_d)} VPA signal(s) detected. Smart money activity noted.")

        lines.append("")
        lines.append("**💎 Valuation Summary:**")
        if avg_iv and price:
            lines.append(f"- **Intrinsic Value (Blended):** ₹{avg_iv:,.0f} vs CMP ₹{price:,.0f}")
            if mos:
                lines.append(f"- **Margin of Safety:** {mos:+.1f}% — {'Undervalued ✅' if mos>0 else 'Overvalued ⚠️'}")

        lines.append("")
        lines.append("**🛡️ Insurance Advisor Recommendation (Capital Preservation Focus):**")
        if strat["stance"] == "STRONG BUY":
            lines.append(f"- Strong conviction buy for **long-term wealth creation (8–10 years)**.")
            lines.append(f"- Suitable for **SIP** — accumulate on every dip below ₹{strat['sl']:,.0f}.")
            lines.append(f"- First target: ₹{strat['target']:,.2f}. Hold for multi-bagger potential.")
        elif strat["stance"] == "CAUTIOUS BUY":
            lines.append(f"- **Cautious buy** — enter in tranches. Don't deploy full capital at once.")
            lines.append(f"- Strict stop-loss at ₹{strat['sl']:,.0f} (92% of CMP).")
            lines.append(f"- Suitable for **3–5 year horizon**. Monitor quarterly results.")
        elif strat["stance"] == "HOLD / WATCH":
            lines.append(f"- **Do not add fresh positions** at current levels.")
            lines.append(f"- If already holding — hold with stop-loss at ₹{strat['sl']:,.0f}.")
            lines.append(f"- Wait for fundamental improvement or price correction before adding.")
        else:
            lines.append(f"- **AVOID** — Multiple red flags detected. Capital at high risk.")
            lines.append(f"- If already invested — consider exiting on any bounce to reduce loss.")
            lines.append(f"- Better opportunities available elsewhere in the market.")

        lines.append("")
        lines.append("---")
        lines.append(f"*⚠️ This is a logic-based quantitative analysis, NOT SEBI registered investment advice. "
                     f"Always consult your financial advisor before investing. Past performance ≠ future returns.*")

        return "\n".join(lines)

    st.markdown(gen_narrative())

    st.markdown("---")

    # ── Trap Summary ──
    sec("🪤 Detected Patterns")
    for trap in traps:
        if trap["type"] != "NEUTRAL":
            cls_map = {"trap-danger":"al-danger","trap-ok":"al-ok","trap-warn":"al-warn"}
            al_cls  = cls_map.get(trap["cls"],"al-info")
            st.markdown(
                f"<div class='al {al_cls}'><b>{trap['title']}</b><br>{trap['desc']}</div>",
                unsafe_allow_html=True)

    st.info(
        "⚠️ **Disclaimer:** This AI Verdict is a quantitative, logic-based research tool. "
        "It does NOT constitute SEBI-registered investment advice. "
        "Money Financial Services provides this as an educational decision-support tool. "
        "Please consult a SEBI-registered financial advisor before making investment decisions.")

# ══════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════
p = st.session_state.page
if   p == "🔍 Discovery Hub":       page_discovery()
elif p == "📋 Pro Watchlist":        page_watchlist()
elif p == "🛠️ Deep Dive Analysis":  page_deep_dive()
elif p == "🤖 AI Verdict & Strategy": page_ai_verdict()

st.markdown(
    "<div style='text-align:center;font-size:0.63rem;color:#94a3b8;"
    "padding:0.6rem 0 1.5rem;border-top:1px solid #e2e8f0;margin-top:1rem;'>"
    "📈 Stock Analysis Pro v6.0 · Money Financial Services · "
    "Yahoo Finance data · Educational use only · Not SEBI registered advice"
    "</div>", unsafe_allow_html=True)
