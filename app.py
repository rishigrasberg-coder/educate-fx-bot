import os
import asyncio
import logging
from telegram import Bot
from flask import Flask, request, jsonify
import json
from datetime import datetime

# Your bot configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = "7333702822"  # Your chat ID

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

class EducateFXBot:
    def __init__(self):
        self.bot = bot
    
    async def send_educate_fx_signal(self, signal_data):
        try:
            message = self.format_educate_fx_message(signal_data)
            await self.bot.send_message(
                chat_id=CHAT_ID, 
                text=message, 
                parse_mode='HTML'
            )
            return True
        except Exception as e:
            logging.error(f"Error sending signal: {e}")
            return False
    
    def format_educate_fx_message(self, data):
        action = data.get('action', 'SIGNAL').upper()
        symbol = data.get('symbol', 'Unknown')
        price = data.get('price', 'N/A')
        timeframe = data.get('timeframe', 'Unknown')
        timestamp = data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        if action == 'BUY' or action == 'LONG':
            emoji = "🟢"
            direction = "LONG"
            color = "GREEN"
        elif action == 'SELL' or action == 'SHORT':
            emoji = "🔴" 
            direction = "SHORT"
            color = "RED"
        else:
            emoji = "🟡"
            direction = action
            color = "YELLOW"
        
        message = f"""
{emoji} <b>EDUCATE FX SIGNAL</b> {emoji}

🏷️ <b>Strategy:</b> Educate FX
📊 <b>Pair:</b> {symbol}
🎯 <b>Direction:</b> {direction}
💰 <b>Entry Price:</b> {price}
⏱️ <b>Timeframe:</b> {timeframe}
📅 <b>Time:</b> {timestamp}

{self.get_forex_context(data, action)}

<i>🤖 Automated from TradingView</i>
        """
        
        return message.strip()
    
    def get_forex_context(self, data, action):
        context = ""
        
        # Add price levels if available
        if 'high' in data and 'low' in data:
            high = data['high']
            low = data['low']
            context += f"📈 <b>Session High:</b> {high}\n"
            context += f"📉 <b>Session Low:</b> {low}\n"
        
        if 'volume' in data:
            volume = data['volume']
            context += f"📊 <b>Volume:</b> {volume}\n"
        
        # Add trading advice based on signal
        if action in ['BUY', 'LONG']:
            context += f"\n💡 <b>Trading Plan:</b>\n"
            context += f"• Look for bullish confirmation\n"
            context += f"• Watch key resistance levels\n"
            context += f"• Consider risk management\n"
        elif action in ['SELL', 'SHORT']:
            context += f"\n💡 <b>Trading Plan:</b>\n"
            context += f"• Bearish signal confirmed\n"
            context += f"• Monitor support levels\n"
            context += f"• Apply proper stop loss\n"
        
        return context

educate_fx_bot = EducateFXBot()

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # Log the received data for debugging
        logging.info(f"Received webhook data: {data}")
        
        asyncio.run(educate_fx_bot.send_educate_fx_signal(data))
        
        return jsonify({
            'status': 'success', 
            'message': f"Educate FX signal sent to Telegram"
        }), 200
    
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test_educate_fx():
    test_signal = {
        'symbol': 'EURUSD',
        'action': 'BUY',
        'strategy': 'Educate FX',
        'price': '1.16044',
        'timeframe': '15m',
        'high': '1.16100',
        'low': '1.15950',
        'volume': '12500'
    }
    
    asyncio.run(educate_fx_bot.send_educate_fx_signal(test_signal))
    return jsonify({'status': 'Test Educate FX signal sent'})

@app.route('/', methods=['GET'])
def home():
    return "EducateFX Bot is running! 🚀"

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
