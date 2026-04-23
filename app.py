import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

    
# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Baguette Bistro Analytics",
    page_icon="🥖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# =========================
# COLOR PALETTE
# =========================
PRIMARY_RED = "#C73A3A"
DEEP_RED = "#8E1F1F"
SOFT_RED = "#D97777"

NAVY = "#4E647D"
SLATE = "#6B7280"
LIGHT_BLUE = "#8FA8C5"
SOFT_GRAY = "#B0B8C4"

BG = "#FCFAF8"
TEXT = "#2B2B2B"
MUTED = "#8A817C"
BORDER = "#E9D9D9"
CARD_BG = "#FFFDFC"
GRID = "#F0EAEA"

# =========================
# CUSTOM CSS
# =========================
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG};
        color: {TEXT};
    }}

    .block-container {{
        padding-top: 0.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1500px;
    }}

    .brand-title {{
        font-size: 22px;
        font-weight: 700;
        color: {DEEP_RED};
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 18px;
        margin-top: 6px;
    }}

    .brand-title::after {{
        content: "";
        display: block;
        width: 60px;
        height: 3px;
        background-color: {PRIMARY_RED};
        margin-top: 8px;
        border-radius: 2px;
    }}

    .kpi-card {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 12px 16px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.03);
        min-height: 82px;
    }}

    .kpi-label {{
        font-size: 0.78rem;
        font-weight: 600;
        color: {MUTED};
        margin-bottom: 8px;
    }}

    .kpi-value {{
        font-size: 1.55rem;
        font-weight: 700;
        line-height: 1.0;
    }}

    .kpi-note {{
        font-size: 0.74rem;
        color: {MUTED};
        margin-top: 6px;
    }}

    div[data-testid="column"] {{
        padding: 0 6px !important;
    }}

    div[data-testid="stPlotlyChart"] {{
        background-color: white;
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 2px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}

    section[data-testid="stSidebar"] {{
        background-color: #fbf7f5;
        border-right: 1px solid {BORDER};
        min-width: 260px !important;
        max-width: 260px !important;
        overflow: hidden !important;
    }}

    section[data-testid="stSidebar"] > div {{
        padding-top: 0.25rem !important;
        overflow: hidden !important;
    }}

    div[data-testid="stSidebarContent"] {{
        padding-top: 0.25rem !important;
        padding-bottom: 0.25rem !important;
        overflow: hidden !important;
        height: 100vh !important;
    }}

    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {DEEP_RED};
    }}

    label, .stDateInput label, .stMultiSelect label {{
        font-weight: 600 !important;
        color: #4e4743 !important;
    }}

    span[data-baseweb="tag"] {{
        background-color: #F4C7C7 !important;
        color: #6B1E1E !important;
        border: none !important;
    }}

    div[data-testid="stSelectbox"],
    div[data-testid="stNumberInput"],
    div[data-testid="stSlider"] {{
        margin-bottom: 0.2rem;
    }}

    div[data-testid="stMarkdownContainer"] p {{
        margin-bottom: 0.25rem;
    }}

    div[data-testid="stVerticalBlock"] > div {{
        gap: 0.35rem;
    }}

    .stButton > button {{
        border-radius: 10px;
        border: 1px solid {BORDER};
        padding: 0.55rem 1rem;
        font-weight: 600;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

USD_RATE = 90000  # 1 USD = 90,000 L.L.

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    tx = pd.read_excel("transactions_final_cleaned.xlsx")
    ratings = pd.read_excel("ratings_summary_cleaned.xlsx")
    items = pd.read_excel("items_cleaned.xlsx")
    users = pd.read_excel("users_cleaned.xlsx")
    daily_orders = pd.read_csv("daily_orders_processed.csv")
    return tx, ratings, items, users, daily_orders

tx, ratings, items, users, daily_orders = load_data()

# =========================
# CLEAN / FORMAT
# =========================
tx["Order Date"] = pd.to_datetime(tx["Order Date"], errors="coerce")
tx["order_date"] = pd.to_datetime(tx["order_date"], errors="coerce")
tx["weekday"] = tx["weekday"].astype(str)
tx["Order Channel"] = tx["Order Channel"].astype(str)

for col in ["Final Total", "Delivery Time_min", "late_flag", "order_hour"]:
    if col in tx.columns:
        tx[col] = pd.to_numeric(tx[col], errors="coerce")



# =========================
# NAVIGATION
# =========================
if "page" not in st.session_state:
    st.session_state.page = "Home"

page_options = ["Home", "Executive Dashboard", "Predictive Models"]

# If NOT on Home → show sidebar navigation
if st.session_state.page != "Home":

    st.sidebar.markdown(
        """
        <div class="brand-title">
            Baguette Bistro
        </div>
        """,
        unsafe_allow_html=True
    )


    page = st.sidebar.radio(
        "Navigation",
        page_options,
        index=page_options.index(st.session_state.page)
    )

# If on Home → no sidebar navigation
else:
    page = "Home"

# Save state
st.session_state.page = page

# =========================
# HIDE SIDEBAR ON HOME
# =========================
if page == "Home":
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none !important;}
            [data-testid="collapsedControl"] {display: none !important;}
        </style>
    """, unsafe_allow_html=True)


# Show filters only on Executive Dashboard
if page == "Executive Dashboard":
    st.sidebar.markdown("## Dashboard Filters")

    min_date = tx["Order Date"].min().date()
    max_date = tx["Order Date"].max().date()

    date_range = st.sidebar.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    channels = st.sidebar.multiselect(
        "Order Channel",
        options=sorted(tx["Order Channel"].dropna().unique()),
        default=sorted(tx["Order Channel"].dropna().unique())
    )

    weekdays = st.sidebar.multiselect(
        "Weekday",
        options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )
else:
    date_range = None
    channels = None
    weekdays = None

# =========================
# SHARED HELPERS
# =========================
def format_ll(x):
    if pd.isna(x):
        return "-"
    if x >= 1_000_000_000:
        return f"LL {x/1_000_000_000:.2f}B"
    if x >= 1_000_000:
        return f"LL {x/1_000_000:.2f}M"
    if x >= 1_000:
        return f"LL {x/1_000:.1f}K"
    return f"LL {x:,.0f}"

chart_config = {
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "zoom2d", "pan2d", "select2d", "lasso2d",
        "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d",
        "toggleSpikelines", "hoverClosestCartesian", "hoverCompareCartesian",
        "toImage"
    ]
}

# =========================
# HOME PAGE
# =========================
if page == "Home":

    # Create 2 columns (text + logo)
    col1, col2 = st.columns([3, 1])

    with col1:
        st.title("Baguette Bistro Analytics Dashboard")
        st.markdown("**By Sandra Sleiman**")
        st.markdown("*Turning restaurant data into actionable insights for better operational decisions.*")

        st.markdown("### About")
        st.markdown("""
        This application helps Baguette Bistro better understand its operations using data analytics and predictive modeling.

        It combines dashboards and machine learning to analyze sales, customer behavior, delivery performance, and demand patterns.
        """)

        st.markdown("### Navigation Guide")
        st.markdown("""
        **1. Executive Dashboard**  
        View revenue trends, order patterns, customer behavior, and delivery performance.

        **2. Predictive Models**  
        Estimate demand and evaluate late delivery risks.
        """)

    with col2:
        st.image("logo.png", use_container_width=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Go to Executive Dashboard", use_container_width=True):
            st.session_state.page = "Executive Dashboard"
            st.rerun()

    with col2:
        if st.button("Go to Predictive Models", use_container_width=True):
            st.session_state.page = "Predictive Models"
            st.rerun()   


# =========================
# EXECUTIVE DASHBOARD PAGE
# =========================
if page == "Executive Dashboard":
    filtered_tx = tx.copy()

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered_tx = filtered_tx[
            (filtered_tx["Order Date"].dt.date >= start_date) &
            (filtered_tx["Order Date"].dt.date <= end_date)
        ]

    if channels is not None and weekdays is not None:
        filtered_tx = filtered_tx[
            filtered_tx["Order Channel"].isin(channels) &
            filtered_tx["weekday"].isin(weekdays)
        ]

    total_revenue_lbp = filtered_tx["Final Total"].sum()
    total_revenue = total_revenue_lbp / USD_RATE
    total_orders = len(filtered_tx)
    avg_orders_day = filtered_tx.groupby(filtered_tx["Order Date"].dt.date).size().mean()

    delivery_only = filtered_tx[
        filtered_tx["Order Channel"].str.contains("Toters", case=False, na=False)
    ].copy()

    avg_delivery_time = delivery_only["Delivery Time_min"].mean()
    late_rate = delivery_only["late_flag"].mean() * 100 if len(delivery_only) > 0 else 0

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    neutral_kpi_color = TEXT
    problem_kpi_color = DEEP_RED if pd.notna(avg_delivery_time) and avg_delivery_time > 35 else TEXT
    late_kpi_color = DEEP_RED if late_rate > 10 else TEXT

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Revenue</div>
                <div class="kpi-value" style="color:{neutral_kpi_color}">${total_revenue:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Orders</div>
                <div class="kpi-value" style="color:{neutral_kpi_color}">{total_orders:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Avg Orders / Day</div>
                <div class="kpi-value" style="color:{neutral_kpi_color}">{avg_orders_day:.1f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Avg Delivery Time</div>
                <div class="kpi-value" style="color:{problem_kpi_color}">{avg_delivery_time:.1f} min</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c5:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Late Delivery Rate</div>
                <div class="kpi-value" style="color:{late_kpi_color}">{late_rate:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    orders_by_hour = (
        filtered_tx.groupby("order_hour")
        .size()
        .reset_index(name="orders")
        .sort_values("order_hour")
    )

    fig_orders_hour = px.bar(
        orders_by_hour,
        x="order_hour",
        y="orders",
        title="Orders by Hour"
    )
    fig_orders_hour.update_traces(
        marker_color=NAVY,
        hovertemplate="Hour %{x}:00<br>Orders: %{y:,.0f}<extra></extra>"
    )
    fig_orders_hour.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font=dict(size=14, color=TEXT),
        font=dict(color=TEXT, size=11),
        xaxis_title="Hour",
        yaxis_title="",
        margin=dict(l=8, r=8, t=34, b=8),
        height=210,
        showlegend=False
    )
    fig_orders_hour.update_xaxes(
        showgrid=False,
        tickmode="array",
        tickvals=[0, 4, 8, 12, 16, 20],
        ticktext=["0", "4", "8", "12", "16", "20"]
    )
    fig_orders_hour.update_yaxes(showgrid=True, gridcolor=GRID)

    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    orders_by_weekday = (
        filtered_tx.groupby("weekday")
        .size()
        .reindex(weekday_order)
        .reset_index(name="orders")
    )

    fig_orders_weekday = px.bar(
        orders_by_weekday,
        x="weekday",
        y="orders",
        title="Orders by Day of Week"
    )
    fig_orders_weekday.update_traces(
        marker_color=LIGHT_BLUE,
        hovertemplate="Orders: %{y:,.0f}<extra></extra>"
    )
    fig_orders_weekday.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font=dict(size=14, color=TEXT),
        font=dict(color=TEXT, size=11),
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=8, r=8, t=34, b=8),
        height=210,
        showlegend=False
    )
    fig_orders_weekday.update_xaxes(showgrid=False)
    fig_orders_weekday.update_yaxes(showgrid=True, gridcolor=GRID)

    revenue_by_channel = (
        filtered_tx.groupby("Order Channel")["Final Total"]
        .sum()
        .reset_index()
        .sort_values("Final Total", ascending=True)
    )

    revenue_by_channel["Revenue_USD"] = revenue_by_channel["Final Total"] / USD_RATE

    fig_revenue_channel = px.bar(
        revenue_by_channel,
        x="Revenue_USD",
        y="Order Channel",
        orientation="h",
        title="Revenue by Channel"
    )
    fig_revenue_channel.update_traces(
        marker_color=NAVY,
        hovertemplate="Revenue: $%{x:,.0f}<extra></extra>"
    )
    fig_revenue_channel.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font=dict(size=14, color=TEXT),
        font=dict(color=TEXT, size=11),
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=8, r=8, t=34, b=8),
        height=210,
        showlegend=False
    )
    fig_revenue_channel.update_xaxes(showgrid=True, gridcolor=GRID)
    fig_revenue_channel.update_yaxes(showgrid=False)

    daily_revenue = (
        filtered_tx.groupby(filtered_tx["Order Date"].dt.date)["Final Total"]
        .sum()
        .reset_index(name="revenue_lbp")
    )

    daily_revenue["revenue"] = daily_revenue["revenue_lbp"] / USD_RATE
    daily_revenue["Order Date"] = pd.to_datetime(daily_revenue["Order Date"])

    fig_daily_revenue = px.line(
        daily_revenue,
        x="Order Date",
        y="revenue",
        title="Revenue Trend Over Time (USD)"
    )
    fig_daily_revenue.update_traces(
        line=dict(color=SLATE, width=2.5),
        hovertemplate="%{x|%d %b %Y}<br>Revenue: $%{y:,.0f}<extra></extra>"
    )
    fig_daily_revenue.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font=dict(size=14, color=TEXT),
        font=dict(color=TEXT, size=11),
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=8, r=8, t=34, b=8),
        height=210,
        showlegend=False
    )
    fig_daily_revenue.update_xaxes(showgrid=False)
    fig_daily_revenue.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        tickprefix="$"
    )
    fig_daily_revenue.update_yaxes(
    showgrid=True,
    gridcolor=GRID,
    tickprefix="$",
    tickformat="~s"
    )
    col1, col2, col3, col4 = st.columns(4, gap="small")

    with col1:
        st.plotly_chart(fig_orders_hour, use_container_width=True, config=chart_config)

    with col2:
        st.plotly_chart(fig_orders_weekday, use_container_width=True, config=chart_config)

    with col3:
        st.plotly_chart(fig_revenue_channel, use_container_width=True, config=chart_config)

    with col4:
        st.plotly_chart(fig_daily_revenue, use_container_width=True, config=chart_config)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    items_cols = items.columns.tolist()
    item_name_col = None
    item_qty_col = None

    for col in items_cols:
        col_lower = col.lower()
        if "item name" in col_lower or "item_name" in col_lower:
            item_name_col = col
        if "quantity sold in 2025" in col_lower or "quantity_sold_in_2025" in col_lower:
            item_qty_col = col

    top_items = items[[item_name_col, item_qty_col]].copy()
    top_items.columns = ["Item", "Quantity"]
    top_items["Quantity"] = pd.to_numeric(top_items["Quantity"], errors="coerce")
    top_items = top_items.dropna().sort_values("Quantity", ascending=False).head(8)
    top_items["Item"] = top_items["Item"].astype(str).str.slice(0, 25)

    fig_top_items = px.bar(
        top_items.sort_values("Quantity", ascending=True),
        x="Quantity",
        y="Item",
        orientation="h",
        title="Top-Selling Dishes"
    )
    fig_top_items.update_traces(
        marker_color=SLATE,
        hovertemplate="Orders: %{x:,.0f}<extra></extra>"
    )
    fig_top_items.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font=dict(size=14, color=TEXT),
        font=dict(color=TEXT, size=11),
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=8, r=8, t=34, b=8),
        height=245,
        showlegend=False
    )
    fig_top_items.update_xaxes(showgrid=True, gridcolor=GRID)
    fig_top_items.update_yaxes(showgrid=False)

    ratings_clean = ratings.copy()
    ratings_clean.columns = [col.strip() for col in ratings_clean.columns]

    ratings_clean = ratings_clean.rename(columns={
        "Reason": "Reason",
        "Count": "Orders",
        "Avg_Rating": "AvgRating"
    })

    ratings_clean = ratings_clean[["Reason", "Orders", "AvgRating"]].copy()
    ratings_clean["Orders"] = pd.to_numeric(ratings_clean["Orders"], errors="coerce")
    ratings_clean["AvgRating"] = pd.to_numeric(ratings_clean["AvgRating"], errors="coerce")
    ratings_clean = ratings_clean.dropna(subset=["Reason", "Orders", "AvgRating"])

    ratings_clean = ratings_clean[
        ~ratings_clean["Reason"].astype(str).str.lower().isin(["grand total", "(blank)", "blank"])
    ]

    ratings_clean["Reason"] = ratings_clean["Reason"].astype(str).str.title()
    ratings_clean = ratings_clean[ratings_clean["Orders"] >= 2]
    ratings_clean = ratings_clean.sort_values(["Orders", "AvgRating"], ascending=[False, True]).head(8)

    fig_ratings = px.bar(
        ratings_clean.sort_values("Orders", ascending=True),
        x="Orders",
        y="Reason",
        orientation="h",
        title="Top Customer Complaints"
    )
    fig_ratings.update_traces(
        marker_color=SOFT_RED,
        hovertemplate="Cases: %{x:,.0f}<extra></extra>"
    )
    fig_ratings.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font=dict(size=14, color=TEXT),
        font=dict(color=TEXT, size=11),
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=8, r=8, t=34, b=8),
        height=245,
        showlegend=False
    )
    fig_ratings.update_xaxes(showgrid=True, gridcolor=GRID)
    fig_ratings.update_yaxes(showgrid=False)

    users_cols = users.columns.tolist()
    month_col = None
    retention_col = None

    for col in users_cols:
        col_lower = col.lower()
        if "month start date" in col_lower or "month_start_date" in col_lower:
            month_col = col
        if "next month retention rate" in col_lower or "next_month_retention_rate" in col_lower:
            retention_col = col

    users_trend = users[[month_col, retention_col]].copy()
    users_trend.columns = ["Month", "RetentionRate"]
    users_trend["Month"] = pd.to_datetime(users_trend["Month"], errors="coerce")
    users_trend["RetentionRate"] = pd.to_numeric(users_trend["RetentionRate"], errors="coerce")
    users_trend = users_trend.dropna().sort_values("Month")

    fig_retention = px.line(
        users_trend,
        x="Month",
        y="RetentionRate",
        title="Customer Retention Trend"
    )
    fig_retention.update_traces(
        line=dict(color=NAVY, width=2.5),
        hovertemplate="%{x|%b %Y}<br>Retention: %{y:.1%}<extra></extra>"
    )
    fig_retention.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font=dict(size=14, color=TEXT),
        font=dict(color=TEXT, size=11),
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=8, r=8, t=34, b=8),
        height=245,
        showlegend=False
    )
    fig_retention.update_xaxes(showgrid=False)
    fig_retention.update_yaxes(showgrid=True, gridcolor=GRID, tickformat=".0%")

    delivery_perf = filtered_tx[
        filtered_tx["Order Channel"].str.contains("Toters", case=False, na=False)
    ].copy()

    delivery_perf = delivery_perf.dropna(subset=["order_hour", "Delivery Time_min"])
    delivery_perf["Delivery Time_min"] = pd.to_numeric(delivery_perf["Delivery Time_min"], errors="coerce")
    delivery_perf = delivery_perf.dropna(subset=["Delivery Time_min"])

    delivery_by_hour = (
        delivery_perf.groupby("order_hour")["Delivery Time_min"]
        .mean()
        .reset_index()
    )

    fig_delivery_perf = px.line(
        delivery_by_hour,
        x="order_hour",
        y="Delivery Time_min",
        title="Delivery Performance by Hour"
    )
    fig_delivery_perf.update_traces(
        line=dict(color=PRIMARY_RED, width=2.8),
        hovertemplate="Hour %{x}:00<br>Avg time: %{y:.1f} min<extra></extra>"
    )
    fig_delivery_perf.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        title_font=dict(size=14, color=TEXT),
        font=dict(color=TEXT, size=11),
        xaxis_title="Hour",
        yaxis_title="",
        margin=dict(l=8, r=8, t=34, b=8),
        height=245,
        showlegend=False
    )
    fig_delivery_perf.update_xaxes(
        showgrid=False,
        tickmode="array",
        tickvals=[0, 4, 8, 12, 16, 20],
        ticktext=["0", "4", "8", "12", "16", "20"]
    )
    fig_delivery_perf.update_yaxes(showgrid=True, gridcolor=GRID)

    r2c1, r2c2, r2c3, r2c4 = st.columns(4, gap="small")

    with r2c1:
        st.plotly_chart(fig_top_items, use_container_width=True, config=chart_config)

    with r2c2:
        st.plotly_chart(fig_ratings, use_container_width=True, config=chart_config)

    with r2c3:
        st.plotly_chart(fig_retention, use_container_width=True, config=chart_config)

    with r2c4:
        st.plotly_chart(fig_delivery_perf, use_container_width=True, config=chart_config)

# =========================
# PREDICTIVE MODELS PAGE
# =========================
elif page == "Predictive Models":
    orders_model = pickle.load(open("rf_daily_orders_model.pkl", "rb"))
    late_model = pickle.load(open("late_delivery_model.pkl", "rb"))

    st.markdown("### Predict Daily Orders")
    st.caption("Estimate daily demand from recent order patterns.")

    o1, o2, o3 = st.columns(3)

    with o1:
        month = st.selectbox("Month", list(range(1, 13)))
        lag_1 = st.number_input("Orders Yesterday", min_value=0.0, value=20.0, step=1.0)

    with o2:
        day_of_week = st.selectbox(
            "Day of Week",
            options=[0, 1, 2, 3, 4, 5, 6],
            format_func=lambda x: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][x]
        )
        lag_7 = st.number_input("Orders Same Day Last Week", min_value=0.0, value=22.0, step=1.0)

    with o3:
        rolling_7 = st.number_input("7-Day Average Orders", min_value=0.0, value=21.0, step=1.0)

    is_weekend = 1 if day_of_week in [5, 6] else 0
    is_friday = 1 if day_of_week == 4 else 0
    trend = 100.0
    week_of_year = datetime.now().isocalendar()[1]
    weekend_trend = trend * is_weekend

    if st.button("Predict Orders", use_container_width=False):
        orders_input = pd.DataFrame([{
            "day_of_week": day_of_week,
            "month": month,
            "is_weekend": is_weekend,
            "lag_1": lag_1,
            "lag_7": lag_7,
            "rolling_7": rolling_7,
            "is_friday": is_friday,
            "trend": trend,
            "week_of_year": week_of_year,
            "weekend_trend": weekend_trend
        }])

        prediction = orders_model.predict(orders_input)[0]

        if prediction > 30:
            st.warning(f"Expected Orders: {round(prediction)} | High demand expected.")
        elif prediction < 15:
            st.info(f"Expected Orders: {round(prediction)} | Low demand expected.")
        else:
            st.success(f"Expected Orders: {round(prediction)} | Moderate demand expected.")

    st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)

    st.markdown("### Predict Late Delivery Risk")
    st.caption("Estimate the probability of delivery delay.")

    d1, d2, d3 = st.columns(3)

    with d1:
        order_hour = st.slider("Order Hour", 0, 23, 18)
        order_month = st.selectbox("Order Month", list(range(1, 13)), key="late_month")

    with d2:
        approved_to_ready = st.number_input(
            "Approved to Ready (min)",
            min_value=0.0,
            value=15.0,
            step=1.0
        )
        instore_to_enroute = st.number_input(
            "In-Store to En Route (min)",
            min_value=0.0,
            value=5.0,
            step=1.0
        )

    with d3:
        is_ready = st.selectbox(
            "Order Ready Status",
            [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )
        late_day_of_week = st.selectbox(
            "Delivery Day of Week",
            options=[0, 1, 2, 3, 4, 5, 6],
            format_func=lambda x: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][x],
            key="late_day_of_week"
        )

    is_weekend_late = 1 if late_day_of_week in [5, 6] else 0
    is_friday_late = 1 if late_day_of_week == 4 else 0
    is_peak_hour = 1 if order_hour in [12, 13, 14, 18, 19, 20, 21] else 0

    delivery_charge = 33.33
    delivery_surcharge = 0.0

    if st.button("Predict Delay Risk", use_container_width=False):
        late_input = pd.DataFrame([{
            "order_hour": order_hour,
            "order_month": order_month,
            "is_weekend": is_weekend_late,
            "is_peak_hour": is_peak_hour,
            "is_friday": is_friday_late,
            "delivery_charge": delivery_charge,
            "delivery_surcharge": delivery_surcharge,
            "is_ready": is_ready,
            "Time from approved to is_ready_min": approved_to_ready,
            "Time from in_store to en_route_to_client_min": instore_to_enroute
        }])

        risk = late_model.predict(late_input)[0]

        if risk == 1:
            st.error("Predicted Risk: High | Prioritize this order.")
        else:
            st.success("Predicted Risk: Low | Operations can continue as planned.")
