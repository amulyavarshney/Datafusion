"""
DataFusion: Advanced File Merger App
-----------------------------------
A Streamlit application for merging multiple file formats with advanced options and visualizations.

Author: Amulya Varshney
GitHub: https://github.com/amulyavarshney/datafusion
License: MIT
"""

import streamlit as st
import json
import os
from pathlib import Path

# Import controllers and UI components
from src.controllers.file_merger import FileMerger
from src.ui.components import render_header, render_sidebar, render_footer
from src.ui.pages import render_about_page

# Set page configuration
st.set_page_config(
    page_title="DataFusion - Advanced File Merger",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load configuration
@st.cache_data
def load_config():
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    return {
        "theme": "light",
        "max_file_size_mb": 100,
        "default_merge_method": "append",
        "plugins_enabled": True,
        "export_formats": ["csv", "xlsx", "json"]
    }

config = load_config()

# Apply theme
if config["theme"] == "dark":
    st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state if needed
if 'page' not in st.session_state:
    st.session_state.page = 'merger'

# Render header with navigation
render_header()

# Render sidebar
render_sidebar(config)

# Render the selected page
if st.session_state.page == 'merger':
    # Initialize and run the file merger
    merger = FileMerger(config)
    merger.handle()
elif st.session_state.page == 'about':
    render_about_page()

# Render footer
render_footer()