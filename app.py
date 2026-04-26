"""
Stock Analysis Pro — v5.1
Author  : Money Financial Services
Structure: 3-Page Navigation — Discovery · Watchlist · Deep Analysis
Features : ALL v4.3 features + 3-page UI
           Piotroski · Graham/DCF IV · Google Trends · VPA · AI Score
           Institutional Holders · RSI Trap Detector · EMA Charts
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
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;background:#fff!important;}
.stApp{background:#ffffff!important;}
.stApp>header{display:none!important;}
#MainMenu,footer{display:none!important;}
.block-container{padding-top:1.25rem!important;padding-bottom:3rem!important;
  padding-left:1.5rem!important;padding-right:1.5rem!important;max-width:1400px!important;}
[data-testid="stSidebar"]{background:#fafafa!important;border-right:1px solid #e4e4e7!important;}
[data-testid="stSidebar"] *{font-family:'Inter',sans-serif!important;}
[data-testid="stButton"]>button{border-radius:7px!important;font-family:'Inter',sans-serif!important;
  font-weight:600!important;font-size:0.82rem!important;}
[data-testid="stTextInput"] input{border-radius:7px!important;font-size:0.9rem!important;
  border:1px solid #d1d5db!important;padding:0.45rem 0.75rem!important;}
[data-testid="stTabs"] [role="tab"]{font-family:'Inter',sans-serif!important;
  font-weight:600!important;font-size:0.8rem!important;}
[data-testid="stMetric"]{background:#fafafa;border:1px solid #e4e4e7;
  border-radius:8px;padding:0.75rem 1rem!important;}
[data-testid="stMetric"] label{font-size:0.68rem!important;font-weight:700!important;
  text-transform:uppercase!important;letter-spacing:0.06em!important;color:#71717a!important;}
[data-testid="stMetric"] [data-testid="stMetricValue"]{font-size:1.25rem!important;
  font-weight:700!important;font-family:'JetBrains Mono',monospace!important;}
hr{border-color:#e4e4e7!important;margin:0.9rem 0!important;}
div[data-testid="stAlert"]{border-radius:8px!important;font-size:0.83rem!important;}
[data-testid="stExpander"]{border:1px solid #e4e4e7!important;border-radius:8px!important;}
.mc{background:#fafafa;border:1px solid #e4e4e7;border-radius:8px;
    padding:0.8rem 0.95rem;margin-bottom:0.65rem;}
.ml{font-size:0.62rem;font-weight:700;text-transform:uppercase;
    letter-spacing:0.07em;color:#71717a;margin-bottom:3px;}
.mv{font-size:1.25rem;font-weight:700;font-family:'JetBrains Mono',monospace;line-height:1.1;}
.ms{font-size:0.65rem;color:#a1a1aa;margin-top:2px;}
.sh{font-size:0.8rem;font-weight:700;color:#0f172a;border-left:2px solid #2563eb;
    padding-left:8px;margin:1.25rem 0 0.65rem;}
.ck{display:flex;align-items:flex-start;gap:0.45rem;padding:0.35rem 0.65rem;
    border-radius:6px;margin-bottom:0.22rem;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════
DB = "stock_v51.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS watchlist (
        ticker TEXT PRIMARY KEY, added_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS notes (
        ticker TEXT PRIMARY KEY, content TEXT, updated_at TEXT)""")
    conn.commit()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    defaults = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","SBIN.NS"]
    for t in defaults:
        try:
            conn.execute("INSERT OR IGNORE INTO watchlist VALUES (?,?)",(t,now))
        except: pass
    conn.commit(); conn.close()

def dbq(sql,p=()):
    conn=sqlite3.connect(DB); r=conn.execute(sql,p).fetchall(); conn.close(); return r

def dbx(sql,p=()):
    conn=sqlite3.connect(DB); conn.execute(sql,p); conn.commit(); conn.close()

def get_wl():
    return [r[0] for r in dbq("SELECT ticker FROM watchlist ORDER BY added_at DESC")]

def add_ticker(t):
    now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    dbx("INSERT OR IGNORE INTO watchlist VALUES (?,?)",(t.upper().strip(),now))

def del_ticker(t):
    dbx("DELETE FROM watchlist WHERE ticker=?",(t,))

def save_note(t,c):
    now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    dbx("INSERT OR REPLACE INTO notes VALUES (?,?,?)",(t.upper(),c,now))

def load_note(t):
    r=dbq("SELECT content,updated_at FROM notes WHERE ticker=?",(t.upper(),))
    return (r[0][0],r[0][1]) if r else ("","")

# ═══════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════
init_db()
for k,v in [("watchlist",None),("selected_stock",None),
            ("page","🔍 Stock Discovery"),("search_result",None)]:
    if k not in st.session_state:
        st.session_state[k] = v
if st.session_state.watchlist is None:
    st.session_state.watchlist = get_wl()

# ═══════════════════════════════════════════════════════════
# DATA FETCHERS
# ═══════════════════════════════════════════════════════════
@st.cache_resource
def _pcache(): return {}

def fetch_price(ticker):
    cache=_pcache(); key=f"p_{ticker}_{datetime.datetime.now().strftime('%Y%m%d%H')}"
    if key in cache: return cache[key]
    try:
        info=yf.Ticker(ticker).info or {}
        price=info.get("regularMarketPrice") or info.get("currentPrice")
        prev=info.get("regularMarketPreviousClose")
        chgp=((price-prev)/prev*100) if price and prev and prev!=0 else None
        r={"price":price,"prev":prev,"chgp":chgp,
           "name":info.get("shortName") or info.get("longName") or ticker,
           "website":info.get("website",""),"info":info}
    except:
        r={"price":None,"prev":None,"chgp":None,"name":ticker,"website":"","info":{}}
    cache[key]=r; return r

def fetch_full(ticker):
    try:
        stk=yf.Ticker(ticker)
        info=stk.info or {}
        hist=stk.history(period="1y")
        try:    fin=stk.financials
        except: fin=pd.DataFrame()
        try:    bs=stk.balance_sheet
        except: bs=pd.DataFrame()
        try:    cf=stk.cashflow
        except: cf=pd.DataFrame()
        try:    mh=stk.major_holders
        except: mh=pd.DataFrame()
        try:    ih=stk.institutional_holders
        except: ih=pd.DataFrame()
        return {"ok":True,"info":info,"hist":hist,"fin":fin,"bs":bs,
                "cf":cf,"mh":mh,"ih":ih}
    except Exception as e:
        return {"ok":False,"error":str(e),"info":{},"hist":pd.DataFrame(),
                "fin":pd.DataFrame(),"bs":pd.DataFrame(),"cf":pd.DataFrame(),
                "mh":pd.DataFrame(),"ih":pd.DataFrame()}

def fetch_trends(keyword):
    try:
        from pytrends.request import TrendReq
        kw=keyword.replace(".NS","").replace(".BO","")
        pt=TrendReq(hl="en-IN",tz=330,timeout=(10,25))
        pt.build_payload([kw],cat=0,timeframe="today 1-m",geo="IN")
        df=pt.interest_over_time()
        if df.empty or kw not in df.columns:
            return None,"Trends data not available for this ticker"
        return df[[kw]],None
    except ImportError:
        return None,"pytrends not installed"
    except:
        return None,"Trends data not available for this ticker"

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════
def _v(d,*keys,default=None):
    for k in keys:
        try:
            v=d.get(k) if isinstance(d,dict) else None
            if v is not None and not(isinstance(v,float) and math.isnan(v)):
                return v
        except: pass
    return default

def _row(df,*names):
    try:
        if df is None or df.empty: return None
        for n in names:
            for idx in df.index:
                if n.lower() in str(idx).lower():
                    s=df.loc[idx].dropna()
                    if not s.empty: return s
    except: pass
    return None

def _lat(s):
    try:
        if s is None: return None
        s2=s.dropna(); return float(s2.iloc[0]) if not s2.empty else None
    except: return None

def sdiv(a,b,default=None):
    try:
        if b is None or b==0: return default
        return a/b
    except: return default

def sf(v):
    try:
        if v is None: return None
        f=float(v); return None if math.isnan(f) else f
    except: return None

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

def logo(website):
    try:
        if not website: return None
        d=website.replace("https://","").replace("http://","").split("/")[0]
        return f"https://logo.clearbit.com/{d}" if d else None
    except: return None

def mcard(lbl,val,sub="",vc="#0f172a"):
    st.markdown(
        f"<div class='mc'><div class='ml'>{lbl}</div>"
        f"<div class='mv' style='color:{vc};'>{val}</div>"
        +(f"<div class='ms'>{sub}</div>" if sub else "")
        +"</div>",unsafe_allow_html=True)

