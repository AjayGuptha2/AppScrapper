"""
Scraper Engine Module
---------------------
Core scraping logic and parallel tab executor for Telangana Transport Portal.
"""

import time
import random
import threading
from io import BytesIO
from queue import Queue, Empty

import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# Import constants and parsing helper from scraper.py
from scraper import (
    URL,
    SEL_DROPDOWN, SEL_INPUT, SEL_CAPTCHA_IMG, SEL_CAPTCHA_IN,
    SEL_SUBMIT, SEL_RESULT,
    DROPDOWN_VALUE_CHASSIS,
    FIELD_MAP,
    parse_vehicle_details,
)


def normalize(s: str) -> str:
    """Lowercase, strip spaces and underscores for forgiving column matching."""
    return str(s).lower().replace(" ", "").replace("_", "").replace("-", "")


def find_column(df: pd.DataFrame, target: str = "CHASSIS_NO") -> str:
    """Match column name forgivingly in a DataFrame."""
    target_norm = normalize(target)
    for col in df.columns:
        if normalize(col) == target_norm:
            return col
    for col in df.columns:
        if "chassis" in normalize(col):
            return col
    return None


def generate_sample_excel() -> bytes:
    """Build a downloadable sample template with sample chassis numbers."""
    df_sample = pd.DataFrame({
        "CHASSIS_NO": [
            "ME4JF5012KT012345",
            "MD625AB34NP098765",
            "MA3EJA12S00112233",
            "MBHJA0156LM998877",
        ],
        "NOTES": [
            "Sample record 1",
            "Sample record 2",
            "Sample record 3",
            "Sample record 4",
        ],
    })
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df_sample.to_excel(writer, index=False, sheet_name="Template")
    buf.seek(0)
    return buf.getvalue()


def scrape_single_chassis(page, chassis: str, search_type: str = "C", max_retries: int = 2) -> dict:
    """Scrapes a single chassis or reg number with captcha retry tolerance."""
    for attempt in range(1, max_retries + 1):
        result = {"INPUT_VALUE": chassis}
        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_selector(SEL_CAPTCHA_IMG, state="attached", timeout=15000)

            # 1. Select search mode in dropdown ('C' for Chassis No, 'R' for Registration No)
            page.select_option(SEL_DROPDOWN, value=search_type)

            # 2. Wait for ASP.NET postback
            page.wait_for_function(
                """(sel) => {
                    const img = document.querySelector(sel);
                    return img && img.complete && img.naturalWidth > 0;
                }""",
                arg=SEL_CAPTCHA_IMG,
                timeout=15000,
            )
            page.wait_for_timeout(400)

            # 3. Fill input
            page.fill(SEL_INPUT, chassis)
            if page.input_value(SEL_INPUT) != chassis:
                result["STATUS"] = "INPUT_FAILED"
                return result

            # 4. Read captcha parameter
            src = page.get_attribute(SEL_CAPTCHA_IMG, "src")
            if not src or "query=" not in src:
                result["STATUS"] = "CAPTCHA_NOT_FOUND"
                return result
            captcha_text = src.split("query=")[1].strip()

            # 5. Fill captcha & submit
            page.fill(SEL_CAPTCHA_IN, captcha_text)
            page.wait_for_timeout(250)
            page.click(SEL_SUBMIT)

            # 6. Wait for table, no-data, or captcha failure
            try:
                page.wait_for_function(
                    """() => {
                        const body = document.body.innerText.toLowerCase();
                        return body.includes('no data found')
                            || document.querySelector('#ctl00_OnlineContent_tblData') !== null
                            || body.includes('invalid captcha')
                            || body.includes('invalid image');
                    }""",
                    timeout=30000,
                )
            except PWTimeout:
                result["STATUS"] = "TIMEOUT"
                return result

            html = page.content()

            if "invalid captcha" in html.lower():
                if attempt < max_retries:
                    time.sleep(1.0)
                    continue
                result["STATUS"] = "CAPTCHA_FAIL"
                return result

            if "No Data Found" in html or "no data found" in html.lower():
                result["STATUS"] = "NOT_FOUND"
                return result

            parsed = parse_vehicle_details(page)
            if parsed is None:
                result["STATUS"] = "UNKNOWN"
                return result

            result.update(parsed)
            result["STATUS"] = "OK"
            return result

        except Exception as e:
            if attempt < max_retries:
                time.sleep(1.0)
                continue
            result["STATUS"] = f"ERROR: {str(e)[:50]}"
            return result

    return result


def split_work(items: list, n: int) -> list:
    """Split items into n roughly-equal chunks."""
    k, m = divmod(len(items), n)
    result = []
    start = 0
    for i in range(n):
        end = start + k + (1 if i < m else 0)
        result.append(items[start:end])
        start = end
    return result
