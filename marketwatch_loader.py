import pandas as pd
import json

URL_PREFIX = 'https://www.marketwatch.com/investing'


def load_df(symbols, start, end, is_index=False):
    df = pd.DataFrame()

    type = 'index' if is_index else 'stock'

    start = start.strftime("%m/%d/%Y")
    end = end.strftime("%m/%d/%Y")

    for symbol in symbols:
        csv_url = f'{URL_PREFIX}/{type}/{symbol}/downloaddatapartial?startdate={start}%2000:00:00&enddate={end}%2000:00:00&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false&countrycode=ph'
        data = pd.read_csv(csv_url, 
                            usecols=['Date', 'Close'], 
                            parse_dates=['Date'],
                            thousands=",")
        
        if 'Date' not in df.columns:
            df['Date'] = data['Date']

        df[symbol.upper()] = data['Close']

    df.set_index('Date', inplace=True)

    return df