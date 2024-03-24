import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import requests, os
# from gwpy.timeseries import TimeSeries
# from gwosc.locate import get_urls
# from gwosc import datasets
# from gwosc.api import fetch_event_json

from yahoo_fin import options
from yahoo_fin import stock_info
from copy import deepcopy
import base64

import plots as plot
import datetime

from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

# from helper import make_audio_file

# Use the non-interactive Agg backend, which is recommended as a
# thread-safe backend.
# See https://matplotlib.org/3.3.2/faq/howto_faq.html#working-with-threads.
import matplotlib as mpl
mpl.use("agg")

##############################################################################
# Workaround for the limited multi-threading support in matplotlib.
# Per the docs, we will avoid using `matplotlib.pyplot` for figures:
# https://matplotlib.org/3.3.2/faq/howto_faq.html#how-to-use-matplotlib-in-a-web-application-server.
# Moreover, we will guard all operations on the figure instances by the
# class-level lock in the Agg backend.
##############################################################################
from matplotlib.backends.backend_agg import RendererAgg
_lock = RendererAgg.lock

# -- Set page config
apptitle = 'Option Profit Calculator'

def get_options_chain(ticker, strategy: str, expiration: str):
    '''
    User enters a stock and the type of option chain they are looking for (long call, long put) and the function returns the chain. 
    '''
    chain = pd.DataFrame()
    if strategy == "Long Call":
        chain = options.get_calls(ticker.lower(),expiration)
    elif strategy == "Long Put":
        chain = options.get_puts(ticker.lower(),expiration)

    chain['Name'] = chain['Contract Name'].apply(plot.transcribe_option)
    cols = chain.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    chain = chain[cols]

    return chain

st.set_page_config(page_title=apptitle, page_icon="📈")
# Title the app
st.title('Options Calculator')

st.sidebar.markdown("## Stock Ticker")
ticker = st.sidebar.text_input('Input desired stock ticker', '')
dates = options.get_expiration_dates(ticker)

if len(dates)==0:
    st.error('Chosen ticker is invalid, please try again')
    st.stop()

st.sidebar.write("Chosen ticker is:", ticker)

expDate = st.sidebar.selectbox('Choose an expiration date', dates)

strategy = st.radio("Which option chain are you looking for?", ["Long Call", "Long Put","None"], index=None)
df = ""
if(strategy != "None"):
    df = get_options_chain(ticker, strategy, expDate)
    gb = GridOptionsBuilder.from_dataframe(df)
    #gb.configure_pagination(enabled=True)
    gb.configure_selection('single', use_checkbox=False, groupSelectsChildren=False, groupSelectsFiltered=False)
    grid_options = gb.build()

    st.subheader("Options List:")
    return_value = AgGrid(df, gridOptions=grid_options)

    # st.subheader("Grid Selection:")
    # st.write(return_value['selected_rows'])
    # st.subheader("DEBUG Values")
    # st.write(return_value['selected_rows'][0].get("Strike"))
    st.markdown("### Strike Price:")
    st.write(f"The strike price of your option is: {return_value['selected_rows'][0].get('Strike')}. At this point, your option will be in the money and you will be able to exercise.")

    heatmap = plot.make_heatmap(contract=return_value['selected_rows'][0],ticker=ticker,strategy=strategy, stock_price=return_value['selected_rows'][0].get("Strike"),exp=expDate) 
    st.write(heatmap[0])