def sec(t):
    st.markdown(f"<div class='sh'>{t}</div>",unsafe_allow_html=True)

def pbbar(pct,color="#2563eb"):
    pct=max(0,min(100,pct))
    return (f"<div style='background:#e4e4e7;border-radius:999px;height:5px;width:100%;margin:.3rem 0;'>"
            f"<div style='width:{pct}%;height:5px;border-radius:999px;background:{color};'></div></div>")

# ═══════════════════════════════════════════════════════════
# METRICS BUILDER  (with all fallbacks)
# ═══════════════════════════════════════════════════════════
def build_m(data):
    info,fin,bs,cf,hist=(data["info"],data["fin"],data["bs"],data["cf"],data["hist"])
    m={}
    m["name"]   =_v(info,"longName","shortName")
    m["sector"] =_v(info,"sector",default="—")
    m["ind"]    =_v(info,"industry",default="—")
    m["exch"]   =_v(info,"exchange",default="—")
    m["curr"]   =_v(info,"currency",default="INR")
    m["web"]    =_v(info,"website",default="")
    m["price"]  =_v(info,"regularMarketPrice","currentPrice")
    m["prev"]   =_v(info,"regularMarketPreviousClose")
    m["mktcap"] =_v(info,"marketCap")
    m["beta"]   =_v(info,"beta")
    m["target"] =_v(info,"targetMeanPrice")
    m["pe"]     =_v(info,"trailingPE")
    m["fpe"]    =_v(info,"forwardPE")
    m["pb"]     =_v(info,"priceToBook")
    m["ps"]     =_v(info,"priceToSalesTrailing12Months")
    m["peg"]    =_v(info,"pegRatio")
    m["roe"]    =_v(info,"returnOnEquity")
    m["roa"]    =_v(info,"returnOnAssets")
    m["pm"]     =_v(info,"profitMargins")
    m["gm"]     =_v(info,"grossMargins")
    m["om"]     =_v(info,"operatingMargins")
    m["de"]     =_v(info,"debtToEquity")
    m["cr"]     =_v(info,"currentRatio")
    m["qr"]     =_v(info,"quickRatio")
    m["fcf"]    =_v(info,"freeCashflow")
    m["ocf"]    =_v(info,"operatingCashflow")
    m["rg"]     =_v(info,"revenueGrowth")
    m["eg"]     =_v(info,"earningsGrowth")
    m["eps"]    =_v(info,"trailingEps")
    m["feps"]   =_v(info,"forwardEps")
    m["dy"]     =_v(info,"dividendYield")
    # Fallbacks
    if m["roe"] is None:
        ni=_lat(_row(fin,"Net Income")); eq=_lat(_row(bs,"Stockholders Equity","Total Stockholder Equity"))
        m["roe"]=sdiv(ni,abs(eq)) if ni and eq else None
    if m["roa"] is None:
        ni=_lat(_row(fin,"Net Income")); ta=_lat(_row(bs,"Total Assets"))
        m["roa"]=sdiv(ni,abs(ta)) if ni and ta else None
    if m["pm"] is None:
        ni=_lat(_row(fin,"Net Income")); rv=_lat(_row(fin,"Total Revenue"))
        m["pm"]=sdiv(ni,abs(rv)) if ni and rv else None
    if m["de"] is None:
        td=_lat(_row(bs,"Total Debt","Long Term Debt"))
        eq=_lat(_row(bs,"Stockholders Equity","Total Stockholder Equity"))
        if td is not None and eq:
            v=sdiv(td,abs(eq)); m["de"]=v*100 if v else None
    if m["fcf"] is None:
        ocf=_lat(_row(cf,"Operating Cash Flow","Cash From Operations"))
        cx=_lat(_row(cf,"Capital Expenditure","Purchases Of Property Plant And Equipment"))
        if ocf is not None: m["ocf"]=ocf; m["fcf"]=ocf+(cx if cx else 0)
    # Technicals
    if not hist.empty:
        try:
            close=hist["Close"]
            m["ph"]  =float(close.iloc[-1])
            m["vol"] =float(hist["Volume"].iloc[-1])
            m["v20"] =float(hist["Volume"].rolling(20).mean().iloc[-1]) if len(hist)>=20 else None
            m["d50"] =float(close.rolling(50).mean().iloc[-1])  if len(close)>=50  else None
            m["d200"]=float(close.rolling(200).mean().iloc[-1]) if len(close)>=200 else None
            m["h52"] =float(close.rolling(252).max().iloc[-1])  if len(close)>=252 else float(close.max())
            m["l52"] =float(close.rolling(252).min().iloc[-1])  if len(close)>=252 else float(close.min())
            delta=close.diff(); gain=delta.clip(lower=0).rolling(14).mean()
            loss=(-delta.clip(upper=0)).rolling(14).mean(); rs=gain/loss.replace(0,float("nan"))
            rsi=100-(100/(1+rs)); m["rsi"]=float(rsi.iloc[-1]) if not rsi.empty else None
            e12=close.ewm(span=12).mean(); e26=close.ewm(span=26).mean()
            macd=e12-e26; sig=macd.ewm(span=9).mean()
            m["macd"]=float(macd.iloc[-1]); m["msig"]=float(sig.iloc[-1]); m["mh"]=float((macd-sig).iloc[-1])
            m["vp"]  =float(close.pct_change().rolling(20).std().iloc[-1]*100) if len(close)>=20 else None
            if m["v20"] and m["v20"]>0:
                mask=(hist["Close"]>hist["Close"].shift(1))&(hist["Volume"]>2*hist["Volume"].rolling(20).mean())
                m["vpa"]=list(hist.index[mask])
            else: m["vpa"]=[]
        except:
            for k in ["ph","vol","v20","d50","d200","h52","l52","rsi","macd","msig","mh","vp","vpa"]: m[k]=None
    else:
        for k in ["ph","vol","v20","d50","d200","h52","l52","rsi","macd","msig","mh","vp","vpa"]: m[k]=None
    return m

# ═══════════════════════════════════════════════════════════
# PIOTROSKI F-SCORE
# ═══════════════════════════════════════════════════════════
def piotroski(data):
    info,fin,bs,cf=data["info"],data["fin"],data["bs"],data["cf"]
    C=[]
    def _l(df,*n): return _lat(_row(df,*n))
    def _lp(df,*n):
        r=_row(df,*n)
        if r is None or len(r.dropna())<2: return None
        return float(r.dropna().iloc[1])
    ni_c=_l(fin,"Net Income"); ni_p=_lp(fin,"Net Income")
    rv_c=_l(fin,"Total Revenue"); rv_p=_lp(fin,"Total Revenue")
    ta_c=_l(bs,"Total Assets"); ta_p=_lp(bs,"Total Assets")
    ocf=_l(cf,"Operating Cash Flow","Cash From Operations")
    roa=_v(info,"returnOnAssets")
    if roa is None and ni_c and ta_c and ta_c!=0: roa=sdiv(ni_c,ta_c)
    def A(g,n,p,note): C.append({"g":g,"n":n,"p":p,"note":note})
    A("P","F1 — ROA Positive",roa is not None and roa>0,f"ROA={roa*100:.1f}%" if roa else "N/A")
    A("P","F2 — OCF Positive",ocf is not None and ocf>0,f"₹{ocf/1e7:.1f}Cr" if ocf else "N/A")
    if roa is not None and ta_p and ni_p and ta_p!=0:
        rp=sdiv(ni_p,ta_p,0); A("P","F3 — ROA Improving",roa>rp,f"Curr {roa*100:.1f}% vs Prev {rp*100:.1f}%")
    else: A("P","F3 — ROA Improving",False,"Insufficient data")
    if ocf and ta_c and ta_c!=0 and roa is not None:
        A("P","F4 — Cash>Paper",sdiv(ocf,ta_c,0)>roa,f"OCF/TA={sdiv(ocf,ta_c,0)*100:.1f}% vs ROA={roa*100:.1f}%")
    else: A("P","F4 — Cash>Paper",False,"N/A")
    ltd=_row(bs,"Long Term Debt")
    if ltd is not None and len(ltd.dropna())>=2 and ta_c and ta_p:
        lv=ltd.dropna(); rc=sdiv(float(lv.iloc[0]),ta_c,0); rp2=sdiv(float(lv.iloc[1]),ta_p,0)
        A("L","F5 — Debt Decreasing",rc<rp2,f"Curr {rc*100:.1f}% vs Prev {rp2*100:.1f}%")
    else: A("L","F5 — Debt Decreasing",False,"N/A")
    ca=_row(bs,"Current Assets"); cl=_row(bs,"Current Liabilities")
    if ca is not None and cl is not None and len(ca.dropna())>=2:
        cav=ca.dropna(); clv=cl.dropna()
        cc=sdiv(float(cav.iloc[0]),float(clv.iloc[0])); cp=sdiv(float(cav.iloc[1]),float(clv.iloc[1]))
        A("L","F6 — CR Improving",bool(cc and cp and cc>cp),f"Curr {cc:.2f} vs Prev {cp:.2f}" if cc and cp else "N/A")
    else:
        cr_i=_v(info,"currentRatio"); A("L","F6 — CR>1.5",cr_i is not None and cr_i>1.5,f"CR={cr_i:.2f}" if cr_i else "N/A")
    sh=_row(bs,"Ordinary Shares Number","Common Stock Shares Outstanding")
    if sh is not None and len(sh.dropna())>=2:
        sv=sh.dropna(); A("L","F7 — No Dilution",float(sv.iloc[0])<=float(sv.iloc[1]),
                          f"Curr {float(sv.iloc[0])/1e7:.2f}Cr vs Prev {float(sv.iloc[1])/1e7:.2f}Cr")
    else: A("L","F7 — No Dilution",False,"N/A")
    gp=_row(fin,"Gross Profit")
    if gp is not None and len(gp.dropna())>=2 and rv_c and rv_p:
        gv=gp.dropna(); gmc=sdiv(float(gv.iloc[0]),rv_c,0); gmp=sdiv(float(gv.iloc[1]),rv_p,0)
        A("E","F8 — GM Improving",gmc>gmp,f"Curr {gmc*100:.1f}% vs Prev {gmp*100:.1f}%")
    else:
        gm_i=_v(info,"grossMargins"); A("E","F8 — GM>20%",gm_i is not None and gm_i>0.20,f"GM={gm_i*100:.1f}%" if gm_i else "N/A")
    if rv_c and rv_p and ta_c and ta_p:
        A("E","F9 — AT Improving",sdiv(rv_c,ta_c,0)>sdiv(rv_p,ta_p,0),
          f"Curr {sdiv(rv_c,ta_c,0):.2f}x vs Prev {sdiv(rv_p,ta_p,0):.2f}x")
    else: A("E","F9 — AT Improving",False,"Insufficient data")
    return sum(1 for c in C if c["p"]),C

