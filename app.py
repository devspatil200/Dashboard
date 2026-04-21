"""
Professional Stock Analysis Dashboard
Author: Money Financial Services
Version: 1.0
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import os
import datetime
import math

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be FIRST Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL CSS – clean white/light professional theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Root variables ── */
:root {
    --bg:        #f7f8fa;
    --card:      #ffffff;
    --border:    #e4e6eb;
    --primary:   #1a56db;
    --success:   #0e9f6e;
    --warning:   #ff5a1f;
    --danger:    #e02424;
    --text-main: #111928;
    --text-muted:#6b7280;
    --radius:    12px;
    --shadow:    0 2px 12px rgba(0,0,0,0.07);
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text-main) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--card) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-main) !important; }

/* ── Main area ── */
.block-container { padding: 1.5rem 2rem 3rem 2rem !important; max-width: 1400px !important; }

/* ── Cards ── */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}
.card-title {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin-bottom: 0.35rem;
}
.card-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text-main);
    line-height: 1.1;
}
.card-sub {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
}

/* ── Section headers ── */
.section-header {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-main);
    border-left: 3px solid var(--primary);
    padding-left: 0.6rem;
    margin: 1.5rem 0 0.75rem 0;
}

/* ── Score badges ── */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-green  { background:#d1fae5; color:#065f46; }
.badge-yellow { background:#fef3c7; color:#92400e; }
.badge-red    { background:#fee2e2; color:#991b1b; }
.badge-blue   { background:#dbeafe; color:#1e40af; }

/* ── Progress bar ── */
.prog-wrap { background:#e5e7eb; border-radius:999px; height:8px; width:100%; margin:0.35rem 0; }
.prog-fill  { height:8px; border-radius:999px; transition: width 0.6s ease; }

/* ── Checklist ── */
.check-row {
    display:flex; align-items:center; gap:0.6rem;
    padding:0.5rem 0;
    border-bottom: 1px solid var(--border);
    font-size:0.88rem;
}
.check-row:last-child { border-bottom:none; }
.check-icon { font-size:1rem; flex-shrink:0; }

/* ── Table overrides ── */
[data-testid="stDataFrame"] { border-radius: var(--radius); overflow:hidden; }

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] select {
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Buttons ── */
[data-testid="stButton"] button {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
}

/* ── Metric tweaks ── */
[data-testid="stMetric"] label { font-size: 0.78rem !important; color: var(--text-muted) !important; text-transform: uppercase; letter-spacing: 0.05em; }
[data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 1.4rem !important; font-weight: 700 !important; }

/* ── Alert boxes ── */
.info-box {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.86rem;
    color: #1e40af;
    margin: 0.5rem 0;
}
.warn-box {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.86rem;
    color: #92400e;
    margin: 0.5rem 0;
}
.danger-box {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.86rem;
    color: #991b1b;
    margin: 0.5rem 0;
}
.success-box {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.86rem;
    color: #065f46;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATABASE  (SQLite – persists research notes)
# ─────────────────────────────────────────────
DB_PATH = "research_notes.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            ticker TEXT PRIMARY KEY,
            content TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_note(ticker: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT OR REPLACE INTO notes (ticker, content, updated_at) VALUES (?,?,?)",
              (ticker.upper(), content, now))
    conn.commit()
    conn.close()

def load_note(ticker: str) -> tuple:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content, updated_at FROM notes WHERE ticker=?", (ticker.upper(),))
    row = c.fetchone()
    conn.close()
    return (row[0], row[1]) if row else ("", "")

def load_all_notes() -> list:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ticker, content, updated_at FROM notes ORDER BY updated_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows


# ─────────────────────────────────────────────
# DATA HELPERS
# ─────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock(ticker: str):
    try:
        stk = yf.Ticker(ticker)
        info = stk.info
        hist = stk.history(period="1y")
        return info, hist
    except Exception as e:
        return {}, pd.DataFrame()

def safe(d, key, default="N/A"):
    val = d.get(key, default)
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return default
    return val

def fmt_cr(val):
    """Format large numbers as Crores (Indian style)."""
    if val == "N/A":
        return "N/A"
    try:
        v = float(val)
        if abs(v) >= 1e7:
            return f"₹{v/1e7:.2f} Cr"
        elif abs(v) >= 1e5:
            return f"₹{v/1e5:.2f} L"
        else:
            return f"₹{v:,.0f}"
    except:
        return str(val)

def fmt_pct(val):
    if val == "N/A":
        return "N/A"
    try:
        return f"{float(val)*100:.1f}%"
    except:
        return str(val)

def fmt_num(val, dec=2):
    if val == "N/A":
        return "N/A"
    try:
        return f"{float(val):,.{dec}f}"
    except:
        return str(val)


# ─────────────────────────────────────────────
# SCORING ENGINE
# ─────────────────────────────────────────────
def compute_score(info: dict, hist: pd.DataFrame) -> tuple[int, list]:
    """
    Returns (score_out_of_10, list_of_check_dicts).
    Each check: {label, pass_, note}
    """
    checks = []

    # 1. PE Ratio (< 40 = reasonable)
    pe = safe(info, "trailingPE")
    if pe != "N/A":
        passed = float(pe) < 40
        checks.append({"label": "PE Ratio < 40 (Not overvalued)", "pass_": passed,
                        "note": f"PE = {float(pe):.1f}"})
    else:
        checks.append({"label": "PE Ratio < 40 (Not overvalued)", "pass_": False, "note": "Data unavailable"})

    # 2. Debt-to-Equity < 1
    de = safe(info, "debtToEquity")
    if de != "N/A":
        passed = float(de) < 100   # yfinance returns as %, so 100 = 1x
        checks.append({"label": "Debt/Equity < 1x (Low leverage)", "pass_": passed,
                        "note": f"D/E = {float(de)/100:.2f}x"})
    else:
        checks.append({"label": "Debt/Equity < 1x (Low leverage)", "pass_": False, "note": "Data unavailable"})

    # 3. ROE > 15%
    roe = safe(info, "returnOnEquity")
    if roe != "N/A":
        passed = float(roe) > 0.15
        checks.append({"label": "ROE > 15% (Quality business)", "pass_": passed,
                        "note": f"ROE = {float(roe)*100:.1f}%"})
    else:
        checks.append({"label": "ROE > 15% (Quality business)", "pass_": False, "note": "Data unavailable"})

    # 4. Positive Free Cash Flow
    fcf = safe(info, "freeCashflow")
    if fcf != "N/A":
        passed = float(fcf) > 0
        checks.append({"label": "Positive Free Cash Flow", "pass_": passed,
                        "note": fmt_cr(fcf)})
    else:
        checks.append({"label": "Positive Free Cash Flow", "pass_": False, "note": "Data unavailable"})

    # 5. Price above 200 DMA
    if not hist.empty and len(hist) >= 200:
        dma200 = hist["Close"].rolling(200).mean().iloc[-1]
        price  = hist["Close"].iloc[-1]
        passed = price > dma200
        pct_diff = (price - dma200) / dma200 * 100
        checks.append({"label": "Price above 200-DMA (Uptrend)", "pass_": passed,
                        "note": f"{pct_diff:+.1f}% from 200 DMA"})
    else:
        checks.append({"label": "Price above 200-DMA (Uptrend)", "pass_": False, "note": "Insufficient history"})

    # 6. Revenue Growth positive
    rg = safe(info, "revenueGrowth")
    if rg != "N/A":
        passed = float(rg) > 0
        checks.append({"label": "Positive Revenue Growth", "pass_": passed,
                        "note": f"Growth = {float(rg)*100:.1f}%"})
    else:
        checks.append({"label": "Positive Revenue Growth", "pass_": False, "note": "Data unavailable"})

    # 7. Profit Margins > 10%
    pm = safe(info, "profitMargins")
    if pm != "N/A":
        passed = float(pm) > 0.10
        checks.append({"label": "Net Profit Margin > 10%", "pass_": passed,
                        "note": f"Margin = {float(pm)*100:.1f}%"})
    else:
        checks.append({"label": "Net Profit Margin > 10%", "pass_": False, "note": "Data unavailable"})

    # 8. Current Ratio > 1.5 (Liquidity)
    cr = safe(info, "currentRatio")
    if cr != "N/A":
        passed = float(cr) > 1.5
        checks.append({"label": "Current Ratio > 1.5 (Liquid)", "pass_": passed,
                        "note": f"Current Ratio = {float(cr):.2f}"})
    else:
        checks.append({"label": "Current Ratio > 1.5 (Liquid)", "pass_": False, "note": "Data unavailable"})

    # 9. Promoter holding proxy (insiders > 10%)
    insider = safe(info, "heldPercentInsiders")
    if insider != "N/A":
        passed = float(insider) > 0.10
        checks.append({"label": "Insider Holding > 10%", "pass_": passed,
                        "note": f"Insiders = {float(insider)*100:.1f}%"})
    else:
        checks.append({"label": "Insider Holding > 10%", "pass_": False, "note": "Data unavailable"})

    # 10. Volume Spike (50-day avg volume > 100k)
    avg_vol = safe(info, "averageVolume")
    if avg_vol != "N/A":
        passed = float(avg_vol) > 100000
        checks.append({"label": "Avg Volume > 1 Lakh (Liquid stock)", "pass_": passed,
                        "note": f"Avg Vol = {float(avg_vol):,.0f}"})
    else:
        checks.append({"label": "Avg Volume > 1 Lakh (Liquid stock)", "pass_": False, "note": "Data unavailable"})

    score = sum(1 for c in checks if c["pass_"])
    return score, checks


# ─────────────────────────────────────────────
# TECHNICAL ANALYSIS HELPERS
# ─────────────────────────────────────────────
def compute_technicals(hist: pd.DataFrame, info: dict) -> dict:
    if hist.empty:
        return {}
    tech = {}
    close = hist["Close"]
    volume = hist["Volume"]

    # Moving Averages
    tech["dma50"]  = close.rolling(50).mean().iloc[-1]  if len(close) >= 50  else None
    tech["dma200"] = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else None
    tech["price"]  = close.iloc[-1]

    if tech["dma200"]:
        tech["pct_from_200"] = (tech["price"] - tech["dma200"]) / tech["dma200"] * 100
    else:
        tech["pct_from_200"] = None

    if tech["dma50"]:
        tech["pct_from_50"] = (tech["price"] - tech["dma50"]) / tech["dma50"] * 100
    else:
        tech["pct_from_50"] = None

    # RSI (14-day)
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, float("nan"))
    rsi   = 100 - (100 / (1 + rs))
    tech["rsi"] = rsi.iloc[-1] if not rsi.empty else None

    # 52-week high/low
    tech["high52"] = close.rolling(252).max().iloc[-1] if len(close) >= 252 else close.max()
    tech["low52"]  = close.rolling(252).min().iloc[-1] if len(close) >= 252 else close.min()

    # Avg volume last 10 days vs last 30 days
    tech["vol10"]  = volume.iloc[-10:].mean() if len(volume) >= 10 else volume.mean()
    tech["vol30"]  = volume.iloc[-30:].mean() if len(volume) >= 30 else volume.mean()

    return tech


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
init_db()

with st.sidebar:
    st.markdown("""
    <div style='padding:0.5rem 0 1rem'>
        <div style='font-size:1.3rem;font-weight:700;color:#111928;'>📊 Stock Analyser</div>
        <div style='font-size:0.78rem;color:#6b7280;'>Money Financial Services</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### 🔍 Watchlist")
    new_ticker = st.text_input("Add Ticker", placeholder="e.g. RELIANCE.NS, TCS.NS, INFY")
    
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

    if st.button("➕ Add to Watchlist", use_container_width=True):
        t = new_ticker.strip().upper()
        if t and t not in st.session_state.watchlist:
            st.session_state.watchlist.append(t)

    # Display watchlist
    st.markdown("---")
    st.markdown("**Your Watchlist**")
    for i, ticker in enumerate(st.session_state.watchlist):
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.markdown(f"<div style='font-size:0.88rem;padding:0.2rem 0;'>📌 {ticker}</div>", unsafe_allow_html=True)
        with col_b:
            if st.button("✕", key=f"del_{i}", help=f"Remove {ticker}"):
                st.session_state.watchlist.pop(i)
                st.rerun()

    st.markdown("---")
    selected = st.selectbox("📈 Analyse Stock", options=st.session_state.watchlist)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem;color:#9ca3af;line-height:1.6;'>
    💡 <b>Tips for Indian Stocks:</b><br>
    • NSE: Add <code>.NS</code> suffix<br>
    • BSE: Add <code>.BO</code> suffix<br>
    • Example: <code>WIPRO.NS</code>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────
