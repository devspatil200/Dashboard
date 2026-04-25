"""
Stock Analysis Pro — v5.0
Author : Money Financial Services
Structure: 3-Page Navigation — Discovery · Watchlist · Deep Analysis
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
import datetime
import math

# ── PAGE CONFIG ─────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Analysis Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBAL CSS ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: #ffffff !important;
}
.stApp { background: #ffffff !important; }

/* Fix top padding on mobile & web */
.stApp > div:first-child { padding-top: 0 !important; }
.block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 3rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 1400px !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #fafafa !important;
    border-right: 1px solid #e4e4e7 !important;
    min-width: 220px !important;
}
[data-testid="stSidebar"] * { font-family: 'Inter', sans-serif !important; }

/* Radio buttons in sidebar */
[data-testid="stSidebar"] [role="radiogroup"] label {
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 0.75rem !important;
    border-radius: 6px !important;
    margin-bottom: 2px !important;
    display: block !important;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: #f0f0f0 !important;
}

/* Buttons */
[data-testid="stButton"] > button {
    border-radius: 7px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    transition: all 0.15s !important;
}

/* Text input */
[data-testid="stTextInput"] input {
    border-radius: 7px !important;
    font-family: 'Inter', monospace !important;
    font-size: 0.9rem !important;
    border: 1px solid #d1d5db !important;
    padding: 0.45rem 0.75rem !important;
}

/* Tabs */
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
}

/* Metric */
[data-testid="stMetric"] {
    background: #fafafa;
    border: 1px solid #e4e4e7;
    border-radius: 8px;
    padding: 0.75rem 1rem !important;
}
[data-testid="stMetric"] label {
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: #71717a !important;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 8px !important; }

/* Divider */
hr { border-color: #e4e4e7 !important; margin: 1rem 0 !important; }

/* Alert */
div[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 0.84rem !important;
    font-family: 'Inter', sans-serif !important;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid #e4e4e7 !important;
    border-radius: 8px !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div {
    border-radius: 7px !important;
    font-size: 0.85rem !important;
}

/* Caption */
.stCaption { color: #71717a !important; font-size: 0.75rem !important; }

/* Hide Streamlit default top header */
.stApp > header { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════
DB = "stock_v5.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS watchlist (
        ticker TEXT PRIMARY KEY,
        added_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS notes (
        ticker TEXT PRIMARY KEY,
        content TEXT,
        updated_at TEXT
    )""")
    conn.commit()
    conn.close()

def db_get_watchlist():
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT ticker FROM watchlist ORDER BY added_at DESC"
    ).fetchall()
    conn.close()
    return [r[0] for r in rows]

def db_add_ticker(ticker):
    conn = sqlite3.connect(DB)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute(
        "INSERT OR IGNORE INTO watchlist (ticker, added_at) VALUES (?,?)",
        (ticker.upper().strip(), now))
    conn.commit()
    conn.close()

def db_del_ticker(ticker):
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM watchlist WHERE ticker=?", (ticker,))
    conn.commit()
    conn.close()

def db_save_note(ticker, content):
    conn = sqlite3.connect(DB)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute("INSERT OR REPLACE INTO notes VALUES (?,?,?)",
                 (ticker.upper(), content, now))
    conn.commit()
    conn.close()

def db_load_note(ticker):
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT content, updated_at FROM notes WHERE ticker=?",
        (ticker.upper(),)).fetchall()
    conn.close()
    return (rows[0][0], rows[0][1]) if rows else ("", "")

# ═══════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════
init_db()

if "watchlist" not in st.session_state:
    st.session_state.watchlist = db_get_watchlist()

if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = None

if "page" not in st.session_state:
    st.session_state.page = "🔍 Stock Discovery"

if "search_result" not in st.session_state:
    st.session_state.search_result = None

# ═══════════════════════════════════════════════════════════
# DATA HELPERS
# ═══════════════════════════════════════════════════════════
@st.cache_resource
def _stock_cache():
    return {}

def safe_fetch_info(ticker):
    """Fetch basic info safely — never crashes app."""
    try:
        info = yf.Ticker(ticker).info or {}
        return info
    except Exception:
        return {}

def safe_fetch_hist(ticker, period="1y"):
    """Fetch price history safely."""
    try:
        hist = yf.Ticker(ticker).history(period=period)
        return hist
    except Exception:
        return pd.DataFrame()

def get_price_data(ticker):
    """Quick price + change for watchlist view."""
    cache = _stock_cache()
    key = f"price_{ticker}_{datetime.datetime.now().strftime('%Y%m%d%H')}"
    if key in cache:
        return cache[key]
    try:
        info = safe_fetch_info(ticker)
        price = info.get("regularMarketPrice") or info.get("currentPrice")
        prev  = info.get("regularMarketPreviousClose")
        name  = info.get("shortName") or info.get("longName") or ticker
        chg_pct = ((price - prev) / prev * 100) if price and prev and prev != 0 else None
        result = {"price": price, "prev": prev, "name": name, "chg_pct": chg_pct, "info": info}
    except Exception:
        result = {"price": None, "prev": None, "name": ticker, "chg_pct": None, "info": {}}
    cache[key] = result
    return result

def safe_float(v):
    try:
        if v is None: return None
        f = float(v)
        return None if math.isnan(f) else f
    except Exception:
        return None

def fmt_price(v):
    try: return f"₹{float(v):,.2f}"
    except: return "—"

def fmt_pct(v):
    try: return f"{float(v)*100:.1f}%"
    except: return "—"

