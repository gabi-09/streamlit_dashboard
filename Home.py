"""
SUSTAINABILITY DASHBOARD ~~ Home page.

This will provide an overview of the three datasets and headline figures that motivate
deeper analysis pages.
"""

# Imports
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import plotly.express as px

from pathlib import Path

# Page configuration !!
st.set_page_config(
    page_title="Sustainability Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load the data
data_path = Path(__file__).parent / "datasets" / "processed" / "sustainability_merged.csv"

@st.cache_data
def load_data():
    """Loading the merged sustainability dataset.
    This is cached so the file is only read once per session!!
    Returns the df"""
    df = pd.read_csv(data_path)
    return df

df = None
try:
    df = load_data()
except FileNotFoundError:
    st.error(
        f'The dataset cannot be found at "{data_path}"'
        f'Run the cleaning data notebook first to generate the file!!'
    )
    st.stop()

# Header
st.title("Sustainability Dashboard")
st.markdown(
    "**Air Pollution, Public health, and the cost of inaction across Europe, 2005-2023**"
)
st.markdown(
    "This dashboard helps decision-makers explore the relationship between"
    "air pollutant emissions, premature deaths from fine particulate matter,"
    "and per-capita healthcare expenditure. Use the sidebar to navigate to"
    "the detailed analysis pages!"
)
st.divider()

# Headline Metrics ( KPI CARDS )

st.subheader("At a glance ~")
col1, col2, col3, col4 = st.columns(4)

with col1:
    n_countries = df["Country"].nunique()
    st.metric(label="Number of countries covered", value=n_countries)

with col2:
    year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
    st.metric(label="Year range", value=f"{year_min}-{year_max}")

with col3:
    latest_year = int(df.dropna(subset=["Premature_deaths"])["Year"].max())
    total_deaths = int(df.loc[df["Year"] == latest_year, "Premature_deaths"].sum())
    st.metric(
        label=f"Premature deaths in {latest_year}",
        value=f"{total_deaths:,}",
        help="Total across all covered countries, attributable to fine particulate matter (PM2.5)"
    )

with col4:
    latest_health = int(df.dropna(subset=["Health_expenditure_per_capita_USD"])["Year"].max())
    avg_health = df.loc[
        df["Year"] == latest_health, "Health_expenditure_per_capita_USD"
    ].mean()
    st.metric(
        label=f"Average health spend per capital ({latest_health})",
        value=f"{avg_health:,.0f}",
    )

st.divider()

# Dataset overview !
st.subheader("The three datasets used...")
ds_col1, ds_col2, ds_col3 = st.columns(3)

with ds_col1:
    st.markdown("### ☁️ Air Pollutant Emissions ☁️")
    st.markdown(
        "**Source:** European Environment Agency \n"
        "**Pollutants:** NH3, NMVOC, NOx, PM10, PM2.5, S0x\n"
        "**Unit:** kilotonnes (kt)\n"
    )

with ds_col2:
    st.markdown("### 🎗 Premature deaths from PM2.5 🎗")
    st.markdown(
        "**Source:** Eurostat \n"
        "**Metrics:** Premature deaths, Years of Life Lost (YLL)\n"
        "**Unit:** Number of people / Years\n"
    )
with ds_col3:
    st.markdown("### 💵 Health Expenditure per Capita 💵")
    st.markdown(
        "**Source:** World Bank \n"
        "**Indicator:** Current Health expenditures per Capita\n"
        "**Unit:** US$ Dollars\n"
    )
st.divider()

# Trend plots (Matplotlib)
st.subheader("Headline Trends")
st.caption(
    "Aggregate trends across all covered countries."
    "For country-level analysis, use the dedicated pages in the side bar~"
)

plot_col1, plot_col2 = st.columns(2)

with plot_col1:
    yearly_pm25 = (
        df.dropna(subset=["PM2_5_kt"])
        .groupby("Year")["PM2_5_kt"]
        .sum()
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(
        yearly_pm25["Year"],
        yearly_pm25["PM2_5_kt"],
        marker="o",
        linewidth=2,
        color="#c0392b"
    )
    ax.fill_between(
        yearly_pm25["Year"], yearly_pm25["PM2_5_kt"], alpha=0.15, color="#c0392b"
    )

    ax.set_title("Total PM2.5 emissions across Europe", fontsize=12, fontweight="bold")
    ax.set_xlabel("Year", fontsize=9)
    ax.set_ylabel("PM2.5 emissions (kilotonnes)", fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True)) # To get rid of matplot 2005.0.. 2007.5 year quirks
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with plot_col2:
    yearly_deaths = (
        df.dropna(subset=["Premature_deaths"])
        .groupby("Year")["Premature_deaths"]
        .sum()
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(
        yearly_deaths["Year"],
        yearly_deaths["Premature_deaths"],
        color="#2c3e50",
        alpha=0.8,
    )

    ax.set_title("Premature deaths from PM2.5 across Europe", fontsize=12, fontweight="bold")
    ax.set_xlabel("Year", fontsize=9)
    ax.set_ylabel("Number of premature deaths", fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.divider()

# Footer ( navigation )

st.subheader("How to use this dashboard")
st.markdown(
    """
    1. **Emissions** - explore air pollutant trends by country and pollutant type
    2. **Health Impact** - see the human cost of fine particulate pollution
    3. **Expenditure** - compare healthcare spending across countries
    4. **Combined Analysis** - explore the relationships between all three metrics
    """
)

with st.expander("Data Prep Note"):
    st.markdown(
        """
        - Data is restricted to the common window between 2005 and 2023.
        - Countries with 18+ years of missing data in any metric were excluded.
        - Sub-national figures for premature deaths were aggregated to national totals.
        - See the cleaning data notebook for the full pipeline.
        """
    )