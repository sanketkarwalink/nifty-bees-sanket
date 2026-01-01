#!/bin/bash

# Multi-ETF Tracker Runner
# Choose which tracker to run

echo "📊 ETF Tracker Options:"
echo ""
echo "1. Single ETF Tracker (NIFTYBEES only)"
echo "2. Multi-ETF Tracker (Compare multiple ETFs) ⭐"
echo ""
read -p "Choose option (1 or 2): " choice

case $choice in
    1)
        echo "Starting Single ETF Tracker..."
        python3 nifty_tracker.py
        ;;
    2)
        echo "Starting Multi-ETF Tracker..."
        python3 multi_etf_tracker.py
        ;;
    *)
        echo "Invalid choice. Starting Multi-ETF Tracker by default..."
        python3 multi_etf_tracker.py
        ;;
esac
