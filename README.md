# Nifty 50 ETF Price Tracker 📊

A Python application that tracks Nifty 50 ETF prices in real-time and sends desktop notifications when significant price dips are detected.

## Features ✨

- **Real-time Price Monitoring**: Tracks Nifty 50 ETF (NIFTYBEES) prices using Yahoo Finance
- **Dip Alerts**: Desktop notifications when price drops by a configurable percentage
- **Daily High Tracking**: Monitors drops from the day's highest price
- **Customizable Settings**: Easy configuration through JSON file
- **Live Status Display**: Terminal dashboard showing current price, changes, and statistics

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

## Configuration ⚙️

Edit `config.json` to customize the tracker:

```json
{
    "symbol": "NIFTYBEES.NS",        // ETF symbol to track
    "check_interval": 60,             // Check price every 60 seconds
    "dip_percentage": 1.0,            // Alert on 1% dip from last check
    "dip_from_high": 2.0,             // Alert on 2% dip from today's high
    "alert_sound": true               // Enable notification sound
}
```

### Configuration Options

- **symbol**: Yahoo Finance ticker symbol (default: NIFTYBEES.NS)
- **check_interval**: Seconds between price checks (default: 60)
- **dip_percentage**: Minimum % drop to trigger alert (default: 1.0%)
- **dip_from_high**: % drop from today's high to trigger alert (default: 2.0%)
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
