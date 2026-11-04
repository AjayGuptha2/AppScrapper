"""
Vehicle Registration Scraper Pro — Streamlit UI
-----------------------------------------------
Telangana Transport Vehicle Registration Intelligence System

Run:
    streamlit run app.py
"""

import importlib
import streamlit as st

import ui.styles
import ui.sidebar
import tabs.batch_tab
import tabs.single_tab
import tabs.docs_tab

# Ensure modules reload cleanly on every execution
importlib.reload(ui.styles)
importlib.reload(ui.sidebar)
importlib.reload(tabs.batch_tab)
importlib.reload(tabs.single_tab)
importlib.reload(tabs.docs_tab)

from ui.styles import apply_custom_styles, render_hero_banner
from ui.sidebar import render_sidebar
from tabs.batch_tab import render_batch_tab
from tabs.single_tab import render_single_tab
from tabs.docs_tab import render_docs_tab


def main():
    # 1. Page Configuration
    st.set_page_config(
        page_title="AutoScrape Pro • TG Transport",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 2. Inject Custom Modern CSS Styles
    apply_custom_styles()

    # 3. Sidebar Configuration & Engine Settings
    engine_cfg = render_sidebar()

    # 4. Top Hero Banner
    render_hero_banner()

    # 5. App Navigation Tabs
    tab_batch, tab_single, tab_docs = st.tabs([
        "📁 Batch Excel Scraper",
        "🔍 Quick Chassis Lookup",
        "📋 Field Reference & Help",
    ])

    with tab_batch:
        render_batch_tab(engine_cfg)

    with tab_single:
        render_single_tab(
            headless=engine_cfg.get("headless", True),
            max_retries=engine_cfg.get("max_retries", 2),
        )

    with tab_docs:
        render_docs_tab()


if __name__ == "__main__":
    main()