"""
Professional Stock Analysis Dashboard
Author: Money Financial Services
Version: 2.0 — Smart Groups + Full Batch Analysis
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import datetime
import math

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
:root {
    --bg:#f7f8fa; --card:#ffffff; --border:#e4e6eb;
    --primary:#1a56db; --success:#0e9f6e;
    --warning:#ff5a1f; --danger:#e02424;
    --text-main:#111928; --text-muted:#6b7280;
    --radius:12px; --shadow:0 2px 12px rgba(0,0,0,0.07);
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;background-color:var(--bg)!important;color:var(--text-main)!important;}
[data-testid="stSidebar"]{background:var(--card)!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebar"] *{color:var(--text-main)!important;}
.block-container{padding:1.5rem 2rem 3rem 2rem!important;max-width:1400px!important;}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:1.25rem 1.5rem;box-shadow:var(--shadow);margin-bottom:1rem;}
.card-title{font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:var(--text-muted);margin-bottom:0.35rem;}
.card-value{font-size:1.6rem;font-weight:700;color:var(--text-main);line-height:1.1;}
.card-sub{font-size:0.8rem;color:var(--text-muted);margin-top:0.2rem;}
.section-header{font-size:1rem;font-weight:600;color:var(--text-main);border-left:3px solid var(--primary);padding-left:0.6rem;margin:1.5rem 0 0.75rem 0;}
.badge{display:inline-block;padding:0.25rem 0.75rem;border-radius:999px;font-size:0.78rem;font-weight:600;letter-spacing:0.03em;}
.badge-green{background:#d1fae5;color:#065f46;}
.badge-yellow{background:#fef3c7;color:#92400e;}
.badge-red{background:#fee2e2;color:#991b1b;}
.badge-blue{background:#dbeafe;color:#1e40af;}
.prog-wrap{background:#e5e7eb;border-radius:999px;height:8px;width:100%;margin:0.35rem 0;}
.prog-fill{height:8px;border-radius:999px;}
.check-row{display:flex;align-items:center;gap:0.6rem;padding:0.5rem 0;border-bottom:1px solid var(--border);font-size:0.88rem;}
.info-box{background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:0.75rem 1rem;font-size:0.86rem;color:#1e40af;margin:0.5rem 0;}
.warn-box{background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:0.75rem 1rem;font-size:0.86rem;color:#92400e;margin:0.5rem 0;}
.danger-box{background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:0.75rem 1rem;font-size:0.86rem;color:#991b1b;margin:0.5rem 0;}
.success-box{background:#ecfdf5;border:1px solid #a7f3d0;border-radius:8px;padding:0.75rem 1rem;font-size:0.86rem;color:#065f46;margin:0.5rem 0;}
.stock-header-card{background:#fff;border:1px solid #e4e6eb;border-radius:12px;padding:1rem 1.25rem;box-shadow:0 2px 12px rgba(0,0,0,0.07);margin-bottom:0.75rem;}
[data-testid="stButton"] button{border-radius:8px!important;font-family:'DM Sans',sans-serif!important;font-weight:600!important;}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{border-radius:8px!important;border:1px solid var(--border)!important;font-family:'DM Sans',sans-serif!important;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# STOCK DATABASE
# ─────────────────────────────────────────────
STOCK_DB = {
    "Reliance Industries":    "RELIANCE.NS",
    "TCS":                    "TCS.NS",
    "Tata Consultancy":       "TCS.NS",
    "Infosys":                "INFY.NS",
    "HDFC Bank":              "HDFCBANK.NS",
    "ICICI Bank":             "ICICIBANK.NS",
    "Kotak Bank":             "KOTAKBANK.NS",
    "Axis Bank":              "AXISBANK.NS",
    "SBI State Bank":         "SBIN.NS",
    "Bajaj Finance":          "BAJFINANCE.NS",
    "Bajaj Finserv":          "BAJAJFINSV.NS",
    "Wipro":                  "WIPRO.NS",
    "HCL Technologies":       "HCLTECH.NS",
    "Tech Mahindra":          "TECHM.NS",
    "Larsen Toubro LT":       "LT.NS",
    "ITC":                    "ITC.NS",
    "Hindustan Unilever HUL": "HINDUNILVR.NS",
    "Nestle India":           "NESTLEIND.NS",
    "Asian Paints":           "ASIANPAINT.NS",
    "Maruti Suzuki":          "MARUTI.NS",
    "Tata Motors":            "TATAMOTORS.NS",
    "Mahindra M&M":           "M&M.NS",
    "Sun Pharma":             "SUNPHARMA.NS",
    "Dr Reddy":               "DRREDDY.NS",
    "Cipla":                  "CIPLA.NS",
    "Divis Lab":              "DIVISLAB.NS",
    "Apollo Hospitals":       "APOLLOHOSP.NS",
    "ONGC":                   "ONGC.NS",
    "Power Grid":             "POWERGRID.NS",
    "NTPC":                   "NTPC.NS",
    "Coal India":             "COALINDIA.NS",
    "Titan":                  "TITAN.NS",
    "Tata Steel":             "TATASTEEL.NS",
    "JSW Steel":              "JSWSTEEL.NS",
    "Hindalco":               "HINDALCO.NS",
    "UltraTech Cement":       "ULTRACEMCO.NS",
    "Adani Ports":            "ADANIPORTS.NS",
    "Adani Enterprises":      "ADANIENT.NS",
    "Adani Green":            "ADANIGREEN.NS",
    "Adani Power":            "ADANIPOWER.NS",
    "Shriram Finance":        "SHRIRAMFIN.NS",
    "Muthoot Finance":        "MUTHOOTFIN.NS",
    "Cholamandalam":          "CHOLAFIN.NS",
    "IDFC First Bank":        "IDFCFIRSTB.NS",
    "IndusInd Bank":          "INDUSINDBK.NS",
    "Bank of Baroda":         "BANKBARODA.NS",
    "Punjab National PNB":    "PNB.NS",
    "Canara Bank":            "CANBK.NS",
    "Union Bank":             "UNIONBANK.NS",
    "Federal Bank":           "FEDERALBNK.NS",
    "Yes Bank":               "YESBANK.NS",
    "Paytm":                  "PAYTM.NS",
    "Zomato":                 "ZOMATO.NS",
    "Nykaa":                  "NYKAA.NS",
    "Tata Power":             "TATAPOWER.NS",
    "Tata Consumer":          "TATACONSUM.NS",
    "Godrej Consumer":        "GODREJCP.NS",
    "Godrej Properties":      "GODREJPROP.NS",
    "Pidilite":               "PIDILITIND.NS",
    "Berger Paints":          "BERGEPAINT.NS",
    "Dabur":                  "DABUR.NS",
    "Marico":                 "MARICO.NS",
    "Britannia":              "BRITANNIA.NS",
    "Colgate":                "COLPAL.NS",
    "Havells":                "HAVELLS.NS",
    "Voltas":                 "VOLTAS.NS",
    "Dixon Technologies":     "DIXON.NS",
    "Hero MotoCorp":          "HEROMOTOCO.NS",
    "Bajaj Auto":             "BAJAJ-AUTO.NS",
    "Eicher Motors":          "EICHERMOT.NS",
    "Ashok Leyland":          "ASHOKLEY.NS",
    "IndiGo InterGlobe":      "INDIGO.NS",
    "Lupin":                  "LUPIN.NS",
    "Biocon":                 "BIOCON.NS",
    "Torrent Pharma":         "TORNTPHARM.NS",
    "Aurobindo Pharma":       "AUROPHARMA.NS",
    "DLF":                    "DLF.NS",
    "Lodha Macrotech":        "LODHA.NS",
    "Prestige Estates":       "PRESTIGE.NS",
    "Oberoi Realty":          "OBEROIRLTY.NS",
    "Varun Beverages":        "VBL.NS",
    "Page Industries":        "PAGEIND.NS",
    "Mphasis":                "MPHASIS.NS",
    "LTI Mindtree":           "LTIM.NS",
    "Persistent Systems":     "PERSISTENT.NS",
    "Coforge":                "COFORGE.NS",
    "BSE":                    "BSE.NS",
    "MCX":                    "MCX.NS",
    "Angel One":              "ANGELONE.NS",
    "CDSL":                   "CDSL.NS",
    "Polycab":                "POLYCAB.NS",
    "KEI Industries":         "KEI.NS",
    "Siemens":                "SIEMENS.NS",
    "ABB India":              "ABB.NS",
    "Bharat Electronics BEL": "BEL.NS",
    "HAL":                    "HAL.NS",
    "Bharat Forge":           "BHARATFORG.NS",
    "Cummins India":          "CUMMINSIND.NS",
    "PI Industries":          "PIIND.NS",
    "UPL":                    "UPL.NS",
    "Grasim":                 "GRASIM.NS",
    "Zydus Life":             "ZYDUSLIFE.NS",
    "IRCTC":                  "IRCTC.NS",
    "IRFC":                   "IRFC.NS",
    "RVNL":                   "RVNL.NS",
    "Mankind Pharma":         "MANKIND.NS",
    "Max Healthcare":         "MAXHEALTH.NS",
    "Fortis Healthcare":      "FORTIS.NS",
    "Dr Lal Path Labs":       "LALPATHLAB.NS",
    "Alkem Lab":              "ALKEM.NS",
    "Torrent Power":          "TORNTPOWER.NS",
    "NHPC":                   "NHPC.NS",
    "SJVN":                   "SJVN.NS",
}

# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
DB_PATH = "research_notes.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS notes (
        ticker TEXT PRIMARY KEY, content TEXT, updated_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_name TEXT NOT NULL,
        ticker TEXT NOT NULL,
        created_at TEXT,
        UNIQUE(group_name, ticker))""")
    conn.commit()
    conn.close()

