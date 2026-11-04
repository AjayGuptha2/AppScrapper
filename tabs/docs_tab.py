"""
Tab 3: Documentation & Field Reference
--------------------------------------
Details the 16 extracted vehicle fields and scraper status codes.
"""

import pandas as pd
import streamlit as st
from scraper import FIELD_MAP


FIELD_DESCRIPTIONS = {
    "Registration Authority": "District RTO office where vehicle is registered (e.g. RTA MAHABOOBNAGAR)",
    "Registration No": "Official license plate number (e.g. TG06A2288)",
    "Owner Name": "Full name of the registered owner (e.g. M VINEELA)",
    "Vehicle Class": "Category of vehicle (e.g. MOTOR CAR, MOTOR CYCLE)",
    "Maker's Name": "Vehicle manufacturer (e.g. MAHINDRA, HONDA, MARUTI)",
    "Maker's Class": "Commercial model name (e.g. THAR LX D MT, ACTIVA 6G)",
    "Mfg. Year": "Vehicle manufacturing date or year",
    "Date Of Registration": "Official registration date at RTA",
    "Engine No": "Unique engine identification number",
    "Chassis No": "17-digit Vehicle Identification Number (VIN)",
    "Fuel Type": "Fuel type (e.g. DIESEL, PETROL, ELECTRIC)",
    "Vehicle Color": "Color registered with RTA (e.g. DARK GREY, WHITE)",
    "Financier": "Bank / Finance company if hypothecated (e.g. INDUSIND BANK)",
    "Status": "Registration validity status (e.g. ACTIVE)",
    "Prev Registration No": "Previous number if re-registered",
    "Harvester Chassis No": "Chassis identifier for harvester equipment (if applicable)",
}


def render_docs_tab():
    """Renders the Documentation & Reference tab."""
    st.markdown("#### Extracted Data Fields")
    st.markdown("Each successful query parses 16 structured attributes from the portal table:")

    doc_data = [
        {"Field": k, "Description": FIELD_DESCRIPTIONS.get(k, f"Official {k} from RTA records")}
        for k in FIELD_MAP.keys()
    ]
    st.table(pd.DataFrame(doc_data))

    st.markdown("#### Status Codes")
    st.markdown(
        """
        - **`OK`**: Successfully retrieved and parsed vehicle details.
        - **`NOT_FOUND`**: Telangana RTA returned *"No Data Found"* for this chassis number.
        - **`CAPTCHA_FAIL`**: Captcha verification failed after max retries.
        - **`TIMEOUT`**: Portal took longer than 30 seconds to reply.
        - **`ERROR`**: Network disruption or server error.
        """
    )
