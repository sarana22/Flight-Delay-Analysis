import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Flight Delay Dashboard", layout="wide")

st.title("✈️ Airline Flight Delay Dashboard")
st.write("Interactive analysis of U.S. flight delays, cancellations, routes, and delay causes.")

# Load dataset from local CSV file and cache it for performance
@st.cache_data
def load_data():
    file_path = Path("data/cleaned_flight_data.csv")

    if not file_path.exists():
        st.error("File not found: data/cleaned_flight_data.csv")
        st.stop()

    df = pd.read_csv(file_path)

    if "FL_DATE" in df.columns:
        df["FL_DATE"] = pd.to_datetime(df["FL_DATE"], errors="coerce")

    if "OP_UNIQUE_CARRIER" in df.columns:
        df = df.rename(columns={"OP_UNIQUE_CARRIER": "OP_CARRIER"})

    return df


df = load_data()

# Feature Engineering: create new variables for analysis
# - Extract time features (Year, Month, Day)
# - Create Route (Origin → Destination)
# - Categorize delays and identify delayed flights
df["Year"] = df["FL_DATE"].dt.year
df["Month"] = df["FL_DATE"].dt.month
df["Month_Name"] = df["FL_DATE"].dt.month_name()
df["Day_Of_Week"] = df["FL_DATE"].dt.day_name()
df["Route"] = df["ORIGIN"] + " → " + df["DEST"]

# Helper function to convert month into season category
def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Fall"


df["Season"] = df["Month"].apply(get_season)

df["Is_Delayed"] = df["ARR_DELAY"] > 15

df["Delay_Category"] = pd.cut(
    df["ARR_DELAY"],
    bins=[-9999, 0, 15, 60, 180, 9999],
    labels=["Early/On-time", "Minor", "Moderate", "Major", "Extreme"]
)

# Handle delay cause columns and compute dominant delay cause
cause_cols = [
    "CARRIER_DELAY",
    "WEATHER_DELAY",
    "NAS_DELAY",
    "SECURITY_DELAY",
    "LATE_AIRCRAFT_DELAY"
]

available_causes = [col for col in cause_cols if col in df.columns]

if available_causes:
    df[available_causes] = df[available_causes].fillna(0)
    df["Total_Cause_Delay"] = df[available_causes].sum(axis=1)
    df["Dominant_Delay_Cause"] = df[available_causes].idxmax(axis=1)
    df.loc[df["Total_Cause_Delay"] == 0, "Dominant_Delay_Cause"] = "No Cause Listed"

# Sidebar filters for interactive exploration (airline, year, origin)
st.sidebar.header("Filters")

airlines = sorted(df["OP_CARRIER"].dropna().unique())
selected_airlines = st.sidebar.multiselect(
    "Select Airlines",
    airlines,
    default=airlines[:5]
)

years = sorted(df["Year"].dropna().unique())
selected_years = st.sidebar.multiselect(
    "Select Years",
    years,
    default=years
)

origins = sorted(df["ORIGIN"].dropna().unique())
selected_origin = st.sidebar.selectbox(
    "Select Origin Airport",
    ["All"] + origins
)

filtered_df = df[
    (df["OP_CARRIER"].isin(selected_airlines)) &
    (df["Year"].isin(selected_years))
]

if selected_origin != "All":
    filtered_df = filtered_df[filtered_df["ORIGIN"] == selected_origin]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# Key performance indicators summarizing filtered dataset
st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Flights", f"{len(filtered_df):,}")
col2.metric("Average Arrival Delay", f"{filtered_df['ARR_DELAY'].mean():.1f} min")
col3.metric("Delay Rate", f"{filtered_df['Is_Delayed'].mean() * 100:.1f}%")

if "CANCELLED" in filtered_df.columns:
    col4.metric("Cancellation Rate", f"{filtered_df['CANCELLED'].mean() * 100:.1f}%")
else:
    col4.metric("Cancellation Rate", "N/A")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Distribution of Arrival Delays",
    "Delay Causes",
    "Carrier Delay Analysis",
    "Route Delay Analysis"
])

