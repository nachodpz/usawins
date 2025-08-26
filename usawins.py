import yfinance as yf
import feedparser

# === LISTA COMPLETA NASDAQ-100 (agosto 2025) ===
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
    return gap, premarket

def get_news(ticker):
    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
    feed = feedparser.parse(url)
    news_items = []
    for entry in feed.entries[:2]:  # solo 2 titulares
        news_items.append(f"{entry.title} ({entry.link})")
    return news_items

print("=== Rick&Nacho USAwins — Radar Pre-market Nasdaq100 ===")
results = []

for t in tickers:
    try:
        data = get_premarket_data(t)
        if not data:
            continue
        gap, price = data
        if abs(gap) >= 0.5:  # umbral bajo
            news = get_news(t)
            results.append((t, gap, price, news))
    except Exception:
        continue

# Mostrar resultados
if not results:
    print("Hoy no hay movimientos relevantes en el Nasdaq-100.")
else:
    results.sort(key=lambda x: abs(x[1]), reverse=True)  # orden por gap
    for t, gap, price, news in results[:10]:  # top 10
        print(f"\n{t} — Gap: {gap:.2f}% | Precio premarket: {price:.2f}")
        if news:
            for n in news:
                print(f" • {n}")
        else:
            print(" • (sin noticias recientes)")
