from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"

st.set_page_config(
    page_title="Digital Payments Analytics",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
