"""
Tab 2: Quick Chassis Lookup
---------------------------
Instant single-vehicle lookup without requiring an Excel file.
"""

import streamlit as st
from playwright.sync_api import sync_playwright
from scraper_engine import scrape_single_chassis


def render_single_tab(headless: bool = True, max_retries: int = 2):
    """Renders the Single Chassis Lookup tab view."""
    st.markdown("#### Instant Single Vehicle Lookup")
    st.caption("Quickly look up a single vehicle without needing to prepare an Excel spreadsheet.")

    single_col1, single_col2 = st.columns([2.5, 1.0])
    with single_col1:
        single_chassis = st.text_input(
            "Enter Full Chassis Number",
            placeholder="e.g. ME4JF5012KT012345",
            help="Case-sensitive or uppercase chassis number.",
        ).strip()
    with single_col2:
        st.write("")
        st.write("")
        search_single = st.button("🔍 Search Portal", type="primary", use_container_width=True)

    if search_single and single_chassis:
        with st.spinner(f"Querying Telangana Transport Portal for {single_chassis}..."):
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(
                        headless=headless,
                        args=["--no-sandbox", "--disable-dev-shm-usage"],
                    )
                    page = browser.new_page()
                    res = scrape_single_chassis(page, single_chassis, max_retries=max_retries)
                    browser.close()

                if res.get("STATUS") == "OK":
                    st.success("Vehicle Record Found!")

                    # Precompute variables to avoid backslash in f-string
                    maker_name = res.get("Maker's Name", "Vehicle Details")
                    maker_class = res.get("Maker's Class", "")
                    reg_no = res.get("Registration No", "N/A")
                    owner_name = res.get("Owner Name", "N/A")
                    veh_class = res.get("Vehicle Class", "N/A")
                    dor = res.get("Date Of Registration", "N/A")
                    chassis_val = res.get("Chassis No", single_chassis)
                    eng_no = res.get("Engine No", "N/A")
                    fuel_type = res.get("Fuel Type", "N/A")
                    mfg_year = res.get("Mfg. Year", "N/A")
                    veh_color = res.get("Vehicle Color", "N/A")
                    reg_auth = res.get("Registration Authority", "N/A")
                    financier = res.get("Financier", "None")
                    status_val = res.get("Status", "ACTIVE")

                    # Render sleek spec card
                    specs_html = f"""
                    <div class="vehicle-spec-card">
                        <div class="spec-header">
                            <span>🚘 {maker_name} • {maker_class}</span>
                            <span class="live-badge" style="background: rgba(16,185,129,0.2);">{status_val}</span>
                        </div>
                        <div class="spec-row">
                            <div class="spec-item">
                                <div class="spec-item-label">Registration No</div>
                                <div class="spec-item-val" style="color: #38bdf8; font-size:16px;">{reg_no}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-item-label">Owner Name</div>
                                <div class="spec-item-val">{owner_name}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-item-label">Vehicle Class</div>
                                <div class="spec-item-val">{veh_class}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-item-label">Date of Registration</div>
                                <div class="spec-item-val">{dor}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-item-label">Chassis No</div>
                                <div class="spec-item-val" style="font-family: monospace;">{chassis_val}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-item-label">Engine No</div>
                                <div class="spec-item-val" style="font-family: monospace;">{eng_no}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-item-label">Fuel Type</div>
                                <div class="spec-item-val">{fuel_type}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-item-label">Mfg. Year</div>
                                <div class="spec-item-val">{mfg_year}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-item-label">Vehicle Color</div>
                                <div class="spec-item-val">{veh_color}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-item-label">Registration Authority</div>
                                <div class="spec-item-val">{reg_auth}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-item-label">Financier</div>
                                <div class="spec-item-val">{financier}</div>
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(specs_html, unsafe_allow_html=True)

                elif res.get("STATUS") == "NOT_FOUND":
                    st.warning(f"No record found for chassis `{single_chassis}` on the Telangana RTA portal.")
                else:
                    st.error(f"Scraper status: {res.get('STATUS')}")

            except Exception as e:
                st.error(f"Error executing search: {e}")
