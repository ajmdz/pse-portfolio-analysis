import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
import json

stock_dict = {}
stocks_df = pd.DataFrame()

with open('stocks.json', 'r') as stocks:
    stock_dict = json.load(stocks)


def load_data(stocks, start, end):
    global stocks_df

    stocks = [stock_dict[stock] for stock in stocks]
    url_prefix = 'https://www.marketwatch.com/investing/stock'
    stocks_df = pd.DataFrame()
    start = start.strftime("%m/%d/%Y")
    end = end.strftime("%m/%d/%Y")

    for stock in stocks:
        csv_url = f'{url_prefix}/{stock}/downloaddatapartial?startdate={start}%2000:00:00&enddate={end}%2000:00:00&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false&countrycode=ph'

        df = pd.read_csv(csv_url, usecols=['Date', 'Close'], parse_dates=['Date'])
        
        if 'Date' not in stocks_df.columns:
            stocks_df['Date'] = df['Date']

        stocks_df[stock.upper()] = df['Close']

    stocks_df.set_index('Date', inplace=True)
    

    

def main():
    st.title("PSE Investment Portfolio Dashboard")

    options = st.multiselect(
        'Select stocks',
        stock_dict.keys(),
        list(stock_dict.keys())[:3],
    )

    start = st.date_input("Start date",
                          value=datetime.now() - timedelta(days=7),
                          max_value=datetime.today())
    end = st.date_input("End date",
                          max_value=datetime.today())
    
    

    st.button(label="LOAD",on_click=load_data(options, start, end))
    # st.write(stocks_df)
    
    data = stocks_df

    # return calculation
    ret_df = data.pct_change()
    cum_ret = (ret_df + 1).cumprod() - 1
    pf_cum_ret = cum_ret.mean(axis=1)

    # benchmark
    psei = f"https://www.marketwatch.com/investing/index/psei/downloaddatapartial?startdate={start}%2000:00:00&enddate={end}%2023:59:59&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false&countrycode=ph"
    benchmark = pd.read_csv(psei, 
                            usecols=['Date', 'Close'], 
                            parse_dates=['Date'],
                            index_col='Date',
                            thousands=",")
    bench_ret = benchmark.pct_change()
    bench_dev = (bench_ret + 1).cumprod() - 1

    # covariance
    W = (np.ones(len(ret_df.cov()))/len(ret_df.cov()))
    pf_std = (W.dot(ret_df.cov()).dot(W)) ** (1/2)

    st.subheader("Portfolio vs. Index Development")
    tog = pd.concat([bench_dev, pf_cum_ret], axis=1)
    tog.columns = ['PSEi Performance', 'Portfolio Performance']
    st.line_chart(data=tog)

    st.subheader('Portfolio Risk:')
    pf_std

    st.subheader("Benchmark Risk:")
    bench_risk = bench_ret.std()
    bench_risk

    st.subheader("Porfolio composition")
    fig, ax = plt.subplots(facecolor='#121212')
    ax.pie(W, labels=data.columns, autopct='%1.1f%%', textprops={'color':'white'})

    st.pyplot(fig)
    

if __name__ == "__main__":
    main()