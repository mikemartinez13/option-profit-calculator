import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

from plots import long_call, long_put, short_call, short_put, plot_payoff, get_stock_prices
from data_utils import get_options_chain, get_options_date, get_price

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

# -- Set page config
APPTITLE = 'Option Profit Calculator'

def main():
    if 'selected_rows' not in st.session_state:
        st.session_state.selected_rows = []
    
    st.set_page_config(page_title=APPTITLE, page_icon="📈")
    # Title the app
    st.title('Options Calculator')

    st.sidebar.markdown("## Stock Ticker")
    ticker = st.sidebar.text_input('Input desired stock ticker', '')

    #dates = options.get_expiration_dates(ticker)
    dates = get_options_date(ticker)

    if len(dates)==0:
        st.error('Chosen ticker is invalid, please try again')
        st.stop()

    st.sidebar.write("Chosen ticker is:", ticker)

    expDate = st.sidebar.selectbox('Choose an expiration date', dates)

    strategy = st.radio("Which option chain are you looking for?", ["Long Call", "Long Put","None"], index=None)
    df = ""
    if(strategy != "None"):
        df = get_options_chain(ticker, strategy, expDate)
        # st.write(str(df))
        # exit()
        gb = GridOptionsBuilder.from_dataframe(df)
        #gb.configure_pagination(enabled=True)
        gb.configure_selection('single', 
                            use_checkbox=False, 
                            groupSelectsChildren=False, 
                            groupSelectsFiltered=False
                            )
        grid_options = gb.build()

        st.subheader("Options List:")
        return_value = AgGrid(df, 
                            gridOptions=grid_options,
                            update_mode=GridUpdateMode.SELECTION_CHANGED,
                            height=200,
                            width='100%',
                            allow_unsafe_jscode=True,  # Set to True to enable certain JS features
                            key='aggrid-options'  # Unique key to preserve state
                        )
        selected_rows = return_value['selected_rows']

        if selected_rows:
            st.session_state.selected_rows = selected_rows
        else:
            pass

        if st.session_state.selected_rows:
            st.write("Selected Row Data:")
            st.json(st.session_state.selected_rows[0])
        else:
            st.write("No row selected.")

        price = get_price(ticker)
        st.write(price)

        S = get_stock_prices(price)

        if strategy == "Long Call":
            P = long_call(S, st.session_state.selected_rows[0]['Strike'], st.session_state.selected_rows[0]['Ask'])
        elif strategy == "Long Put":
            P = long_put(S, st.session_state.selected_rows[0]['Strike'], st.session_state.selected_rows[0]['Ask'])
        
        fig = plot_payoff(S, P)

        st.pyplot(fig)


if __name__ == '__main__':
    main()
