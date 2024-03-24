import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import requests, os

from yahoo_fin import options
from copy import deepcopy
import base64

def get_options_chain(ticker):
    chain = options.get_options_chain(ticker.lower())
    return chain

