# Dashboard Preview

The PhonePe Pulse dashboard is built using Streamlit and Plotly.

## Dashboard Sections

- Executive Overview
- Transaction Trends
- Geography Analysis
- User & Merchant Analysis
- Data & Methodology

## Key Features

- Interactive filters
- KPI cards
- Quarterly transaction trends
- Transaction category analysis
- State-level analysis
- User and merchant trends
- Interactive Plotly visualizations

## Data Flow

PhonePe Pulse Public Data
        ↓
Python Data Pipeline
        ↓
Data Validation
        ↓
Processed CSV Files
        ↓
SQL & Python Analysis
        ↓
Streamlit Dashboard

## Running the Dashboard

After generating the processed datasets, run:

```bash
streamlit run app/streamlit_app.py
