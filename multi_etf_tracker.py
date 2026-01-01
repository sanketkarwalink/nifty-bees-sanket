"""
Multi-ETF Tracker - Track multiple ETFs and compare opportunities
Extension of the single ETF tracker for portfolio management
"""

import yfinance as yf
import time
import json
from datetime import datetime
from nifty_tracker import NiftyTracker

class MultiETFTracker:
    def __init__(self, config_file='config.json'):
        """Initialize multi-ETF tracker"""
        self.config_file = config_file
        self.load_config()
        
        # Create individual trackers for each ETF
        self.trackers = {}
        for symbol_info in self.etf_symbols:
            symbol = symbol_info['symbol']
            print(f"\n{'='*60}")
            print(f"Initializing {symbol_info['name']} ({symbol})")
            print(f"{'='*60}")
            
            # Create a single tracker instance for this symbol
            # We'll patch it to use the specific symbol
            tracker = NiftyTracker(self.config_file)
            tracker.symbol = symbol  # Override symbol
            
            self.trackers[symbol] = {
                'tracker': tracker,
                'name': symbol_info['name'],
                'allocation': symbol_info['allocation']
            }
            
            time.sleep(2)  # Avoid rate limits
        
        print(f"\n{'='*60}")
        print(f"✅ All ETFs initialized")
        print(f"{'='*60}\n")
    
    def load_config(self):
        """Load multi-ETF configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        except:
            config = {}
        
        # ETFs to track
        self.etf_symbols = config.get('etf_symbols', [
            {'symbol': 'NIFTYBEES.NS', 'name': 'Nifty 50', 'allocation': 0.15},
            {'symbol': 'JUNIORBEES.NS', 'name': 'Nifty Next 50', 'allocation': 0.10},
            {'symbol': 'BANKBEES.NS', 'name': 'Bank Nifty', 'allocation': 0.15},
        ])
        
        # Base config for individual trackers
        self.base_config = config
        self.base_config.pop('etf_symbols', None)  # Remove to avoid confusion
    
    def get_all_prices(self):
        """Get current prices for all ETFs"""
        prices = {}
        for symbol, data in self.trackers.items():
            tracker = data['tracker']
            price, volume = tracker.get_current_price()
            if price:
                prices[symbol] = {
                    'price': price,
                    'volume': volume,
                    'name': data['name'],
                    'allocation': data['allocation'],
                    'percentile': tracker.get_price_percentile(price),
                    'in_value_zone': tracker.is_in_value_zone(price),
                    'historical_stats': tracker.historical_stats
                }
        return prices
    
    def compare_opportunities(self, prices):
        """Compare all ETFs and rank opportunities"""
        opportunities = []
        
        for symbol, data in prices.items():
            if not data.get('percentile'):
                continue
            
            score = 0
            reasons = []
            
            # Lower percentile = better opportunity
            if data['percentile'] <= 30:
                score += 50
                reasons.append(f"In value zone ({data['percentile']}%)")
            elif data['percentile'] <= 50:
                score += 25
                reasons.append(f"Below median ({data['percentile']}%)")
            
            # Check distance from 90-day low
            if data['historical_stats']:
                price_min = data['historical_stats']['min']
                dist_from_low = ((data['price'] - price_min) / price_min) * 100
                if dist_from_low <= 5:
                    score += 30
                    reasons.append(f"Near 90-day low (+{dist_from_low:.1f}%)")
            
            if score > 0:
                opportunities.append({
                    'symbol': symbol,
                    'name': data['name'],
                    'price': data['price'],
                    'percentile': data['percentile'],
                    'allocation': data['allocation'],
                    'score': score,
                    'reasons': reasons,
                    'historical_stats': data.get('historical_stats', {})
                })
        
        # Sort by score (highest first)
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        return opportunities
    
    def send_comparison_alert(self, opportunities):
        """Send Telegram alert comparing all opportunities"""
        if not opportunities:
            return
        
        # Get first tracker for sending alert
        first_tracker = list(self.trackers.values())[0]['tracker']
        
        message = "🎯 BEST ETF OPPORTUNITIES 🎯\\n\\n"
        message += f"Found {len(opportunities)} good entry points:\\n\\n"
        
        for i, opp in enumerate(opportunities[:3], 1):  # Top 3
            message += f"{i}. {opp['name']} ({opp['symbol'].replace('.NS', '')})\\n"
            message += f"   Price: ₹{opp['price']:.2f} | Percentile: {opp['percentile']}%\\n"
            
            # Calculate investment amount
            portfolio = first_tracker.portfolio_amount
            invest_amount = portfolio * opp['allocation'] * 0.1  # 10% of target allocation
            units = int(invest_amount / opp['price'])
            
            message += f"   💰 Consider: ₹{invest_amount:,.0f} (~{units} units)\\n"
            message += f"   ✓ {', '.join(opp['reasons'])}\\n"
            
            if opp['historical_stats']:
                stats = opp['historical_stats']
                message += f"   Range: ₹{stats['min']:.2f} - ₹{stats['max']:.2f}\\n"
            message += "\\n"
        
        message += "⏰ Act fast on the best opportunities!"
        
        first_tracker.send_alert(message, "Multi-ETF Comparison", "etf_comparison")
    
    def display_dashboard(self, prices):
        """Display comparison dashboard"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\\n{'='*80}")
        print(f"MULTI-ETF DASHBOARD - {timestamp}")
        print(f"{'='*80}")
        
        print(f"\\n{'ETF':<20} {'Price':<10} {'Zone':<15} {'Percentile':<12} {'Action'}")
        print(f"{'-'*80}")
        
        for symbol, data in prices.items():
            name = data['name']
            price = data['price']
            percentile = data.get('percentile', 0)
            
            if percentile <= 30:
                zone = "🟢 BUY ZONE"
                action = "⭐ STRONG BUY"
            elif percentile <= 50:
                zone = "🟡 FAIR"
                action = "✓ Consider"
            elif percentile <= 70:
                zone = "🟠 MODERATE"
                action = "⏸ Hold"
            else:
                zone = "🔴 HIGH"
                action = "⚠ Wait"
            
            print(f"{name:<20} ₹{price:<9.2f} {zone:<15} {percentile:>3.0f}%         {action}")
        
        print(f"{'='*80}")
        
        # Show best opportunity
        opportunities = self.compare_opportunities(prices)
        if opportunities:
            best = opportunities[0]
            print(f"\\n💎 BEST OPPORTUNITY: {best['name']} - Score: {best['score']}")
            print(f"   {', '.join(best['reasons'])}")
        
        print()
    
    def run(self):
        """Main tracking loop for all ETFs"""
        print(f"\\n🚀 Starting Multi-ETF Tracker")
        print(f"Tracking {len(self.trackers)} ETFs")
        print(f"Check Interval: {self.base_config.get('check_interval', 60)} seconds\\n")
        
        try:
            while True:
                # Get prices for all ETFs
                prices = self.get_all_prices()
                
                if prices:
                    # Display dashboard
                    self.display_dashboard(prices)
                    
                    # Compare and find opportunities
                    opportunities = self.compare_opportunities(prices)
                    
                    # Send alert if good opportunities found
                    if opportunities and opportunities[0]['score'] >= 50:
                        first_tracker = list(self.trackers.values())[0]['tracker']
                        if first_tracker.can_send_alert('etf_comparison'):
                            self.send_comparison_alert(opportunities)
                
                # Wait before next check
                time.sleep(self.base_config.get('check_interval', 60))
                
        except KeyboardInterrupt:
            print("\\n\\n👋 Multi-ETF Tracker stopped")


def main():
    """Main entry point"""
    tracker = MultiETFTracker()
    tracker.run()

if __name__ == "__main__":
    main()