# Tab 1: Distribution of delays
with tab1:
    st.subheader("Distribution of Arrival Delays")

    # Histogram showing distribution of arrival delays
    fig7 = px.histogram(
        filtered_df,
        x="ARR_DELAY",
        nbins=50,
        title="Distribution of Arrival Delays",
        labels={"ARR_DELAY": "Delay (minutes)"}
    )

    st.plotly_chart(fig7, use_container_width=True)

    st.subheader("Delay Category Distribution")

    category_counts = (
        filtered_df["Delay_Category"]
        .value_counts()
        .reset_index()
    )

    category_counts.columns = ["Delay Category", "Count"]
    st.caption(
    "Insight: The distribution of arrival delays is strongly right-skewed, with most flights experiencing small delays near zero. However, a long tail of large delays indicates that while severe delays are rare, they can be extremely high and contribute significantly to overall variability."
    )

    fig8 = px.bar(
        category_counts,
        x="Delay Category",
        y="Count",
        title="Delay Category Distribution"
    )

    st.plotly_chart(fig8, use_container_width=True)
    st.caption(
    "Insight: The majority of flights fall into early/on-time or minor delay categories, indicating generally stable operations. However, the presence of moderate, major, and extreme delays shows that while rare, severe delays do occur and contribute to variability in overall flight performance."
    )
    
# Tab 2: Analysis of delay causes
with tab2:
    st.subheader("Proportion of Delay Occurrences by Cause")

    available_delay_cols = [col for col in cause_cols if col in filtered_df.columns]

    if available_delay_cols:
        delay_counts = pd.DataFrame({
            col: (filtered_df[col] > 0).sum()
            for col in available_delay_cols
        }, index=[0]).T.reset_index()

        delay_counts.columns = ["Delay Cause", "Number of Delays"]

        fig6 = px.pie(
            delay_counts,
            names="Delay Cause",
            values="Number of Delays",
            title="Proportion of Delay Occurrences by Cause"
        )

        st.plotly_chart(fig6, use_container_width=True)

        st.caption(
            "Insight: Delay occurrences are overwhelmingly concentrated in carrier, late aircraft, and NAS-related factors, which together account for over 95% of all delays. In contrast, weather and security delays are minimal, indicating that most delays stem from operational and system-level inefficiencies rather than external disruptions."
        )

    else:
        st.warning("No delay cause columns found in this dataset.")


    st.subheader("Average Delay by Cause")

    if available_causes:
        avg_delay_by_cause = filtered_df[available_causes].mean().reset_index()
        avg_delay_by_cause.columns = ["Cause", "Average Delay (in minutes)"]

        fig9 = px.bar(
            avg_delay_by_cause,
            x="Cause",
            y="Average Delay (in minutes)",
            color="Cause",
            title="Average Delay by Cause",
            labels={
                "Cause": "Cause",
                "Average Delay": "Average Delay"
            }
        )

        fig9.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(fig9, use_container_width=True)
    else:
        st.warning("Delay cause columns were not found.")

    st.caption(
    "Insight: Late aircraft delays result in the highest average delay time, making them the most severe cause. Carrier and NAS delays also contribute significantly, while security delays have minimal impact."
)