def save_note(ticker, content):
    conn = sqlite3.connect(DB_PATH)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute("INSERT OR REPLACE INTO notes (ticker,content,updated_at) VALUES (?,?,?)",
                 (ticker.upper(), content, now))
    conn.commit(); conn.close()

def load_note(ticker):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content,updated_at FROM notes WHERE ticker=?", (ticker.upper(),))
    row = c.fetchone(); conn.close()
    return (row[0], row[1]) if row else ("", "")

def load_all_notes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ticker,content,updated_at FROM notes ORDER BY updated_at DESC")
    rows = c.fetchall(); conn.close()
    return rows

# ── Group DB functions ──
def get_all_groups():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT group_name FROM groups ORDER BY group_name")
    rows = [r[0] for r in c.fetchall()]
    conn.close(); return rows

def get_group_tickers(group_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ticker FROM groups WHERE group_name=? ORDER BY ticker", (group_name,))
    rows = [r[0] for r in c.fetchall()]
    conn.close(); return rows

def add_to_group(group_name, ticker):
    conn = sqlite3.connect(DB_PATH)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        conn.execute("INSERT OR IGNORE INTO groups (group_name,ticker,created_at) VALUES (?,?,?)",
                     (group_name, ticker.upper(), now))
        conn.commit()
    except: pass
    conn.close()

def remove_from_group(group_name, ticker):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM groups WHERE group_name=? AND ticker=?", (group_name, ticker))
    conn.commit(); conn.close()

def delete_group(group_name):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM groups WHERE group_name=?", (group_name,))
    conn.commit(); conn.close()

def rename_group(old_name, new_name):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE groups SET group_name=? WHERE group_name=?", (new_name, old_name))
    conn.commit(); conn.close()

# ─────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock(ticker):
    try:
        stk = yf.Ticker(ticker)
        info = stk.info
        hist = stk.history(period="1y")
        return info, hist
    except:
        return {}, pd.DataFrame()

def safe(d, key, default="N/A"):
    val = d.get(key, default)
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return default
    return val

def fmt_cr(val):
    if val == "N/A":
        return "N/A"
    try:
        v = float(val)
        if abs(v) >= 1e7: return f"₹{v/1e7:.2f} Cr"
        elif abs(v) >= 1e5: return f"₹{v/1e5:.2f} L"
        else: return f"₹{v:,.0f}"
    except: return str(val)

def fmt_pct(val):
    if val == "N/A": return "N/A"
    try: return f"{float(val)*100:.1f}%"
    except: return str(val)

def fmt_num(val, dec=2):
    if val == "N/A": return "N/A"
    try: return f"{float(val):,.{dec}f}"
    except: return str(val)

def compute_technicals(hist):
    if hist.empty: return {}
    tech = {}
    close = hist["Close"]; volume = hist["Volume"]
    tech["dma50"]  = close.rolling(50).mean().iloc[-1]  if len(close) >= 50  else None
    tech["dma200"] = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None
    tech["price"]  = close.iloc[-1]
    tech["pct_from_200"] = (tech["price"] - tech["dma200"]) / tech["dma200"] * 100 if tech["dma200"] else None
    tech["pct_from_50"]  = (tech["price"] - tech["dma50"])  / tech["dma50"]  * 100 if tech["dma50"]  else None
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))
    tech["rsi"] = rsi.iloc[-1] if not rsi.empty else None
    tech["high52"] = close.rolling(252).max().iloc[-1] if len(close) >= 252 else close.max()
    tech["low52"]  = close.rolling(252).min().iloc[-1] if len(close) >= 252 else close.min()
    tech["vol10"]  = volume.iloc[-10:].mean() if len(volume) >= 10 else volume.mean()
    tech["vol30"]  = volume.iloc[-30:].mean() if len(volume) >= 30 else volume.mean()
    return tech

