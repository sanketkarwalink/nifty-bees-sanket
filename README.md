# Nifty 50 ETF Price Tracker 📊

A Python application that tracks Indian ETF prices with smart buy signals for long-term investing.

## 🎯 Two Tracking Modes

### 1. Single ETF Tracker (nifty_tracker.py)
- Track one ETF with deep historical analysis
- 90-day historical data with value zones
- 3 smart buy strategies
- Detailed investment recommendations

### 2. Multi-ETF Tracker (multi_etf_tracker.py) ⭐ NEW!
- Track multiple ETFs simultaneously
- Compare opportunities across ETFs
- Unified dashboard with all prices
- Get alerts for the best opportunities
- Perfect for portfolio management

## Features ✨

- **90-Day Historical Analysis**: Calculate price percentiles and identify value zones
- **Smart Buy Signals**: 3 data-driven strategies for finding entry points
- **Telegram Alerts**: Get actionable buy/sell signals on your phone
- **Investment Recommendations**: Exact amounts to invest based on your portfolio
- **Multi-ETF Comparison**: See all opportunities side-by-side
- **Rate Limit Handling**: Robust retry logic for Yahoo Finance API

## Installation 🚀

### Prerequisites
- Python 3.7 or higher
- macOS (for desktop notifications)

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd "/Users/sanketkarwa/Project STOCK"
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start 🚀

### Option 1: Interactive Runner (Easiest)
```bash
./run_tracker.sh
```
Choose between single or multi-ETF tracking!

### Option 2: Run Directly

**Single ETF Tracker:**
```bash
python3 nifty_tracker.py
```

**Multi-ETF Tracker:**
```bash
python3 multi_etf_tracker.py
```

## Configuration ⚙️

### Single ETF (config.json)
```json
{
    "symbol": "NIFTYBEES.NS",
    "check_interval": 60,
    "dip_from_high": 1.0,
    "moving_avg_period": 20,
    "alert_cooldown_minutes": 30,
    "telegram_alerts": true,
    "investment_config": {
        "portfolio_amount": 100000,
        "target_allocation": 0.20,
        "buy_on_dip": 1.5,
        "sell_on_spike": 4.0
    }
}
```

### Multi-ETF (config.json)
```json
{
    "etf_symbols": [
        {"symbol": "NIFTYBEES.NS", "name": "Nifty 50", "allocation": 0.15},
        {"symbol": "JUNIORBEES.NS", "name": "Nifty Next 50", "allocation": 0.10},
        {"symbol": "BANKBEES.NS", "name": "Bank Nifty", "allocation": 0.15}
    ],
    ... (same settings as single ETF)
}
```
- **alert_sound**: Enable/disable notification sounds

### Alternative ETF Symbols

You can track other ETFs by changing the symbol:
- `NIFTYBEES.NS` - Nifty 50 ETF
- `JUNIORBEES.NS` - Nifty Next 50 ETF
- `BANKBEES.NS` - Bank ETF
- `LIQUIDBEES.NS` - Liquid ETF

## Usage 🎯

### Start the Tracker

```bash
python nifty_tracker.py
```

### What You'll See

The tracker displays:
- Current timestamp
- Symbol being tracked
- Current price
- Price change from last check
- Today's highest price
- Drop from today's high

### Notifications

You'll receive desktop notifications when:
1. Price drops by more than `dip_percentage` from the previous check
2. Price drops by more than `dip_from_high` from today's highest price

### Stop the Tracker

Press `Ctrl+C` to stop the tracker gracefully.

## Example Output

```
🚀 Starting Nifty 50 ETF Tracker
Symbol: NIFTYBEES.NS
Check Interval: 60 seconds
Dip Alert Threshold: 1.0%
High Dip Alert Threshold: 2.0%

Press Ctrl+C to stop

============================================================
Time: 2025-12-31 14:30:15
Symbol: NIFTYBEES.NS
Current Price: ₹245.50
Change: 📉 ₹-1.20 (-0.49%)
Today's High: ₹250.30
From High: -₹4.80 (-1.92%)
============================================================
```

