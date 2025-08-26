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

def get_premarket_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="5d", prepost=True, interval="30m")
    if len(data) < 2:
        return None
    last_close = data["Close"].iloc[-2]
    premarket = data["Close"].iloc[-1]
    gap = (premarket - last_close) / last_close * 100
    return gap, float(premarket)

def get_news(ticker):
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    feed = feedparser.parse(url)
    news_items = []
    for entry in feed.entries[:2]:
        news_items.append({"title": entry.title, "link": entry.link})
    return news_items

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
                    "premarket_price": price,
                    "news": news
                })
        except Exception:
            continue

    results.sort(key=lambda x: abs(x["gap_pct"]), reverse=True)
    return results[:limit]
