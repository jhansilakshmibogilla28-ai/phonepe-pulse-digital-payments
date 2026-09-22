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

st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_csv(filename):
    path = DATA / filename
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def compact(value):
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


transactions = load_csv("aggregated_transactions.csv")
state_transactions = load_csv("state_transactions.csv")
users = load_csv("users.csv")
merchants = load_csv("merchants.csv")

if transactions.empty:
    st.title("◈ Digital Payments Analytics")
    st.warning(
        "Processed data is not available. Run `python run_pipeline.py` "
        "from the project root first."
    )
    st.stop()

st.sidebar.title("◈ PhonePe Pulse")
st.sidebar.caption("Digital Payments Analytics")
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

years = sorted(transactions["year"].dropna().unique().tolist())
selected_years = st.sidebar.multiselect(
    "Year",
    years,
    default=years,
)

if selected_years:
    tx = transactions[transactions["year"].isin(selected_years)].copy()
else:
    tx = transactions.copy()


def period_frame(frame):
    result = (
        frame.groupby(["year", "quarter"], as_index=False)
        .agg(
            transactions=("transaction_count", "sum"),
            value=("transaction_amount", "sum"),
        )
    )
    result["period"] = (
        result["year"].astype(str)
        + " Q"
        + result["quarter"].astype(str)
    )
    return result


