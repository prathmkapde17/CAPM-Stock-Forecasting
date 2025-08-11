# Importing libraries

import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import datetime
import capm_functions

st.set_page_config(page_title = "CAPM",
    page_icon = "chart_with_upwards_trend",
    layout = 'wide') 

st.title("Capital Asset Pricing Model with Stock Forecasting 💰")
st.caption("The Capital Asset Pricing Model (CAPM) describes the relationship between systematic risk, or the general perils of investing, and expected return for assets, particularly stocks.It is a finance model that establishes a linear relationship between the required return on an investment and risk.")


# Getting input from user

col1, col2 = st.columns([1,1])
with col1:
    stock_list = st.multiselect("Choose stocks by ticker",('AAPL', 'MSFT', 'AMZN', 'NVDA', 'GOOGL', 'TSLA', 'META', 'GOOG', 'BRK', 'UNH', 'XOM', 'JNJ', 'JPM', 'V', 'LLY', 'AVGO', 'PG', 'MA', 'HD', 'MRK', 'CVX', 'PEP', 'COST', 'ABBV', 'KO', 'ADBE', 'WMT', 'MCD', 'CSCO', 'PFE', 'CRM', 'TMO', 'BAC', 'NFLX', 'ACN', 'A','DE', 'GS', 'ELV', 'LMT', 'AXP', 'BLK', 'SYK', 'BKNG', 'MDLZ', 'ADI', 'TJX', 'GILD', 'MMC', 'ADP', 'VRTX', 'AMT', 'C', 'CVS', 'LRCX', 'SCHW', 'CI', 'MO', 'ZTS', 'TMUS', 'ETN', 'CB', 'FI'),('AAPL','TSLA','AMZN','GOOGL'))
with col2:
    year = st.number_input("Years of investment",1,10)

# Downloading data for SP500
try:
    end = datetime.date.today()
    start = datetime.date(datetime.date.today().year-year, datetime.date.today().month, datetime.date.today().day)
    SP500 = web.DataReader(['sp500'], 'fred', start, end)
    print(SP500.tail())

    stocks_df = pd.DataFrame()

    for stock in stock_list:
        data = yf.download(stock, period = f'{year}y')
        stocks_df[f'{stock}'] =  data['Close']

    stocks_df.reset_index(inplace = True)
    SP500.reset_index(inplace = True)
    SP500.columns = ['Date', 'sp500']
    stocks_df['Date'] = stocks_df['Date'].astype('datetime64[ns]')
    stocks_df['Date'] = stocks_df['Date'].apply(lambda x:str(x)[:10])
    stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
    stocks_df = pd.merge(stocks_df, SP500, on = 'Date', how = 'inner')

    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown("### Stock Prices (Head)")
        st.dataframe(stocks_df.head(), use_container_width = True)
    with col2:
        st.markdown("### Stock Prices (Tail)")
        st.dataframe(stocks_df.tail(), use_container_width = True)

    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown("### Price of all the Stocks")
        st.caption("initial stock prices")
        st.plotly_chart(capm_functions.interactive_plot(stocks_df))
    with col2:
        st.markdown("### Price of all the Stocks (After Normalizing)")
        st.caption("prices being normalized over initial stock prices")
        st.plotly_chart(capm_functions.interactive_plot(capm_functions.normalize(stocks_df)))

    stocks_daily_return = capm_functions.daily_return(stocks_df)

    beta  = {}
    alpha = {}

    for i in stocks_daily_return.columns:
        if i !='Date' and i != 'sp500':
            b, a = capm_functions.calculate_beta(stocks_daily_return, i)
            beta[i] = b
            alpha[i] = a

    beta_df = pd.DataFrame(columns = ['Stock', 'Beta Value'])
    beta_df['Stock'] = beta.keys()
    beta_df['Beta Value'] = [str(round(i,2)) for i in beta.values()]

    with col1:
        st.markdown('### Calculated Risk (β)')
        st.caption("risk of market is considered as 1")
        st.dataframe(beta_df, use_container_width = True)

    rf = 0
    rm = stocks_daily_return['sp500'].mean()*252

    return_df = pd.DataFrame()
    return_value = []
    for stocks, value in beta.items():
        return_value.append(str(round(rf+(value*(rm-rf)),2)))
    return_df['Stock'] = stock_list

    return_df['Return Value'] = return_value

    with col2:
        st.markdown('### Calculated Return using CAPM')
        st.caption("the risk-free rate + the beta (or risk) of the investment * the expected return on the market - the risk free rate")
        st.dataframe(return_df, use_container_width = True) 

except:
    st.write("Please select valid input...")
