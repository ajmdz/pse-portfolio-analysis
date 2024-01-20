import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import json
from datetime import datetime, timedelta
from marketwatch_loader import load_df

with open('stocks.json', 'r') as stocks:
    stock_dict = json.load(stocks)
    sym_to_name = {sym: name for name, sym in stock_dict.items()}


def main():
    st.title("PSE Investment Portfolio Dashboard")

    options = st.multiselect('Select stocks', stock_dict.keys())

    if options != []:

        col1, col2 = st.columns(2)

        with col1:
            start = st.date_input("Start date",
                                  value=datetime.now() - timedelta(days=7),
                                  max_value=datetime.today())
        with col2:
            end = st.date_input("End date",
                                max_value=datetime.today())
        
        symbols = [stock_dict[stock] for stock in options]

        button = st.button('LOAD', use_container_width=True)

        if button:
            with st.spinner('Downloading data...'):
                index = load_df(['psei'],start,end, is_index=True)
                stocks = load_df(symbols,start,end)
            load_analysis(index, stocks)
        
    
def load_analysis(index, stocks):
    st.divider()
    st.subheader('Analysis')
    # portfolio
    returns = stocks.pct_change()
    cumulative_ret = (returns + 1).cumprod() - 1
    pf_cumulative_ret = cumulative_ret.mean(axis=1)

    # benchmark
    bench_ret = index.pct_change()
    bench_dev = (bench_ret + 1).cumprod() - 1

    # covariance
    equal_weights = (np.ones(len(returns.cov()))/len(returns.cov()))
    pf_std = (equal_weights.dot(returns.cov()).dot(equal_weights)) ** (1/2)
    
    plot_performance(pf_cumulative_ret, bench_dev)
    plot_allocation(equal_weights, stocks)

    
def plot_performance(portfolio_perf, benchmark_perf):
    tog = pd.concat([benchmark_perf, portfolio_perf], axis=1)
    tog.columns = ['PSEi Performance', 'Portfolio Performance']
    fig = px.line(tog, x=tog.index, y=tog.columns,
                  title='Portfolio (Balanced) vs. Index Performance')
    fig.update_xaxes(
        dtick="M1",
        ticklabelmode="period")
    
    st.plotly_chart(fig)


def plot_allocation(portfolio_weights, stocks):
    fig = px.pie(portfolio_weights, 
                 names=[sym_to_name[stock.lower()] for stock in stocks.columns], 
                 color_discrete_sequence=px.colors.qualitative.Dark24,
                 title='Portfolio Distribution')
    st.plotly_chart(fig)


if __name__ == "__main__":
    main()

