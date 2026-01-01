"""
Nifty 50 ETF Price Tracker with Dip Alerts
Monitors Nifty 50 ETF price and sends alerts when price dips below threshold
"""

import yfinance as yf
import time
import json
from datetime import datetime
from plyer import notification
import os
import requests

class NiftyTracker:
    def __init__(self, config_file='config.json'):
        """Initialize the tracker with configuration"""
        self.config_file = config_file
        self.config_mtime = None
        self.load_config(config_file)
        self.previous_price = None
        self.highest_price_today = None
        self.lowest_price_today = None
        self.price_history = []  # Store recent prices for moving average
        self.alert_cooldown = {}  # Prevent spam alerts
        self.daily_open_price = None
        self.consecutive_drops = 0
        
        # Historical data for smarter analysis
        self.historical_data = None
        self.historical_stats = {}
        self.load_historical_data()

    def _apply_config(self, config):
        """Apply config dict to runtime settings"""
        self.symbol = config.get('symbol', 'NIFTYBEES.NS')
        self.check_interval = config.get('check_interval', 60)
        self.dip_percentage = config.get('dip_percentage', 1.0)
        self.dip_from_high = config.get('dip_from_high', 2.0)
        self.alert_sound = config.get('alert_sound', True)
        self.headless = config.get('headless', False)
        self.moving_avg_period = config.get('moving_avg_period', 5)
        self.volume_spike_threshold = config.get('volume_spike_threshold', 1.5)
        self.consecutive_drop_threshold = config.get('consecutive_drop_threshold', 3)
        self.alert_cooldown_minutes = config.get('alert_cooldown_minutes', 5)

        # Telegram configuration
        self.telegram_alerts = config.get('telegram_alerts', False)
        self.telegram_config = config.get('telegram_config', {})
        # Environment overrides for Telegram (avoid hardcoding secrets)
        env_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        env_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        if env_bot_token:
            self.telegram_config['bot_token'] = env_bot_token
        if env_chat_id:
            self.telegram_config['chat_id'] = env_chat_id

        # Investment configuration
        self.investment_config = config.get('investment_config', {})
        # Environment overrides for investment sizing
        env_portfolio = os.getenv('PORTFOLIO_AMOUNT')
        env_target_alloc = os.getenv('TARGET_ALLOCATION')
        if env_portfolio:
            try:
                self.investment_config['portfolio_amount'] = float(env_portfolio)
            except ValueError:
                pass
        if env_target_alloc:
            try:
                self.investment_config['target_allocation'] = float(env_target_alloc)
            except ValueError:
                pass

        self.portfolio_amount = self.investment_config.get('portfolio_amount', 100000)
        self.target_allocation = self.investment_config.get('target_allocation', 0.20)
        self.buy_on_dip = self.investment_config.get('buy_on_dip', 2.0)
        self.sell_on_spike = self.investment_config.get('sell_on_spike', 3.0)
        
    def load_config(self, config_file=None):
        """Load configuration from JSON file"""
        cfg_path = config_file or self.config_file
        if os.path.exists(cfg_path):
            with open(cfg_path, 'r') as f:
                config = json.load(f)
        else:
            # Default configuration
            config = {
                'symbol': 'NIFTYBEES.NS',  # Nifty 50 ETF (NIFTY BeES)
                'check_interval': 60,  # Check every 60 seconds
                'dip_percentage': 0.7,  # Alert on 0.7% dip (realistic for Indian market)
                'dip_from_high': 1.0,  # Alert on 1%+ dip from today's high (more frequent opportunities)
                'alert_sound': True,
                'headless': False,  # Skip desktop notifications on servers
                'moving_avg_period': 20,  # 20-period MA (more stable for daily tracking)
                'volume_spike_threshold': 1.5,  # Volume spike multiplier
                'consecutive_drop_threshold': 3,  # Alert after N consecutive drops
                'alert_cooldown_minutes': 30,  # 30 minutes between alerts (reduce noise)
                'telegram_alerts': True,
                'telegram_config': {
                    'bot_token': '',
                    'chat_id': ''
                },
                'investment_config': {
                    'portfolio_amount': 100000,  # Total portfolio value
                    'target_allocation': 0.20,  # 20% of portfolio in this ETF
                    'buy_on_dip': 1.5,  # BUY signal when 1.5% below MA (realistic for India)
                    'sell_on_spike': 4.0  # SELL signal when 4% above MA (take profits)
                }
            }
            # Save default config
            with open(cfg_path, 'w') as f:
                json.dump(config, f, indent=4)
        
        self._apply_config(config)
        if os.path.exists(cfg_path):
            self.config_mtime = os.path.getmtime(cfg_path)
        
    def get_current_price(self):
        """Fetch current price of Nifty 50 ETF with additional metrics"""
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period='1d', interval='1m')
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                volume = data['Volume'].iloc[-1] if 'Volume' in data.columns else 0
                
                # Get opening price for the day
                if self.daily_open_price is None and len(data) > 0:
                    self.daily_open_price = data['Open'].iloc[0]
                
                return current_price, volume
            else:
                print("No data available")
                return None, None
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None, None
    
    def load_historical_data(self):
        """Load 90 days of historical data for analysis"""
        try:
            print("📊 Loading historical data for analysis...")
            ticker = yf.Ticker(self.symbol)
            # Get 90 days of historical data
            self.historical_data = ticker.history(period='90d')
            
            if not self.historical_data.empty:
                # Calculate historical statistics
                prices = self.historical_data['Close'].values
                self.historical_stats = {
                    'mean': float(prices.mean()),
                    'std': float(prices.std()),
                    'min': float(prices.min()),
                    'max': float(prices.max()),
                    'p25': float(self.historical_data['Close'].quantile(0.25)),  # 25th percentile
                    'p50': float(self.historical_data['Close'].quantile(0.50)),  # Median
                    'p75': float(self.historical_data['Close'].quantile(0.75)),  # 75th percentile
                }
                
                # Calculate moving averages from historical data
                self.historical_stats['sma_20'] = float(prices[-20:].mean()) if len(prices) >= 20 else float(prices.mean())
                self.historical_stats['sma_50'] = float(prices[-50:].mean()) if len(prices) >= 50 else float(prices.mean())
                
                print(f"✅ Historical data loaded: 90 days")
                print(f"   Price range: ₹{self.historical_stats['min']:.2f} - ₹{self.historical_stats['max']:.2f}")
                print(f"   Average: ₹{self.historical_stats['mean']:.2f}")
                print(f"   25th percentile (Good buy zone): ₹{self.historical_stats['p25']:.2f}")
                print(f"   50-day MA: ₹{self.historical_stats['sma_50']:.2f}")
            else:
                print("⚠️  No historical data available")
        except Exception as e:
            print(f"⚠️  Error loading historical data: {e}")
    
    def calculate_moving_average(self):
        """Calculate moving average from recent prices"""
        if len(self.price_history) < self.moving_avg_period:
            return None
        recent_prices = self.price_history[-self.moving_avg_period:]
        return sum(recent_prices) / len(recent_prices)
    
    def get_price_percentile(self, current_price):
        """Calculate where current price stands in historical range (0-100)"""
        if not self.historical_stats:
            return None
        
        price_min = self.historical_stats['min']
        price_max = self.historical_stats['max']
        
        if price_max == price_min:
            return 50
        
        percentile = ((current_price - price_min) / (price_max - price_min)) * 100
        return round(percentile, 1)
    
    def is_in_value_zone(self, current_price):
        """Check if price is in historical value zone (bottom 30%)"""
        percentile = self.get_price_percentile(current_price)
        if percentile is None:
            return False
        return percentile <= 30  # Bottom 30% of historical range
    
    def can_send_alert(self, alert_type):
        """Check if alert cooldown period has passed"""
        if alert_type not in self.alert_cooldown:
            return True
        
        time_since_last = time.time() - self.alert_cooldown[alert_type]
        cooldown_seconds = self.alert_cooldown_minutes * 60
        return time_since_last >= cooldown_seconds
    
    
    def send_telegram_alert(self, message):
        """Send Telegram alert via bot API"""
        if not self.telegram_alerts:
            return
        
        try:
            bot_token = self.telegram_config.get('bot_token')
            chat_id = self.telegram_config.get('chat_id')
            
            if not all([bot_token, chat_id]):
                print("Telegram not configured (missing bot_token or chat_id)")
                return
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            print(f"💬 Telegram sent: {message[:50]}...")
        except Exception as e:
            print(f"Telegram error: {e}")
    
    def send_alert(self, message, title="Nifty 50 ETF Alert", alert_type="general"):
        """Send desktop notification and Telegram. Continues even if desktop notify fails."""
        if not self.can_send_alert(alert_type):
            return  # Skip if in cooldown period

        # Try desktop notification unless headless; do not block email if it fails
        if not self.headless:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Nifty Tracker",
                    timeout=10
                )
            except Exception as e:
                print(f"Desktop alert unavailable: {e}")

        # Always log and proceed with email
        print(f"\n🔔 ALERT: {message}")
        self.alert_cooldown[alert_type] = time.time()

        if self.telegram_alerts:
            telegram_message = f"<b>{title}</b>\n{message}\n<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
            self.send_telegram_alert(telegram_message)
    
    def check_for_dip(self, current_price, volume):
        """Check for price dips using historical data - realistic for Indian market"""
        alerts = []
        
        # Add to price history
        self.price_history.append(current_price)
        if len(self.price_history) > 50:
            self.price_history.pop(0)
        
        # Update today's high and low
        if self.highest_price_today is None or current_price > self.highest_price_today:
            self.highest_price_today = current_price
        
        if self.lowest_price_today is None or current_price < self.lowest_price_today:
            self.lowest_price_today = current_price
        
        # Track consecutive drops
        if self.previous_price is not None:
            if current_price < self.previous_price:
                self.consecutive_drops += 1
            else:
                self.consecutive_drops = 0
        
        # Get investment recommendation
        recommendation = self.get_investment_recommendation(current_price)
        if not recommendation:
            return alerts
        
        # Get historical context
        percentile = self.get_price_percentile(current_price)
        in_value_zone = self.is_in_value_zone(current_price)
        
        # STRATEGY 1: Price in historical value zone (bottom 30% of 90-day range)
        if in_value_zone and self.can_send_alert('value_zone'):
            if recommendation['signal'] in ['STRONG BUY', 'BUY']:
                message = f"💎 VALUE ZONE ALERT 💎\n\n"
                message += f"Price in bottom 30% of 90-day range!\n"
                message += f"Current: ₹{current_price:.2f} (Percentile: {percentile}%)\n"
                if self.historical_stats:
                    message += f"90-day range: ₹{self.historical_stats['min']:.2f} - ₹{self.historical_stats['max']:.2f}\n"
                    message += f"90-day average: ₹{self.historical_stats['mean']:.2f}\n\n"
                
                message += f"💰 {recommendation['strength']} {recommendation['signal']}\n\n"
                message += f"🎯 ACTION TO TAKE:\n"
                for rec in recommendation['recommendations']:
                    message += f"• {rec}\n"
                message += f"\n📊 Analysis:\n"
                for reason in recommendation['reasoning']:
                    message += f"• {reason}\n"
                message += f"\n⏰ This is a statistically good entry point!"
                
                alerts.append((message, "value_zone"))
        
        # STRATEGY 2: Dip from today's high + Below 50-day MA
        if self.highest_price_today is not None and self.historical_stats:
            dip_from_high_pct = ((current_price - self.highest_price_today) / self.highest_price_today) * 100
            sma_50 = self.historical_stats.get('sma_50')
            
            # Alert on 1%+ dip from high AND price below 50-day MA
            if (dip_from_high_pct <= -self.dip_from_high and 
                sma_50 and current_price < sma_50 and 
                self.can_send_alert('dip_opportunity')):
                
                if recommendation['signal'] in ['STRONG BUY', 'BUY']:
                    below_sma = ((current_price - sma_50) / sma_50) * 100
                    
                    message = f"🎯 DIP + TREND SIGNAL 🎯\n\n"
                    message += f"✓ Dipped {abs(dip_from_high_pct):.2f}% from today's high\n"
                    message += f"✓ Below 50-day MA by {abs(below_sma):.2f}%\n\n"
                    message += f"Current: ₹{current_price:.2f}\n"
                    message += f"Today's High: ₹{self.highest_price_today:.2f}\n"
                    message += f"50-day MA: ₹{sma_50:.2f}\n\n"
                    
                    message += f"💰 {recommendation['strength']} {recommendation['signal']}\n\n"
                    message += f"🎯 RECOMMENDED ACTION:\n"
                    for rec in recommendation['recommendations']:
                        message += f"• {rec}\n"
                    message += f"\n📊 Why buy now:\n"
                    for reason in recommendation['reasoning']:
                        message += f"• {reason}\n"
                    
                    alerts.append((message, "dip_opportunity"))
        
        # STRATEGY 3: Strong buy - price near 90-day low
        if self.historical_stats and self.can_send_alert('near_low'):
            price_min = self.historical_stats['min']
            distance_from_low_pct = ((current_price - price_min) / price_min) * 100
            
            # Alert if within 2% of 90-day low
            if distance_from_low_pct <= 2.0 and recommendation['signal'] == 'STRONG BUY':
                message = f"🔥 NEAR 90-DAY LOW 🔥\n\n"
                message += f"Price is only {distance_from_low_pct:.2f}% above 90-day low!\n"
                message += f"Current: ₹{current_price:.2f}\n"
                message += f"90-day Low: ₹{price_min:.2f}\n\n"
                message += f"💰 {recommendation['strength']} {recommendation['signal']}\n\n"
                message += f"⚡ STRONG BUY RECOMMENDATION:\n"
                for rec in recommendation['recommendations']:
                    message += f"• {rec}\n"
                message += f"\n🎯 Excellent long-term entry point!"
                
                alerts.append((message, "near_low"))
        
        return alerts

    def reload_config_if_changed(self):
        """Hot-reload config if file changed on disk"""
        try:
            if not self.config_file or not os.path.exists(self.config_file):
                return
            current_mtime = os.path.getmtime(self.config_file)
            if self.config_mtime is None or current_mtime > self.config_mtime:
                self.load_config(self.config_file)
                print("[config] reloaded")
        except Exception as e:
            print(f"Config reload error: {e}")
    
    def get_investment_recommendation(self, current_price):
        """Generate investment recommendation based on technical analysis"""
        recommendations = []
        
        moving_avg = self.calculate_moving_average()
        if moving_avg is None:
            return None  # Not enough data yet
        
        ma_diff_pct = ((current_price - moving_avg) / moving_avg) * 100
        
        # Calculate current and target holdings
        current_value = self.portfolio_amount * self.target_allocation
        units_to_hold = current_value / current_price
        
        # Recommendation logic
        signal = None
        strength = ""
        reasoning = []
        
        # BUY signals
        if ma_diff_pct <= -self.buy_on_dip:
            signal = "STRONG BUY"
            strength = "🟢🟢🟢"
            reasoning.append(f"Price {abs(ma_diff_pct):.2f}% below MA - Great dip opportunity")
            
            # Calculate buy amount
            buy_percentage = min(abs(ma_diff_pct) / 2, 5)  # Max 5% of portfolio
            buy_amount = self.portfolio_amount * (buy_percentage / 100)
            buy_units = buy_amount / current_price
            
            recommendations.append(f"Invest ₹{buy_amount:,.0f} (~{int(buy_units)} units)")
            
        elif -self.buy_on_dip < ma_diff_pct <= -1.0:
            signal = "BUY"
            strength = "🟢🟢"
            reasoning.append(f"Price {abs(ma_diff_pct):.2f}% below MA - Good entry point")
            
            buy_percentage = 2  # 2% of portfolio
            buy_amount = self.portfolio_amount * (buy_percentage / 100)
            buy_units = buy_amount / current_price
            
            recommendations.append(f"Consider investing ₹{buy_amount:,.0f} (~{int(buy_units)} units)")
            
        # SELL signals
        elif ma_diff_pct >= self.sell_on_spike:
            signal = "CONSIDER SELLING"
            strength = "🔴🔴"
            reasoning.append(f"Price {ma_diff_pct:.2f}% above MA - Take profits")
            
            sell_percentage = min(ma_diff_pct / 3, 10)  # Max 10% of holdings
            sell_units = units_to_hold * (sell_percentage / 100)
            sell_amount = sell_units * current_price
            
            recommendations.append(f"Book profits: ~{int(sell_units)} units (₹{sell_amount:,.0f})")
            
        # HOLD signals
        elif -1.0 < ma_diff_pct < 1.5:
            signal = "HOLD"
            strength = "🟡"
            reasoning.append("Price near moving average - Wait for better opportunity")
            recommendations.append("Maintain current position")
        else:
            signal = "HOLD/WATCH"
            strength = "🟡"
            reasoning.append("Price slightly elevated - Monitor for better entry")
            recommendations.append("Wait for dip before adding more")
        
        # Additional context
        if self.highest_price_today and self.lowest_price_today:
            day_range_pct = ((self.highest_price_today - self.lowest_price_today) / self.lowest_price_today) * 100
            if day_range_pct > 2:
                reasoning.append(f"High volatility today ({day_range_pct:.1f}% range)")
        
        if self.consecutive_drops >= 2:
            reasoning.append(f"Downtrend: {self.consecutive_drops} consecutive drops")
        
        return {
            'signal': signal,
            'strength': strength,
            'recommendations': recommendations,
            'reasoning': reasoning,
            'ma_diff_pct': ma_diff_pct,
            'moving_avg': moving_avg,
            'target_value': current_value,
            'target_units': int(units_to_hold)
        }
    
    def display_status(self, current_price, volume):
        """Display current status with enhanced metrics"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        status = f"\n{'='*60}\n"
        status += f"Time: {timestamp}\n"
        status += f"Symbol: {self.symbol}\n"
        status += f"Current Price: ₹{current_price:.2f}\n"
        
        if self.previous_price:
            change = current_price - self.previous_price
            change_pct = (change / self.previous_price) * 100
            change_symbol = "📈" if change >= 0 else "📉"
            status += f"Change: {change_symbol} ₹{change:.2f} ({change_pct:+.2f}%)\n"
        
        if self.daily_open_price:
            day_change = current_price - self.daily_open_price
            day_change_pct = (day_change / self.daily_open_price) * 100
            status += f"Day Change: ₹{day_change:+.2f} ({day_change_pct:+.2f}%)\n"
        
        if self.highest_price_today:
            status += f"Today's High: ₹{self.highest_price_today:.2f}\n"
        
        if self.lowest_price_today:
            status += f"Today's Low: ₹{self.lowest_price_today:.2f}\n"
            
        if self.highest_price_today and self.lowest_price_today:
            day_range = self.highest_price_today - self.lowest_price_today
            day_range_pct = (day_range / self.lowest_price_today) * 100
            status += f"Day Range: ₹{day_range:.2f} ({day_range_pct:.2f}%)\n"
        
        # Moving average
        moving_avg = self.calculate_moving_average()
        if moving_avg:
            ma_diff = current_price - moving_avg
            ma_diff_pct = (ma_diff / moving_avg) * 100
            ma_symbol = "⬆️" if ma_diff >= 0 else "⬇️"
            status += f"MA({self.moving_avg_period}): {ma_symbol} ₹{moving_avg:.2f} ({ma_diff_pct:+.2f}%)\n"
        
        # Historical context
        if self.historical_stats:
            percentile = self.get_price_percentile(current_price)
            sma_50 = self.historical_stats.get('sma_50', 0)
            if percentile:
                zone = "🟢 BUY ZONE" if percentile <= 30 else "🟡 FAIR" if percentile <= 70 else "🔴 HIGH"
                status += f"90-day Percentile: {percentile}% {zone}\n"
            if sma_50:
                sma50_diff_pct = ((current_price - sma_50) / sma_50) * 100
                status += f"50-day MA: ₹{sma_50:.2f} ({sma50_diff_pct:+.2f}%)\n"
        
        # Consecutive drops indicator
        if self.consecutive_drops > 0:
            status += f"Consecutive Drops: {self.consecutive_drops} {'🔴' if self.consecutive_drops >= self.consecutive_drop_threshold else ''}\n"
        
        # Investment recommendation
        recommendation = self.get_investment_recommendation(current_price)
        if recommendation:
            status += f"\n{'─'*60}\n"
            status += f"💡 INVESTMENT SIGNAL: {recommendation['strength']} {recommendation['signal']}\n"
            for rec in recommendation['recommendations']:
                status += f"   • {rec}\n"
            status += f"📋 Analysis:\n"
            for reason in recommendation['reasoning']:
                status += f"   • {reason}\n"
            status += f"Target Holdings: {recommendation['target_units']} units (₹{recommendation['target_value']:,.0f})\n"
        
        status += f"{'='*60}"
        print(status)
    
    def run(self):
        """Main tracking loop"""
        print(f"\n🚀 Starting Nifty 50 ETF Tracker (Long-Term Investment Mode)")
        print(f"Symbol: {self.symbol}")
        print(f"Check Interval: {self.check_interval} seconds")
        print(f"Buy Signal Threshold: {self.dip_from_high}% dip from high")
        print(f"Strong Buy: 3%+ below moving average")
        print(f"Portfolio: ₹{self.portfolio_amount:,.0f} | Target Allocation: {self.target_allocation*100:.0f}%")
        print(f"\nWaiting for buying opportunities...\n")
        print(f"Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Hot-reload config so you can edit config.json while running
                self.reload_config_if_changed()

                current_price, volume = self.get_current_price()
                
                if current_price:
                    # Display current status
                    self.display_status(current_price, volume)
                    
                    # Check for dips and send alerts
                    alerts = self.check_for_dip(current_price, volume)
                    for alert_message, alert_type in alerts:
                        self.send_alert(alert_message, alert_type=alert_type)
                    
                    # Update previous price
                    self.previous_price = current_price
                else:
                    print(f"Failed to fetch price at {datetime.now().strftime('%H:%M:%S')}")
                
                # Wait before next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Tracker stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    """Main entry point"""
    tracker = NiftyTracker()
    tracker.run()

if __name__ == "__main__":
    main()
