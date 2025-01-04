from goldhand import *
import datetime
from tqdm import tqdm
import pandas as pd 
import os
current_date = datetime.datetime.now()
tw = Tw()

def smma(data, window, colname):
    hl2 = data['hl2'].values
    smma_values = [hl2[0]]

    for i in range(1, len(hl2)):
        smma_val = (smma_values[-1] * (window - 1) + hl2[i]) / window
        smma_values.append(smma_val)

    data[colname] = smma_values
    return data

def add_ghl_color(df):
    # goldline
    df = smma(df, 15, 'v1')
    df = smma(df, 19, 'v2')
    df = smma(df, 25, 'v3')
    df = smma(df, 29, 'v4')

    df['ghl_color'] = 'grey'  # Set default color to grey

    # Update color based on conditions
    df.loc[(df['v4'] < df['v3']) & (df['v3'] < df['v2']) & (df['v2'] < df['v1']), 'ghl_color'] = 'gold'
    df.loc[(df['v1'] < df['v2']) & (df['v2'] < df['v3']) & (df['v3'] < df['v4']), 'ghl_color'] = 'blue'
    return df

def get_one_ticker_info(ticker):
    try:
        t = GoldHand(ticker)
        df = t.df
        data_dict = dict(df.iloc[-1])
        last_price = data_dict['close']

        # goldline
        # Apply SMMA to the dataframe
        df = add_ghl_color(df)

        # goldhand line

        df['ghl_prev_color'] = df['ghl_color'].shift(1)
        df['ghl_change'] = (df['ghl_color'] != df['ghl_prev_color'] )

        # last change
        ghl_last_change_date = df.loc[df['ghl_change'], 'date'].max()
        ghl_last_change_price = df.loc[df['date']==ghl_last_change_date, 'close'].iloc[0]

        # days past of last change
        current_date = pd.Timestamp.now()
        days_since_last_change = (current_date.date() - ghl_last_change_date).days


        # aqd the values
        data_dict['ghl_status'] = 'open' if df['ghl_color'].iloc[-1] == 'gold' else 'close'
        data_dict['ghl_color'] = df['ghl_color'].iloc[-1]
        data_dict['ghl_last_change_date'] = ghl_last_change_date
        data_dict['ghl_days_since_last_change'] = days_since_last_change
        data_dict['ghl_last_change_price'] = ghl_last_change_price
        data_dict['ghl_change_percent_from_last_change'] = ((last_price/ ghl_last_change_price )-1) * 100

        # rsi
        # filter rows wher rsi is na
        df['rsi_lag'] = df['rsi'].shift(1)


        df['position_open'] = (df['rsi']<=30) & (df['rsi_lag'] > 30)
        df['position_close'] = (df['rsi']>=70) & (df['rsi_lag'] < 70)

        # which change has oocured last time
        last_open = df.loc[df['position_open'], 'date'].max()
        last_close = df.loc[df['position_close'], 'date'].max()


        rsi_status = 'open' if last_open > last_close else 'close'
        last_change_date = last_open if last_open > last_close else last_close
        last_change_price = df.loc[df['date']==last_change_date, 'close'].iloc[0]

        # days pőast from last change

        days_since_last_change = (current_date.date() - last_change_date).days

        # aqd the values
        data_dict['rsi_status'] = rsi_status
        data_dict['rsi_last_change_date'] = last_change_date
        data_dict['rsi_days_since_last_change'] = days_since_last_change
        data_dict['rsi_last_change_price'] = last_change_price
        data_dict['rsi_change_percent_from_last_change'] = ((last_price/ last_change_price )-1) * 100


        #fell form the last maximum
        # select the last 3 local maximum find the maximum
        last_max = df.loc[df['local']=="maximum"].tail(3)['close'].max()
        # fell from last max
        data_dict['last_max'] =last_max
        data_dict['fell_from_last_max'] = ((last_price/ last_max )-1) * -100


        # ad sector industry p/e anmd other important metric
        data_dict['sector'] = tw.stock.loc[tw.stock['name']==ticker, 'sector'].iloc[0]
        data_dict['industry'] = tw.stock.loc[tw.stock['name']==ticker, 'industry'].iloc[0]
        data_dict['price_per_earning'] = tw.stock.loc[tw.stock['name']==ticker, 'price_earnings_ttm'].iloc[0]
        data_dict['earnings_per_share_basic_ttm'] = tw.stock.loc[tw.stock['name']==ticker, 'earnings_per_share_basic_ttm'].iloc[0]
        data_dict['number_of_employees'] = tw.stock.loc[tw.stock['name']==ticker, 'number_of_employees'].iloc[0]
        return data_dict
    except:
        return None

get_one_ticker_info('MSTR')

df = pd.DataFrame(list(map(get_one_ticker_info, tqdm(tw.stock['name'].to_list()[0:10]) )))

# create data folder if does not exist
if not os.path.exists('data'):
    os.makedirs('data')

df.to_csv('data/top_10_stocks.csv')
df.to_csv('last_stocks_update.csv')
