"""
Health Impact page - premature deaths and years of life lost from PM2.5
"""

import plotly.express as px
import streamlit as st

from Utils import filtered_default_countries, load_data

# Page configuration
st.set_page_config(
    page_title="Health Impact ~ ",
    page_icon="🎗",
    layout="wide"
)

st.title("Health Impact of fine particulate pollution ")
st.markdown(
    "The human cost of PM2.5 pollution. Switch between *premature deaths* "
    "(absolute numbers) and *years of life lost* (a measure of how early "
    "those deaths occurred) to see the different angles on the same problem. "
)

# load the data
df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# dictionary mapping for user-friendly labels
metric_options = {
    "Premature_deaths": "Premature deaths",
    "Years_of_life_lost": "Years of life lost (YLL)",
}

# metric toggle using radio button
# format_func uses a lambda to display the label in the UI
# this keeps the actual CSV column name as the underlying variable
metric_col = st.sidebar.radio(
    "Metric",
    options=list(metric_options.keys()),
    format_func=lambda x: metric_options[x],
    help="Premature deaths counts people| YLL weights deaths by years lost."
)

# grabbing the selected metric
metric_label = metric_options[metric_col]

# country filter
selected_countries = st.sidebar.multiselect(
    "Countries",
    options=sorted(df["Country"].unique()),
    default=filtered_default_countries(df),
)

# year range slider
# Restricting the year slider to years when this metric actually has data
metric_years = df.dropna(subset=[metric_col])["Year"]

# stop the app if there is no data.
if metric_years.empty:
    st.error(f"No data available for {metric_label}. ")
    st.stop()

# min/max years (*should be 2005, 2023)
year_min, year_max = int(metric_years.min()), int(metric_years.max())
year_range = st.sidebar.slider(
    "Years range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min,year_max),
    step=1,
)

# Apply filters

# stop if no countries are selected
if not selected_countries:
    st.info("Select at least one country in the sidebar to see the charts.")
    st.stop()

# filtering the df based on countries, year range, and drop rows missing the chosen metric!
filtered = df[
    df["Country"].isin(selected_countries)
    & df["Year"].between(*year_range)
].dropna(subset=[metric_col])

# stop app if no data
if filtered.empty:
    st.warning("No data for the chosen filters!")
    st.stop()

# Headline figure for lastest year
# finding the most recent year
latest = int(filtered["Year"].max())
total_latest = int(filtered.loc[filtered["Year"]== latest, metric_col].sum())
st.metric(
    label=f"Total {metric_label.lower()} across selected countries in {latest}",
    value=f"{total_latest},",
)

# first chart
st.subheader(f"{metric_label} over time")

# creating line chart using plotly express
trend_fig = px.line(
    filtered,
    x="Year",
    y=metric_col,
    color="Country",
    markers=True,
    labels={metric_col: metric_label, "Year": "Year"},
)
# updating the layout, showing all values for the year
trend_fig.update_layout(
    hovermode="x unified",
    legend_title_text="Country",
    margin=dict(l=10, r=10, t=10, b=10),
    height=500,
)
# no fractional years
trend_fig.update_xaxes(dtick=1, tickangle=-45)
st.plotly_chart(trend_fig, use_container_width=True)

# Second chart ( comparison barchart)
st.subheader(f"Country Ranking {latest}")

# snippet of the data from the most recent year
snapshot = (
    filtered[filtered["Year"]==latest]
    .sort_values(metric_col, ascending=True)
)

# creating the barchart
bar_fig = px.bar(
    snapshot,
    x=metric_col,
    y="Country",
    orientation="h",
    text=metric_col,
    labels={ metric_col: metric_label, "Country": ""},
)

# formatting the labels to include commas and sit outside the bars
bar_fig.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside",
    cliponaxis=False,
)

# same as last page, adjusting the height based on no. countries
bar_fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    height=max(300, 35*len(snapshot)),
    showlegend=False,
)
st.plotly_chart(bar_fig, use_container_width=True)

# data and download !

with st.expander("view and download the data~"):
    # creating a clean view of the data
    table = (
        filtered[["Country", "Year", metric_col]]
        .sort_values(["Country", "Year"])
        .reset_index(drop=True)
    )
    st.dataframe(table, use_container_width=True, hide_index=True)

    # download button
    st.download_button(
        label="📥 Download the data",
        data=table.to_csv(index=False).encode("utf-8"),
        file_name=f"health_{metric_col}_{year_range[0]}-{year_range[1]}.csv",
        mime="text/csv",
        )