# Tab 3: Airline performance analysis    
with tab3:
    st.subheader("Arrival Delay Rate by Airline (%)")

    delay_rate = (
    filtered_df.groupby("OP_CARRIER")["Is_Delayed"]
    .mean()
    .reset_index()
    )

    delay_rate["Is_Delayed"] = delay_rate["Is_Delayed"] * 100

    fig1 = px.bar(
    delay_rate,
    x="OP_CARRIER",
    y="Is_Delayed",
    color="Is_Delayed",
    title="Delay Rate by Airline",
    labels={"OP_CARRIER": "Airline", 
        "Is_Delayed": "Delay Rate (%)"}
    )

    st.plotly_chart(fig1, use_container_width=True)
    st.caption(
    "Insight: Delay rates vary across airlines, generally ranging between 15% and 30%. While no single airline dominates in delays, some carriers consistently show higher delay rates, suggesting differences in operational efficiency and scheduling performance."
    )

    st.subheader("Monthly Delay Trend")
    monthly_delay = (
        filtered_df.groupby(["Year", "Month"])["ARR_DELAY"]
        .mean()
        .reset_index()
    )

    monthly_delay["Time"] = (
        monthly_delay["Year"].astype(str)
        + "-"
        + monthly_delay["Month"].astype(str).str.zfill(2)
    )

    fig2 = px.line(
        monthly_delay,
        x="Time",
        y="ARR_DELAY",
        markers=True,
        title="Monthly Delay Trend",
        labels={"ARR_DELAY": "Delay (minutes)", "Time": "Time"}
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(
    "Insight: Delay patterns fluctuate over time, with noticeable peaks during mid-year periods across multiple years. This suggests that delays may increase during high travel seasons, such as summer, when flight demand and air traffic volume are higher."
    )

    st.subheader("Average Delay by Season")

    season_order = ["Winter", "Spring", "Summer", "Fall"]

    season_delay = (
        filtered_df.groupby("Season")["ARR_DELAY"]
        .mean()
        .reset_index()
    )

    season_delay["Season"] = pd.Categorical(
        season_delay["Season"],
        categories=season_order,
        ordered=True
    )

    season_delay = season_delay.sort_values("Season")

    fig3 = px.bar(
        season_delay,
        x="Season",
        y="ARR_DELAY",
        title="Average Delay by Season",
        labels={"ARR_DELAY": "Delay (minutes)", "Season": "Season"}
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.caption(
    "Insight: Seasonal trends reveal that delays peak during the summer months, likely due to increased travel demand and airport congestion. In contrast, fall experiences the lowest delays, suggesting more stable and less crowded flight operations."
    )
    
# Tab 4: Route-level delay analysis
with tab4:
    st.subheader("High-Risk Routes Based on Delay Frequency and Severity")

    top_airports = filtered_df["ORIGIN"].value_counts().head(10).index

    heatmap_data = filtered_df[
        filtered_df["ORIGIN"].isin(top_airports)
        & filtered_df["DEST"].isin(top_airports)
    ]

    heatmap_pivot = heatmap_data.pivot_table(
        values="ARR_DELAY",
        index="ORIGIN",
        columns="DEST",
        aggfunc="mean"
    )

    fig5 = px.imshow(
        heatmap_pivot,
        text_auto=".1f",
        title="Average Delay Heatmap: Origin vs Destination",
        labels={
            "x": "Destination",
            "y": "Origin",
            "color": "Average Delay"
        }
    )

    st.plotly_chart(fig5, use_container_width=True)
    st.write("This heatmap shows average delay between major airport pairs, helping identify high-risk routes.")
    st.caption(
    "Insight: The heatmap reveals clear variation in average delays across routes, with certain airport pairs consistently experiencing higher delays. This suggests that delays are not uniform across the network but are concentrated in specific routes, likely due to congestion, demand, or operational constraints at key airports."
    ) 

    # Scatter plot combining delay severity, frequency, and volume
    route_risk = (
        filtered_df.groupby("Route")
        .agg(
            Number_of_Flights=("Route", "count"),
            Average_Delay=("ARR_DELAY", "mean"),
            Delay_Rate=("Is_Delayed", "mean")
        )
        .reset_index()
    )

    route_risk = route_risk[route_risk["Number_of_Flights"] >= 10]

    fig10 = px.scatter(
        route_risk,
        x="Number_of_Flights",
        y="Average_Delay",
        color="Delay_Rate",
        size="Delay_Rate",
        hover_name="Route",
        title="Route Delay Risk Analysis",
        labels={
            "Number_of_Flights": "Number of Flights",
            "Average_Delay": "Average Delay",
            "Delay_Rate": "Delay Rate"
        }
    )

    st.plotly_chart(fig10, use_container_width=True)

    st.caption(
    "Insight: The relationship between flight volume and delays shows that low-frequency routes exhibit higher variability and more extreme delays, while high-volume routes tend to maintain more stable delay patterns. This indicates that operational consistency improves with route frequency, even under higher traffic conditions."
    )

st.markdown("---")
st.subheader("Key Insights")

st.write("""
- Flight delays are an industry-wide issue, with similar delay rates across airlines.
- Delays are highly route-specific, with certain airport pairs consistently experiencing higher delays.
- Delay causes occur at similar frequencies, but their impact differs significantly.
- Late aircraft delays are the most severe, making them the most impactful contributor.
- Most delays are small to moderate, indicating generally stable but imperfect operations.
""")

st.subheader("Limitations")

st.write("""
- The dataset contains only partial time coverage, limiting temporal and seasonal analysis.
- External factors such as detailed weather conditions and airport congestion are not fully captured.
- This analysis is descriptive and does not predict future delays.
""")