# ═══════════════════════════════════════════════════════════
# INTRINSIC VALUE
# ═══════════════════════════════════════════════════════════
def calc_iv(m):
    r={}; eps=m.get("eps"); pb=m.get("pb"); price=m.get("price") or m.get("ph")
    bvps=sdiv(price,pb) if(pb and pb>0 and price) else None
    r["graham"]=math.sqrt(22.5*eps*bvps) if(eps and eps>0 and bvps and bvps>0) else None
    g=m.get("eg") or m.get("rg")
    if eps and eps>0 and g is not None:
        g2=max(-20,min(50,g*100)); dcf=eps*(8.5+2*g2)*4.4/7.5
        r["dcf"]=dcf if dcf>0 else None
    else: r["dcf"]=None
    tg=m.get("target")
    r["au"]=sdiv(tg-price,price,0)*100 if tg and price else None; r["at"]=tg
    valid=[v for v in [r.get("graham"),r.get("dcf")] if v]
    if valid and price:
        avg=sum(valid)/len(valid); r["avg"]=avg
        r["mos"]=sdiv(avg-price,avg,0)*100; r["up"]=sdiv(avg-price,price,0)*100
    else: r["avg"]=r["mos"]=r["up"]=None
    return r

# ═══════════════════════════════════════════════════════════
# AI SCORE (0-100)
# ═══════════════════════════════════════════════════════════
def calc_ai(m,pio,iv):
    bd={}; price=m.get("price") or m.get("ph") or 0
    v=0; pe=m.get("pe"); pb=m.get("pb")
    if pe: v+=10 if pe<15 else(7 if pe<25 else(4 if pe<40 else 0))
    if pb: v+=10 if pb<1.5 else(7 if pb<3 else(3 if pb<5 else 0))
    bd["Valuation"]=min(v,20)
    p=0; roe=m.get("roe"); pm=m.get("pm"); fcf=m.get("fcf")
    if roe: p+=8 if roe>0.25 else(5 if roe>0.15 else(2 if roe>0 else 0))
    if pm: p+=7 if pm>0.20 else(4 if pm>0.10 else(1 if pm>0 else 0))
    if fcf and fcf>0: p+=5
    bd["Profitability"]=min(p,20)
    h=0; de=m.get("de"); cr=m.get("cr")
    if de is not None:
        dr=de/100; h+=8 if dr<0.3 else(5 if dr<0.7 else(2 if dr<1 else 0))
    if cr: h+=7 if cr>2 else(4 if cr>1.5 else(1 if cr>1 else 0))
    h+=min(pio,5); bd["Fin. Health"]=min(h,20)
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
    if total>=75: gr,col="Excellent — Strong Buy","#16a34a"
    elif total>=60: gr,col="Good — Buy","#2563eb"
    elif total>=45: gr,col="Average — Watch","#d97706"
    elif total>=30: gr,col="Weak — Caution","#ea580c"
    else: gr,col="Poor — Avoid","#dc2626"
    return total,bd,gr,col

# ═══════════════════════════════════════════════════════════
# CHARTS
# ═══════════════════════════════════════════════════════════
def candle_chart(hist,d50,d200,vpa=None):
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        if hist.empty: return None
        ema20=hist["Close"].ewm(span=20).mean()
        ema50=hist["Close"].ewm(span=50).mean()
        fig=make_subplots(rows=2,cols=1,shared_xaxes=True,
                          vertical_spacing=0.03,row_heights=[0.75,0.25])
        fig.add_trace(go.Candlestick(x=hist.index,open=hist["Open"],high=hist["High"],
            low=hist["Low"],close=hist["Close"],name="Price",
            increasing_line_color="#16a34a",decreasing_line_color="#dc2626",
            increasing_fillcolor="#16a34a",decreasing_fillcolor="#dc2626"),row=1,col=1)
        fig.add_trace(go.Scatter(x=hist.index,y=ema20,name="EMA 20",
            line=dict(color="#2563eb",width=1.5)),row=1,col=1)
        fig.add_trace(go.Scatter(x=hist.index,y=ema50,name="EMA 50",
            line=dict(color="#d97706",width=1.5,dash="dot")),row=1,col=1)
        if d200:
            fig.add_trace(go.Scatter(x=hist.index,y=hist["Close"].rolling(200).mean(),
                name="200 DMA",line=dict(color="#7c3aed",width=1,dash="dot")),row=1,col=1)
        if vpa:
            vd=[d for d in vpa if d in hist.index]
            vp=[hist.loc[d,"High"]*1.01 for d in vd]
            if vd:
                fig.add_trace(go.Scatter(x=vd,y=vp,mode="markers",name="🏦 Inst.Buy",
                    marker=dict(symbol="triangle-up",size=10,color="#7c3aed",
                                line=dict(color="#fff",width=1.5))),row=1,col=1)
        colors=["#16a34a" if c>=o else "#dc2626" for c,o in zip(hist["Close"],hist["Open"])]
        fig.add_trace(go.Bar(x=hist.index,y=hist["Volume"],name="Volume",
            marker_color=colors,opacity=0.5,showlegend=False),row=2,col=1)
        fig.update_layout(height=450,margin=dict(l=0,r=0,t=18,b=0),
            paper_bgcolor="#fff",plot_bgcolor="#fff",template="plotly_white",
            font=dict(family="Inter",size=11,color="#3f3f46"),
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h",yanchor="bottom",y=1.01,
                        xanchor="right",x=1,bgcolor="rgba(0,0,0,0)",font=dict(size=10)),
            yaxis=dict(showgrid=True,gridcolor="#f4f4f5",side="right",
                       zeroline=False,tickfont=dict(size=10)),
            yaxis2=dict(showgrid=False,side="right",zeroline=False,tickfont=dict(size=9)),
            xaxis2=dict(showgrid=True,gridcolor="#f4f4f5",tickfont=dict(size=10)))
        return fig
    except: return None

