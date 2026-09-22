from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"


st.set_page_config(
    page_title="Digital Payments Analytics",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------
# Custom styling
# -----------------------------
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .metric-card {
        background: linear-gradient(
            135deg,
            rgba(255,255,255,0.08),
            rgba(255,255,255,0.03)
        );
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 10px;
    }

    .section-title {
        font-size: 1.45rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    .small-text {
        color: #aab2bf;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Helper functions
# -----------------------------
@st.cache_data
def load_csv(filename):
    path = DATA / filename

    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)


def format_number(value):
    if pd.isna(value):
        return "0"

    return f"{value:,.0f}"


def format_value(value):
    if pd.isna(value):
        return "0"

    if value >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.2f}T"

    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"

    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    if value >= 1_000:
        return f"{value / 1_000:.2f}K"

    return f"{value:,.0f}"


# -----------------------------
# Load processed datasets
# -----------------------------
transactions = load_csv("aggregated_transactions.csv")
state_transactions = load_csv("state_transactions.csv")
users = load_csv("users.csv")
merchants = load_csv("merchants.csv")


# -----------------------------
# Data availability check
# -----------------------------
if transactions.empty:
    st.title("◈ Digital Payments Analytics")

    st.warning(
        "Processed data is not available yet. "
        "Run `python run_pipeline.py` from the project root first."
    )

    st.markdown(
        """
        ### Expected workflow

        ```text
        PhonePe Pulse Public Data
                ↓
        Python Data Pipeline
                ↓
        Data Validation
                ↓
        Processed CSV Files
                ↓
        SQL / Python Analysis
                ↓
        Streamlit Dashboard
        ```
        """
    )

    st.stop()


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("◈ PhonePe Pulse")

st.sidebar.markdown(
    """
    **Digital Payments Analytics**

    Explore transaction trends, geography,
    users and merchants using PhonePe Pulse data.
    """
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    [
        "Executive Overview",
        "Transactions",
        "Geography",
        "Users & Merchants",
        "Data & Methodology",
    ],
)


# -----------------------------
# Common filters
# -----------------------------
available_years = sorted(
    transactions["year"].dropna().unique().tolist()
)

if available_years:
    selected_years = st.sidebar.multiselect(
        "Year",
        available_years,
        default=available_years,
    )
else:
    selected_years = []


if selected_years:
    filtered_transactions = transactions[
        transactions["year"].isin(selected_years)
    ].copy()
else:
    filtered_transactions = transactions.copy()


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================
if page == "Executive Overview":

    st.title("Digital Payments Analytics")
    st.caption(
        "PhonePe Pulse — Executive Overview of digital payment activity"
    )

    st.divider()

    total_transactions = filtered_transactions[
        "transaction_count"
    ].sum()

    total_value = filtered_transactions[
        "transaction_amount"
    ].sum()

    categories = filtered_transactions[
        "category"
    ].nunique()

    quarters = filtered_transactions[
        ["year", "quarter"]
    ].drop_duplicates().shape[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Transactions",
            format_value(total_transactions),
        )

    with col2:
        st.metric(
            "Transaction Value",
            format_value(total_value),
        )

    with col3:
        st.metric(
            "Payment Categories",
            categories,
        )

    with col4:
        st.metric(
            "Quarters Analysed",
            quarters,
        )

    st.markdown(
        '<div class="section-title">Quarterly Transaction Trend</div>',
        unsafe_allow_html=True,
    )

    quarterly = (
        filtered_transactions
        .groupby(
            ["year", "quarter"],
            as_index=False,
        )
        .agg(
            transactions=("transaction_count", "sum"),
            value=("transaction_amount", "sum"),
        )
    )

    quarterly["period"] = (
        quarterly["year"].astype(str)
        + " Q"
        + quarterly["quarter"].astype(str)
    )

    fig = px.line(
        quarterly,
        x="period",
        y="transactions",
        markers=True,
        title="Transaction Volume by Quarter",
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Quarter",
        yaxis_title="Transactions",
        hovermode="x unified",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="section-title">Category Contribution</div>',
            unsafe_allow_html=True,
        )

        category_summary = (
            filtered_transactions
            .groupby("category", as_index=False)
            .agg(
                transactions=("transaction_count", "sum"),
                value=("transaction_amount", "sum"),
            )
            .sort_values(
                "transactions",
                ascending=False,
            )
        )

        fig_category = px.bar(
            category_summary,
            x="category",
            y="transactions",
            title="Transactions by Category",
        )

        fig_category.update_layout(
            template="plotly_dark",
            xaxis_title="Category",
            yaxis_title="Transactions",
        )

        st.plotly_chart(
            fig_category,
            use_container_width=True,
        )

    with col2:
        st.markdown(
            '<div class="section-title">Transaction Value</div>',
            unsafe_allow_html=True,
        )

        fig_value = px.bar(
            category_summary,
            x="category",
            y="value",
            title="Transaction Value by Category",
        )

        fig_value.update_layout(
            template="plotly_dark",
            xaxis_title="Category",
            yaxis_title="Transaction Value",
        )

        st.plotly_chart(
            fig_value,
            use_container_width=True,
        )


# ============================================================
# TRANSACTIONS
# ============================================================
elif page == "Transactions":

    st.title("Transaction Analysis")
    st.caption(
        "Explore transaction volume, value and payment categories."
    )

    st.divider()

    quarterly = (
        filtered_transactions
        .groupby(
            ["year", "quarter"],
            as_index=False,
        )
        .agg(
            transactions=("transaction_count", "sum"),
            value=("transaction_amount", "sum"),
        )
    )

    quarterly["average_transaction_value"] = (
        quarterly["value"]
        / quarterly["transactions"].replace(0, pd.NA)
    )

    quarterly["period"] = (
        quarterly["year"].astype(str)
        + " Q"
        + quarterly["quarter"].astype(str)
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            quarterly,
            x="period",
            y="transactions",
            markers=True,
            title="Transaction Volume Trend",
        )

        fig.update_layout(
            template="plotly_dark",
            xaxis_title="Quarter",
            yaxis_title="Transactions",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with col2:
        fig = px.line(
            quarterly,
            x="period",
            y="value",
            markers=True,
            title="Transaction Value Trend",
        )

        fig.update_layout(
            template="plotly_dark",
            xaxis_title="Quarter",
            yaxis_title="Transaction Value",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    st.markdown(
        '<div class="section-title">Category Analysis</div>',
        unsafe_allow_html=True,
    )

    category_summary = (
        filtered_transactions
        .groupby("category", as_index=False)
        .agg(
            transactions=("transaction_count", "sum"),
            value=("transaction_amount", "sum"),
        )
        .sort_values(
            "transactions",
            ascending=False,
        )
    )

    category_summary["average_transaction_value"] = (
        category_summary["value"]
        / category_summary["transactions"].replace(
            0,
            pd.NA,
        )
    )

    st.dataframe(
        category_summary,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# GEOGRAPHY
# ============================================================
elif page == "Geography":

    st.title("Geographic Analysis")
    st.caption(
        "State-level analysis of digital payment activity."
    )

    st.divider()

    if state_transactions.empty:

        st.info(
            "State transaction data is not available."
        )

    else:

        if selected_years:
            geo = state_transactions[
                state_transactions["year"].isin(
                    selected_years
                )
            ].copy()
        else:
            geo = state_transactions.copy()

        state_summary = (
            geo
            .groupby("state", as_index=False)
            .agg(
                transactions=("transaction_count", "sum"),
                value=("transaction_amount", "sum"),
            )
            .sort_values(
                "transactions",
                ascending=False,
            )
        )

        col1, col2 = st.columns(2)

        with col1:

            top_volume = state_summary.head(10)

            fig = px.bar(
                top_volume.sort_values(
                    "transactions"
                ),
                x="transactions",
                y="state",
                orientation="h",
                title="Top 10 States by Transaction Volume",
            )

            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Transactions",
                yaxis_title="State",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        with col2:

            top_value = (
                state_summary
                .sort_values(
                    "value",
                    ascending=False,
                )
                .head(10)
            )

            fig = px.bar(
                top_value.sort_values(
                    "value"
                ),
                x="value",
                y="state",
                orientation="h",
                title="Top 10 States by Transaction Value",
            )

            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Transaction Value",
                yaxis_title="State",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        st.markdown(
            '<div class="section-title">State-level Summary</div>',
            unsafe_allow_html=True,
        )

        st.dataframe(
            state_summary,
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# USERS & MERCHANTS
# ============================================================
elif page == "Users & Merchants":

    st.title("Users & Merchants")
    st.caption(
        "Registered user and merchant growth over time."
    )

    st.divider()

    if users.empty and merchants.empty:

        st.info(
            "User and merchant datasets are not available."
        )

    else:

        if not users.empty:

            users_filtered = users.copy()

            if selected_years:
                users_filtered = users_filtered[
                    users_filtered["year"].isin(
                        selected_years
                    )
                ]

            users_trend = (
                users_filtered
                .groupby(
                    ["year", "quarter"],