if page == "Executive Overview":
    st.title("Digital Payments Analytics")
    st.caption("PhonePe Pulse — Executive Overview")
    st.divider()

    total_transactions = tx["transaction_count"].sum()
    total_value = tx["transaction_amount"].sum()
    category_count = tx["category"].nunique()
    quarter_count = tx[["year", "quarter"]].drop_duplicates().shape[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Transactions", compact(total_transactions))
    c2.metric("Transaction Value", compact(total_value))
    c3.metric("Payment Categories", category_count)
    c4.metric("Quarters Analysed", quarter_count)

    quarterly = period_frame(tx)
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
    st.plotly_chart(fig, use_container_width=True)

    category = (
        tx.groupby("category", as_index=False)
        .agg(
            transactions=("transaction_count", "sum"),
            value=("transaction_amount", "sum"),
        )
        .sort_values("transactions", ascending=False)
    )

    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(
            category,
            x="category",
            y="transactions",
            title="Transactions by Category",
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.bar(
            category,
            x="category",
            y="value",
            title="Transaction Value by Category",
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)


elif page == "Transactions":
    st.title("Transaction Analysis")
    st.caption("Explore transaction volume, value and categories.")
    st.divider()

    quarterly = period_frame(tx)
    quarterly["average_transaction_value"] = (
        quarterly["value"]
        / quarterly["transactions"].replace(0, pd.NA)
    )

    c1, c2 = st.columns(2)

    with c1:
        fig = px.line(
            quarterly,
            x="period",
            y="transactions",
            markers=True,
            title="Transaction Volume Trend",
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.line(
            quarterly,
            x="period",
            y="value",
            markers=True,
            title="Transaction Value Trend",
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    category = (
        tx.groupby("category", as_index=False)
        .agg(
            transactions=("transaction_count", "sum"),
            value=("transaction_amount", "sum"),
        )
        .sort_values("transactions", ascending=False)
    )

    category["average_transaction_value"] = (
        category["value"]
        / category["transactions"].replace(0, pd.NA)
    )

    st.subheader("Category Analysis")
    st.dataframe(
        category,
        use_container_width=True,
        hide_index=True,
    )


elif page == "Geography":
    st.title("Geographic Analysis")
    st.caption("State-level digital payment activity.")
    st.divider()

    if state_transactions.empty:
        st.info("State transaction data is not available.")
    else:
        if selected_years:
            geo = state_transactions[
                state_transactions["year"].isin(selected_years)
            ].copy()
        else:
            geo = state_transactions.copy()

        summary = (
            geo.groupby("state", as_index=False)
            .agg(
                transactions=("transaction_count", "sum"),
                value=("transaction_amount", "sum"),
            )
            .sort_values("transactions", ascending=False)
        )

        c1, c2 = st.columns(2)

        with c1:
            top = summary.head(10).sort_values("transactions")
            fig = px.bar(
                top,
                x="transactions",
                y="state",
                orientation="h",
                title="Top 10 States by Transaction Volume",
            )
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            top = summary.sort_values(
                "value",
                ascending=False,
            ).head(10)
            top = top.sort_values("value")

            fig = px.bar(
                top,
                x="value",
                y="state",
                orientation="h",
                title="Top 10 States by Transaction Value",
            )
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("State-level Summary")
        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True,
        )


elif page == "Users & Merchants":
    st.title("Users & Merchants")
    st.caption("Registered user and merchant trends.")
    st.divider()

    c1, c2 = st.columns(2)

    if users.empty:
        c1.info("User data is not available.")
    else:
        user_data = users.copy()

        if selected_years:
            user_data = user_data[
                user_data["year"].isin(selected_years)
            ]

        user_trend = (
            user_data.groupby(
                ["year", "quarter"],
                as_index=False,
            )
            .agg(
                registered_users=("registered_count", "max")
            )
        )

        user_trend["period"] = (
            user_trend["year"].astype(str)
            + " Q"
            + user_trend["quarter"].astype(str)
        )

        fig = px.line(
            user_trend,
            x="period",
            y="registered_users",
            markers=True,
            title="Registered Users",
        )
        fig.update_layout(template="plotly_dark")
        c1.plotly_chart(fig, use_container_width=True)

    if merchants.empty:
        c2.info("Merchant data is not available.")
    else:
        merchant_data = merchants.copy()

        if selected_years:
            merchant_data = merchant_data[
                merchant_data["year"].isin(selected_years)
            ]

        merchant_trend = (
            merchant_data.groupby(
                ["year", "quarter"],
                as_index=False,
            )
            .agg(
                registered_merchants=("registered_count", "max")
            )
        )

        merchant_trend["period"] = (
            merchant_trend["year"].astype(str)
            + " Q"
            + merchant_trend["quarter"].astype(str)
        )

        fig = px.line(
            merchant_trend,
            x="period",
            y="registered_merchants",
            markers=True,
            title="Registered Merchants",
        )
        fig.update_layout(template="plotly_dark")
        c2.plotly_chart(fig, use_container_width=True)

    if not users.empty:
        st.subheader("User Growth Data")
        st.dataframe(
            user_trend,
            use_container_width=True,
            hide_index=True,
        )

    if not merchants.empty:
        st.subheader("Merchant Growth Data")
        st.dataframe(
            merchant_trend,
            use_container_width=True,
            hide_index=True,
        )


elif page == "Data & Methodology":
    st.title("Data & Methodology")
    st.caption("Project architecture, datasets and analytical workflow.")
    st.divider()

    st.subheader("Data Source")
    st.write("PhonePe Pulse public dataset.")

    st.subheader("Data Pipeline")

    st.code(
        """PhonePe Pulse Public Data
        ↓
Python Data Extraction
        ↓
Data Transformation
        ↓
Data Validation
        ↓
Processed CSV Files
        ↓
SQL / Python Analysis
        ↓
Streamlit Dashboard""",
        language="text",
    )

    st.subheader("Processed Datasets")

    datasets = {
        "aggregated_transactions.csv": transactions,
        "state_transactions.csv": state_transactions,
        "users.csv": users,
        "merchants.csv": merchants,
    }

    for name, dataframe in datasets.items():
        with st.expander(name):
            if dataframe.empty:
                st.info("Dataset not available.")
            else:
                st.write(f"Rows: {len(dataframe):,}")
                st.write(f"Columns: {len(dataframe.columns):,}")
                st.dataframe(
                    dataframe.head(10),
                    use_container_width=True,
                    hide_index=True,
                )

    st.subheader("Technology Stack")

    st.markdown(
        """
        - **Python** — data extraction and transformation
        - **Pandas** — data analysis
        - **SQL** — analytical queries
        - **Plotly** — interactive visualizations
        - **Streamlit** — dashboard application
        - **Pytest** — automated validation tests
        - **GitHub Actions** — CI workflow
        """
    )

    st.info(
        "Raw source data is intentionally not bundled with the repository. "
        "The pipeline downloads the public PhonePe Pulse source data when run."
    )


st.sidebar.divider()
st.sidebar.caption("PhonePe Pulse Digital Payments Analytics")
st.sidebar.caption("Python • Pandas • Plotly • Streamlit")