def compute_score(info, hist):
    checks = []
    pe = safe(info, "trailingPE")
    checks.append({"label": "PE Ratio < 40", "pass_": pe != "N/A" and float(pe) < 40,
                   "note": f"PE = {float(pe):.1f}" if pe != "N/A" else "N/A"})
    de = safe(info, "debtToEquity")
    checks.append({"label": "Debt/Equity < 1x", "pass_": de != "N/A" and float(de) < 100,
                   "note": f"D/E = {float(de)/100:.2f}x" if de != "N/A" else "N/A"})
    roe = safe(info, "returnOnEquity")
    checks.append({"label": "ROE > 15%", "pass_": roe != "N/A" and float(roe) > 0.15,
                   "note": f"ROE = {float(roe)*100:.1f}%" if roe != "N/A" else "N/A"})
    fcf = safe(info, "freeCashflow")
    checks.append({"label": "Positive Free Cash Flow", "pass_": fcf != "N/A" and float(fcf) > 0,
                   "note": fmt_cr(fcf)})
    if not hist.empty and len(hist) >= 200:
        dma200 = hist["Close"].rolling(200).mean().iloc[-1]
        price  = hist["Close"].iloc[-1]
        pct_diff = (price - dma200) / dma200 * 100
        checks.append({"label": "Price above 200 DMA", "pass_": price > dma200,
                       "note": f"{pct_diff:+.1f}% from 200 DMA"})
    else:
        checks.append({"label": "Price above 200 DMA", "pass_": False, "note": "Insufficient history"})
    rg = safe(info, "revenueGrowth")
    checks.append({"label": "Positive Revenue Growth", "pass_": rg != "N/A" and float(rg) > 0,
                   "note": f"Growth = {float(rg)*100:.1f}%" if rg != "N/A" else "N/A"})
    pm = safe(info, "profitMargins")
    checks.append({"label": "Net Profit Margin > 10%", "pass_": pm != "N/A" and float(pm) > 0.10,
                   "note": f"Margin = {float(pm)*100:.1f}%" if pm != "N/A" else "N/A"})
    cr = safe(info, "currentRatio")
    checks.append({"label": "Current Ratio > 1.5", "pass_": cr != "N/A" and float(cr) > 1.5,
                   "note": f"CR = {float(cr):.2f}" if cr != "N/A" else "N/A"})
    insider = safe(info, "heldPercentInsiders")
    checks.append({"label": "Insider Holding > 10%", "pass_": insider != "N/A" and float(insider) > 0.10,
                   "note": f"Insiders = {float(insider)*100:.1f}%" if insider != "N/A" else "N/A"})
    avg_vol = safe(info, "averageVolume")
    checks.append({"label": "Avg Volume > 1 Lakh", "pass_": avg_vol != "N/A" and float(avg_vol) > 100000,
                   "note": f"Avg Vol = {float(avg_vol):,.0f}" if avg_vol != "N/A" else "N/A"})
    score = sum(1 for c in checks if c["pass_"])
    return score, checks