def rsi_chart(hist):
    try:
        import plotly.graph_objects as go
        if hist.empty: return None
        close=hist["Close"]; delta=close.diff()
        gain=delta.clip(lower=0).rolling(14).mean()
        loss=(-delta.clip(upper=0)).rolling(14).mean()
        rs=gain/loss.replace(0,float("nan")); rsi=100-(100/(1+rs))
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=hist.index,y=rsi,name="RSI(14)",
            line=dict(color="#7c3aed",width=2),fill="tozeroy",fillcolor="rgba(124,58,237,.06)"))
        fig.add_hrect(y0=70,y1=100,fillcolor="rgba(220,38,38,.07)",line_width=0,
            annotation_text="Overbought >70",annotation_position="top left",
            annotation=dict(font_size=10,font_color="#dc2626"))
        fig.add_hrect(y0=0,y1=30,fillcolor="rgba(22,163,74,.07)",line_width=0,
            annotation_text="Oversold <30",annotation_position="bottom left",
            annotation=dict(font_size=10,font_color="#16a34a"))
        fig.add_hline(y=70,line_dash="dash",line_color="#dc2626",line_width=1,opacity=0.5)
        fig.add_hline(y=30,line_dash="dash",line_color="#16a34a",line_width=1,opacity=0.5)
        fig.add_hline(y=50,line_dash="dot", line_color="#94a3b8",line_width=1,opacity=0.4)
        fig.update_layout(height=210,margin=dict(l=0,r=0,t=14,b=0),
            paper_bgcolor="#fff",plot_bgcolor="#fff",template="plotly_white",showlegend=False,
            yaxis=dict(range=[0,100],side="right",showgrid=True,gridcolor="#f4f4f5",
                       tickfont=dict(size=10),zeroline=False),
            xaxis=dict(showgrid=True,gridcolor="#f4f4f5",tickfont=dict(size=10)),
            font=dict(family="Inter",size=11))
        return fig
    except: return None

def gauge_chart(score,grade,color):
    try:
        import plotly.graph_objects as go
        fig=go.Figure(go.Indicator(
            mode="gauge+number",value=score,
            number={"font":{"size":34,"family":"JetBrains Mono","color":color}},
            gauge=dict(
                axis=dict(range=[0,100],tickfont=dict(size=9,color="#71717a"),nticks=6),
                bar=dict(color=color,thickness=0.25),bgcolor="white",borderwidth=0,
                steps=[dict(range=[0,30],color="#fef2f2"),dict(range=[30,45],color="#fff7ed"),
                       dict(range=[45,60],color="#fffbeb"),dict(range=[60,75],color="#eff6ff"),
                       dict(range=[75,100],color="#f0fdf4")],
                threshold=dict(line=dict(color=color,width=3),thickness=0.75,value=score)),
            domain={"x":[0,1],"y":[0,1]},
            title={"text":grade,"font":{"size":10,"family":"Inter","color":"#3f3f46"}}))
        fig.update_layout(height=195,margin=dict(l=10,r=10,t=25,b=0),
            paper_bgcolor="#fff",template="plotly_white",font=dict(family="Inter"))
        return fig
    except: return None

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        "<div style='padding:0.5rem 0 1rem;'>"
        "<div style='font-size:1rem;font-weight:800;color:#0f172a;'>📈 Stock Analysis Pro</div>"
        "<div style='font-size:0.68rem;color:#71717a;margin-top:2px;'>Money Financial Services · v5.1</div>"
        "</div>",unsafe_allow_html=True)

    page=st.radio("",
        ["🔍 Stock Discovery","📋 My Watchlist","📊 Deep Analysis"],
        index=["🔍 Stock Discovery","📋 My Watchlist","📊 Deep Analysis"].index(
            st.session_state.page),
        label_visibility="collapsed",key="nav")
    if page!=st.session_state.page:
        st.session_state.page=page; st.rerun()

    st.markdown("---")
    st.markdown(
        f"<div style='font-size:0.7rem;color:#71717a;margin-bottom:4px;'>"
        f"📌 Watchlist: <b>{len(st.session_state.watchlist)} stocks</b></div>",
        unsafe_allow_html=True)
    for t in st.session_state.watchlist[:7]:
        if st.button(t,key=f"sb_{t}",use_container_width=True):
            st.session_state.selected_stock=t
            st.session_state.page="📊 Deep Analysis"; st.rerun()
    if len(st.session_state.watchlist)>7:
        st.caption(f"+ {len(st.session_state.watchlist)-7} more")
    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.66rem;color:#a1a1aa;line-height:1.65;'>"
        "NSE: Add .NS (e.g. SBIN.NS)<br>"
        "BSE: Add .BO<br>US: Plain (AAPL, MSFT)"
        "</div>",unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# PAGE 1 — STOCK DISCOVERY