def fmt_cr(v):
    try:
        v = float(v)
        if abs(v) >= 1e12: return f"₹{v/1e12:.2f}T"
        if abs(v) >= 1e7:  return f"₹{v/1e7:.2f}Cr"
        if abs(v) >= 1e5:  return f"₹{v/1e5:.2f}L"
        return f"₹{v:,.0f}"
    except: return "—"

def logo_url(website):
    try:
        if not website: return None
        d = website.replace("https://","").replace("http://","").split("/")[0]
        return f"https://logo.clearbit.com/{d}" if d else None
    except: return None

# ═══════════════════════════════════════════════════════════
# TECHNICAL INDICATORS
# ═══════════════════════════════════════════════════════════
def compute_ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def compute_rsi(series, period=14):
    try:
        delta = series.diff()
        gain  = delta.clip(lower=0).rolling(period).mean()
        loss  = (-delta.clip(upper=0)).rolling(period).mean()
        rs    = gain / loss.replace(0, float("nan"))
        return 100 - (100 / (1 + rs))
    except Exception:
        return pd.Series(dtype=float)

def compute_macd(series):
    try:
        e12  = series.ewm(span=12).mean()
        e26  = series.ewm(span=26).mean()
        macd = e12 - e26
        sig  = macd.ewm(span=9).mean()
        return macd, sig
    except Exception:
        return pd.Series(dtype=float), pd.Series(dtype=float)

