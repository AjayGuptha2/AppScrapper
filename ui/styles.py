"""
UI Styling & Aesthetics — Deep Navy / Midnight Blue Edition
------------------------------------------------------------
Custom CSS, theme injection, and hero banner for AutoScrape Pro.
"""

import streamlit as st


def apply_custom_styles():
    """Injects high-end midnight navy glassmorphism, typography, and responsive styles."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Hide Streamlit Deploy Button */
        [data-testid="stDeployButton"],
        .stDeployButton,
        .stAppDeployButton,
        [data-testid="stToolbarActions"] {
            display: none !important;
        }

        /* Deep Navy Main App Canvas */
        .stApp {
            background: radial-gradient(circle at 18% 12%, #142038 0%, #0c1424 55%, #070d18 100%) !important;
            color: #e2e8f0;
        }

        /* Main Container Padding */
        .block-container {
            padding-top: 0.8rem;
            padding-bottom: 2rem;
            max-width: 1250px;
        }

        /* Top Hero Banner */
        .hero-card {
            background: linear-gradient(135deg, rgba(20, 32, 54, 0.85) 0%, rgba(13, 21, 38, 0.95) 100%);
            border: 1px solid rgba(56, 189, 248, 0.18);
            border-radius: 14px;
            padding: 14px 20px;
            margin-bottom: 14px;
            box-shadow: 0 8px 30px -4px rgba(2, 6, 23, 0.7), 0 0 20px rgba(14, 165, 233, 0.08);
            backdrop-filter: blur(14px);
            position: relative;
            overflow: hidden;
        }
        .hero-card::before {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; height: 3px;
            background: linear-gradient(90deg, #0284c7, #38bdf8, #6366f1, #3b82f6);
        }
        .hero-title {
            margin: 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .hero-icon-badge {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: linear-gradient(135deg, #0284c7 0%, #1d4ed8 100%);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 16px rgba(2, 132, 199, 0.45), inset 0 1px 1px rgba(255, 255, 255, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.22);
            flex-shrink: 0;
        }
        .hero-title-text {
            font-size: 21px;
            font-weight: 800;
            letter-spacing: -0.4px;
            background: linear-gradient(90deg, #f8fafc, #93c5fd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero-subtitle {
            color: #94a3b8;
            font-size: 13px;
            margin: 2px 0 0 0;
            line-height: 1.4;
        }

        /* Status Pill / Live Badge */
        .live-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            background: rgba(14, 165, 233, 0.15);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.35);
        }
        .live-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: #38bdf8;
            box-shadow: 0 0 8px #38bdf8;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.15); }
        }

        /* Metric Cards */
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin: 18px 0;
        }
        .stat-card {
            background: rgba(19, 31, 52, 0.7);
            border: 1px solid rgba(56, 189, 248, 0.14);
            border-radius: 14px;
            padding: 16px 20px;
            transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .stat-card:hover {
            transform: translateY(-2px);
            border-color: rgba(56, 189, 248, 0.4);
            box-shadow: 0 6px 20px rgba(2, 132, 199, 0.2);
        }
        .stat-label {
            font-size: 12px;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            margin-bottom: 6px;
        }
        .stat-value {
            font-size: 26px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        /* Custom File Upload Dragzone */
        [data-testid="stFileUploader"] {
            border-radius: 14px;
            padding: 6px;
        }
        [data-testid="stFileUploaderDropzone"] {
            background: rgba(16, 26, 46, 0.6) !important;
            border: 1.5px dashed rgba(56, 189, 248, 0.35) !important;
            border-radius: 14px !important;
            transition: all 0.2s ease;
        }
        [data-testid="stFileUploaderDropzone"]:hover {
            border-color: #38bdf8 !important;
            background: rgba(56, 189, 248, 0.1) !important;
        }

        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(13, 21, 38, 0.85);
            padding: 6px;
            border-radius: 12px;
            border: 1px solid rgba(56, 189, 248, 0.12);
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 18px;
            font-weight: 600;
            font-size: 13px;
            color: #94a3b8;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #0284c7 0%, #1d4ed8 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 3px 14px rgba(2, 132, 199, 0.4);
        }

        /* Buttons */
        div.stButton > button {
            border-radius: 10px;
            font-weight: 600;
            font-size: 14px;
            padding: 10px 20px;
            transition: all 0.2s ease;
        }
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #0284c7 0%, #1d4ed8 100%);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4);
        }
        div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #0369a1 0%, #1e40af 100%);
            box-shadow: 0 6px 20px rgba(2, 132, 199, 0.55);
            transform: translateY(-1px);
        }

        /* Spec Grid in Single Query */
        .vehicle-spec-card {
            background: rgba(16, 26, 45, 0.85);
            border: 1px solid rgba(56, 189, 248, 0.16);
            border-radius: 16px;
            padding: 22px;
            margin-top: 16px;
            box-shadow: 0 8px 30px rgba(2, 6, 23, 0.5);
        }
        .spec-header {
            font-size: 18px;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 16px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(56, 189, 248, 0.14);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .spec-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
        }
        .spec-item {
            background: rgba(22, 35, 58, 0.6);
            padding: 10px 14px;
            border-radius: 10px;
            border: 1px solid rgba(56, 189, 248, 0.08);
        }
        .spec-item-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #94a3b8;
            margin-bottom: 3px;
        }
        .spec-item-val {
            font-size: 14px;
            font-weight: 600;
            color: #e2e8f0;
        }

        /* Sidebar Clean Deep Navy styling */
        [data-testid="stSidebar"] {
            background-color: #090e1b !important;
            border-right: 1px solid rgba(56, 189, 248, 0.12) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero_banner():
    """Renders the top hero header and status indicator."""
    st.markdown(
        """
        <div class="hero-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                <div>
                    <h1 class="hero-title" style="display: flex; align-items: center; margin: 0;">
                        <div class="hero-icon-badge" style="background: linear-gradient(135deg, rgba(2, 132, 199, 0.35), rgba(30, 64, 175, 0.5)); width: 44px; height: 44px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(2, 132, 199, 0.4); border: 1.5px solid rgba(56, 189, 248, 0.45); margin-right: 12px; flex-shrink: 0;">
                            <span style="font-size: 26px; line-height: 1; -webkit-text-fill-color: initial !important; display: inline-block;">🚗</span>
                        </div>
                        <span class="hero-title-text" style="font-size: 21px; font-weight: 800; letter-spacing: -0.4px; background: linear-gradient(90deg, #f8fafc, #93c5fd); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                            Telangana Vehicle Data Scraper
                        </span>
                    </h1>
                    <p class="hero-subtitle">
                        Automated, high-precision retrieval of vehicle registration particulars, owner data, and specs from TG Transport.
                    </p>
                </div>
                <div class="live-badge">
                    <span class="live-dot"></span> RTA PORTAL ONLINE
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
