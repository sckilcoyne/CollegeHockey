# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 20:45:45 2021

Set up streamlit app and create cached functions

@author: Scott
"""

import streamlit as st

# Modules with functions to cache
from utils.Ranking_Coefficients import coefficients

# %% Set up streamlit app
st.set_page_config(page_title='College Hockey Ranking',
                   page_icon=':ice_hockey_stick_and_puck:',
                   initial_sidebar_state='expanded',
                   layout='wide')

# %% Cached versions of functions


@st.cache
def coefficients_cache():
    """
    Load rating coeffiecients as streamlit cache.

    Returns
    -------
    coefficients : dict
        Dict of rating coefficients.

    """
    return coefficients()