## How It Works 🔧

1. **Data Source**: Uses Yahoo Finance API through `yfinance` library
2. **Price Monitoring**: Fetches latest 1-minute candle data every interval
3. **Alert Logic**: Compares current price against previous price and daily high
4. **Notifications**: Uses `plyer` library for cross-platform desktop notifications

## Troubleshooting 🔍

### No Data Available
- Check if markets are open (NSE trading hours: 9:15 AM - 3:30 PM IST)
- Verify internet connection
- Ensure the symbol is correct

### Notification Issues
- On macOS, ensure Terminal has notification permissions:
  - System Preferences → Notifications → Terminal → Allow Notifications

### Price Not Updating
- Market hours: NSE operates Monday-Friday (excluding holidays)
- Real-time data may have a slight delay

## Customization Ideas 💡

- Add SMS/Email alerts using Twilio or SMTP
- Track multiple ETFs simultaneously
- Log price history to CSV for analysis
- Add technical indicators (RSI, Moving Averages)
- Create a web dashboard with Flask
- Add buy/sell signal generation

## Dependencies 📦

- **yfinance**: Fetches real-time stock data from Yahoo Finance
- **plyer**: Cross-platform desktop notifications

## Deploy to Fly.io (always-on) 🚀

1) Install flyctl and log in

- macOS: `brew install flyctl`
- Log in: `flyctl auth login`

2) Build and deploy

- From the repo root: `flyctl launch --copy-config --no-deploy --machines`
- This reuses `Dockerfile` and `fly.toml` (worker app; no HTTP port needed).

3) Set secrets (avoid keeping passwords in config.json)

```bash
flyctl secrets set \
   EMAIL_SENDER="you@example.com" \
   EMAIL_PASSWORD="app-password" \
   EMAIL_RECEIVER="you@example.com" \
   SMTP_SERVER="smtp.gmail.com" \
   SMTP_PORT="587" \
   PORTFOLIO_AMOUNT="0" \
   TARGET_ALLOCATION="0.40"
```

4) Deploy a machine and keep it running

- `flyctl deploy --machines --ha=false`
- Check status: `flyctl status`
- View logs: `flyctl logs`

Notes

- The app runs headless in the container. Config changes in `config.json` can still hot-reload if you bake a new image or mount a volume; for secrets and sizing, prefer env vars (already supported).
- Default region in `fly.toml` is `sin`; change `primary_region` if you want a closer region.

## Deploy to Render (no card) 🆓

Render free **Web Service** is used (worker is paid). `web_runner.py` runs the tracker in a background thread and serves `/health` for Render.

1) Connect repo to Render

- Push this repo to GitHub. In Render: "New" → "Blueprint" → repo URL. Branch `main`.

2) Verify `render.yaml`

- Type `web`, plan `free`, region `singapore`, healthCheckPath `/health`.
- Auto-deploy is off; you deploy manually.

3) Set environment variables (Settings → Environment)

- `EMAIL_SENDER`, `EMAIL_PASSWORD`, `EMAIL_RECEIVER`, `SMTP_SERVER`, `SMTP_PORT`
- `PORTFOLIO_AMOUNT`, `TARGET_ALLOCATION`
- Optional: `HEADLESS=true` (defaults true) and `symbol` override if needed.

4) Deploy

- Click "Manual Deploy" → "Deploy latest commit" for the web service.
- Check logs to confirm the tracker loop is running; `/health` returns 200.

Notes

- Keep secrets out of `config.json`; env vars override at runtime.
- If you change code/config defaults, deploy again to bake changes into the image.

## License

Free to use and modify for personal and commercial purposes.

## Disclaimer ⚠️

This tool is for informational purposes only. Not financial advice. Always do your own research before making investment decisions.
