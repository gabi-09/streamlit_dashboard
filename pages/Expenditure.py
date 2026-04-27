"""
Expenditure page, health expenditure per capital across Europe!
"""

# Imports
import plotly.express as px
import streamlit as st

from Utils import colourblind_palette, filtered_default_countries, load_data

# Page configuration ~
st.set_page_config(
    page_title="Expenditure",
    page_icon="💵",
    layout="wide",
)

st.title("Health Expenditure per Capita")
st.markdown(
    "Current health expenditure per capita, in US dollars, across Europe. "
    "Useful context for the human cost figures on the Health Impact page- "
    "pollution driven illness drives spending..."
)

expenditure_col = "Health_expenditure_per_capita_USD"

# Loading the dataset
df = load_data()

# sidebar filters

st.sidebar.header("Filters")

selected_countries = st.sidebar.multiselect(
    "Countries",
    options= sorted(df["Country"].unique()),
    default=filtered_default_countries(df),
)

health_years = df.dropna(subset=[expenditure_col])["Year"]
year_min, year_max = int(health_years.min()), int(health_years.max())
year_range = st.sidebar.slider(
    "Year range",
    min_value = year_min,
    max_value = year_max,
    value = (year_min, year_max),
    step=1
)

# Apply filters

if not selected_countries:
    st.info("Select at least one country in the sidebar to see the data")
    st.stop()

filtered = df[
    df["Country"].isin(selected_countries)
    & df["Year"].between(*year_range)
    ].dropna(subset=[expenditure_col])

# stop the app if there is no data to display
if filtered.empty:
    st.warning("No data for the chosen filters!")
    st.stop()

# Headline metrics

latest = int(filtered["Year"].max())
latest_snapshot = filtered[filtered["Year"] == latest]

# 3 column display
c1, c2, c3 = st.columns(3)

# Highest spender
with c1:
    top = latest_snapshot.loc[latest_snapshot[expenditure_col].idxmax()]
    st.metric(
        label=f"Highest spender ({latest})",
        value=f"${top[expenditure_col]:,.0f}",
        help=top["Country"]
    )

# Lowest spender
with c2:
    bottom = latest_snapshot.loc[latest_snapshot[expenditure_col].idmin()]
    st.metric(
        label=f"Lowest spender ({latest})",
        value=f"${bottom[expenditure_col]:,.0f}",
        help=bottom["Country"]
    )

# Average spending
with c3:
    avg = latest_snapshot[expenditure_col].mean()
    st.metric(
        label=f"Average ({latest})",
        value=f"${avg:,.0f}",
    )

# first chart, trend over time per country
st.subheader("Health Expenditure per Capita over time")

trend_fig = px.line(
    filtered,
    x="Year",
    y=expenditure_col,
    color="Country",
    markers=True,
    labels={
        expenditure_col: "Health expenditure per capita (US$)",
        "Year": "Year",
    },
    color_discrete_sequence= colourblind_palette,
)

# updating the layout
trend_fig.update_layout(
    hovermode="x unified",
    legend_title_text="Country",
    margin=dict(l=10, r=10, t=10, b=10),
    height=500,
)

trend_fig.update_xaxes(dtick=1, tickangle=-45)
trend_fig.update_yaxes(tickprefix="$", tickformat=",")
st.plotly_chart(trend_fig, use_container_width=True)

# Latest year ranking bar chart !
ranking = latest_snapshot.sort_values(expenditure_col, ascending=True)

bar_fig = px.bar(
    ranking,
    x=expenditure_col,
    y="Country",
    orientation="h",
    text=expenditure_col,
    labels={expenditure_col: "Health expenditure per capita (US$)", "Country": "" },
    color_discrete_sequence= colourblind_palette,

)
# updating the layout
bar_fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside",
    cliponaxis=False,
)

bar_fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    height=max(300, 35*len(ranking)),
    showlegend=False,
)
bar_fig.update_xaxes(tickprefix="$", tickformat=",")
st.plotly_chart(bar_fig, use_container_width=True)

# Download the data option
with st.expander(" View and download the filtered data"):
    table = (
        filtered[["Country", "Year", expenditure_col]]
        .sort_values(["Country", "Year"])
        .reset_index(drop=True)
    )
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.download_button(
        label="Download as CSV",
        data = table.to_csv(index=False).encode("utf-8"),
        file_name=f"Health_expenditure{year_range[0]}-{year_range[1]}.csv",
        mime="text/csv",
    )
