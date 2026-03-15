from flask import Flask, render_template, request
import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyArrowPatch
import base64
import io
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

POPULAR_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
    "TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS", "WIPRO.NS"
]

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    if hist.empty:
        return None, None
    info = stock.info
    name = info.get("longName") or info.get("shortName") or ticker
    return hist, name

def predict_next_day(hist):
    closes = hist['Close'].values
    X = np.arange(len(closes)).reshape(-1, 1)
    y = closes
    model = LinearRegression()
    model.fit(X, y)
    next_day = np.array([[len(closes)]])
    predicted = model.predict(next_day)[0]
    return round(float(predicted), 2)

def get_trend(hist):
    last_30 = hist['Close'].tail(30)
    if len(last_30) < 2:
        return "neutral"
    start = last_30.iloc[0]
    end = last_30.iloc[-1]
    pct = ((end - start) / start) * 100
    return pct

def get_downtrend_stocks():
    downtrend = []
    for ticker in POPULAR_STOCKS:
        try:
            hist = yf.Ticker(ticker).history(period="35d")
            if hist.empty or len(hist) < 5:
                continue
            pct = get_trend(hist)
            if pct < -1.5:
                current = round(float(hist['Close'].iloc[-1]), 2)
                downtrend.append({
                    "ticker": ticker,
                    "pct": round(float(pct), 2),
                    "price": current
                })
        except:
            continue
    downtrend.sort(key=lambda x: x["pct"])
    return downtrend

def generate_chart(hist, ticker, predicted_price):
    fig, ax = plt.subplots(figsize=(11, 4.5))
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#0d1117')

    dates = hist.index
    closes = hist['Close'].values

    # Gradient line effect using segments
    from matplotlib.collections import LineCollection
    points = np.array([mdates.date2num(d.to_pydatetime()) for d in dates])
    segs_x = np.array(list(zip(points[:-1], points[1:])))
    segs_y = np.array(list(zip(closes[:-1], closes[1:])))
    segments = [[(x[0], y[0]), (x[1], y[1])] for x, y in zip(segs_x, segs_y)]

    trend_color = '#00e5a0' if closes[-1] >= closes[0] else '#ff4d6d'
    lc = LineCollection(segments, colors=trend_color, linewidths=2, alpha=0.9)
    ax.add_collection(lc)

    # Fill under line
    ax.fill_between(
        [mdates.date2num(d.to_pydatetime()) for d in dates],
        closes, closes.min(),
        alpha=0.08, color=trend_color
    )

    # 30-day moving average
    if len(closes) >= 30:
        ma30 = np.convolve(closes, np.ones(30)/30, mode='valid')
        ma_dates = dates[29:]
        ax.plot(
            [mdates.date2num(d.to_pydatetime()) for d in ma_dates],
            ma30, color='#f0a500', linewidth=1.2, alpha=0.7, linestyle='--', label='30-day MA'
        )

    # Predicted point
    next_date = dates[-1] + timedelta(days=1)
    next_num = mdates.date2num(next_date.to_pydatetime())
    ax.scatter([next_num], [predicted_price], color='#ffffff', s=100, zorder=5, linewidths=2, edgecolors='#f0a500')
    ax.annotate(
        f'  ₹{predicted_price:.2f}' if '.NS' in ticker else f'  ${predicted_price:.2f}',
        (next_num, predicted_price),
        fontsize=9, color='#f0a500', fontweight='bold',
        va='center'
    )

    # Current price marker
    ax.scatter([mdates.date2num(dates[-1].to_pydatetime())], [closes[-1]],
               color=trend_color, s=70, zorder=5)

    # Axes styling
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.tick_params(colors='#8b949e', labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#21262d')
    ax.set_xlim(mdates.date2num(dates[0].to_pydatetime()),
                mdates.date2num(next_date.to_pydatetime()) + 5)
    ax.set_ylabel('Price', color='#8b949e', fontsize=9)
    ax.grid(axis='y', color='#21262d', linewidth=0.6, linestyle='-')
    ax.grid(axis='x', color='#21262d', linewidth=0.3, linestyle=':')
    ax.legend(loc='upper left', fontsize=8, framealpha=0, labelcolor='#f0a500')

    plt.tight_layout(pad=1.0)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=130, bbox_inches='tight',
                facecolor='#0d1117', edgecolor='none')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    downtrend_stocks = get_downtrend_stocks()

    if request.method == 'POST':
        ticker = request.form.get('ticker', '').strip().upper()
        if not ticker:
            error = "Please enter a stock ticker."
        else:
            try:
                hist, stock_name = get_stock_data(ticker)
                if hist is None or len(hist) < 10:
                    error = f"Could not fetch data for '{ticker}'. Please check the ticker symbol."
                else:
                    current_price = round(float(hist['Close'].iloc[-1]), 2)
                    predicted_price = predict_next_day(hist)
                    trend_pct = get_trend(hist)
                    currency = "₹" if ".NS" in ticker or ".BO" in ticker else "$"

                    if trend_pct > 0:
                        suggestion = "Uptrend – May be good to invest"
                        suggestion_class = "uptrend"
                        trend_icon = "▲"
                    else:
                        suggestion = "Downtrend – Be cautious / avoid investing"
                        suggestion_class = "downtrend"
                        trend_icon = "▼"

                    chart_b64 = generate_chart(hist, ticker, predicted_price)

                    result = {
                        "ticker": ticker,
                        "name": stock_name,
                        "current_price": current_price,
                        "predicted_price": predicted_price,
                        "trend_pct": round(float(trend_pct), 2),
                        "suggestion": suggestion,
                        "suggestion_class": suggestion_class,
                        "trend_icon": trend_icon,
                        "chart": chart_b64,
                        "currency": currency
                    }
            except Exception as e:
                error = f"Error fetching data: {str(e)}"

    return render_template('index.html', result=result, error=error, downtrend_stocks=downtrend_stocks)

if __name__ == '__main__':
    app.run(debug=True)