# ═══════════════════════════════════════════════════════════
# CHARTS
# ═══════════════════════════════════════════════════════════
def build_candlestick(hist, ticker):
    """Full candlestick with EMA20, EMA50, Volume."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        if hist.empty:
            return None

        ema20 = compute_ema(hist["Close"], 20)
        ema50 = compute_ema(hist["Close"], 50)

        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.75, 0.25],
        )

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist["Open"], high=hist["High"],
            low=hist["Low"],  close=hist["Close"],
            name="Price",
            increasing_line_color="#16a34a",
            decreasing_line_color="#dc2626",
            increasing_fillcolor="#16a34a",
            decreasing_fillcolor="#dc2626",
        ), row=1, col=1)

        # EMA 20
        fig.add_trace(go.Scatter(
            x=hist.index, y=ema20,
            name="EMA 20",
            line=dict(color="#2563eb", width=1.5),
        ), row=1, col=1)

        # EMA 50
        fig.add_trace(go.Scatter(
            x=hist.index, y=ema50,
            name="EMA 50",
            line=dict(color="#d97706", width=1.5, dash="dot"),
        ), row=1, col=1)

        # Volume
        vol_colors = [
            "#16a34a" if c >= o else "#dc2626"
            for c, o in zip(hist["Close"], hist["Open"])
        ]
        fig.add_trace(go.Bar(
            x=hist.index, y=hist["Volume"],
            name="Volume",
            marker_color=vol_colors,
            opacity=0.55,
            showlegend=False,
        ), row=2, col=1)

        fig.update_layout(
            height=460,
            margin=dict(l=0, r=0, t=20, b=0),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            template="plotly_white",
            font=dict(family="Inter", size=11, color="#3f3f46"),
            xaxis_rangeslider_visible=False,
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.01,
                xanchor="right",  x=1,
                bgcolor="rgba(0,0,0,0)",
                font=dict(size=10),
            ),
            yaxis=dict(
                showgrid=True, gridcolor="#f4f4f5",
                side="right", zeroline=False,
                tickfont=dict(size=10),
            ),
            yaxis2=dict(
                showgrid=False, side="right",
                zeroline=False, tickfont=dict(size=9),
            ),
            xaxis2=dict(
                showgrid=True, gridcolor="#f4f4f5",
                tickfont=dict(size=10),
            ),
        )
        return fig
    except Exception:
        return None

def build_rsi_chart(hist):
    """RSI chart with overbought/oversold zones."""
    try:
        import plotly.graph_objects as go

        if hist.empty:
            return None

        rsi = compute_rsi(hist["Close"])
        if rsi.empty:
            return None

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist.index, y=rsi,
            name="RSI (14)",
            line=dict(color="#7c3aed", width=2),
            fill="tozeroy",
            fillcolor="rgba(124,58,237,0.06)",
        ))

        # Overbought zone
        fig.add_hrect(y0=70, y1=100,
                      fillcolor="rgba(220,38,38,0.08)",
                      line_width=0, annotation_text="Overbought (>70)",
                      annotation_position="top left",
                      annotation=dict(font_size=10, font_color="#dc2626"))
        # Oversold zone
        fig.add_hrect(y0=0, y1=30,
                      fillcolor="rgba(22,163,74,0.08)",
                      line_width=0, annotation_text="Oversold (<30)",
                      annotation_position="bottom left",
                      annotation=dict(font_size=10, font_color="#16a34a"))

        # Reference lines
        fig.add_hline(y=70, line_dash="dash",
                      line_color="#dc2626", line_width=1, opacity=0.6)
        fig.add_hline(y=30, line_dash="dash",
                      line_color="#16a34a", line_width=1, opacity=0.6)
        fig.add_hline(y=50, line_dash="dot",
                      line_color="#94a3b8", line_width=1, opacity=0.4)

        fig.update_layout(
            height=220,
            margin=dict(l=0, r=0, t=16, b=0),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            template="plotly_white",
            showlegend=False,
            yaxis=dict(
                range=[0, 100], side="right",
                showgrid=True, gridcolor="#f4f4f5",
                tickfont=dict(size=10), zeroline=False,
            ),
            xaxis=dict(
                showgrid=True, gridcolor="#f4f4f5",
                tickfont=dict(size=10),
            ),
            font=dict(family="Inter", size=11),
        )
        return fig
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        "<div style='padding:0.5rem 0 1rem;'>"
        "<div style='font-size:1.05rem;font-weight:800;color:#0f172a;'>📈 Stock Analysis Pro</div>"
        "<div style='font-size:0.7rem;color:#71717a;margin-top:2px;'>Money Financial Services · v5.0</div>"
        "</div>",
        unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🔍 Stock Discovery",
         "📋 My Watchlist",
         "📊 Deep Analysis"],
        index=["🔍 Stock Discovery",
               "📋 My Watchlist",
               "📊 Deep Analysis"].index(st.session_state.page),
        label_visibility="collapsed",
        key="nav_radio",
    )
    if page != st.session_state.page:
        st.session_state.page = page
        st.rerun()

    st.markdown("---")

    # Watchlist count
    wl_count = len(st.session_state.watchlist)
    st.markdown(
        f"<div style='font-size:0.72rem;color:#71717a;margin-bottom:4px;'>"
        f"📌 Watchlist: <b>{wl_count} stocks</b></div>",
        unsafe_allow_html=True)

    # Quick links
    for t in st.session_state.watchlist[:6]:
        if st.button(t, key=f"side_{t}", use_container_width=True):
            st.session_state.selected_stock = t
            st.session_state.page = "📊 Deep Analysis"
            st.rerun()

    if wl_count > 6:
        st.caption(f"+ {wl_count-6} more in Watchlist")

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.68rem;color:#a1a1aa;line-height:1.6;'>"
        "Data: Yahoo Finance<br>"
        "NSE: Add .NS suffix<br>"
        "BSE: Add .BO suffix<br>"
        "e.g. RELIANCE.NS"
        "</div>",
        unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# PAGE 1 — STOCK DISCOVERY
# ═══════════════════════════════════════════════════════════
def page_discovery():
    st.markdown(
        "<h2 style='font-size:1.4rem;font-weight:800;color:#0f172a;margin-bottom:0.25rem;'>"
        "🔍 Stock Discovery</h2>"
        "<p style='font-size:0.84rem;color:#71717a;margin-bottom:1.25rem;'>"
        "Search any stock and add it to your watchlist.</p>",
        unsafe_allow_html=True)

    # ── Search bar ──────────────────────────────────────────
    col_inp, col_btn = st.columns([4, 1])
    with col_inp:
        ticker_input = st.text_input(
            "",
            placeholder="Enter ticker — e.g. RELIANCE.NS, TCS.NS, INFY.NS, AAPL",
            key="disco_input",
            label_visibility="collapsed",
        )
    with col_btn:
        search_btn = st.button("🔍 Search", use_container_width=True, type="primary")

    # Popular suggestions
    st.markdown(
        "<div style='font-size:0.72rem;color:#a1a1aa;margin-bottom:1rem;'>"
        "Popular: "
        "</div>",
        unsafe_allow_html=True)

    pop_stocks = [
        "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
        "SBIN.NS","BAJFINANCE.NS","WIPRO.NS","LT.NS","TITAN.NS",
        "SUNPHARMA.NS","MARUTI.NS","ONGC.NS","NTPC.NS","ADANIPORTS.NS",
    ]
    cols_pop = st.columns(5)
    for i, ps in enumerate(pop_stocks):
        with cols_pop[i % 5]:
            if st.button(ps.replace(".NS",""), key=f"pop_{ps}",
                         use_container_width=True):
                st.session_state.search_result = ps
                st.rerun()

    st.markdown("---")

    # Trigger search
    query = None
    if search_btn and ticker_input.strip():
        query = ticker_input.strip().upper()
        st.session_state.search_result = query

    if not search_btn and st.session_state.search_result:
        query = st.session_state.search_result

    # ── Results ──────────────────────────────────────────────
    if query:
        with st.spinner(f"Fetching data for **{query}**…"):
            info = safe_fetch_info(query)
            hist = safe_fetch_hist(query, "6mo")

        name = info.get("longName") or info.get("shortName") or query
        price = safe_float(info.get("regularMarketPrice") or info.get("currentPrice"))
        prev  = safe_float(info.get("regularMarketPreviousClose"))

        if not price:
            st.error(f"❌ Could not find **{query}**. "
                     "Check ticker symbol. NSE → add .NS  |  BSE → add .BO")
            return

        chg   = price - prev if prev else 0
        chgp  = (chg / prev * 100) if prev and prev != 0 else 0
        chg_c = "#16a34a" if chg >= 0 else "#dc2626"
        arr   = "▲" if chg >= 0 else "▼"
        curr  = info.get("currency", "INR")

        # Stock header card
        lurl = logo_url(info.get("website",""))
        logo_html = (
            f'<img src="{lurl}" width="40" height="40" '
            f'style="border-radius:8px;object-fit:contain;border:1px solid #e4e4e7;'
            f'margin-right:10px;vertical-align:middle;" '
            f'onerror="this.style.display=\'none\'"> '
        ) if lurl else ""

        st.markdown(
            f"<div style='background:#fafafa;border:1px solid #e4e4e7;border-radius:10px;"
            f"padding:1rem 1.25rem;margin-bottom:1rem;display:flex;"
            f"justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.75rem;'>"
            f"<div style='display:flex;align-items:center;'>"
            f"{logo_html}"
            f"<div>"
            f"<div style='font-size:1.15rem;font-weight:800;color:#0f172a;'>{name}</div>"
            f"<div style='font-size:0.75rem;color:#71717a;margin-top:2px;'>"
            f"{query} · {info.get('exchange','—')} · "
            f"{info.get('sector','—')} · {info.get('industry','—')}</div>"
            f"</div></div>"
            f"<div style='text-align:right;'>"
            f"<div style='font-size:1.65rem;font-weight:800;color:#0f172a;"
            f"font-family:JetBrains Mono,monospace;'>{curr} {price:,.2f}</div>"
            f"<div style='font-size:0.85rem;font-weight:600;color:{chg_c};margin-top:2px;'>"
            f"{arr} {abs(chg):,.2f} ({chgp:+.2f}%)</div>"
            f"</div></div>",
            unsafe_allow_html=True)

        # Add to watchlist
        already = query in st.session_state.watchlist
        ca, cb, cc = st.columns([2, 2, 3])
        with ca:
            if already:
                st.success("✅ Already in watchlist")
            else:
                if st.button("➕ Add to My Watchlist", type="primary",
                             use_container_width=True, key="add_wl"):
                    db_add_ticker(query)
                    st.session_state.watchlist = db_get_watchlist()
                    st.success(f"✅ **{query}** added to watchlist!")
                    st.rerun()
        with cb:
            if st.button("📊 View Deep Analysis",
                         use_container_width=True, key="goto_analysis"):
                st.session_state.selected_stock = query
                st.session_state.page = "📊 Deep Analysis"
                st.rerun()
        with cc:
            pass  # spacer

        st.markdown("---")

        # Key metrics
        st.markdown(
            "<div style='font-size:0.82rem;font-weight:700;color:#0f172a;"
            "border-left:2px solid #2563eb;padding-left:8px;margin-bottom:0.75rem;'>"
            "Key Metrics</div>",
            unsafe_allow_html=True)

        m1,m2,m3,m4,m5,m6 = st.columns(6)
        with m1: st.metric("Market Cap", fmt_cr(info.get("marketCap")))
        with m2: st.metric("P/E Ratio",  f"{info.get('trailingPE','—'):.1f}" if safe_float(info.get('trailingPE')) else "—")
        with m3: st.metric("52W High",   fmt_price(info.get("fiftyTwoWeekHigh")))
        with m4: st.metric("52W Low",    fmt_price(info.get("fiftyTwoWeekLow")))
        with m5: st.metric("Volume",     f"{info.get('regularMarketVolume',0):,.0f}" if info.get('regularMarketVolume') else "—")
        with m6: st.metric("Avg Volume", f"{info.get('averageVolume',0):,.0f}"  if info.get('averageVolume')        else "—")

        # Quick chart
        if not hist.empty:
            st.markdown(
                "<div style='font-size:0.82rem;font-weight:700;color:#0f172a;"
                "border-left:2px solid #2563eb;padding-left:8px;margin:1rem 0 0.75rem;'>"
                "6-Month Price Chart</div>",
                unsafe_allow_html=True)
            fig_q = build_candlestick(hist, query)
            if fig_q:
                st.plotly_chart(fig_q, use_container_width=True,
                                config={"displayModeBar": False})

        # Company description
        desc = info.get("longBusinessSummary","")
        if desc:
            with st.expander("📖 About the Company"):
                st.markdown(
                    f"<p style='font-size:0.84rem;line-height:1.8;color:#3f3f46;'>"
                    f"{desc[:1500]}{'…' if len(desc)>1500 else ''}</p>",
                    unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# PAGE 2 — MY WATCHLIST
# ═══════════════════════════════════════════════════════════
def page_watchlist():
    st.markdown(
        "<h2 style='font-size:1.4rem;font-weight:800;color:#0f172a;margin-bottom:0.25rem;'>"
        "📋 My Watchlist</h2>"
        "<p style='font-size:0.84rem;color:#71717a;margin-bottom:1.25rem;'>"
        "Real-time prices and quick access to deep analysis.</p>",
        unsafe_allow_html=True)

    wl = st.session_state.watchlist

    if not wl:
        st.info("📭 Your watchlist is empty. Go to **🔍 Stock Discovery** to add stocks.")
        if st.button("🔍 Go to Stock Discovery", type="primary"):
            st.session_state.page = "🔍 Stock Discovery"
            st.rerun()
        return

    # Refresh button
    ca, cb = st.columns([5,1])
    with cb:
        if st.button("🔄 Refresh", use_container_width=True):
            _stock_cache().clear()
            st.rerun()

    st.markdown("---")

    # Column headers
    hcols = st.columns([0.4, 2.5, 1.5, 1.2, 1.2, 1.2, 1.5, 0.8])
    headers = ["", "Stock", "LTP", "Change", "Mkt Cap", "P/E", "52W H/L", ""]
    for col, hdr in zip(hcols, headers):
        col.markdown(
            f"<div style='font-size:0.62rem;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.07em;color:#a1a1aa;padding-bottom:4px;'>{hdr}</div>",
            unsafe_allow_html=True)

    st.markdown(
        "<hr style='border:none;border-top:2px solid #e4e4e7;margin:0 0 4px;'>",
        unsafe_allow_html=True)

    # Stock rows
    for ticker in wl:
        data = get_price_data(ticker)
        info = data.get("info",{})

        price   = data.get("price")
        chg_pct = data.get("chg_pct")
        name    = data.get("name", ticker)

        # Price display
        p_str = f"₹{price:,.2f}" if price else "—"

        # Change display
        if chg_pct is not None:
            chg_c  = "#16a34a" if chg_pct >= 0 else "#dc2626"
            chg_bg = "#f0fdf4" if chg_pct >= 0 else "#fef2f2"
            arr    = "▲" if chg_pct >= 0 else "▼"
            chg_str = f"{arr} {abs(chg_pct):.2f}%"
        else:
            chg_c = "#71717a"; chg_bg = "#fafafa"; chg_str = "—"

        mktcap = fmt_cr(info.get("marketCap"))
        pe_val = safe_float(info.get("trailingPE"))
        pe_str = f"{pe_val:.1f}" if pe_val else "—"
        h52    = safe_float(info.get("fiftyTwoWeekHigh"))
        l52    = safe_float(info.get("fiftyTwoWeekLow"))
        hl_str = f"₹{h52:,.0f} / ₹{l52:,.0f}" if h52 and l52 else "—"

        lurl = logo_url(info.get("website",""))
        tabbr = ticker.replace(".NS","").replace(".BO","")[:2].upper()

        row_cols = st.columns([0.4, 2.5, 1.5, 1.2, 1.2, 1.2, 1.5, 0.8])

        # Col 0: Logo
        with row_cols[0]:
            if lurl:
                st.markdown(
                    f'<img src="{lurl}" width="26" height="26" '
                    f'style="border-radius:5px;object-fit:contain;border:1px solid #e4e4e7;'
                    f'margin-top:6px;" '
                    f'onerror="this.style.display=\'none\'">',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div style="width:26px;height:26px;border-radius:5px;'
                    f'background:#e4e4e7;display:flex;align-items:center;'
                    f'justify-content:center;font-size:0.6rem;font-weight:700;'
                    f'color:#71717a;margin-top:6px;">{tabbr}</div>',
                    unsafe_allow_html=True)

        # Col 1: Ticker + Name
        with row_cols[1]:
            st.markdown(
                f"<div style='padding-top:4px;'>"
                f"<div style='font-size:0.82rem;font-weight:700;color:#0f172a;"
                f"font-family:JetBrains Mono,monospace;'>"
                f"{ticker.replace('.NS','').replace('.BO','')}</div>"
                f"<div style='font-size:0.68rem;color:#94a3b8;'>{name[:28]}</div>"
                f"</div>",
                unsafe_allow_html=True)

        # Col 2: LTP
        with row_cols[2]:
            st.markdown(
                f"<div style='font-size:0.85rem;font-weight:600;color:#0f172a;"
                f"font-family:JetBrains Mono,monospace;padding-top:6px;'>{p_str}</div>",
                unsafe_allow_html=True)

        # Col 3: % Change
        with row_cols[3]:
            st.markdown(
                f"<div style='padding-top:6px;'>"
                f"<span style='font-size:0.78rem;font-weight:700;color:{chg_c};"
                f"background:{chg_bg};padding:2px 7px;border-radius:4px;'>{chg_str}</span>"
                f"</div>",
                unsafe_allow_html=True)

        # Col 4: Mkt Cap
        with row_cols[4]:
            st.markdown(
                f"<div style='font-size:0.78rem;color:#3f3f46;padding-top:6px;'>{mktcap}</div>",
                unsafe_allow_html=True)

        # Col 5: P/E
        with row_cols[5]:
            st.markdown(
                f"<div style='font-size:0.78rem;color:#3f3f46;padding-top:6px;'>{pe_str}</div>",
                unsafe_allow_html=True)

        # Col 6: 52W H/L
        with row_cols[6]:
            st.markdown(
                f"<div style='font-size:0.72rem;color:#71717a;padding-top:6px;'>{hl_str}</div>",
                unsafe_allow_html=True)

        # Col 7: Actions
        with row_cols[7]:
            ac1, ac2 = st.columns([1,1])
            with ac1:
                if st.button("📊", key=f"view_{ticker}", help=f"View Analysis for {ticker}"):
                    st.session_state.selected_stock = ticker
                    st.session_state.page = "📊 Deep Analysis"
                    st.rerun()
            with ac2:
                if st.button("🗑️", key=f"del_{ticker}", help=f"Remove {ticker}"):
                    db_del_ticker(ticker)
                    st.session_state.watchlist = db_get_watchlist()
                    st.rerun()

        st.markdown(
            "<hr style='border:none;border-top:1px solid #f0f0f0;margin:2px 0;'>",
            unsafe_allow_html=True)

    st.markdown("---")
    st.caption(f"Data via Yahoo Finance · {len(wl)} stocks · Auto-refreshes hourly")

# ═══════════════════════════════════════════════════════════
# PAGE 3 — DEEP ANALYSIS (Trap Detector)
# ═══════════════════════════════════════════════════════════
def page_analysis():
    st.markdown(
        "<h2 style='font-size:1.4rem;font-weight:800;color:#0f172a;margin-bottom:0.25rem;'>"
        "📊 Deep Analysis — Trap Detector</h2>",
        unsafe_allow_html=True)

    # Stock selector
    wl = st.session_state.watchlist
    options = wl if wl else []

    sel = st.session_state.selected_stock
    if sel and sel not in options:
        options = [sel] + options

    if not options:
        st.info("📭 No stocks to analyse. Add stocks in **🔍 Stock Discovery** first.")
        if st.button("🔍 Go to Stock Discovery", type="primary"):
            st.session_state.page = "🔍 Stock Discovery"
            st.rerun()
        return

    ca, cb, cc = st.columns([3, 1, 3])
    with ca:
        sel_ticker = st.selectbox(
            "Select Stock",
            options=options,
            index=options.index(sel) if sel in options else 0,
            key="analysis_sel",
            label_visibility="visible",
        )
    with cb:
        period_map = {"1M":"1mo","3M":"3mo","6M":"6mo","1Y":"1y","2Y":"2y"}
        period_lbl = st.selectbox(
            "Period", list(period_map.keys()), index=3,
            key="period_sel", label_visibility="visible")
    with cc:
        pass

    if sel_ticker != st.session_state.selected_stock:
        st.session_state.selected_stock = sel_ticker
        st.rerun()

    ticker = sel_ticker
    period = period_map[period_lbl]

    # Fetch data
    with st.spinner(f"Loading analysis for **{ticker}**…"):
        info = safe_fetch_info(ticker)
        hist = safe_fetch_hist(ticker, period)

    price = safe_float(info.get("regularMarketPrice") or info.get("currentPrice"))
    prev  = safe_float(info.get("regularMarketPreviousClose"))

    if not price:
        st.error(f"❌ Data unavailable for **{ticker}**. Verify ticker symbol.")
        return

    chg   = price - prev if prev else 0
    chgp  = (chg / prev * 100) if prev and prev != 0 else 0
    chg_c = "#16a34a" if chg >= 0 else "#dc2626"
    arr   = "▲" if chg >= 0 else "▼"
    curr  = info.get("currency","INR")
    name  = info.get("longName") or info.get("shortName") or ticker
    lurl  = logo_url(info.get("website",""))

    # ── Header ──────────────────────────────────────────────
    logo_html = (
        f'<img src="{lurl}" width="36" height="36" '
        f'style="border-radius:7px;object-fit:contain;border:1px solid #e4e4e7;'
        f'margin-right:10px;vertical-align:middle;" '
        f'onerror="this.style.display=\'none\'">'
    ) if lurl else ""

    h1, h2 = st.columns([3,2])
    with h1:
        st.markdown(
            f"{logo_html}"
            f"<span style='font-size:1.2rem;font-weight:800;color:#0f172a;"
            f"vertical-align:middle;'>{name}</span>",
            unsafe_allow_html=True)
        st.caption(f"{ticker} · {info.get('exchange','—')} · "
                   f"{info.get('sector','—')} · {info.get('industry','—')}")
    with h2:
        st.markdown(
            f"<div style='text-align:right;'>"
            f"<div style='font-size:1.65rem;font-weight:800;color:#0f172a;"
            f"font-family:JetBrains Mono,monospace;line-height:1;'>"
            f"{curr} {price:,.2f}</div>"
            f"<div style='font-size:0.85rem;font-weight:600;color:{chg_c};margin-top:3px;'>"
            f"{arr} {abs(chg):,.2f} ({chgp:+.2f}%)</div>"
            f"<div style='font-size:0.68rem;color:#a1a1aa;margin-top:2px;'>"
            f"Mkt Cap: {fmt_cr(info.get('marketCap'))} · "
            f"Beta: {safe_float(info.get('beta')) or '—'}</div>"
            f"</div>",
            unsafe_allow_html=True)

    st.markdown("---")

    # ── RSI Trap Detection ───────────────────────────────────
    rsi_val = None
    if not hist.empty:
        rsi_series = compute_rsi(hist["Close"])
        if not rsi_series.empty:
            rsi_val = safe_float(rsi_series.iloc[-1])

    if rsi_val is not None:
        if rsi_val > 70:
            st.markdown(
                f"<div style='background:linear-gradient(135deg,#fef2f2,#fee2e2);"
                f"border:2px solid #dc2626;border-radius:10px;"
                f"padding:0.9rem 1.1rem;margin-bottom:0.75rem;'>"
                f"<div style='font-size:1rem;font-weight:800;color:#991b1b;'>"
                f"🚨 OVERBOUGHT TRAP DETECTED — RSI: {rsi_val:.1f}</div>"
                f"<div style='font-size:0.82rem;color:#b91c1c;margin-top:4px;line-height:1.6;'>"
                f"RSI above 70 indicates the stock is overbought. "
                f"Risk of reversal or pullback is high. "
                f"<b>Avoid chasing at these levels. Wait for RSI to cool below 60.</b>"
                f"</div></div>",
                unsafe_allow_html=True)
        elif rsi_val < 30:
            st.markdown(
                f"<div style='background:linear-gradient(135deg,#f0fdf4,#dcfce7);"
                f"border:2px solid #16a34a;border-radius:10px;"
                f"padding:0.9rem 1.1rem;margin-bottom:0.75rem;'>"
                f"<div style='font-size:1rem;font-weight:800;color:#15803d;'>"
                f"🔎 OVERSOLD ZONE — RSI: {rsi_val:.1f}</div>"
                f"<div style='font-size:0.82rem;color:#166534;margin-top:4px;line-height:1.6;'>"
                f"RSI below 30 indicates the stock is oversold. "
                f"Potential bounce or reversal opportunity. "
                f"<b>Wait for RSI confirmation above 35 before entering.</b>"
                f"</div></div>",
                unsafe_allow_html=True)
        else:
            st.success(
                f"✅ **RSI: {rsi_val:.1f}** — Neutral zone. "
                f"No extreme overbought/oversold condition detected.")

    # ── Key Metrics ──────────────────────────────────────────
    m1,m2,m3,m4,m5,m6 = st.columns(6)
    with m1: st.metric("P/E", f"{safe_float(info.get('trailingPE')):.1f}" if safe_float(info.get('trailingPE')) else "—")
    with m2: st.metric("ROE", fmt_pct(info.get("returnOnEquity")))
    with m3: st.metric("D/E", f"{safe_float(info.get('debtToEquity'))/100:.2f}x" if safe_float(info.get('debtToEquity')) else "—")
    with m4: st.metric("RSI (14)", f"{rsi_val:.1f}" if rsi_val else "—")
    with m5: st.metric("52W High", fmt_price(info.get("fiftyTwoWeekHigh")))
    with m6: st.metric("52W Low",  fmt_price(info.get("fiftyTwoWeekLow")))

    st.markdown("---")

    # ── Charts ────────────────────────────────────────────────
    if hist.empty:
        st.warning("⚠️ Price history not available for this period.")
    else:
        # Candlestick + EMA + Volume
        st.markdown(
            "<div style='font-size:0.82rem;font-weight:700;color:#0f172a;"
            "border-left:2px solid #2563eb;padding-left:8px;margin-bottom:0.6rem;'>"
            "📈 Candlestick — EMA 20 & 50 — Volume</div>",
            unsafe_allow_html=True)

        fig_c = build_candlestick(hist, ticker)
        if fig_c:
            st.plotly_chart(fig_c, use_container_width=True,
                            config={"displayModeBar": False})
        else:
            st.warning("Chart unavailable.")

        # VPA — Institutional Buying
        if "Volume" in hist.columns and len(hist) >= 20:
            v20  = hist["Volume"].rolling(20).mean()
            mask = (hist["Close"] > hist["Close"].shift(1)) & \
                   (hist["Volume"] > 2 * v20)
            vpa_count = mask.sum()
            if vpa_count > 0:
                last_vpa = str(hist.index[mask][-1])[:10]
                st.info(
                    f"🏦 **Institutional Buying Detected** — "
                    f"{int(vpa_count)} signal(s) found "
                    f"(Price↑ + Volume > 2× 20-day avg). "
                    f"Last signal: **{last_vpa}**")

        # RSI Chart
        st.markdown(
            "<div style='font-size:0.82rem;font-weight:700;color:#0f172a;"
            "border-left:2px solid #7c3aed;padding-left:8px;margin:1rem 0 0.6rem;'>"
            "📉 RSI (14) — Overbought / Oversold Zones</div>",
            unsafe_allow_html=True)

        fig_rsi = build_rsi_chart(hist)
        if fig_rsi:
            st.plotly_chart(fig_rsi, use_container_width=True,
                            config={"displayModeBar": False})

    st.markdown("---")

    # ── Tabs: Fundamentals · Trends · Notes ─────────────────
    T1, T2, T3 = st.tabs(["📋 Fundamentals", "📈 Price Stats", "📝 My Notes"])

    with T1:
        st.markdown(
            "<div style='font-size:0.78rem;font-weight:700;color:#0f172a;"
            "border-left:2px solid #2563eb;padding-left:8px;margin-bottom:0.65rem;'>"
            "Valuation & Profitability</div>",
            unsafe_allow_html=True)
        c1,c2,c3,c4,c5 = st.columns(5)
        pe_v  = safe_float(info.get("trailingPE"))
        roe_v = safe_float(info.get("returnOnEquity"))
        pm_v  = safe_float(info.get("profitMargins"))
        gm_v  = safe_float(info.get("grossMargins"))
        fcf_v = safe_float(info.get("freeCashflow"))

        with c1: st.metric("Trailing PE",  f"{pe_v:.1f}"       if pe_v  else "—",
                           delta="Reasonable" if pe_v and pe_v<30 else ("High" if pe_v else None),
                           delta_color="normal" if pe_v and pe_v<30 else "inverse")
        with c2: st.metric("ROE",          f"{roe_v*100:.1f}%" if roe_v else "—")
        with c3: st.metric("Net Margin",   f"{pm_v*100:.1f}%"  if pm_v  else "—")
        with c4: st.metric("Gross Margin", f"{gm_v*100:.1f}%"  if gm_v  else "—")
        with c5: st.metric("Free Cash Flow", fmt_cr(fcf_v))

        st.markdown(
            "<div style='font-size:0.78rem;font-weight:700;color:#0f172a;"
            "border-left:2px solid #2563eb;padding-left:8px;margin:1rem 0 0.65rem;'>"
            "Growth</div>",
            unsafe_allow_html=True)
        c1,c2,c3,c4,c5 = st.columns(5)
        rg_v  = safe_float(info.get("revenueGrowth"))
        eg_v  = safe_float(info.get("earningsGrowth"))
        eps_v = safe_float(info.get("trailingEps"))
        cr_v  = safe_float(info.get("currentRatio"))
        dy_v  = safe_float(info.get("dividendYield"))
        with c1: st.metric("Revenue Growth",  f"{rg_v*100:.1f}%"  if rg_v  else "—")
        with c2: st.metric("Earnings Growth", f"{eg_v*100:.1f}%"  if eg_v  else "—")
        with c3: st.metric("Trailing EPS",    f"{eps_v:.2f}"       if eps_v else "—")
        with c4: st.metric("Current Ratio",   f"{cr_v:.2f}"        if cr_v  else "—")
        with c5: st.metric("Dividend Yield",  f"{dy_v*100:.2f}%"  if dy_v  else "—")

        desc = info.get("longBusinessSummary","")
        if desc:
            with st.expander("📖 About the Company"):
                st.markdown(
                    f"<p style='font-size:0.84rem;line-height:1.8;color:#3f3f46;'>"
                    f"{desc[:1500]}{'…' if len(desc)>1500 else ''}</p>",
                    unsafe_allow_html=True)

    with T2:
        if not hist.empty:
            st.markdown(
                "<div style='font-size:0.78rem;font-weight:700;color:#0f172a;"
                "border-left:2px solid #2563eb;padding-left:8px;margin-bottom:0.65rem;'>"
                "Price Statistics</div>",
                unsafe_allow_html=True)
            close  = hist["Close"]
            ema20  = compute_ema(close, 20)
            ema50  = compute_ema(close, 50)
            macd, sig = compute_macd(close)

            c1,c2,c3,c4 = st.columns(4)
            with c1:
                st.metric("Current Price",  fmt_price(close.iloc[-1]))
                st.metric("EMA 20",         fmt_price(ema20.iloc[-1]))
            with c2:
                st.metric("Period High",    fmt_price(close.max()))
                st.metric("EMA 50",         fmt_price(ema50.iloc[-1]))
            with c3:
                st.metric("Period Low",     fmt_price(close.min()))
                st.metric("MACD",           f"{macd.iloc[-1]:.2f}" if not macd.empty else "—")
            with c4:
                vol_20d = hist["Volume"].rolling(20).mean().iloc[-1]
                curr_vol = hist["Volume"].iloc[-1]
                vol_ratio = curr_vol/vol_20d if vol_20d > 0 else None
                st.metric("Vol vs 20D Avg", f"{vol_ratio:.2f}×" if vol_ratio else "—",
                          delta="Spike" if vol_ratio and vol_ratio>1.5 else None)
                st.metric("RSI (14)", f"{rsi_val:.1f}" if rsi_val else "—",
                          delta="Overbought ⚠️" if rsi_val and rsi_val>70
                          else ("Oversold 🔎" if rsi_val and rsi_val<30 else "Neutral"),
                          delta_color="inverse" if rsi_val and rsi_val>70 else "normal")

            # 52W Range bar
            h52 = safe_float(info.get("fiftyTwoWeekHigh"))
            l52 = safe_float(info.get("fiftyTwoWeekLow"))
            if h52 and l52 and h52 != l52:
                pos = (price - l52) / (h52 - l52) * 100
                st.markdown(
                    f"<div style='margin-top:1rem;'>"
                    f"<div style='font-size:0.72rem;font-weight:600;color:#71717a;"
                    f"margin-bottom:4px;'>52-WEEK RANGE — {pos:.0f}th percentile</div>"
                    f"<div style='display:flex;justify-content:space-between;font-size:0.72rem;"
                    f"color:#71717a;margin-bottom:3px;'>"
                    f"<span>Low ₹{l52:,.0f}</span>"
                    f"<span style='font-weight:700;color:#0f172a;'>₹{price:,.2f}</span>"
                    f"<span>High ₹{h52:,.0f}</span></div>"
                    f"<div style='background:#e4e4e7;border-radius:999px;height:6px;'>"
                    f"<div style='width:{pos:.1f}%;height:6px;border-radius:999px;"
                    f"background:linear-gradient(90deg,#dc2626 0%,#f59e0b 50%,#16a34a 100%);'>"
                    f"</div></div></div>",
                    unsafe_allow_html=True)
        else:
            st.warning("Price history not available.")

    with T3:
        existing, last_upd = db_load_note(ticker)
        st.markdown(
            f"<div style='font-size:0.78rem;font-weight:700;color:#0f172a;"
            f"border-left:2px solid #2563eb;padding-left:8px;margin-bottom:0.65rem;'>"
            f"My Research Notes — {ticker}</div>",
            unsafe_allow_html=True)

        if st.button("📋 Load Template", key=f"tmpl_{ticker}"):
            existing = (
                f"📌 {ticker}  |  📅 {datetime.date.today()}\n\n"
                f"🎯 INVESTMENT THESIS:\n\n"
                f"📊 KEY METRICS:\n"
                f"- P/E:\n- ROE:\n- D/E:\n- FCF:\n- RSI:\n\n"
                f"⚠️ RISKS:\n\n"
                f"🎯 TRADE PLAN:\n"
                f"- Entry: ₹\n- Stop Loss: ₹\n- Target: ₹\n"
                f"- Time Horizon:\n\n"
                f"✅ DECISION (Buy/Hold/Avoid):")

        note_txt = st.text_area(
            "", value=existing, height=280,
            key=f"note_{ticker}", label_visibility="collapsed",
            placeholder="Write your research, thesis, trade plan here…")

        nc1, nc2 = st.columns([3,1])
        with nc1:
            if st.button("💾 Save Note", key=f"save_{ticker}",
                         use_container_width=True, type="primary"):
                db_save_note(ticker, note_txt)
                st.success("✅ Note saved!")
        with nc2:
            if last_upd:
                st.caption(f"Last saved:\n{last_upd}")

    st.markdown("---")
    st.caption(
        f"📊 Stock Analysis Pro v5.0 · {ticker} · "
        f"Data: Yahoo Finance · Educational only · Not SEBI advice")

# ═══════════════════════════════════════════════════════════
# MAIN ROUTER
# ═══════════════════════════════════════════════════════════
current_page = st.session_state.page

if current_page == "🔍 Stock Discovery":
    page_discovery()
elif current_page == "📋 My Watchlist":
    page_watchlist()
elif current_page == "📊 Deep Analysis":
    page_analysis()