# ═══════════════════════════════════════════════════════════
def page_discovery():
    st.markdown(
        "<h2 style='font-size:1.35rem;font-weight:800;color:#0f172a;margin-bottom:4px;'>"
        "🔍 Stock Discovery</h2>"
        "<p style='font-size:0.82rem;color:#71717a;margin-bottom:1.1rem;'>"
        "Search any stock · Add to Watchlist · Quick chart preview</p>",
        unsafe_allow_html=True)

    ci,cb=st.columns([4,1])
    with ci:
        ticker_in=st.text_input("",placeholder="Enter ticker: RELIANCE.NS, TCS.NS, AAPL…",
                                key="d_in",label_visibility="collapsed")
    with cb:
        go_btn=st.button("🔍 Search",use_container_width=True,type="primary")

    # Popular
    popular=["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
             "SBIN.NS","BAJFINANCE.NS","WIPRO.NS","TITAN.NS","SUNPHARMA.NS",
             "MARUTI.NS","ONGC.NS","NTPC.NS","ADANIPORTS.NS","ITC.NS"]
    st.caption("Popular stocks:")
    pc=st.columns(5)
    for i,ps in enumerate(popular):
        with pc[i%5]:
            if st.button(ps.replace(".NS",""),key=f"pp_{ps}",use_container_width=True):
                st.session_state.search_result=ps; st.rerun()

    st.markdown("---")
    if go_btn and ticker_in.strip():
        st.session_state.search_result=ticker_in.strip().upper()
    query=st.session_state.search_result
    if not query: return

    with st.spinner(f"Fetching {query}…"):
        info={}
        try: info=yf.Ticker(query).info or {}
        except: pass
        hist=pd.DataFrame()
        try: hist=yf.Ticker(query).history(period="6mo")
        except: pass

    price=sf(_v(info,"regularMarketPrice","currentPrice"))
    if not price:
        st.error(f"❌ **{query}** not found. Check ticker symbol. NSE → .NS suffix"); return

    prev=sf(_v(info,"regularMarketPreviousClose"))
    chg=(price-prev) if prev else 0
    chgp=(chg/prev*100) if prev and prev!=0 else 0
    cc="#16a34a" if chg>=0 else "#dc2626"; arr="▲" if chg>=0 else "▼"
    name=info.get("longName") or info.get("shortName") or query
    curr=info.get("currency","INR")
    lurl=logo(info.get("website",""))
    logo_html=(f'<img src="{lurl}" width="38" height="38" '
               f'style="border-radius:7px;object-fit:contain;border:1px solid #e4e4e7;'
               f'margin-right:10px;vertical-align:middle;" onerror="this.style.display=\'none\'"> ') if lurl else ""

    st.markdown(
        f"<div style='background:#fafafa;border:1px solid #e4e4e7;border-radius:10px;"
        f"padding:1rem 1.25rem;margin-bottom:0.9rem;display:flex;"
        f"justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.75rem;'>"
        f"<div style='display:flex;align-items:center;'>{logo_html}"
        f"<div><div style='font-size:1.1rem;font-weight:800;color:#0f172a;'>{name}</div>"
        f"<div style='font-size:0.72rem;color:#71717a;margin-top:2px;'>"
        f"{query} · {info.get('exchange','—')} · {info.get('sector','—')} · {info.get('industry','—')}"
        f"</div></div></div>"
        f"<div style='text-align:right;'>"
        f"<div style='font-size:1.55rem;font-weight:800;color:#0f172a;font-family:JetBrains Mono,monospace;'>"
        f"{curr} {price:,.2f}</div>"
        f"<div style='font-size:0.83rem;font-weight:600;color:{cc};margin-top:3px;'>"
        f"{arr} {abs(chg):,.2f} ({chgp:+.2f}%)</div>"
        f"</div></div>",unsafe_allow_html=True)

    already=query in st.session_state.watchlist
    c1,c2,c3=st.columns([2,2,3])
    with c1:
        if already: st.success("✅ Already in watchlist")
        elif st.button("➕ Add to Watchlist",type="primary",use_container_width=True,key="add_wl"):
            add_ticker(query); st.session_state.watchlist=get_wl()
            st.success(f"✅ {query} added!"); st.rerun()
    with c2:
        if st.button("📊 Deep Analysis",use_container_width=True,key="goto_a"):
            st.session_state.selected_stock=query
            st.session_state.page="📊 Deep Analysis"; st.rerun()

    st.markdown("---")
    m1,m2,m3,m4,m5,m6=st.columns(6)
    with m1: st.metric("Market Cap",fc(info.get("marketCap")))
    with m2: st.metric("P/E",f"{sf(info.get('trailingPE')):.1f}" if sf(info.get('trailingPE')) else "—")
    with m3: st.metric("52W High",f"₹{sf(info.get('fiftyTwoWeekHigh')):,.0f}" if sf(info.get('fiftyTwoWeekHigh')) else "—")
    with m4: st.metric("52W Low", f"₹{sf(info.get('fiftyTwoWeekLow')):,.0f}"  if sf(info.get('fiftyTwoWeekLow'))  else "—")
    with m5: st.metric("Volume",  f"{info.get('regularMarketVolume',0):,.0f}"  if info.get('regularMarketVolume') else "—")
    with m6: st.metric("Avg Vol", f"{info.get('averageVolume',0):,.0f}"         if info.get('averageVolume') else "—")

    if not hist.empty:
        st.markdown("---")
        sec("6-Month Price Chart")
        fig=candle_chart(hist,None,None)
        if fig: st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    desc=info.get("longBusinessSummary","")
    if desc:
        with st.expander("📖 About"):
            st.markdown(f"<p style='font-size:0.83rem;line-height:1.8;color:#3f3f46;'>{desc[:1400]}{'…' if len(desc)>1400 else ''}</p>",unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# PAGE 2 — WATCHLIST
# ═══════════════════════════════════════════════════════════
def page_watchlist():
    st.markdown(
        "<h2 style='font-size:1.35rem;font-weight:800;color:#0f172a;margin-bottom:4px;'>"
        "📋 My Watchlist</h2>"
        "<p style='font-size:0.82rem;color:#71717a;margin-bottom:1.1rem;'>"
        "Real-time LTP · % Change · Click 📊 for Deep Analysis</p>",
        unsafe_allow_html=True)

    wl=st.session_state.watchlist
    if not wl:
        st.info("📭 Watchlist empty. Go to 🔍 Stock Discovery to add stocks.")
        if st.button("🔍 Stock Discovery",type="primary"): st.session_state.page="🔍 Stock Discovery"; st.rerun()
        return

    ca,cb=st.columns([6,1])
    with cb:
        if st.button("🔄 Refresh",use_container_width=True): _pcache().clear(); st.rerun()

    st.markdown("---")
    # Headers
    hc=st.columns([0.4,2.5,1.5,1.2,1.2,1.1,1.5,0.9])
    for col,h in zip(hc,["","Stock","LTP","Change","Mkt Cap","P/E","52W H/L",""]):
        col.markdown(f"<div style='font-size:0.6rem;font-weight:700;text-transform:uppercase;"
                     f"letter-spacing:0.07em;color:#a1a1aa;padding-bottom:3px;'>{h}</div>",
                     unsafe_allow_html=True)
    st.markdown("<hr style='border:none;border-top:2px solid #e4e4e7;margin:0 0 3px;'>",unsafe_allow_html=True)

    for ticker in wl:
        data=get_price_data(ticker)
        info=data.get("info",{}); price=data.get("price"); chgp=data.get("chgp"); name=data.get("name",ticker)
        p_str=f"₹{price:,.2f}" if price else "—"
        if chgp is not None:
            cc2="#16a34a" if chgp>=0 else "#dc2626"; bg2="#f0fdf4" if chgp>=0 else "#fef2f2"
            cs=f"{'▲' if chgp>=0 else '▼'}{abs(chgp):.2f}%"
        else: cc2="#71717a"; bg2="#fafafa"; cs="—"
        h52=sf(info.get("fiftyTwoWeekHigh")); l52=sf(info.get("fiftyTwoWeekLow"))
        hl=f"₹{h52:,.0f} / ₹{l52:,.0f}" if h52 and l52 else "—"
        pe_v=sf(info.get("trailingPE"))
        lurl=logo(info.get("website","")); tabbr=ticker.replace(".NS","").replace(".BO","")[:2].upper()

        rc=st.columns([0.4,2.5,1.5,1.2,1.2,1.1,1.5,0.9])
        with rc[0]:
            if lurl:
                st.markdown(f'<img src="{lurl}" width="24" height="24" style="border-radius:4px;'
                            f'object-fit:contain;border:1px solid #e4e4e7;margin-top:7px;" '
                            f'onerror="this.style.display=\'none\'">',unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="width:24px;height:24px;border-radius:4px;background:#e4e4e7;'
                            f'display:flex;align-items:center;justify-content:center;font-size:0.55rem;'
                            f'font-weight:700;color:#71717a;margin-top:7px;">{tabbr}</div>',unsafe_allow_html=True)
        with rc[1]:
            st.markdown(f"<div style='padding-top:3px;'>"
                        f"<div style='font-size:0.8rem;font-weight:700;color:#0f172a;font-family:JetBrains Mono,monospace;'>"
                        f"{ticker.replace('.NS','').replace('.BO','')}</div>"
                        f"<div style='font-size:0.66rem;color:#94a3b8;'>{name[:26]}</div></div>",unsafe_allow_html=True)
        with rc[2]:
            st.markdown(f"<div style='font-size:0.82rem;font-weight:600;color:#0f172a;"
                        f"font-family:JetBrains Mono,monospace;padding-top:7px;'>{p_str}</div>",unsafe_allow_html=True)
        with rc[3]:
            st.markdown(f"<div style='padding-top:7px;'><span style='font-size:0.75rem;font-weight:700;"
                        f"color:{cc2};background:{bg2};padding:2px 6px;border-radius:4px;'>{cs}</span></div>",
                        unsafe_allow_html=True)
        with rc[4]:
            st.markdown(f"<div style='font-size:0.76rem;color:#3f3f46;padding-top:7px;'>{fc(info.get('marketCap'))}</div>",unsafe_allow_html=True)
        with rc[5]:
            st.markdown(f"<div style='font-size:0.76rem;color:#3f3f46;padding-top:7px;'>{f'{pe_v:.1f}' if pe_v else '—'}</div>",unsafe_allow_html=True)
        with rc[6]:
            st.markdown(f"<div style='font-size:0.7rem;color:#71717a;padding-top:7px;'>{hl}</div>",unsafe_allow_html=True)
        with rc[7]:
            ba,bb=st.columns([1,1])
            with ba:
                if st.button("📊",key=f"v_{ticker}",help=f"Analyse {ticker}"):
                    st.session_state.selected_stock=ticker
                    st.session_state.page="📊 Deep Analysis"; st.rerun()
            with bb:
                if st.button("🗑️",key=f"d_{ticker}",help=f"Remove {ticker}"):
                    del_ticker(ticker); st.session_state.watchlist=get_wl(); st.rerun()

        st.markdown("<hr style='border:none;border-top:1px solid #f0f0f0;margin:2px 0;'>",unsafe_allow_html=True)

    st.caption(f"Data via Yahoo Finance · {len(wl)} stocks · Refreshes hourly")

# ═══════════════════════════════════════════════════════════
# PAGE 3 — DEEP ANALYSIS (with ALL v4.3 features)
# ═══════════════════════════════════════════════════════════
def page_analysis():
    st.markdown(
        "<h2 style='font-size:1.35rem;font-weight:800;color:#0f172a;margin-bottom:4px;'>"
        "📊 Deep Analysis — Trap Detector</h2>",unsafe_allow_html=True)

    wl=st.session_state.watchlist
    options=wl[:]
    sel=st.session_state.selected_stock
    if sel and sel not in options: options=[sel]+options
    if not options:
        st.info("📭 No stocks. Go to 🔍 Stock Discovery first.")
        if st.button("🔍 Go to Discovery",type="primary"): st.session_state.page="🔍 Stock Discovery"; st.rerun()
        return

    ca,cb,_=st.columns([3,1,3])
    with ca:
        sel_t=st.selectbox("Select Stock",options,
            index=options.index(sel) if sel in options else 0,key="a_sel")
    with cb:
        period=st.selectbox("Period",["1mo","3mo","6mo","1y","2y"],index=3,key="a_per")
    if sel_t!=st.session_state.selected_stock:
        st.session_state.selected_stock=sel_t; st.rerun()
    ticker=sel_t

    with st.spinner(f"Loading full analysis for {ticker}…"):
        data=fetch_full(ticker)
    if not data["ok"]:
        st.error(f"❌ Failed: {ticker} — {data.get('error','')}"); return

    m=build_m(data); hist=data["hist"]
    price=m.get("price") or m.get("ph")
    if not price:
        st.warning(f"Price unavailable for {ticker}."); return

    pio_s,pio_c=piotroski(data); iv=calc_iv(m); total,bd,grade,color=calc_ai(m,pio_s,iv)
    prev=m.get("prev"); chg=(price-prev) if prev else 0
    chgp=(chg/prev*100) if prev and prev!=0 else 0
    cc="#16a34a" if chg>=0 else "#dc2626"; arr="▲" if chg>=0 else "▼"
    curr=m.get("curr","INR"); name=m.get("name") or ticker
    lurl=logo(m.get("web",""))
    logo_html=(f'<img src="{lurl}" width="34" height="34" style="border-radius:7px;'
               f'object-fit:contain;border:1px solid #e4e4e7;margin-right:10px;vertical-align:middle;" '
               f'onerror="this.style.display=\'none\'">') if lurl else ""

    # ── Stock Header ──
    h1,h2=st.columns([3,2])
    with h1:
        st.markdown(f"{logo_html}<span style='font-size:1.15rem;font-weight:800;color:#0f172a;"
                    f"vertical-align:middle;'>{name}</span>",unsafe_allow_html=True)
        st.caption(f"{ticker} · {m.get('exch','—')} · {m.get('sector','—')} · {m.get('ind','—')}")
    with h2:
        st.markdown(
            f"<div style='text-align:right;'>"
            f"<div style='font-size:1.6rem;font-weight:800;color:#0f172a;"
            f"font-family:JetBrains Mono,monospace;line-height:1;'>{curr} {price:,.2f}</div>"
            f"<div style='font-size:0.83rem;font-weight:600;color:{cc};margin-top:3px;'>"
            f"{arr} {abs(chg):,.2f} ({chgp:+.2f}%)</div>"
            f"<div style='font-size:0.67rem;color:#a1a1aa;margin-top:2px;'>"
            f"Cap: {fc(m.get('mktcap'))} · Beta: {fn(m.get('beta'))} · Target: {fn(m.get('target'))}"
            f"</div></div>",unsafe_allow_html=True)

    st.markdown("---")

    # ── RSI Trap Alert ──
    rsi_v=m.get("rsi")
    if rsi_v is not None:
        if rsi_v>70:
            st.markdown(
                f"<div style='background:linear-gradient(135deg,#fef2f2,#fee2e2);"
                f"border:2px solid #dc2626;border-radius:10px;padding:0.85rem 1.1rem;margin-bottom:0.7rem;'>"
                f"<div style='font-size:0.95rem;font-weight:800;color:#991b1b;'>"
                f"🚨 OVERBOUGHT TRAP — RSI: {rsi_v:.1f}</div>"
                f"<div style='font-size:0.8rem;color:#b91c1c;margin-top:3px;line-height:1.55;'>"
                f"RSI > 70 = Overbought. High reversal risk. <b>Avoid chasing. Wait for RSI < 60.</b>"
                f"</div></div>",unsafe_allow_html=True)
        elif rsi_v<30:
            st.markdown(
                f"<div style='background:linear-gradient(135deg,#f0fdf4,#dcfce7);"
                f"border:2px solid #16a34a;border-radius:10px;padding:0.85rem 1.1rem;margin-bottom:0.7rem;'>"
                f"<div style='font-size:0.95rem;font-weight:800;color:#15803d;'>"
                f"🔎 OVERSOLD ZONE — RSI: {rsi_v:.1f}</div>"
                f"<div style='font-size:0.8rem;color:#166534;margin-top:3px;line-height:1.55;'>"
                f"RSI < 30 = Oversold. Potential bounce. <b>Wait for RSI > 35 before entering.</b>"
                f"</div></div>",unsafe_allow_html=True)
        else:
            st.success(f"✅ RSI: {rsi_v:.1f} — Neutral zone. No extreme signals.")

    # Quick metrics
    m1,m2,m3,m4,m5,m6=st.columns(6)
    with m1: st.metric("P/E", f"{sf(m.get('pe')):.1f}" if sf(m.get('pe')) else "—")
    with m2: st.metric("ROE", fp(m.get("roe")))
    with m3: st.metric("D/E", f"{sf(m.get('de'))/100:.2f}x" if sf(m.get('de')) else "—")
    with m4: st.metric("RSI (14)", f"{rsi_v:.1f}" if rsi_v else "—")
    with m5: st.metric("Piotroski", f"{pio_s}/9 {'✅' if pio_s>=7 else '⚠️' if pio_s>=5 else '🔴'}")
    with m6: st.metric("AI Score", f"{total}/100")

    st.markdown("---")

    # ── TABS ──
    T1,T2,T3,T4,T5,T6,T7=st.tabs([
        "📈 Charts","📋 Fundamentals","📊 AI Verdict",
        "🏆 Piotroski","💎 Intrinsic Value",
        "🏦 Holders","📈 Trends + Notes"])

    # ── TAB 1: CHARTS ──
    with T1:
        sec("Candlestick — EMA 20/50 — Volume + VPA Signals")
        vpa_d=m.get("vpa") or []
        fig_c=candle_chart(hist,m.get("d50"),m.get("d200"),vpa_d)
        if fig_c: st.plotly_chart(fig_c,use_container_width=True,config={"displayModeBar":False})
        else: st.warning("Chart unavailable.")

        if vpa_d:
            st.info(f"🏦 **Institutional Buying** — {len(vpa_d)} signal(s) (Price↑ + Vol > 2× 20D avg). Last: {str(vpa_d[-1])[:10]}")
        else:
            st.info("ℹ️ No institutional buying signals in last 1 year.")

        sec("RSI (14) — Trap Detector")
        fig_r=rsi_chart(hist)
        if fig_r: st.plotly_chart(fig_r,use_container_width=True,config={"displayModeBar":False})

        sec("Key Technical Levels")
        ph=m.get("ph") or price
        c1,c2,c3,c4=st.columns(4)
        with c1: mcard("Price",f"₹{ph:,.2f}","Current")
        with c2:
            d50=m.get("d50")
            if d50: p50=sdiv(ph-d50,d50,0)*100; mcard("EMA 50",f"₹{d50:,.2f}",f"{p50:+.1f}%","#16a34a" if ph>d50 else "#dc2626")
            else: mcard("EMA 50","N/A","—")
        with c3:
            d200=m.get("d200")
            if d200: p200=sdiv(ph-d200,d200,0)*100; mcard("200 DMA",f"₹{d200:,.2f}",f"{p200:+.1f}%","#16a34a" if ph>d200 else "#dc2626")
            else: mcard("200 DMA","N/A","—")
        with c4:
            mh2=m.get("mh")
            mcard("MACD Hist",f"{mh2:.2f}" if mh2 else "N/A","Bullish 🟢" if mh2 and mh2>0 else "Bearish 🔴","#16a34a" if mh2 and mh2>0 else "#dc2626")

        h52=m.get("h52"); l52=m.get("l52")
        if h52 and l52 and h52!=l52:
            sec("52-Week Range")
            pos=sdiv(ph-l52,h52-l52,0)*100; pfh=sdiv(ph-h52,h52,0)*100
            ca2,cb2=st.columns([3,1])
            with ca2:
                st.markdown(
                    f"<div style='background:#fafafa;border:1px solid #e4e4e7;border-radius:8px;"
                    f"padding:0.7rem 0.9rem;'>"
                    f"<div style='display:flex;justify-content:space-between;margin-bottom:4px;'>"
                    f"<span style='font-size:0.68rem;color:#71717a;'>Low ₹{l52:,.0f}</span>"
                    f"<span style='font-size:0.76rem;font-weight:700;'>📍 ₹{ph:,.1f} ({pos:.0f}th%ile)</span>"
                    f"<span style='font-size:0.68rem;color:#71717a;'>High ₹{h52:,.0f}</span></div>"
                    f"{pbbar(pos,'linear-gradient(90deg,#dc2626 0%,#f59e0b 50%,#16a34a 100%)')}"
                    f"</div>",unsafe_allow_html=True)
            with cb2: mcard("From 52W High",f"{pfh:+.1f}%","","#16a34a" if pfh>-5 else "#dc2626")

        sec("Volume Analysis")
        cv=m.get("vol"); v20=m.get("v20")
        c1,c2,c3,c4=st.columns(4)
        with c1: mcard("Today Vol",f"{cv:,.0f}" if cv else "N/A","Shares")
        with c2: mcard("20D Avg Vol",f"{v20:,.0f}" if v20 else "N/A","Rolling avg")
        with c3:
            if cv and v20 and v20>0:
                vr=cv/v20; vc2="#16a34a" if vr>1.5 else("#dc2626" if vr<0.5 else "#d97706")
                vl="📈 Spike" if vr>1.5 else("📉 Dry" if vr<0.5 else "➡️ Normal")
                mcard("Vol Ratio",f"{vr:.2f}×",vl,vc2)
            else: mcard("Vol Ratio","N/A","—")
        with c4:
            vp=m.get("vp")
            mcard("Price Volatility (20D)",f"{vp:.1f}%" if vp else "N/A","std dev","#16a34a" if vp and vp<5 else "#d97706")

    # ── TAB 2: FUNDAMENTALS ──
    with T2:
        sec("Valuation")
        pe_v=m.get("pe")
        pe_c=("#16a34a" if pe_v and pe_v<25 else "#d97706" if pe_v and pe_v<40 else "#dc2626") if pe_v else "#71717a"
        c1,c2,c3,c4,c5=st.columns(5)
        with c1: mcard("Trailing PE",fn(m.get("pe"),1),"< 25 ideal",pe_c)
        with c2: mcard("Forward PE",fn(m.get("fpe"),1),"Estimated")
        with c3: mcard("Price/Book",fn(m.get("pb"),2),"< 3 ideal")
        with c4: mcard("Price/Sales",fn(m.get("ps"),2),"Revenue mult.")
        with c5: mcard("PEG",fn(m.get("peg"),2),"< 1 cheap")

        sec("Profitability")
        roe_v=m.get("roe"); pm_v=m.get("pm")
        c1,c2,c3,c4,c5=st.columns(5)
        with c1: mcard("ROE",fp(roe_v),"> 15%","#16a34a" if roe_v and roe_v>0.15 else "#dc2626" if roe_v else "#71717a")
        with c2: mcard("ROA",fp(m.get("roa")),"Asset return")
        with c3: mcard("Net Margin",fp(pm_v),"> 10%","#16a34a" if pm_v and pm_v>0.10 else "#dc2626" if pm_v else "#71717a")
        with c4: mcard("Gross Margin",fp(m.get("gm")),"Quality")
        with c5: mcard("Oper. Margin",fp(m.get("om")),"Efficiency")

        sec("Balance Sheet & Cash Flow")
        de_v=m.get("de"); cr_v=m.get("cr"); fcf_v=m.get("fcf"); de_r=de_v/100 if de_v else None
        c1,c2,c3,c4,c5=st.columns(5)
        with c1: mcard("Debt/Equity",f"{de_r:.2f}x" if de_r else "N/A","< 1x","#16a34a" if de_r and de_r<1 else "#dc2626" if de_r else "#71717a")
        with c2: mcard("Current Ratio",fn(cr_v,2),"> 1.5","#16a34a" if cr_v and cr_v>1.5 else "#dc2626" if cr_v else "#71717a")
        with c3: mcard("Quick Ratio",fn(m.get("qr"),2),"Acid test")
        with c4: mcard("Free Cash Flow",fc(fcf_v),"Positive=healthy","#16a34a" if fcf_v and fcf_v>0 else "#dc2626" if fcf_v else "#71717a")
        with c5: mcard("Oper. Cash Flow",fc(m.get("ocf")),"Generated")

        sec("Growth & EPS")
        rg_v=m.get("rg"); eg_v=m.get("eg")
        c1,c2,c3,c4,c5=st.columns(5)
        with c1: mcard("Revenue Growth",fp(rg_v),"YoY","#16a34a" if rg_v and rg_v>0 else "#dc2626" if rg_v else "#71717a")
        with c2: mcard("Earnings Growth",fp(eg_v),"YoY","#16a34a" if eg_v and eg_v>0 else "#dc2626" if eg_v else "#71717a")
        with c3: mcard("Trailing EPS",fn(m.get("eps"),2),"Per share")
        with c4: mcard("Forward EPS",fn(m.get("feps"),2),"Estimated")
        with c5: mcard("Dividend Yield",fp(m.get("dy"),2),"Annual")

        desc=_v(data["info"],"longBusinessSummary",default="")
        if desc:
            with st.expander("📖 About"):
                st.markdown(f"<p style='font-size:0.83rem;line-height:1.8;color:#3f3f46;'>{desc[:1400]}{'…' if len(desc)>1400 else ''}</p>",unsafe_allow_html=True)

    # ── TAB 3: AI VERDICT ──
    with T3:
        ca2,cb2=st.columns([1,2])
        with ca2:
            fig_g=gauge_chart(total,grade,color)
            if fig_g: st.plotly_chart(fig_g,use_container_width=True,config={"displayModeBar":False})
        with cb2:
            sec("Score by Pillar")
            pc_map={"Valuation":"#2563eb","Profitability":"#16a34a","Fin. Health":"#7c3aed","Technical":"#d97706","Growth":"#0891b2"}
            for pillar,pts in bd.items():
                pc2=pc_map.get(pillar,"#71717a"); bc2="🟢" if pts>=15 else("🟡" if pts>=10 else "🔴")
                st.markdown(
                    f"<div style='background:#fafafa;border:1px solid #e4e4e7;border-radius:6px;"
                    f"padding:0.55rem 0.85rem;margin-bottom:0.3rem;'>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;'>"
                    f"<div style='font-size:0.78rem;font-weight:600;'>{pillar}</div>"
                    f"<div style='font-size:0.72rem;font-weight:700;color:{pc2};'>{bc2} {pts}/20</div></div>"
                    f"{pbbar(pts/20*100,pc2)}</div>",unsafe_allow_html=True)
        sec("Investment Summary")
        ab="above" if price>(m.get("d200") or 0) else "below"
        if total>=75: st.success(f"**{ticker}** → **{total}/100 — {grade}**. ROE {fp(m.get('roe'))}, D/E {fn(sdiv(m.get('de'),100),2) if m.get('de') else 'N/A'}x. Piotroski {pio_s}/9. Trading {ab} 200 DMA."+(f" IV upside: {iv.get('up'):.1f}%." if iv.get('up') else ""))
        elif total>=45: st.warning(f"**{ticker}** → **{total}/100 — {grade}**. Mixed signals. Piotroski {pio_s}/9.")
        else: st.error(f"**{ticker}** → **{total}/100 — {grade}**. High risk. Piotroski {pio_s}/9.")
        st.info("⚠️ Research tool only — Not SEBI registered advice.")

    # ── TAB 4: PIOTROSKI ──
    with T4:
        pc=("#16a34a" if pio_s>=7 else "#d97706" if pio_s>=5 else "#dc2626")
        pt="Strong 💪" if pio_s>=7 else("Moderate" if pio_s>=5 else "Weak ⚠️")
        ca2,cb2=st.columns([1,2])
        with ca2:
            st.markdown(
                f"<div style='background:#fafafa;border:1px solid #e4e4e7;border-radius:10px;"
                f"text-align:center;padding:1.75rem 1rem;'>"
                f"<div style='font-size:0.6rem;font-weight:700;text-transform:uppercase;"
                f"letter-spacing:0.07em;color:#71717a;margin-bottom:4px;'>PIOTROSKI F-SCORE</div>"
                f"<div style='font-size:5rem;font-weight:800;color:{pc};line-height:1;"
                f"font-family:JetBrains Mono,monospace;'>{pio_s}</div>"
                f"<div style='font-size:0.7rem;color:#71717a;margin:3px 0 8px;'>out of 9</div>"
                f"{pbbar(pio_s/9*100,pc)}"
                f"<div style='margin-top:8px;font-size:0.76rem;font-weight:700;color:{pc};'>{pt}</div>"
                f"</div>",unsafe_allow_html=True)
        with cb2:
            sec("F-Score Breakdown")
            gn={"P":"Profitability","L":"Leverage","E":"Efficiency"}; gps={}
            for c in pio_c: gps.setdefault(c["g"],[]).append(c)
            for gk,items in gps.items():
                gs=sum(1 for x in items if x["p"])
                st.markdown(f"<div style='font-size:0.62rem;font-weight:700;text-transform:uppercase;"
                            f"letter-spacing:0.05em;color:#a1a1aa;margin:8px 0 3px;'>{gn.get(gk,gk)} ({gs}/{len(items)})</div>",unsafe_allow_html=True)
                for item in items:
                    ic="✅" if item["p"] else "❌"; bg="#f0fdf4" if item["p"] else "#fef2f2"; tc="#15803d" if item["p"] else "#b91c1c"
                    st.markdown(f"<div class='ck' style='background:{bg};'><span style='font-size:0.82rem;'>{ic}</span>"
                                f"<div><div style='font-size:0.76rem;font-weight:600;color:{tc};'>{item['n']}</div>"
                                f"<div style='font-size:0.65rem;color:#71717a;'>{item['note']}</div></div></div>",unsafe_allow_html=True)
        st.info("ℹ️ Piotroski: 7–9 = Strong · 4–6 = Moderate · 0–3 = Weak")

    # ── TAB 5: INTRINSIC VALUE ──
    with T5:
        sec("Intrinsic Value Estimates")
        curr_p=m.get("price") or m.get("ph")
        c1,c2,c3,c4=st.columns(4)
        gv=iv.get("graham"); dv=iv.get("dcf"); avg_iv=iv.get("avg"); up_v=iv.get("up"); mos_v=iv.get("mos")
        with c1:
            if gv and curr_p: diff=sdiv(curr_p-gv,gv,0)*100; mcard("Graham Number",f"₹{gv:,.1f}",f"{'Under' if curr_p<gv else 'Over'}valued {abs(diff):.1f}%","#16a34a" if curr_p<gv else "#dc2626")
            else: mcard("Graham Number","N/A","EPS/BVPS N/A")
        with c2:
            if dv and curr_p: diff2=sdiv(curr_p-dv,dv,0)*100; mcard("Graham DCF",f"₹{dv:,.1f}",f"{'Under' if curr_p<dv else 'Over'}valued {abs(diff2):.1f}%","#16a34a" if curr_p<dv else "#dc2626")
            else: mcard("Graham DCF","N/A","EPS/Growth N/A")
        with c3:
            if avg_iv and curr_p: mcard("Blended IV",f"₹{avg_iv:,.1f}",f"{'↑' if up_v and up_v>0 else '↓'} {abs(up_v):.1f}% | MOS: {mos_v:.1f}%","#16a34a" if up_v and up_v>0 else "#dc2626")
            else: mcard("Blended IV","N/A","Insufficient data")
        with c4:
            at=iv.get("at"); au=iv.get("au")
            if at and au is not None: mcard("Analyst Target",f"₹{at:,.1f}",f"Upside: {au:+.1f}%","#16a34a" if au>0 else "#dc2626")
            else: mcard("Analyst Target","N/A","Not available")
        if avg_iv and curr_p:
            if mos_v>20: st.success(f"✅ **MOS: {mos_v:.1f}%** — Significantly undervalued. Upside: {up_v:.1f}%")
            elif mos_v>0: st.success(f"✅ Marginally undervalued. MOS: {mos_v:.1f}%")
            elif mos_v>-20: st.warning(f"⚠️ Near fair value. Overvalued by {abs(mos_v):.1f}%.")
            else: st.error(f"🚨 Overvalued {abs(mos_v):.1f}%. Downside: {abs(up_v):.1f}%.")
        st.info("ℹ️ Graham Number = √(22.5 × EPS × BVPS). DCF uses India bond yield ~7.5%.")

    # ── TAB 6: HOLDERS ──
    with T6:
        sec("Major Holders")
        mh_df=data.get("mh",pd.DataFrame())
        if mh_df is not None and not mh_df.empty:
            try: st.dataframe(mh_df,use_container_width=True,hide_index=True)
            except: st.warning("Could not display major holders.")
        else: st.info("Major holders data not available.")

        sec("Institutional Holders (Top 10)")
        ih_df=data.get("ih",pd.DataFrame())
        if ih_df is not None and not ih_df.empty:
            try:
                d=ih_df.head(10).copy()
                if "Value" in d.columns:
                    d["Value"]=d["Value"].apply(lambda x: f"₹{x/1e7:.1f}Cr" if isinstance(x,(int,float)) and not math.isnan(float(x)) else "N/A")
                if "% Out" in d.columns:
                    d["% Out"]=d["% Out"].apply(lambda x: f"{float(x)*100:.2f}%" if isinstance(x,(int,float)) else str(x))
                st.dataframe(d,use_container_width=True,hide_index=True)
                st.info("🟢 Rising institutional holding = positive signal.")
            except: st.warning("Could not display institutional holders.")
        else: st.info("Institutional holders data not available.")

    # ── TAB 7: TRENDS + NOTES ──
    with T7:
        sec("📊 Google Trends — India Search Interest (30 Days)")
        kw=ticker.replace(".NS","").replace(".BO","")
        with st.spinner("Fetching Google Trends…"):
            tdf,terr=fetch_trends(kw)
        if terr:
            st.warning(f"⚠️ {terr}")
        elif tdf is not None and not tdf.empty:
            try:
                import plotly.graph_objects as go
                half=len(tdf)//2; f1=tdf[kw].iloc[:half].mean(); f2=tdf[kw].iloc[half:].mean()
                growth=sdiv(f2-f1,f1,0)*100; vp=m.get("vp") or 999
                fig_t=go.Figure()
                fig_t.add_trace(go.Scatter(x=tdf.index,y=tdf[kw],
                    line=dict(color="#7c3aed",width=2),fill="tozeroy",fillcolor="rgba(124,58,237,.08)"))
                fig_t.update_layout(height=180,margin=dict(l=0,r=0,t=10,b=0),
                    paper_bgcolor="#fff",plot_bgcolor="#fff",template="plotly_white",showlegend=False,
                    yaxis=dict(range=[0,105],gridcolor="#f4f4f5",tickfont=dict(size=10)),
                    xaxis=dict(gridcolor="#f4f4f5",tickfont=dict(size=10)))
                st.plotly_chart(fig_t,use_container_width=True,config={"displayModeBar":False})
                c1,c2,c3=st.columns(3)
                with c1: mcard("Current Interest",f"{tdf[kw].iloc[-1]:.0f}/100","Google scale")
                with c2: mcard("30-Day Growth",f"{growth:+.1f}%","Search trend","#16a34a" if growth>15 else "#71717a")
                with c3: mcard("Price Volatility",f"{vp:.1f}%" if vp!=999 else "N/A","20D std","#16a34a" if vp<5 else "#d97706")
                if growth>15 and vp<5:
                    st.markdown(
                        f"<div style='background:linear-gradient(135deg,#fefce8,#fef9c3);"
                        f"border:2px solid #f59e0b;border-radius:10px;"
                        f"padding:0.85rem 1.1rem;margin:.65rem 0;text-align:center;'>"
                        f"<div style='font-size:1.3rem;'>🚨</div>"
                        f"<div style='font-size:0.95rem;font-weight:800;color:#92400e;margin:.2rem 0;'>ACCUMULATION ZONE DETECTED</div>"
                        f"<div style='font-size:0.8rem;color:#78350f;line-height:1.6;'>"
                        f"Search interest ↑<b>{growth:+.1f}%</b> · Volatility only <b>{vp:.1f}%</b><br>"
                        f"Quiet accumulation — institutions may be buying before breakout.</div>"
                        f"</div>",unsafe_allow_html=True)
                elif growth>15: st.success(f"📈 Rising interest ({growth:+.1f}%) — Watch for breakout.")
                elif growth<-15: st.warning(f"📉 Declining interest ({growth:+.1f}%) — Caution.")
                else: st.info("ℹ️ Stable interest — No extreme signals.")
            except Exception as e:
                st.warning(f"Trends chart error: {e}")
        else:
            st.warning("⚠️ Trends data not available for this ticker.")

        st.divider()
        sec("📝 My Research Notes")
        existing,last_upd=load_note(ticker)
        if st.button("📋 Load Template",key=f"tmpl_{ticker}"):
            existing=(f"📌 {ticker}  |  📅 {datetime.date.today()}\n\n🎯 THESIS:\n\n"
                      f"📊 METRICS:\n- PE:\n- ROE:\n- D/E:\n- FCF:\n- Piotroski: /9\n- AI: /100\n- IV: ₹\n\n"
                      f"⚠️ RISKS:\n\n🎯 TRADE:\n- Entry: ₹  Stop: ₹  Target: ₹\n\n✅ DECISION:")
        note=st.text_area("",value=existing,height=260,key=f"note_{ticker}",label_visibility="collapsed")
        nc1,nc2=st.columns([3,1])
        with nc1:
            if st.button("💾 Save Note",key=f"save_{ticker}",use_container_width=True,type="primary"):
                save_note(ticker,note); st.success("✅ Saved!")
        with nc2:
            if last_upd: st.caption(f"Saved: {last_upd}")

# ═══════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════
p=st.session_state.page
if p=="🔍 Stock Discovery": page_discovery()
elif p=="📋 My Watchlist":  page_watchlist()
elif p=="📊 Deep Analysis": page_analysis()

st.markdown(
    "<div style='text-align:center;font-size:0.63rem;color:#a1a1aa;"
    "padding:0.5rem 0 1.5rem;border-top:1px solid #e4e4e7;margin-top:0.75rem;'>"
    "📊 Stock Analysis Pro v5.1 · Money Financial Services · "
    "Yahoo Finance + Google Trends · Educational only · Not SEBI advice"
    "</div>",unsafe_allow_html=True)
