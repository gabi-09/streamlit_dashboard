"""
Emissions page ( air pollutant trends across europe.) ~

"""

# imports
import plotly.express as px
import streamlit as st

# importing from Utils.py
from Utils import (
    colourblind_palette,
    pollutant_cols,
    filtered_default_countries,
    label_to_col,
    load_data,
)

# Configuration

st.set_page_config(
    page_title="Emissions",
    page_icon="☁️",
    layout="wide",
)

st.title("Air Pollutant Emissions")
st.markdown(
    "Explore the long-term trends in air pollutant emissions across europe. "
    "Use the sidebar to choose which countries and pollutant to focus on, "
    "and which years to include."

)

# load the data
df = load_data()
# Sidebar filters

st.sidebar.header("Filters")

# creating country filter
selected_countries = st.sidebar.multiselect(
    "Countries",
    options=sorted(df["Country"].unique()),
    default=filtered_default_countries(df),
    help="Pick one or more countries to compare!",
)

# pollutant filter
selected_pollutant_label = st.sidebar.selectbox(
    "Pollutant",
    options=list(pollutant_cols.values()),
    index=1,
    help="Which Pollutant to display."
)
# converting frontend to backend so pandas is happy and no KeyErrors
selected_pollutant_col = label_to_col(selected_pollutant_label)

# 2005(min), 2023(max) | year range filter
year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
year_range = st.sidebar.slider(
    "Year range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
    step=1,
)

# Apply filters

# stopping the app early if user clears all countries from the multiselect
if not selected_countries:
    st.info("Select at least one country to see the chart!")
    st.stop()

# Filtering the df based on all three sidebar inputs
filtered = df[
    df["Country"].isin(selected_countries)
    & df["Year"].between(*year_range)
].dropna(subset=[selected_pollutant_col])

# again, stopping the app if the combination results in an empty graph
if filtered.empty:
    st.warning(
        "No data available for the chosen combination of countries/pollutant "
        "and year range. Try widening your selection."
    )
    st.stop()

# First plot !! Trend over time, line chart
st.subheader(f"{selected_pollutant_label} emissions over time")
# Creating a plotly line chart for more interactivity
trend_fig = px.line(
    filtered,
    x="Year",
    y=selected_pollutant_col,
    color="Country",
    markers=True,
    labels={
        selected_pollutant_col: f"{selected_pollutant_label} emissions (kt)",
        "Year": "Year",
    },
    color_discrete_sequence= colourblind_palette,
)

# Showing all values for a given year, updating the layout
trend_fig.update_layout(
    hovermode="x unified",
    legend_title_text="Country",
    margin=dict(l=10, r=10, t=10, b=10),
    height=450,
)
# no fractional years by focing x-axis to show integers, angle the labels
trend_fig.update_xaxes(dtick=1, tickangle=-45) # one tick per year, no decimals
st.plotly_chart(trend_fig, use_container_width=True)

# Chart 2 cross-section comparison, bar chart
st.header("Country comparison")

# allowing the user to pick a specific year from their filtered subset
available_years = sorted(filtered["Year"].unique(), reverse=True)
comparison_year = st.selectbox(
    "Year for country comparison",
    options=available_years,
    index=0,
    help="Pick a single year to rank countries by emissions.",
)

# Creating a snippet of that specific year, sorted by smallest to largest pollutants
snapshot = (
    filtered[filtered["Year"] == comparison_year]
    .sort_values(selected_pollutant_col, ascending=True)
)

if snapshot.empty:
    st.info(f"No data for {comparison_year} with the current filters")
else:
    # creating a horizontal bar chart
    bar_fig = px.bar(
        snapshot,
        x=selected_pollutant_col,
        y="Country",
        orientation="h",
        text=selected_pollutant_col,
        labels={
            selected_pollutant_col : f"{selected_pollutant_label} emissions (kt)",
            "Country": "",
        },
        color_discrete_sequence= colourblind_palette,
    )

    # formatting data labels to include commas, no decimals
    bar_fig.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        cliponaxis=False,
    )

    # adjusting the height based on how many countries are selected
    bar_fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=max(300, 35 *len(snapshot)),
        showlegend=False,
    )
    st.plotly_chart(bar_fig, use_container_width=True)

    # Data table + download option

    with st.expander("View and download the filtered data"):
        display_cols = ["Country", "Year", selected_pollutant_col]
        # prepping the final table for display
        table = (
            filtered[display_cols]
            .sort_values(["Country", "Year"])
            .reset_index(drop=True)
        )
        # render
        st.dataframe(table, use_container_width=True, hide_index=True)

        st.download_button(
            label="📥 Download as CSV",
            data=table.to_csv(index=False).encode("utf-8"),
            file_name=f"emissions_{selected_pollutant_col}_{year_range[0]}-{year_range[1]}.csv",
            mime="text/csv",
        )
