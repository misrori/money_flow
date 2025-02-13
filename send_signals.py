import os
import telebot
import pandas as pd
from goldhand import *
from dotenv import load_dotenv
load_dotenv()


tw = Tw()

# stock signals telegram goldhand
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

bot = telebot.TeleBot(BOT_TOKEN)

df = pd.read_csv('last_stocks_update.csv')
df =pd.merge(df, tw.stock[['name', 'description']], left_on='ticker', right_on='name', how='left')
df['rank'] = df.index + 1
df['display_name'] = df['description'] + ' (' + df['name'] + ')'


# Message 1
message1 = """
*TRADING DAY ENDED* 🔴
Markets are closed! Results analyzed!
"""

# ---------------------------------------------------------------
strategy1_message = """
*STRATEGY 1️⃣: SMA 200 + PEAK DROPOUT* 🚀
*Near 200 SMA*: Stocks close to 200-day simple moving average
*35-45% drop*: Fell 35-45% from previous peak
*Top 1000*: Filtered from largest market cap stocks
"""

bot.send_message(chat_id=CHAT_ID, text=message1, parse_mode='markdown')
bot.send_message(chat_id=CHAT_ID, text=strategy1_message, parse_mode='markdown')


strategy1 = (df[
    (abs(df['diff_sma200']) < 10) &
    (df['fell_from_last_max'] < 45) &
    (df['fell_from_last_max'] >35) &
    (df['rank'] < 1000)
 ]).head(10).reset_index(drop=True)


for index, row in strategy1.iterrows():
    try:
        ticker = row['ticker']
        t = GoldHand(ticker)
        fig = t.plotly_last_year(tw.get_plotly_title(ticker))
        fig.update_layout(
            xaxis_title="Date 🗓️",
            yaxis_title="Price (USD) 💵",
            template="plotly")
        fig.update_layout(height=600, width=1000)
        fig.write_image("static_plot.png")
        bot.send_photo(CHAT_ID, photo=open('static_plot.png', 'rb'))

        time.sleep(2)

    except Exception as e:
        print(f"Error processing {ticker}: {e}")

# ---------------------------------------------------------------

strategy2_message = """
*STRATEGY 2️⃣: Goldhandline indicator* 🚀
*It turned gold* and the change from the turning point less than 10%
*Top 3000*: Filtered from largest market cap stocks
"""

bot.send_message(chat_id=CHAT_ID, text=strategy2_message, parse_mode='markdown')

strategy2 = (df[
    (df['ghl_color'] =='gold') &
    (df['ghl_days_since_last_change'] < 2) &
    (df['ghl_change_percent_from_last_change'] <10) &
    (df['rank'] < 3000)
 ]).head(10).reset_index(drop=True)


for index, row in strategy2.iterrows():
    try:
        ticker = row['ticker']
        t = GoldHand(ticker)
        fig = t.plotly_last_year(tw.get_plotly_title(ticker), ndays=500 )
        fig.update_layout(
            xaxis_title="Date 🗓️",
            yaxis_title="Price (USD) 💵",
            template="plotly")
        fig.update_layout(height=600, width=1000)
        fig.write_image("static_plot.png")
        bot.send_photo(CHAT_ID, photo=open('static_plot.png', 'rb'))

        time.sleep(2)

    except Exception as e:
        print(f"Error processing {ticker}: {e}")





