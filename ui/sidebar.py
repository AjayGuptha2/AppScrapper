"""
Sidebar Component
-----------------
Engine parameters, concurrency configuration, and starter template download.
"""

import streamlit as st
from scraper_engine import generate_sample_excel


def render_sidebar() -> dict:
    """
    Renders sidebar settings and returns an engine configuration dictionary:
    {
        "num_workers": int,
        "min_delay": float,
        "max_delay": float,
        "max_retries": int,
        "headless": bool,
        "speed_preset": str,
    }
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 18px;">
                <div style="background: linear-gradient(135deg, #0284c7, #2563eb); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; color: white; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4);">
                    ⚡
                </div>
                <div>
                    <div style="font-weight: 800; font-size: 16px; color: #f8fafc; line-height: 1.1;">AutoScrape</div>
                    <div style="font-size: 11px; color: #38bdf8; font-weight: 600; letter-spacing: 0.5px;">TG RTA EDITION</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### ⚙️ Engine Settings")

        speed_preset = st.radio(
            "Request Speed Profile",
            ["Balanced (1.5s - 3.0s)", "Fast (0.8s - 1.5s)", "Stealth (3.0s - 5.0s)"],
            index=1,
            help="Delays between requests prevent rate-limits from the RTA server.",
        )

        if "Fast" in speed_preset:
            min_delay, max_delay = 0.8, 1.5
        elif "Stealth" in speed_preset:
            min_delay, max_delay = 3.0, 5.0
        else:
            min_delay, max_delay = 1.5, 3.0

        num_workers = st.slider(
            "⚡ Parallel Tabs",
            min_value=1,
            max_value=8,
            value=5,
            help="Number of browser tabs scraping simultaneously. 5 tabs = ~5× speed. Higher = more RAM & chance of rate-limiting.",
        )

        with st.expander("🛠️ Advanced Parameters", expanded=False):
            min_delay = st.number_input("Min Delay (sec)", 0.3, 10.0, float(min_delay), 0.2)
            max_delay = st.number_input("Max Delay (sec)", 0.5, 20.0, float(max_delay), 0.5)
            max_retries = st.slider("Captcha Retries", 1, 4, 2)

        headless = st.toggle(
            "Headless Mode (Silent)",
            value=True,
            help="Turn OFF if you wish to see the real Chromium browser window while it works.",
        )

        st.divider()

        st.markdown("### 📥 Starter Template")
        st.caption("Need an Excel template with the correct column header?")
        st.download_button(
            label="📄 Download Sample .xlsx",
            data=generate_sample_excel(),
            file_name="sample_chassis_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        st.divider()
        st.markdown(
            """
            <div style="font-size: 11px; color: #64748b; line-height: 1.5;">
                Connected to: <br/>
                <code style="font-size: 10px; color: #94a3b8;">tgtransport.net/VehicleRegistrationSearch</code>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return {
        "num_workers": num_workers,
        "min_delay": min_delay,
        "max_delay": max_delay,
        "max_retries": max_retries,
        "headless": headless,
        "speed_preset": speed_preset,
    }
