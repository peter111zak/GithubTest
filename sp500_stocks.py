import streamlit as st
import pandas as pd
import base64
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf

st.title("SP500 Companies List")
st.markdown("""\n This webapp does this and that....
            \n----
* **Data Source**: [Wikipedia] (https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
            \n----
            """)

st.sidebar.header("Input Features")

# scraping part


@st.cache_data
def load_data():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = pd.read_html(url, header=0)
    df = html[0]
    return df


df = load_data()
sector = df.groupby("GICS Sector")

# Sidebar - selection of sector(s)
sorted_sector_unique = sorted(df["GICS Sector"].unique())
selected_sectors = st.sidebar.multiselect(
    "Sector", sorted_sector_unique, sorted_sector_unique[:])

# Filtering out data of interest
df_selected_sectors = df[(df["GICS Sector"].isin(selected_sectors))]

# printing out data
st.header("List of Companies in the Selected Sector")
st.write("Data Dimension: " + str(df_selected_sectors.shape[0]) + " rows and " + str(
    df_selected_sectors.shape[1]) + "columns")
st.dataframe(df_selected_sectors, use_container_width=True)

# create a CSV (available for download) file


def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href


st.markdown(filedownload(df_selected_sectors), unsafe_allow_html=True)

data = yf.download(
    tickers=list(df_selected_sectors[:10].Symbol),
    period="max",
    interval="1d",
    group_by='ticker',
    auto_adjust=True,
    prepost=True,
    threads=True,
    proxy=None
)

# Plot Closing Price of Query Symbol

# COMMAND DIASBLING THE ERROR MESSAGE DISPLAYED **** /
st.set_option('deprecation.showPyplotGlobalUse', False)


def price_plot(symbol):
    df = pd.DataFrame(data[symbol].Close)
    df['Date'] = df.index
    plt.fill_between(df.Date, df.Close, color='skyblue', alpha=0.3)
    plt.plot(df.Date, df.Close, color='skyblue', alpha=0.8)
    plt.xticks(rotation=360)
    plt.title(symbol, fontweight='bold')
    plt.xlabel('Date', fontweight='bold')
    plt.ylabel('Closing Price', fontweight='bold')
    return st.pyplot()


num_company = st.sidebar.slider("Number of Companies: ", 1, 5)

if st.button('Show Plots'):
    st.header('Stock Closing Price')
    for stock_price_graph in list(df_selected_sectors.Symbol)[:num_company]:
        price_plot(stock_price_graph)