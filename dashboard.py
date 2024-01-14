import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

tickers = ['AYYLF', 'AYAAF', 'BDOUY', 'BPHLY', 'GTMEY', 'JBFCF',
           'JGSHF', 'MAEOY', 'SVTMF', 'SMGBF', 'UVRBF', 'PHI']

def main():
    st.title("PSE Investment Portfolio Dashboard")

    options = st.multiselect(
        'Select stocks',
        tickers,
        ['AYYLF', 'JBFCF', 'SMGBF']
    )
    assets = ','.join(options)

    start = st.date_input("Pick a starting date for analysis",
                          value=pd.to_datetime('2023-01-01'))
    
    data = yf.download(assets, start=start)['Adj Close']

    # return calculation
    ret_df = data.pct_change()
    cum_ret = (ret_df + 1).cumprod() - 1
    pf_cum_ret = cum_ret.mean(axis=1)

    # benchmark
    benchmark = yf.download('PSEI.PS', start=start)['Adj Close']
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