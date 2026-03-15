# StockSense – ML Stock Price Prediction Dashboard
### MCA Student Project | Flask + yfinance + scikit-learn

---

## Features
- Real-time stock data via yfinance (US & Indian NSE stocks)
- Next-day price prediction using Linear Regression (scikit-learn)
- 30-day trend analysis with investment suggestion
- 1-year closing price chart (matplotlib, embedded as base64)
- Sidebar: auto-detected downtrend stocks to avoid
- Fully responsive dark UI (mobile + desktop)

---

## Project Structure
```
StockPrediction/
├── app.py
├── requirements.txt
├── README.md
└── templates/
    └── index.html
```

---

## Setup & Run

### 1. Install dependencies
```bash
pip install flask yfinance scikit-learn numpy matplotlib
```

### 2. Run the app
```bash
python app.py
```

### 3. Open in browser
```
http://127.0.0.1:5000
```

---

## Supported Tickers
| Exchange | Examples |
|----------|----------|
| US (NASDAQ/NYSE) | AAPL, MSFT, TSLA, GOOGL, AMZN |
| NSE India | TCS.NS, INFY.NS, RELIANCE.NS, HDFCBANK.NS, WIPRO.NS |
| BSE India | Use `.BO` suffix e.g. TCS.BO |

---

## Deployment

### Render
1. Push project to GitHub
2. Create a new Web Service on render.com
3. Set Start Command: `python app.py`
4. Set Build Command: `pip install -r requirements.txt`

### PythonAnywhere
1. Upload files via Files tab
2. Create a new Web App → Flask
3. Point WSGI file to `app.py`

### Replit
1. Import from GitHub or paste files
2. Set run command: `python app.py`

---

## Tech Stack
- **Backend**: Python 3.x, Flask
- **Data**: yfinance
- **ML**: scikit-learn LinearRegression, numpy
- **Charts**: matplotlib (base64 embedded)
- **Frontend**: HTML5, CSS3 (no frameworks, fully responsive)

---

*This project is for educational purposes only. Not financial advice.*
