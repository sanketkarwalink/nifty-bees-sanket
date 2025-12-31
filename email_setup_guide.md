# Email Alert Setup Guide 📧

## Why Email is Best for Stock Alerts

**Email is recommended over WhatsApp because:**
- ✅ **Free & Easy** - No API costs or complex setup
- ✅ **Reliable** - Works 24/7 without rate limits
- ✅ **Instant** - Notifications on phone + desktop
- ✅ **Professional** - Better for financial alerts
- ✅ **Searchable** - Easy to find past alerts
- ✅ **No Third Party** - Direct delivery, no WhatsApp Business API needed

## Gmail Setup (Recommended)

### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account: https://myaccount.google.com
2. Click **Security** in the left menu
3. Under "Signing in to Google", select **2-Step Verification**
4. Follow the prompts to set it up

### Step 2: Create App Password
1. Go to: https://myaccount.google.com/apppasswords
2. In the "Select app" dropdown, choose **Mail**
3. In the "Select device" dropdown, choose **Other (Custom name)**
4. Type "Nifty Tracker" and click **Generate**
5. **Copy the 16-character password** (example: `abcd efgh ijkl mnop`)
6. Save this password - you'll need it for configuration

### Step 3: Configure the Tracker

Edit `config.json` and update these fields:

```json
{
    "email_alerts": true,
    "email_config": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "youremail@gmail.com",
        "sender_password": "abcd efgh ijkl mnop",
        "receiver_email": "youremail@gmail.com"
    }
}
```

**Replace:**
- `youremail@gmail.com` - Your Gmail address
- `abcd efgh ijkl mnop` - The app password from Step 2 (include spaces)

## Other Email Providers

### Outlook/Hotmail
```json
{
    "smtp_server": "smtp-mail.outlook.com",
    "smtp_port": 587
}
```

### Yahoo Mail
```json
{
    "smtp_server": "smtp.mail.yahoo.com",
    "smtp_port": 587
}
```
*Note: Yahoo also requires app passwords*

## Investment Configuration

Update your portfolio settings in `config.json`:

```json
{
    "investment_config": {
        "portfolio_amount": 100000,      // Your total portfolio value
        "target_allocation": 0.20,       // 20% allocation to Nifty 50 ETF
        "buy_on_dip": 2.0,              // Buy when 2% below moving average
        "sell_on_spike": 3.0            // Consider selling when 3% above MA
    }
}
```

### Configuration Explained:

**portfolio_amount**: Total investment capital
- Example: `100000` = ₹1 lakh portfolio

**target_allocation**: What % should be in this ETF
- `0.20` = 20% of portfolio in Nifty 50 ETF
- `0.15` = 15%, `0.30` = 30%, etc.

**buy_on_dip**: When to buy more
- `2.0` = Strong buy signal when price is 2% below moving average
- Lower value (1.5) = More aggressive buying
- Higher value (3.0) = More conservative buying

**sell_on_spike**: When to book profits
- `3.0` = Consider selling when 3% above moving average
- Lower value = Take profits earlier
- Higher value = Let profits run longer

## Investment Signal Guide

The tracker provides automated recommendations:

### 🟢🟢🟢 STRONG BUY
- Price significantly below moving average
- Good dip opportunity
- Recommends specific investment amount

### 🟢🟢 BUY
- Price moderately below MA
- Good entry point
- Suggests smaller investment amount

### 🟡 HOLD
- Price near moving average
- Wait for better opportunity
- Maintain current position

### 🔴🔴 CONSIDER SELLING
- Price significantly above MA
- Take profits
- Recommends partial sell amount

## Example Alerts You'll Receive

### Email Alert Example:
```
Subject: ⚠️ Sharp Drop - Nifty 50 ETF Alert

Price dipped 1.5% to ₹292.00
Time: 2025-12-31 14:30:00

💡 STRONG BUY Signal
Invest ₹3,000 (~10 units)
```

### Investment Recommendation Example:
```
💡 INVESTMENT SIGNAL: 🟢🟢🟢 STRONG BUY
   • Invest ₹3,500 (~12 units)
📋 Analysis:
   • Price 2.5% below MA - Great dip opportunity
   • Downtrend: 3 consecutive drops
Target Holdings: 68 units (₹20,000)
```

## Testing Your Setup

1. Set `email_alerts: true` in config.json
2. Add your credentials
3. Restart the tracker
4. Wait for the first price check
5. You should receive a test notification

## Troubleshooting

**"Authentication failed"**
- Make sure you're using an App Password, not your regular password
- Check 2FA is enabled
- Verify email address is correct

**"Connection refused"**
- Check SMTP server and port are correct
- Ensure firewall isn't blocking port 587

**Not receiving emails**
- Check spam/junk folder
- Verify receiver_email is correct
- Test with a simple email client first

## Security Best Practices

- ✅ Use app-specific passwords (never your main password)
- ✅ Keep config.json private (don't share or commit to git)
- ✅ Use a dedicated email if sharing the tracker
- ✅ Review Google account activity regularly

## WhatsApp Alternative (Advanced)

If you absolutely need WhatsApp, you'll need:
1. **Twilio** - Paid service ($0.005/msg + WhatsApp Business API)
2. **WhatsApp Business API** - Requires business verification
3. **Setup cost**: ~$50-100/month minimum

*Email is free and works just as well for most users!*
