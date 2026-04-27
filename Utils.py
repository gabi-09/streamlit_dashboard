"""
Centralises the data loaders and columns ! Every page imports the
 same definitions, so their individual page is kept clean to focus
  on visualisations.
"""

# imports

from pathlib import Path

import pandas as pd
import streamlit as st

# Constants ~~
# data pathfile
data_path = Path(__file__).parent / "datasets" / "proccessed" / "sustainability_merged.csv"

# renaming pollutant columns to more readable names
pollutant_cols = {
    "NOx_kt": "NOₓ",
    "PM2_5_kt": "PM2.5",
    "PM10_kt": "PM10",
    "NH3_kt": "NH₃",
    "NMVOC_kt": "NMVOC",
    "SOx_kt": "SOₓ"
}

# Random EU countries for the chart to load by default
default_countries = ["Germany", "Spain", "Sweden", "Portugal"]

@st.cache_data
def load_data():
    """
    Loading the merged sustainability dataset.
    Cached for the streamlit session so the CSV is read from disk only
    once for the other pages.

    Returns a dataframe with necessary columns. :)
    """
    return pd.read_csv(data_path)

def label_to_col(label):
    """
     turning the display label back to csv format
    """
    for col, lbl in pollutant_cols.items():
        if lbl == label:
            return col
    raise ValueError(f"The display label {label} is unknown...")

def filtered_default_countries(df):
    """
     Returns the default country list, intersected with countries in df.

     if the datafile is regenerated and one of the defaults is dropped
     , the page will still load with whatever defaults remain...
    """
    available = set(df["Country"].unique())
    return [c for c in default_countries if c in available]