if not selected:
    st.info("Add at least one ticker to your watchlist to begin analysis.")
    st.stop()

# Fetch data
with st.spinner(f"Fetching data for **{selected}**…"):
    info, hist = fetch_stock(selected)
if not info or not info.get("regularMarketPrice") and hist.empty:
    st.error(f"❌ Could not fetch data for **{selected}**. Check the ticker symbol and try again.")
    st.stop()

# ── Header ──────────────────────────────────────────────────────
company  = safe(info, "longName", selected)
sector   = safe(info, "sector", "—")
industry = safe(info, "industry", "—")
exchange = safe(info, "exchange", "—")
currency = safe(info, "currency", "INR")
price    = safe(info, "regularMarketPrice")
prev_close = safe(info, "regularMarketPreviousClose")

if price != "N/A" and prev_close != "N/A":
    change    = float(price) - float(prev_close)
    change_pct = change / float(prev_close) * 100
    chg_str   = f"{'▲' if change>=0 else '▼'} {abs(change):.2f} ({change_pct:+.2f}%)"
    chg_color = "#0e9f6e" if change >= 0 else "#e02424"
else:
    chg_str, chg_color = "—", "#6b7280"

st.markdown(f"""
<div style='background:#fff;border:1px solid #e4e6eb;border-radius:12px;padding:1.25rem 1.5rem;
            box-shadow:0 2px 12px rgba(0,0,0,0.07);margin-bottom:1rem;display:flex;
            justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;'>
  <div>
    <div style='font-size:1.5rem;font-weight:700;color:#111928;'>{company}</div>
    <div style='font-size:0.82rem;color:#6b7280;margin-top:0.15rem;'>
      <span style='background:#dbeafe;color:#1e40af;border-radius:4px;padding:0.1rem 0.45rem;
                   font-weight:600;font-size:0.75rem;'>{exchange}</span>
      &nbsp;{sector} &nbsp;·&nbsp; {industry}
    </div>
  </div>
  <div style='text-align:right;'>
    <div style='font-size:2rem;font-weight:700;color:#111928;'>
      {currency} {float(price):,.2f if price != "N/A" else "—"}
    </div>
    <div style='font-size:0.9rem;font-weight:600;color:{chg_color};'>{chg_str}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Fundamentals",
    "📡 Technicals",
    "✅ Decision Checklist",
    "🔬 My Research",
    "📚 All Notes"
])


# ═══════════════════════════════════════════════════════════════
# TAB 1 – FUNDAMENTALS
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("<div class='section-header'>Valuation</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    pe  = safe(info, "trailingPE")
    fpe = safe(info, "forwardPE")
    pb  = safe(info, "priceToBook")
    ps  = safe(info, "priceToSalesTrailing12Months")

    with c1:
        v = fmt_num(pe, 1)
        color = "#0e9f6e" if pe != "N/A" and float(pe) < 25 else ("#ff5a1f" if pe != "N/A" and float(pe) < 50 else "#e02424")
        st.markdown(f"""<div class='card'>
            <div class='card-title'>Trailing PE</div>
            <div class='card-value' style='color:{color};'>{v}</div>
            <div class='card-sub'>{"✅ Reasonable" if pe != "N/A" and float(pe) < 30 else "⚠️ High" if pe != "N/A" else ""}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='card'>
            <div class='card-title'>Forward PE</div>
            <div class='card-value'>{fmt_num(fpe, 1)}</div>
            <div class='card-sub'>Expected earnings</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='card'>
            <div class='card-title'>Price / Book</div>
            <div class='card-value'>{fmt_num(pb, 2)}</div>
            <div class='card-sub'>{"✅ < 3" if pb != "N/A" and float(pb) < 3 else "⚠️ High"}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class='card'>
            <div class='card-title'>Price / Sales</div>
            <div class='card-value'>{fmt_num(ps, 2)}</div>
            <div class='card-sub'>Revenue multiple</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Profitability</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    roe  = safe(info, "returnOnEquity")
    roa  = safe(info, "returnOnAssets")
    pm   = safe(info, "profitMargins")
    gm   = safe(info, "grossMargins")

    with c1:
        color = "#0e9f6e" if roe != "N/A" and float(roe) > 0.15 else "#e02424"
        st.markdown(f"""<div class='card'>
            <div class='card-title'>ROE</div>
            <div class='card-value' style='color:{color};'>{fmt_pct(roe)}</div>
            <div class='card-sub'>{"✅ > 15%" if roe != "N/A" and float(roe) > 0.15 else "⚠️ Below 15%"}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='card'>
            <div class='card-title'>ROA</div>
            <div class='card-value'>{fmt_pct(roa)}</div>
            <div class='card-sub'>Asset efficiency</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        color = "#0e9f6e" if pm != "N/A" and float(pm) > 0.10 else "#e02424"
        st.markdown(f"""<div class='card'>
            <div class='card-title'>Net Profit Margin</div>
            <div class='card-value' style='color:{color};'>{fmt_pct(pm)}</div>
            <div class='card-sub'>{"✅ > 10%" if pm != "N/A" and float(pm) > 0.10 else "⚠️ Low"}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class='card'>
            <div class='card-title'>Gross Margin</div>
            <div class='card-value'>{fmt_pct(gm)}</div>
            <div class='card-sub'>Revenue efficiency</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Balance Sheet & Cash Flow</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    de    = safe(info, "debtToEquity")
    cr    = safe(info, "currentRatio")
    fcf   = safe(info, "freeCashflow")
    mc    = safe(info, "marketCap")

    with c1:
        de_ratio = float(de)/100 if de != "N/A" else None
        color = "#0e9f6e" if de_ratio and de_ratio < 1 else "#e02424"
        st.markdown(f"""<div class='card'>
            <div class='card-title'>Debt / Equity</div>
            <div class='card-value' style='color:{color};'>{f"{de_ratio:.2f}x" if de_ratio is not None else "N/A"}</div>
            <div class='card-sub'>{"✅ Low debt" if de_ratio and de_ratio < 1 else "⚠️ High debt"}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        color = "#0e9f6e" if cr != "N/A" and float(cr) > 1.5 else "#ff5a1f"
        st.markdown(f"""<div class='card'>
            <div class='card-title'>Current Ratio</div>
            <div class='card-value' style='color:{color};'>{fmt_num(cr, 2)}</div>
            <div class='card-sub'>{"✅ Liquid" if cr != "N/A" and float(cr) > 1.5 else "⚠️ Watch liquidity"}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        color = "#0e9f6e" if fcf != "N/A" and float(fcf) > 0 else "#e02424"
        st.markdown(f"""<div class='card'>
            <div class='card-title'>Free Cash Flow</div>
            <div class='card-value' style='color:{color};font-size:1.2rem;'>{fmt_cr(fcf)}</div>
            <div class='card-sub'>{"✅ Positive FCF" if fcf != "N/A" and float(fcf) > 0 else "⚠️ Negative FCF"}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class='card'>
            <div class='card-title'>Market Cap</div>
            <div class='card-value' style='font-size:1.2rem;'>{fmt_cr(mc)}</div>
            <div class='card-sub'>Total valuation</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Growth Indicators</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    rg   = safe(info, "revenueGrowth")
    eg   = safe(info, "earningsGrowth")
    eps  = safe(info, "trailingEps")
    beta = safe(info, "beta")

    with c1:
        color = "#0e9f6e" if rg != "N/A" and float(rg) > 0 else "#e02424"
        st.markdown(f"""<div class='card'>
            <div class='card-title'>Revenue Growth (YoY)</div>
            <div class='card-value' style='color:{color};'>{fmt_pct(rg)}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        color = "#0e9f6e" if eg != "N/A" and float(eg) > 0 else "#e02424"
        st.markdown(f"""<div class='card'>
            <div class='card-title'>Earnings Growth (YoY)</div>
            <div class='card-value' style='color:{color};'>{fmt_pct(eg)}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='card'>
            <div class='card-title'>Trailing EPS</div>
            <div class='card-value'>{fmt_num(eps, 2)}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        b_color = "#0e9f6e" if beta != "N/A" and float(beta) < 1 else "#ff5a1f"
        st.markdown(f"""<div class='card'>
            <div class='card-title'>Beta (Risk)</div>
            <div class='card-value' style='color:{b_color};'>{fmt_num(beta, 2)}</div>
            <div class='card-sub'>{"✅ Less volatile" if beta != "N/A" and float(beta) < 1 else "⚠️ More volatile" if beta != "N/A" else ""}</div>
        </div>""", unsafe_allow_html=True)

    # Business Description
    desc = safe(info, "longBusinessSummary", "")
    if desc and desc != "N/A":
        with st.expander("📖 About the Company"):
            st.markdown(f"<div style='font-size:0.88rem;line-height:1.75;color:#374151;'>{desc[:1200]}{'…' if len(desc)>1200 else ''}</div>",
                        unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB 2 – TECHNICALS (Anti-Trap)
# ═══════════════════════════════════════════════════════════════
with tab2:
    tech = compute_technicals(hist, info)
    
    if not tech:
        st.warning("Historical price data not available for this ticker.")
    else:
        st.markdown("<div class='section-header'>Price & Moving Averages</div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.markdown(f"""<div class='card'>
                <div class='card-title'>Current Price</div>
                <div class='card-value'>₹ {tech['price']:.2f}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            dma50_str = f"₹{tech['dma50']:.2f}" if tech['dma50'] else "N/A"
            pct50 = tech.get("pct_from_50")
            color50 = "#0e9f6e" if pct50 and pct50 > 0 else "#e02424"
            st.markdown(f"""<div class='card'>
                <div class='card-title'>50-Day DMA</div>
                <div class='card-value'>{dma50_str}</div>
                <div class='card-sub' style='color:{color50};font-weight:600;'>{f"{pct50:+.1f}% from price" if pct50 else ""}</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            dma200_str = f"₹{tech['dma200']:.2f}" if tech['dma200'] else "N/A"
            pct200 = tech.get("pct_from_200")
            color200 = "#0e9f6e" if pct200 and pct200 > 0 else "#e02424"
            st.markdown(f"""<div class='card'>
                <div class='card-title'>200-Day DMA</div>
                <div class='card-value'>{dma200_str}</div>
                <div class='card-sub' style='color:{color200};font-weight:600;'>{f"{pct200:+.1f}% from price" if pct200 else ""}</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            rsi = tech.get("rsi")
            if rsi:
                rsi_label = "Overbought ⚠️" if rsi > 70 else ("Oversold 🔎" if rsi < 30 else "Neutral ✅")
                rsi_color = "#e02424" if rsi > 70 else ("#ff5a1f" if rsi < 30 else "#0e9f6e")
            else:
                rsi_label, rsi_color = "N/A", "#6b7280"
            st.markdown(f"""<div class='card'>
                <div class='card-title'>RSI (14-day)</div>
                <div class='card-value' style='color:{rsi_color};'>{f"{rsi:.1f}" if rsi else "N/A"}</div>
                <div class='card-sub'>{rsi_label}</div>
            </div>""", unsafe_allow_html=True)

        # 200 DMA visual bar
        if tech["dma200"] and tech["price"]:
            st.markdown("<div class='section-header'>Distance from 200-DMA (Anti-Trap Signal)</div>", unsafe_allow_html=True)
            pct200 = tech["pct_from_200"]
            
            # Clamp between -50 and +50 for visualization
            clamped = max(-50, min(50, pct200))
            fill_pct = (clamped + 50) / 100 * 100   # 0-100 range
            fill_color = "#0e9f6e" if pct200 >= 0 else "#e02424"
            
            if pct200 > 20:
                trap_msg = "⚠️ <b>Overextended above 200 DMA</b> – Risk of pullback. Avoid chasing."
                msg_class = "warn-box"
            elif pct200 > 0:
                trap_msg = "✅ <b>Healthy uptrend</b> – Price is above 200 DMA. Good sign for positional entry."
                msg_class = "success-box"
            elif pct200 > -15:
                trap_msg = "🔎 <b>Near or below 200 DMA</b> – Borderline. Wait for recovery confirmation."
                msg_class = "warn-box"
            else:
                trap_msg = "🚨 <b>Far below 200 DMA</b> – Downtrend. Avoid unless deep value play with margin of safety."
                msg_class = "danger-box"

            st.markdown(f"""
            <div class='card'>
              <div style='display:flex;justify-content:space-between;margin-bottom:0.5rem;'>
                <span style='font-size:0.82rem;color:#6b7280;'>−50%</span>
                <span style='font-size:0.95rem;font-weight:700;color:{fill_color};'>{pct200:+.1f}% from 200 DMA</span>
                <span style='font-size:0.82rem;color:#6b7280;'>+50%</span>
              </div>
              <div class='prog-wrap'>
                <div class='prog-fill' style='width:{fill_pct}%;background:{fill_color};'></div>
              </div>
              <div style='text-align:center;font-size:0.75rem;color:#6b7280;margin-top:0.3rem;'>
                ← Below 200 DMA &nbsp;|&nbsp; Above 200 DMA →
              </div>
            </div>
            <div class='{msg_class}'>{trap_msg}</div>
            """, unsafe_allow_html=True)

        # 52-Week Range
        st.markdown("<div class='section-header'>52-Week Range</div>", unsafe_allow_html=True)
        h52 = tech.get("high52")
        l52 = tech.get("low52")
        cp  = tech["price"]
        
        if h52 and l52 and h52 != l52:
            pos_pct = (cp - l52) / (h52 - l52) * 100
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"""
                <div class='card'>
                  <div style='display:flex;justify-content:space-between;margin-bottom:0.4rem;'>
                    <span style='font-size:0.82rem;color:#6b7280;'>52W Low: ₹{l52:.1f}</span>
                    <span style='font-size:0.82rem;font-weight:600;'>📍 ₹{cp:.1f} ({pos_pct:.0f}%ile)</span>
                    <span style='font-size:0.82rem;color:#6b7280;'>52W High: ₹{h52:.1f}</span>
                  </div>
                  <div class='prog-wrap'>
                    <div class='prog-fill' style='width:{pos_pct:.1f}%;background:linear-gradient(90deg,#ef4444,#f59e0b,#10b981);'></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                pct_from_high = (cp - h52) / h52 * 100
                st.markdown(f"""<div class='card'>
                    <div class='card-title'>From 52W High</div>
                    <div class='card-value' style='color:{"#0e9f6e" if pct_from_high > -5 else "#e02424"};'>{pct_from_high:+.1f}%</div>
                </div>""", unsafe_allow_html=True)

        # Volume Analysis
        st.markdown("<div class='section-header'>Volume Analysis (Delivery vs Avg)</div>", unsafe_allow_html=True)
        vol10 = tech.get("vol10")
        vol30 = tech.get("vol30")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class='card'>
                <div class='card-title'>10-Day Avg Volume</div>
                <div class='card-value' style='font-size:1.2rem;'>{f"{vol10:,.0f}" if vol10 else "N/A"}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class='card'>
                <div class='card-title'>30-Day Avg Volume</div>
                <div class='card-value' style='font-size:1.2rem;'>{f"{vol30:,.0f}" if vol30 else "N/A"}</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            if vol10 and vol30 and vol30 > 0:
                vol_ratio = vol10 / vol30
                color_v = "#0e9f6e" if vol_ratio > 1.2 else ("#ff5a1f" if vol_ratio < 0.8 else "#111928")
                vlabel = "📈 Volume Spike" if vol_ratio > 1.2 else ("📉 Volume Dry" if vol_ratio < 0.8 else "➡️ Normal")
            else:
                vol_ratio, color_v, vlabel = None, "#6b7280", "N/A"
            st.markdown(f"""<div class='card'>
                <div class='card-title'>10D vs 30D Volume</div>
                <div class='card-value' style='color:{color_v};font-size:1.2rem;'>{f"{vol_ratio:.2f}x" if vol_ratio else "N/A"}</div>
                <div class='card-sub'>{vlabel}</div>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("""<div class='info-box'>
        ℹ️ <b>Delivery % Note:</b> Precise BSE/NSE delivery % data requires a broker API (Zerodha, Upstox).
        yfinance provides volume data which is used here as a proxy. 
        High volume + rising price = strong confirmation. High volume + falling price = distribution trap.
        </div>""", unsafe_allow_html=True)

        # Price Chart (1 year)
        st.markdown("<div class='section-header'>1-Year Price History</div>", unsafe_allow_html=True)
        if not hist.empty:
            chart_df = hist[["Close"]].copy()
            if tech["dma50"]:
                chart_df["50 DMA"] = hist["Close"].rolling(50).mean()
            if tech["dma200"]:
                chart_df["200 DMA"] = hist["Close"].rolling(200).mean()
            st.line_chart(chart_df, use_container_width=True, height=300)


# ═══════════════════════════════════════════════════════════════
# TAB 3 – DECISION CHECKLIST & SCORE
# ═══════════════════════════════════════════════════════════════
with tab3:
    score, checks = compute_score(info, hist)
    max_score = len(checks)
    score_pct = int(score / max_score * 100)
    
    if score_pct >= 70:
        grade, badge_cls, verdict_icon, verdict_text = "Strong Buy Zone", "badge-green", "🟢", \
            "Fundamentals are solid. Stock passes majority of quality filters."
    elif score_pct >= 50:
        grade, badge_cls, verdict_icon, verdict_text = "Watchlist / Wait", "badge-yellow", "🟡", \
            "Mixed signals. Some concerns exist. Wait for improvement or buy with smaller position."
    else:
        grade, badge_cls, verdict_icon, verdict_text = "Avoid / High Risk", "badge-red", "🔴", \
            "Multiple red flags detected. High risk of capital loss. Avoid blind entry."

    # Score display
    col_score, col_detail = st.columns([1, 2])
    with col_score:
        st.markdown(f"""
        <div class='card' style='text-align:center;padding:2rem 1rem;'>
          <div style='font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;
                      color:#6b7280;margin-bottom:0.5rem;'>DECISION SCORE</div>
          <div style='font-size:4rem;font-weight:800;
                      color:{"#0e9f6e" if score_pct>=70 else "#f59e0b" if score_pct>=50 else "#e02424"};
                      line-height:1;'>{score}/{max_score}</div>
          <div style='font-size:0.9rem;color:#6b7280;margin:0.3rem 0 1rem;'>{score_pct}% pass rate</div>
          <div class='prog-wrap'>
            <div class='prog-fill' style='width:{score_pct}%;
              background:{"#0e9f6e" if score_pct>=70 else "#f59e0b" if score_pct>=50 else "#e02424"};'></div>
          </div>
          <div style='margin-top:1rem;'>
            <span class='badge {badge_cls}' style='font-size:0.88rem;padding:0.35rem 1rem;'>{verdict_icon} {grade}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_detail:
        st.markdown(f"""<div class='{"success-box" if score_pct>=70 else "warn-box" if score_pct>=50 else "danger-box"}'>
        <b>{verdict_icon} Verdict:</b> {verdict_text}
        </div>""", unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-header' style='margin-top:0;'>Quality Checklist</div>", unsafe_allow_html=True)
        
        for chk in checks:
            icon = "✅" if chk["pass_"] else "❌"
            color = "#065f46" if chk["pass_"] else "#991b1b"
            bg    = "#f0fdf4" if chk["pass_"] else "#fff1f2"
            st.markdown(f"""
            <div class='check-row' style='background:{bg};border-radius:6px;padding:0.5rem 0.75rem;margin-bottom:0.3rem;border:none;'>
              <span class='check-icon'>{icon}</span>
              <div style='flex:1;'>
                <div style='font-size:0.88rem;font-weight:500;color:{color};'>{chk["label"]}</div>
                <div style='font-size:0.78rem;color:#6b7280;'>{chk["note"]}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # Sector context placeholder
    st.markdown("<div class='section-header'>Sector Trend Context</div>", unsafe_allow_html=True)
    sector_tips = {
        "Technology":      ("IT exports, Rupee vs USD, deal wins", "Infosys, TCS guidance = sector barometer"),
        "Financial Services":("RBI rate policy, NPA trends, credit growth", "Track banking index (Bank Nifty)"),
        "Energy":          ("Crude oil price, refining margins, Govt policy", "OPEC decisions = sector trigger"),
        "Consumer Cyclical":("Urban consumption, festive demand, inflation", "GST collections = proxy"),
        "Healthcare":      ("USFDA approvals, domestic market growth", "Watch generic drug pricing in USA"),
        "Industrials":     ("Capex cycle, infra spending, order books", "Govt budget allocation = key trigger"),
        "Real Estate":     ("Home loan rates, inventory, launches", "RBI repo rate = direct impact"),
        "Utilities":       ("Power demand, tariff revision, fuel cost", "Monsoon affects hydro power stocks"),
        "Basic Materials": ("Commodity prices, China demand, Dollar index", "LME metals = leading indicator"),
        "Consumer Defensive":("Steady demand, rural income, FMCG volumes", "FMCG = defensive in downturn"),
    }
    s_info = sector_tips.get(sector, ("Track sector-specific macro indicators", "Compare with sector index performance"))
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class='card'>
          <div class='card-title'>Key Sector Triggers – {sector}</div>
          <div style='font-size:0.9rem;margin-top:0.4rem;'>📌 {s_info[0]}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='card'>
          <div class='card-title'>Advisor Tip</div>
          <div style='font-size:0.9rem;margin-top:0.4rem;'>💡 {s_info[1]}</div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB 4 – MY RESEARCH (NotebookLM-style)
# ═══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("<div class='section-header'>Personal Research & Insights</div>", unsafe_allow_html=True)
    st.markdown(f"""<div class='info-box'>
    ✍️ Save your personal research, thesis, risk factors, and notes for <b>{selected}</b>.
    All notes are stored locally in SQLite database.
    </div>""", unsafe_allow_html=True)
    
    existing_note, last_updated = load_note(selected)

    # Template prompts
    st.markdown("**Quick Template** – Fill what's relevant:")
    template = f"""📌 STOCK: {selected}
📅 Date of Analysis: {datetime.date.today()}

🎯 WHY AM I INTERESTED?
(Your thesis / entry reason)

📊 KEY NUMBERS I NOTED:
- PE: 
- Debt/Equity: 
- ROE: 
- FCF: 

⚠️ RISKS I SEE:
1. 
2. 

💡 SECTOR INSIGHT:
(What's happening in {sector}?)

🎯 MY ENTRY PLAN:
- Target Entry Price: ₹
- Stop Loss: ₹
- Target: ₹
- Time Horizon:

📰 NEWS / TRIGGERS:
- 

✅ CONCLUSION:
(Buy / Watch / Avoid and why)
"""
    use_template = st.button("📋 Load Template", key="template_btn")

    default_text = template if use_template and not existing_note else existing_note
    
    note_content = st.text_area(
        label="Your Research Notes",
        value=default_text,
        height=450,
        placeholder="Type your research, price targets, risks, news triggers…",
        key=f"note_{selected}"
    )
    
    c1, c2 = st.columns([2, 1])
    with c1:
        if st.button("💾 Save Research Note", use_container_width=True, type="primary"):
            if note_content.strip():
                save_note(selected, note_content)
                st.success(f"✅ Research note saved for **{selected}**!")
            else:
                st.warning("Note is empty. Nothing to save.")
    with c2:
        if last_updated:
            st.markdown(f"<div style='font-size:0.8rem;color:#6b7280;padding-top:0.6rem;'>Last saved: {last_updated}</div>",
                        unsafe_allow_html=True)

    # NotebookLM export tip
    st.markdown("""<div class='info-box' style='margin-top:1rem;'>
    🔗 <b>NotebookLM Tip:</b> Copy your notes above → Paste into Google NotebookLM → 
    Use AI to ask questions like "What are the risks in my analysis?" or 
    "Compare my thesis with general sector outlook."
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# TAB 5 – ALL NOTES
# ═══════════════════════════════════════════════════════════════
with tab5:
    st.markdown("<div class='section-header'>All Saved Research Notes</div>", unsafe_allow_html=True)
    all_notes = load_all_notes()
    
    if not all_notes:
        st.markdown("<div class='info-box'>No research notes saved yet. Analyse a stock and save your notes in the 'My Research' tab.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size:0.85rem;color:#6b7280;margin-bottom:1rem;'>Total notes saved: <b>{len(all_notes)}</b></div>", unsafe_allow_html=True)
        for ticker_n, content_n, updated_n in all_notes:
            with st.expander(f"📌 {ticker_n}  —  Last updated: {updated_n}"):
                st.text_area(
                    label="",
                    value=content_n,
                    height=200,
                    disabled=True,
                    key=f"view_{ticker_n}"
                )
                if st.button(f"🗑️ Delete Note – {ticker_n}", key=f"del_note_{ticker_n}"):
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("DELETE FROM notes WHERE ticker=?", (ticker_n,))
                    conn.commit()
                    conn.close()
                    st.rerun()

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;font-size:0.78rem;color:#9ca3af;padding:0.5rem 0 1rem;'>
  📊 <b>Stock Analysis Dashboard</b> · Money Financial Services · 
  Data via <a href='https://finance.yahoo.com' target='_blank' style='color:#6b7280;'>Yahoo Finance</a> · 
  For educational purposes only. Not SEBI registered investment advice. · 
  Refresh data every 5 min (cached)
</div>
""", unsafe_allow_html=True)
