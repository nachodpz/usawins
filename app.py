from fastapi import FastAPI
import yfinance as yf
import feedparser

app = FastAPI(title="Rick&Nacho USAwins", version="1.0")

# === Lista completa NASDAQ-100 (agosto 2025) ===
tickers = [
    # Tecnología & software
    "ADBE","AMD","INTC","ISRG","INTU","CRWD","DDOG","APP","TEAM","ADSK","AAPL","AMAT","ARM",
    "ASML","AVGO","CDNS","CSCO","CTSH","FAST","FTNT","GFS","KLAC","LRCX","MRVL","MCHP","MU",
    "MSFT","NVDA","NXPI","PANW","PAYX","PYPL","QCOM","ROP","SHOP","SNPS","WDAY","ZS",
    # Servicios & plataformas
    "ABNB","GOOGL","GOOG","AMZN","META","DASH","EA","TMUS","TTWO","BIDU","MDB",
    # Salud & biotecnología
    "AMGN","BIIB","AZN","GEHC","GILD","IDXX","REGN","VRTX",
    # Consumo & retail
    "BKNG","COST","LULU","MELI","MNST","SBUX","TSLA","ROST","PDD","PEP","KDP","MDLZ",
    # Industriales & transporte
    "ADP","AXON","CEG","CTAS","CSX","HON","ODFL","PCAR","TRI","TWLO","WBD","XEL",
    # Utilities & energía
    "AEP","BKR","EXC",
    # Otros sectores
    "CCEP","CSGP","LIN","TTD",
    # Inclusiones recientes
    "PLTR","MSTR","AXON",
]

# ---------- Utilidades comunes ----------

def get_news(ticker: str):
    """2 titulares recientes de Yahoo Finance para el ticker."""
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:2]:
        items.append({"title": entry.title, "link": entry.link})
    return items

# ---------- PRE-MARKET (ya existía) ----------

def get_premarket_data(ticker: str):
    """
    Calcula el gap pre-market: último cierre vs. última vela extended (prepost=True).
    Usa 30m para aligerar llamadas.
    """
    stock = yf.Ticker(ticker)
    data = stock.history(period="5d", prepost=True, interval="30m")
    if len(data) < 2:
        return None
    last_close = float(data["Close"].iloc[-2])
    premarket = float(data["Close"].iloc[-1])
    gap = (premarket - last_close) / last_close * 100
    return gap, premarket

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok", "message": "Rick&Nacho USAwins API is running"}

@app.get("/premarket/ideas")
def premarket_ideas(limit: int = 5, min_gap: float = 0.5):
    results = []
    for t in tickers:
        try:
            data = get_premarket_data(t)
            if not data:
                continue
            gap, price = data
            if abs(gap) >= min_gap:
                news = get_news(t)
                results.append({
                    "ticker": t,
                    "gap_pct": round(gap, 2),
                    "premarket_price": round(price, 2),
                    "news": news
                })
        except Exception:
            continue
    results.sort(key=lambda x: abs(x["gap_pct"]), reverse=True)
    return results[:limit]

# ---------- NUEVO: LIVE (mercado abierto / post-market) ----------

def get_live_data(ticker: str):
    """
    Movimiento intradía: precio actual (última vela 5m) vs. CIERRE anterior.
    Devuelve (move_pct, last_price, session_volume).
    """
    stock = yf.Ticker(ticker)

    # Últimas velas de hoy (incluye pre/post por si consultas fuera de horario)
    intraday = stock.history(period="1d", interval="5m", prepost=True)
    if len(intraday) == 0:
        return None
    last_price = float(intraday["Close"].iloc[-1])
    session_vol = int(intraday["Volume"].sum())

    # Cierre del día anterior
    daily = stock.history(period="2d", interval="1d")
    if len(daily) < 2:
        return None
    prev_close = float(daily["Close"].iloc[-2])

    move_pct = (last_price - prev_close) / prev_close * 100
    return move_pct, last_price, session_vol

@app.get("/live_movers")
def live_movers(limit: int = 5, min_move: float = 1.0):
    """
    Top movimientos durante el mercado (o post-market) por % contra el cierre previo.
    Filtra por |move| >= min_move. Ordena por magnitud.
    """
    results = []
    for t in tickers:
        try:
            data = get_live_data(t)
            if not data:
                continue
            move, price, vol = data
            if abs(move) >= min_move:
                news = get_news(t)
                results.append({
                    "ticker": t,
                    "session_move_pct": round(move, 2),
                    "last_price": round(price, 2),
                    "session_volume": vol,
                    "news": news
                })
        except Exception:
            continue
    results.sort(key=lambda x: abs(x["session_move_pct"]), reverse=True)
    return results[:limit]