# ─────────────────────────────────────────────
# FULL STOCK ANALYSIS RENDERER (used in both single & group view)
# ─────────────────────────────────────────────
def render_full_analysis(ticker, info, hist, show_research=True):
    """Render complete analysis for one stock — used in single view & group batch view."""

    company    = safe(info, "longName", ticker)
    sector     = safe(info, "sector", "—")
    industry   = safe(info, "industry", "—")
    exchange   = safe(info, "exchange", "—")
    currency   = safe(info, "currency", "INR")
    price      = safe(info, "regularMarketPrice")
    prev_close = safe(info, "regularMarketPreviousClose")

    if price != "N/A" and prev_close != "N/A":
        change     = float(price) - float(prev_close)
        change_pct = change / float(prev_close) * 100
        chg_str    = f"{'▲' if change>=0 else '▼'} {abs(change):.2f} ({change_pct:+.2f}%)"
        chg_color  = "#0e9f6e" if change >= 0 else "#e02424"
    else:
        chg_str, chg_color = "—", "#6b7280"

    price_display = f"{f'{float(price):,.2f}' if price != 'N/A' else '—'}"

    # ── Stock Header ──
    st.markdown(f"""
    <div class='stock-header-card'>
      <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;'>
        <div>
          <div style='font-size:1.2rem;font-weight:700;color:#111928;'>{company}</div>
          <div style='font-size:0.78rem;color:#6b7280;margin-top:0.1rem;'>
            <span style='background:#dbeafe;color:#1e40af;border-radius:4px;padding:0.1rem 0.4rem;font-weight:600;font-size:0.72rem;'>{exchange}</span>
            &nbsp;{sector} · {industry}
          </div>
        </div>
        <div style='text-align:right;'>
          <div style='font-size:1.5rem;font-weight:700;'>{currency} {price_display}</div>
          <div style='font-size:0.85rem;font-weight:600;color:{chg_color};'>{chg_str}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs inside each stock ──
    t1, t2, t3, t4 = st.tabs(["📋 Fundamentals", "📡 Technicals", "✅ Decision Score", "🔬 Research"])

    # ══ TAB 1 – FUNDAMENTALS ══
    with t1:
        st.markdown("<div class='section-header'>Valuation</div>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        pe=safe(info,"trailingPE"); fpe=safe(info,"forwardPE")
        pb=safe(info,"priceToBook"); ps=safe(info,"priceToSalesTrailing12Months")
        with c1:
            color="#0e9f6e" if pe!="N/A" and float(pe)<25 else ("#ff5a1f" if pe!="N/A" and float(pe)<50 else "#e02424") if pe!="N/A" else "#111928"
            st.markdown(f"""<div class='card'><div class='card-title'>Trailing PE</div>
            <div class='card-value' style='color:{color};'>{fmt_num(pe,1)}</div>
            <div class='card-sub'>{"✅ Reasonable" if pe!="N/A" and float(pe)<30 else "⚠️ High" if pe!="N/A" else "—"}</div></div>""",unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class='card'><div class='card-title'>Forward PE</div>
            <div class='card-value'>{fmt_num(fpe,1)}</div><div class='card-sub'>Expected earnings</div></div>""",unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class='card'><div class='card-title'>Price / Book</div>
            <div class='card-value'>{fmt_num(pb,2)}</div>
            <div class='card-sub'>{"✅ < 3" if pb!="N/A" and float(pb)<3 else "⚠️ High" if pb!="N/A" else "—"}</div></div>""",unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class='card'><div class='card-title'>Price / Sales</div>
            <div class='card-value'>{fmt_num(ps,2)}</div><div class='card-sub'>Revenue multiple</div></div>""",unsafe_allow_html=True)

        st.markdown("<div class='section-header'>Profitability</div>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        roe=safe(info,"returnOnEquity"); roa=safe(info,"returnOnAssets")
        pm=safe(info,"profitMargins"); gm=safe(info,"grossMargins")
        with c1:
            color="#0e9f6e" if roe!="N/A" and float(roe)>0.15 else "#e02424"
            st.markdown(f"""<div class='card'><div class='card-title'>ROE</div>
            <div class='card-value' style='color:{color};'>{fmt_pct(roe)}</div>
            <div class='card-sub'>{"✅ > 15%" if roe!="N/A" and float(roe)>0.15 else "⚠️ Below 15%"}</div></div>""",unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class='card'><div class='card-title'>ROA</div>
            <div class='card-value'>{fmt_pct(roa)}</div><div class='card-sub'>Asset efficiency</div></div>""",unsafe_allow_html=True)
        with c3:
            color="#0e9f6e" if pm!="N/A" and float(pm)>0.10 else "#e02424"
            st.markdown(f"""<div class='card'><div class='card-title'>Net Profit Margin</div>
            <div class='card-value' style='color:{color};'>{fmt_pct(pm)}</div>
            <div class='card-sub'>{"✅ > 10%" if pm!="N/A" and float(pm)>0.10 else "⚠️ Low"}</div></div>""",unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class='card'><div class='card-title'>Gross Margin</div>
            <div class='card-value'>{fmt_pct(gm)}</div><div class='card-sub'>Revenue efficiency</div></div>""",unsafe_allow_html=True)

        st.markdown("<div class='section-header'>Balance Sheet & Cash Flow</div>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        de=safe(info,"debtToEquity"); cr=safe(info,"currentRatio")
        fcf=safe(info,"freeCashflow"); mc=safe(info,"marketCap")
        de_ratio = float(de)/100 if de!="N/A" else None
        with c1:
            color="#0e9f6e" if de_ratio and de_ratio<1 else "#e02424"
            st.markdown(f"""<div class='card'><div class='card-title'>Debt / Equity</div>
            <div class='card-value' style='color:{color};'>{f"{de_ratio:.2f}x" if de_ratio is not None else "N/A"}</div>
            <div class='card-sub'>{"✅ Low debt" if de_ratio and de_ratio<1 else "⚠️ High debt"}</div></div>""",unsafe_allow_html=True)
        with c2:
            color="#0e9f6e" if cr!="N/A" and float(cr)>1.5 else "#ff5a1f"
            st.markdown(f"""<div class='card'><div class='card-title'>Current Ratio</div>
            <div class='card-value' style='color:{color};'>{fmt_num(cr,2)}</div>
            <div class='card-sub'>{"✅ Liquid" if cr!="N/A" and float(cr)>1.5 else "⚠️ Watch"}</div></div>""",unsafe_allow_html=True)
        with c3:
            color="#0e9f6e" if fcf!="N/A" and float(fcf)>0 else "#e02424"
            st.markdown(f"""<div class='card'><div class='card-title'>Free Cash Flow</div>
            <div class='card-value' style='color:{color};font-size:1.2rem;'>{fmt_cr(fcf)}</div>
            <div class='card-sub'>{"✅ Positive FCF" if fcf!="N/A" and float(fcf)>0 else "⚠️ Negative FCF"}</div></div>""",unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class='card'><div class='card-title'>Market Cap</div>
            <div class='card-value' style='font-size:1.2rem;'>{fmt_cr(mc)}</div>
            <div class='card-sub'>Total valuation</div></div>""",unsafe_allow_html=True)

        st.markdown("<div class='section-header'>Growth</div>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        rg=safe(info,"revenueGrowth"); eg=safe(info,"earningsGrowth")
        eps=safe(info,"trailingEps"); beta=safe(info,"beta")
        with c1:
            color="#0e9f6e" if rg!="N/A" and float(rg)>0 else "#e02424"
            st.markdown(f"""<div class='card'><div class='card-title'>Revenue Growth YoY</div>
            <div class='card-value' style='color:{color};'>{fmt_pct(rg)}</div></div>""",unsafe_allow_html=True)
        with c2:
            color="#0e9f6e" if eg!="N/A" and float(eg)>0 else "#e02424"
            st.markdown(f"""<div class='card'><div class='card-title'>Earnings Growth YoY</div>
            <div class='card-value' style='color:{color};'>{fmt_pct(eg)}</div></div>""",unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class='card'><div class='card-title'>Trailing EPS</div>
            <div class='card-value'>{fmt_num(eps,2)}</div></div>""",unsafe_allow_html=True)
        with c4:
            b_color="#0e9f6e" if beta!="N/A" and float(beta)<1 else "#ff5a1f"
            st.markdown(f"""<div class='card'><div class='card-title'>Beta (Risk)</div>
            <div class='card-value' style='color:{b_color};'>{fmt_num(beta,2)}</div>
            <div class='card-sub'>{"✅ Less volatile" if beta!="N/A" and float(beta)<1 else "⚠️ More volatile" if beta!="N/A" else ""}</div></div>""",unsafe_allow_html=True)

        desc = safe(info,"longBusinessSummary","")
        if desc and desc != "N/A":
            with st.expander("📖 About the Company"):
                st.markdown(f"<div style='font-size:0.88rem;line-height:1.75;color:#374151;'>{desc[:1000]}…</div>",unsafe_allow_html=True)

    # ══ TAB 2 – TECHNICALS ══
    with t2:
        tech = compute_technicals(hist)
        if not tech:
            st.warning("Historical data not available.")
        else:
            st.markdown("<div class='section-header'>Price & Moving Averages</div>", unsafe_allow_html=True)
            c1,c2,c3,c4 = st.columns(4)
            with c1:
                st.markdown(f"""<div class='card'><div class='card-title'>Current Price</div>
                <div class='card-value'>₹{tech['price']:.2f}</div></div>""",unsafe_allow_html=True)
            with c2:
                dma50_str = f"₹{tech['dma50']:.2f}" if tech['dma50'] else "N/A"
                pct50 = tech.get("pct_from_50")
                color50 = "#0e9f6e" if pct50 and pct50>0 else "#e02424"
                st.markdown(f"""<div class='card'><div class='card-title'>50-Day DMA</div>
                <div class='card-value'>{dma50_str}</div>
                <div class='card-sub' style='color:{color50};font-weight:600;'>{f"{pct50:+.1f}%" if pct50 else ""}</div></div>""",unsafe_allow_html=True)
            with c3:
                dma200_str = f"₹{tech['dma200']:.2f}" if tech['dma200'] else "N/A"
                pct200 = tech.get("pct_from_200")
                color200 = "#0e9f6e" if pct200 and pct200>0 else "#e02424"
                st.markdown(f"""<div class='card'><div class='card-title'>200-Day DMA</div>
                <div class='card-value'>{dma200_str}</div>
                <div class='card-sub' style='color:{color200};font-weight:600;'>{f"{pct200:+.1f}%" if pct200 else ""}</div></div>""",unsafe_allow_html=True)
            with c4:
                rsi = tech.get("rsi")
                if rsi:
                    rsi_label = "Overbought ⚠️" if rsi>70 else ("Oversold 🔎" if rsi<30 else "Neutral ✅")
                    rsi_color = "#e02424" if rsi>70 else ("#ff5a1f" if rsi<30 else "#0e9f6e")
                else:
                    rsi_label, rsi_color = "N/A", "#6b7280"
                st.markdown(f"""<div class='card'><div class='card-title'>RSI (14-day)</div>
                <div class='card-value' style='color:{rsi_color};'>{f"{rsi:.1f}" if rsi else "N/A"}</div>
                <div class='card-sub'>{rsi_label}</div></div>""",unsafe_allow_html=True)

            # 200 DMA bar
            pct200 = tech.get("pct_from_200")
            if pct200 is not None:
                clamped = max(-50, min(50, pct200))
                fill_pct = (clamped + 50) / 100 * 100
                fill_color = "#0e9f6e" if pct200>=0 else "#e02424"
                if pct200>20: trap_msg,msg_class="⚠️ <b>Overextended above 200 DMA</b> — Risk of pullback.","warn-box"
                elif pct200>0: trap_msg,msg_class="✅ <b>Healthy uptrend</b> — Price above 200 DMA.","success-box"
                elif pct200>-15: trap_msg,msg_class="🔎 <b>Near/below 200 DMA</b> — Wait for recovery.","warn-box"
                else: trap_msg,msg_class="🚨 <b>Far below 200 DMA</b> — Downtrend. Avoid.","danger-box"
                st.markdown(f"""
                <div class='card'>
                  <div style='display:flex;justify-content:space-between;margin-bottom:0.4rem;'>
                    <span style='font-size:0.8rem;color:#6b7280;'>−50%</span>
                    <span style='font-size:0.9rem;font-weight:700;color:{fill_color};'>{pct200:+.1f}% from 200 DMA</span>
                    <span style='font-size:0.8rem;color:#6b7280;'>+50%</span>
                  </div>
                  <div class='prog-wrap'><div class='prog-fill' style='width:{fill_pct}%;background:{fill_color};'></div></div>
                </div>
                <div class='{msg_class}'>{trap_msg}</div>
                """,unsafe_allow_html=True)

            # 52W Range
            h52=tech.get("high52"); l52=tech.get("low52"); cp=tech["price"]
            if h52 and l52 and h52!=l52:
                pos_pct = (cp-l52)/(h52-l52)*100
                pct_from_high = (cp-h52)/h52*100
                c1,c2 = st.columns([3,1])
                with c1:
                    st.markdown(f"""<div class='card'>
                      <div style='display:flex;justify-content:space-between;margin-bottom:0.4rem;'>
                        <span style='font-size:0.8rem;color:#6b7280;'>52W Low ₹{l52:.0f}</span>
                        <span style='font-size:0.82rem;font-weight:600;'>📍 ₹{cp:.1f} ({pos_pct:.0f}%ile)</span>
                        <span style='font-size:0.8rem;color:#6b7280;'>52W High ₹{h52:.0f}</span>
                      </div>
                      <div class='prog-wrap'><div class='prog-fill' style='width:{pos_pct:.1f}%;background:linear-gradient(90deg,#ef4444,#f59e0b,#10b981);'></div></div>
                    </div>""",unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""<div class='card'><div class='card-title'>From 52W High</div>
                    <div class='card-value' style='color:{"#0e9f6e" if pct_from_high>-5 else "#e02424"};'>{pct_from_high:+.1f}%</div></div>""",unsafe_allow_html=True)

            # Volume
            vol10=tech.get("vol10"); vol30=tech.get("vol30")
            c1,c2,c3 = st.columns(3)
            with c1:
                st.markdown(f"""<div class='card'><div class='card-title'>10-Day Avg Volume</div>
                <div class='card-value' style='font-size:1.1rem;'>{f"{vol10:,.0f}" if vol10 else "N/A"}</div></div>""",unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class='card'><div class='card-title'>30-Day Avg Volume</div>
                <div class='card-value' style='font-size:1.1rem;'>{f"{vol30:,.0f}" if vol30 else "N/A"}</div></div>""",unsafe_allow_html=True)
            with c3:
                if vol10 and vol30 and vol30>0:
                    vr=vol10/vol30
                    vc="#0e9f6e" if vr>1.2 else ("#ff5a1f" if vr<0.8 else "#111928")
                    vl="📈 Volume Spike" if vr>1.2 else ("📉 Volume Dry" if vr<0.8 else "➡️ Normal")
                else: vr,vc,vl=None,"#6b7280","N/A"
                st.markdown(f"""<div class='card'><div class='card-title'>10D vs 30D Volume</div>
                <div class='card-value' style='color:{vc};font-size:1.1rem;'>{f"{vr:.2f}x" if vr else "N/A"}</div>
                <div class='card-sub'>{vl}</div></div>""",unsafe_allow_html=True)

            # Price chart
            if not hist.empty:
                st.markdown("<div class='section-header'>1-Year Price Chart</div>", unsafe_allow_html=True)
                chart_df = hist[["Close"]].copy()
                if tech["dma50"]:  chart_df["50 DMA"]  = hist["Close"].rolling(50).mean()
                if tech["dma200"]: chart_df["200 DMA"] = hist["Close"].rolling(200).mean()
                st.line_chart(chart_df, use_container_width=True, height=280)

    # ══ TAB 3 – DECISION SCORE ══
    with t3:
        score, checks = compute_score(info, hist)
        max_score = len(checks)
        score_pct = int(score / max_score * 100)
        if score_pct >= 70:
            grade,badge_cls,verdict_icon,verdict_text = "Strong Buy Zone","badge-green","🟢","Fundamentals solid. Majority of quality filters passed."
        elif score_pct >= 50:
            grade,badge_cls,verdict_icon,verdict_text = "Watchlist / Wait","badge-yellow","🟡","Mixed signals. Wait for improvement or smaller position."
        else:
            grade,badge_cls,verdict_icon,verdict_text = "Avoid / High Risk","badge-red","🔴","Multiple red flags. High risk of capital loss."

        col_score, col_detail = st.columns([1,2])
        with col_score:
            st.markdown(f"""<div class='card' style='text-align:center;padding:1.5rem 1rem;'>
              <div style='font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:#6b7280;margin-bottom:0.4rem;'>DECISION SCORE</div>
              <div style='font-size:3.5rem;font-weight:800;color:{"#0e9f6e" if score_pct>=70 else "#f59e0b" if score_pct>=50 else "#e02424"};line-height:1;'>{score}/{max_score}</div>
              <div style='font-size:0.85rem;color:#6b7280;margin:0.25rem 0 0.75rem;'>{score_pct}% pass rate</div>
              <div class='prog-wrap'><div class='prog-fill' style='width:{score_pct}%;background:{"#0e9f6e" if score_pct>=70 else "#f59e0b" if score_pct>=50 else "#e02424"};'></div></div>
              <div style='margin-top:0.75rem;'><span class='badge {badge_cls}'>{verdict_icon} {grade}</span></div>
            </div>""",unsafe_allow_html=True)
        with col_detail:
            st.markdown(f"""<div class='{"success-box" if score_pct>=70 else "warn-box" if score_pct>=50 else "danger-box"}'>
            <b>{verdict_icon} Verdict:</b> {verdict_text}</div>""",unsafe_allow_html=True)
            for chk in checks:
                icon="✅" if chk["pass_"] else "❌"
                color="#065f46" if chk["pass_"] else "#991b1b"
                bg="#f0fdf4" if chk["pass_"] else "#fff1f2"
                st.markdown(f"""<div style='background:{bg};border-radius:6px;padding:0.4rem 0.7rem;margin-bottom:0.25rem;display:flex;gap:0.5rem;align-items:center;'>
                  <span>{icon}</span>
                  <div>
                    <div style='font-size:0.85rem;font-weight:500;color:{color};'>{chk["label"]}</div>
                    <div style='font-size:0.75rem;color:#6b7280;'>{chk["note"]}</div>
                  </div>
                </div>""",unsafe_allow_html=True)

    # ══ TAB 4 – RESEARCH ══
    with t4:
        existing_note, last_updated = load_note(ticker)
        st.markdown(f"<div class='info-box'>✍️ Personal research notes for <b>{ticker}</b></div>",unsafe_allow_html=True)

        template = f"""📌 STOCK: {ticker}
📅 Date: {datetime.date.today()}

🎯 WHY AM I INTERESTED?

📊 KEY NUMBERS:
- PE: 
- Debt/Equity: 
- ROE: 
- FCF: 

⚠️ RISKS:

💡 SECTOR INSIGHT:

🎯 ENTRY PLAN:
- Entry Price: ₹
- Stop Loss: ₹
- Target: ₹
- Time Horizon:

✅ CONCLUSION:
"""
        if st.button("📋 Load Template", key=f"tmpl_{ticker}"):
            existing_note = template

        note_content = st.text_area("Notes", value=existing_note, height=350, key=f"note_{ticker}")
        c1,c2 = st.columns([2,1])
        with c1:
            if st.button("💾 Save Note", key=f"save_{ticker}", use_container_width=True, type="primary"):
                if note_content.strip():
                    save_note(ticker, note_content)
                    st.success(f"✅ Saved for {ticker}!")
        with c2:
            if last_updated:
                st.markdown(f"<div style='font-size:0.78rem;color:#6b7280;padding-top:0.6rem;'>Saved: {last_updated}</div>",unsafe_allow_html=True)


# ─────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────
init_db()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:0.5rem 0 1rem'>
      <div style='font-size:1.3rem;font-weight:700;color:#111928;'>📊 Stock Analyser</div>
      <div style='font-size:0.75rem;color:#6b7280;'>Money Financial Services · v2.0</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Mode selector ──
    mode = st.radio("", ["📈 Single Analysis", "📁 Group Analysis"], horizontal=True, label_visibility="collapsed")
    st.markdown("---")

    if mode == "📈 Single Analysis":
        # ── Smart Search ──
        st.markdown("##### 🔍 Stock Search")

        if "watchlist" not in st.session_state:
            st.session_state.watchlist = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

        search_query = st.text_input("Search Company", placeholder="Type: SBI, Bajaj, Wipro…", key="search_input")

        if search_query:
            sq = search_query.lower()
            matches = {}
            seen = set()
            for name, ticker in STOCK_DB.items():
                if (sq in name.lower() or sq in ticker.lower()) and ticker not in seen:
                    seen.add(ticker); matches[name] = ticker

            if matches:
                st.markdown(f"<div style='font-size:0.75rem;color:#6b7280;margin-bottom:0.25rem;'>🔍 {len(matches)} found — ➕ to add:</div>",unsafe_allow_html=True)
                for name, ticker in list(matches.items())[:7]:
                    already = ticker in st.session_state.watchlist
                    ca, cb = st.columns([4,1])
                    with ca:
                        st.markdown(f"<div style='font-size:0.8rem;padding:0.1rem 0;'><b>{ticker}</b><br><span style='color:#6b7280;font-size:0.72rem;'>{name}</span></div>",unsafe_allow_html=True)
                    with cb:
                        if already:
                            st.markdown("<div style='padding-top:0.3rem;'>✅</div>",unsafe_allow_html=True)
                        else:
                            if st.button("➕", key=f"add_{ticker}"):
                                st.session_state.watchlist.append(ticker)
                                st.rerun()
            else:
                st.markdown("<div style='font-size:0.78rem;color:#e02424;'>Not found. Use manual add below.</div>",unsafe_allow_html=True)

        with st.expander("✏️ Manual Add"):
            nt = st.text_input("Ticker", placeholder="SBIN.NS", key="manual_t")
            if st.button("➕ Add", use_container_width=True, key="manual_add"):
                t = nt.strip().upper()
                if t and t not in st.session_state.watchlist:
                    st.session_state.watchlist.append(t); st.rerun()

        st.markdown("---")
        st.markdown("**Your Watchlist**")
        for i, t in enumerate(st.session_state.watchlist):
            ca, cb = st.columns([4,1])
            with ca:
                st.markdown(f"<div style='font-size:0.86rem;padding:0.2rem 0;'>📌 {t}</div>",unsafe_allow_html=True)
            with cb:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.watchlist.pop(i); st.rerun()

        st.markdown("---")
        selected = st.selectbox("📈 Analyse Stock", options=st.session_state.watchlist)

    else:
        # ── GROUP MANAGEMENT ──
        st.markdown("##### 📁 My Groups")

        # Create new group
        with st.expander("➕ Create New Group"):
            new_grp = st.text_input("Group Name", placeholder="e.g. Banking Sector", key="new_grp_name")
            if st.button("Create Group", use_container_width=True, key="create_grp"):
                if new_grp.strip():
                    add_to_group(new_grp.strip(), "__placeholder__")
                    st.success(f"✅ '{new_grp}' created!")
                    st.rerun()

        groups = get_all_groups()

        if not groups:
            st.markdown("<div class='warn-box'>No groups yet. Create one above!</div>",unsafe_allow_html=True)
            selected = None
        else:
            # Add stock to group
            with st.expander("📌 Add Stock to Group"):
                sq2 = st.text_input("Search Stock", placeholder="Type company name…", key="grp_search")
                target_grp = st.selectbox("Select Group", groups, key="target_grp")

                if sq2:
                    sq2l = sq2.lower()
                    m2 = {}; seen2 = set()
                    for name, ticker in STOCK_DB.items():
                        if (sq2l in name.lower() or sq2l in ticker.lower()) and ticker not in seen2:
                            seen2.add(ticker); m2[name] = ticker
                    if m2:
                        for name, ticker in list(m2.items())[:5]:
                            ca, cb = st.columns([4,1])
                            with ca:
                                st.markdown(f"<div style='font-size:0.78rem;'><b>{ticker}</b><br><span style='color:#6b7280;font-size:0.7rem;'>{name}</span></div>",unsafe_allow_html=True)
                            with cb:
                                if st.button("➕", key=f"gadd_{ticker}_{target_grp}"):
                                    add_to_group(target_grp, ticker); st.rerun()

                manual_t2 = st.text_input("Manual Ticker", placeholder="SBIN.NS", key="grp_manual")
                if st.button("Add Manually", use_container_width=True, key="grp_manual_add"):
                    if manual_t2.strip():
                        add_to_group(target_grp, manual_t2.strip().upper()); st.rerun()

            # Show all groups with stocks
            st.markdown("**Groups & Stocks:**")
            for grp in groups:
                tickers = [t for t in get_group_tickers(grp) if t != "__placeholder__"]
                with st.expander(f"📁 {grp} ({len(tickers)} stocks)"):
                    if not tickers:
                        st.markdown("<div style='font-size:0.78rem;color:#6b7280;'>No stocks. Add above.</div>",unsafe_allow_html=True)
                    else:
                        for t in tickers:
                            ca, cb = st.columns([4,1])
                            with ca:
                                st.markdown(f"<div style='font-size:0.82rem;'>📌 {t}</div>",unsafe_allow_html=True)
                            with cb:
                                if st.button("✕", key=f"grm_{grp}_{t}"):
                                    remove_from_group(grp, t); st.rerun()
                    if st.button(f"🗑️ Delete '{grp}'", key=f"delgrp_{grp}", use_container_width=True):
                        delete_group(grp); st.rerun()

            selected = st.selectbox("🔍 Analyse Group", groups, key="analyse_grp")


# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────

# ══ SINGLE ANALYSIS MODE ══
if mode == "📈 Single Analysis":
    if not st.session_state.get("watchlist"):
        st.info("Add stocks to your watchlist to begin."); st.stop()

    with st.spinner(f"Fetching **{selected}**…"):
        info, hist = fetch_stock(selected)

    if not info or not info.get("regularMarketPrice"):
        st.error(f"❌ Could not fetch **{selected}**. Check ticker symbol."); st.stop()

    st.markdown("## 📈 Single Stock Analysis")
    render_full_analysis(selected, info, hist)

# ══ GROUP ANALYSIS MODE ══
else:
    groups = get_all_groups()
    if not groups:
        st.info("📁 No groups yet. Create a group in the sidebar and add stocks to it.")
        st.stop()

    if not selected:
        st.stop()

    tickers = [t for t in get_group_tickers(selected) if t != "__placeholder__"]

    if not tickers:
        st.warning(f"Group **{selected}** has no stocks. Add stocks from the sidebar.")
        st.stop()

    # Group header
    score_summary = []
    st.markdown(f"""
    <div style='background:#fff;border:1px solid #e4e6eb;border-radius:12px;padding:1rem 1.5rem;
                box-shadow:0 2px 12px rgba(0,0,0,0.07);margin-bottom:1.5rem;'>
      <div style='font-size:1.4rem;font-weight:700;'>📁 {selected}</div>
      <div style='font-size:0.82rem;color:#6b7280;margin-top:0.2rem;'>{len(tickers)} stocks · Full Analysis View</div>
    </div>
    """, unsafe_allow_html=True)

    # Quick summary scorecard at top
    st.markdown("<div class='section-header'>⚡ Quick Scorecard — All Stocks</div>", unsafe_allow_html=True)

    summary_cols = st.columns(min(len(tickers), 4))
    summary_data = []
    for i, ticker in enumerate(tickers):
        with st.spinner(f"Loading {ticker}…"):
            s_info, s_hist = fetch_stock(ticker)
        if s_info:
            s_score, _ = compute_score(s_info, s_hist)
            s_price = safe(s_info, "regularMarketPrice")
            s_name  = safe(s_info, "longName", ticker)
            s_pct   = int(s_score / 10 * 100)
            summary_data.append((ticker, s_name, s_score, s_pct, s_price, s_info, s_hist))

    # Summary cards
    for i, (ticker, s_name, s_score, s_pct, s_price, s_info, s_hist) in enumerate(summary_data):
        col = summary_cols[i % 4]
        color = "#0e9f6e" if s_pct>=70 else "#f59e0b" if s_pct>=50 else "#e02424"
        grade_short = "🟢 Buy" if s_pct>=70 else "🟡 Watch" if s_pct>=50 else "🔴 Avoid"
        col.markdown(f"""<div class='card' style='text-align:center;'>
          <div style='font-size:0.72rem;font-weight:600;color:#6b7280;text-transform:uppercase;'>{ticker}</div>
          <div style='font-size:0.82rem;font-weight:500;color:#374151;margin:0.1rem 0;'>{s_name[:20]}</div>
          <div style='font-size:1.8rem;font-weight:800;color:{color};'>{s_score}/10</div>
          <div style='font-size:0.78rem;margin:0.2rem 0;'><span class='badge {"badge-green" if s_pct>=70 else "badge-yellow" if s_pct>=50 else "badge-red"}'>{grade_short}</span></div>
          <div style='font-size:0.82rem;color:#6b7280;'>₹{f"{float(s_price):,.1f}" if s_price!="N/A" else "—"}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Full analysis for each stock
    st.markdown(f"<div class='section-header'>📊 Full Analysis — {selected}</div>", unsafe_allow_html=True)

    for ticker, s_name, s_score, s_pct, s_price, s_info, s_hist in summary_data:
        color = "#0e9f6e" if s_pct>=70 else "#f59e0b" if s_pct>=50 else "#e02424"
        grade_short = "🟢 Strong Buy" if s_pct>=70 else "🟡 Watch" if s_pct>=50 else "🔴 Avoid"

        with st.expander(f"📌 {ticker} — {s_name}   |   Score: {s_score}/10   {grade_short}", expanded=False):
            render_full_analysis(ticker, s_info, s_hist)
            st.markdown("---")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;font-size:0.75rem;color:#9ca3af;padding:0.5rem 0 1rem;'>
  📊 <b>Stock Analysis Dashboard v2.0</b> · Money Financial Services ·
  Data via Yahoo Finance · For educational purposes only · Not SEBI registered investment advice
</div>
""", unsafe_allow_html=True)
