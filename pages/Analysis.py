"""
Combined Analysis page, shows the relationship between emissions, deaths and spending
"""

# Imports
import plotly.express as px
import streamlit as st

from Utils import pollutant_cols, label_to_col, load_data

# Page configuration
st.set_page_config(
    page_title="Combined Analysis",
    page_icon="💹",
    layout="wide",
)

st.title("The Pollution-Health-Cost Relationship")
st.markdown(
    "Each bubble below is a country, sized by its per-capita health spending. "
    "The horizontal axis shows pollutant emissions and the vertical shows "
    "premature deaths from PM2.5. ~ Hover for the exact values."
)

deaths_col = "Premature_deaths"
yll_col = "Years_of_life_lost"
spending_col = "Health_expenditure_per_capita_USD"

# loading the data
df = load_data()

# sidebar

st.sidebar.header("Controls")

selected_pollutant_label = st.sidebar.selectbox(
    "Pollutant on x-axis",
    options=list(pollutant_cols.values()),
    index=1,
)
pollutant_col = label_to_col(selected_pollutant_label)

# death related y-axis can be absolute deaths or YLL
y_metric_options = {
    deaths_col: "Premature deaths",
    yll_col: "Years of life lost (YLL)",
}
y_col = st.sidebar.radio(
    "Y-axis metric",
    options=list(y_metric_options.keys()),
    format_func=lambda x: y_metric_options[x],
)
y_label = y_metric_options[y_col]

# restricting the year selector to years where all three columns have data!!
required_cols = [pollutant_col, yll_col, spending_col]
years_with_full_data = sorted(
    df.dropna(subset=required_cols)["Year"].unique()
)

# stopping app if no data
if not years_with_full_data:
    st.error(
        "No years have data for all three required metrics with this "
        "combination. Try a different pollutant or Y-axis metric.."
    )
    st.stop()

selected_year = st.sidebar.select_slider(
    "Year",
    options=years_with_full_data,
    value=years_with_full_data[-1],
)

show_trendline = st.sidebar.checkbox(
    "Show trendline",
    value=True,
    help="Regression line across all visible countries",
)

# Snapshot

snapshot = df[df["Year"] == selected_year].dropna(subset=required_cols).copy()

if snapshot.empty:
    st.warning(f"No countries have complete data for {selected_year}")
    st.stop()

# headlining numbers across the snapshot, 3 column layout

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(
        label=f"Total {selected_pollutant_label} emissions ({selected_year})",
        value=f"{snapshot[pollutant_col].sum():,.0f} kt",
    )

with c2:
    st.metric(
        label=f"Total {y_label.lower()} ({selected_year})",
        value=f"{snapshot[y_col].sum():,.0f}",
    )

with c3:
    st.metric(
        label=f"Average health spend per capita ({selected_year})",
        value=f"${snapshot[spending_col].mean():,.0f}",
    )

# creating the bubble chart
st.subheader(
    f"Emissions vs {y_label.lower()} in {selected_year} "
    f"(bubble size = health spend per capita)"
)

scatter_kwargs = dict(
    x=pollutant_col,
    y=y_col,
    size=spending_col,
    color="Country",
    hover_name="Country",
    hover_data={
        pollutant_col: ":,.1f",
        y_col: ":,.0f",
        spending_col: ":$,0f",
        "Country": False,
    },
    labels={
        pollutant_col: f"{selected_pollutant_label} emissions (kt)",
        y_col: y_label,
        spending_col: f"Health spending per capita",
    },
    size_max=55,
)

if show_trendline:
    bubble_fig = px.scatter(
        snapshot,
        trendline="ols",
        trendline_scope="overall",
        trendline_color_override="blue",
        **scatter_kwargs,
    )
else:
    bubble_fig = px.scatter(
        snapshot,
        **scatter_kwargs,
    )

bubble_fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    height=600,
    legend_title_text="Country",
)
st.plotly_chart(bubble_fig, use_container_width=True)

# Correlation summary!
with st.expander("Pairwise correlations across countries this year"):
    corr_df = snapshot[[pollutant_col, y_col, spending_col]].rename(
        columns={
            pollutant_col: f"{selected_pollutant_label} kt",
            y_col: y_label,
            spending_col: "Spend per capita",
        }
    )
    correlations = corr_df.corr(numeric_only=True).round(2)
    st.dataframe(correlations, use_container_width=True)
    st.caption(
        "Pearson correlation coefficients. "
        "Values closer to 1 or -1 indicate a strong linear relationship. "
        "Values closer to 0 indicate little linear relationship, important "
        "to know that correlation does not always imply causation."

    )

# Download option
with st.expander("View and download the data"):
    display = snapshot[["Country", "Year"] + required_cols].sort_values(
        y_col, ascending=True
    ).reset_index(drop=True)
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.download_button(
        label="Download as CSV",
        data=display.to_csv(index=False).encode("utf-8"),
        file_name=f"combined_analysis_{selected_year}.csv",
        mime="text/csv",
    )
