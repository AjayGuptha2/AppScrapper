"""
Telangana Vehicle Registration Scraper
--------------------------------------
Reads chassis numbers from input.xlsx, fetches details from
tgtransport.net, writes results to output.xlsx.

Setup:
    pip3 install playwright openpyxl
    python3 -m playwright install chromium

Run:
    python3 scraper.py
"""

import time
import random
import traceback
from pathlib import Path

from openpyxl import Workbook, load_workbook
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ============================================================
# CONFIG
# ============================================================
URL = "https://tgtransport.net/TGCFSTONLINE/Reports/VehicleRegistrationSearch.aspx"

INPUT_FILE  = "input.xlsx"
OUTPUT_FILE = "output.xlsx"
CHASSIS_COL = "CHASSIS_NO"          # column name in input.xlsx

MIN_DELAY_SEC = 1.5
MAX_DELAY_SEC = 3.0
MAX_RETRIES   = 3                   # retries on captcha failure

# ============================================================
# SELECTORS
# ============================================================
SEL_DROPDOWN    = "#ctl00_OnlineContent_ddlInput"
SEL_INPUT       = "#ctl00_OnlineContent_txtInput"
SEL_CAPTCHA_IMG = "#ctl00_OnlineContent_imgCaptcha"
SEL_CAPTCHA_IN  = "#ctl00_OnlineContent_txtCaptcha"
SEL_SUBMIT      = "#ctl00_OnlineContent_btnGetData"
SEL_RESULT      = "#ctl00_OnlineContent_tblData"

# Value "C" in the dropdown = Chassis No
DROPDOWN_VALUE_CHASSIS = "C"

# ============================================================
# RESULT FIELD MAP
# Each result field has a predictable ID ending in a name.
# ============================================================
FIELD_MAP = {
    "Registration No":          "ctl00_OnlineContent_tdRegnNo",
    "Owner Name":               "ctl00_OnlineContent_tdOwner",
    "Vehicle Class":            "ctl00_OnlineContent_tdVehClass",
    "Mfg. Year":                "ctl00_OnlineContent_tdMfgYear",
    "Engine No":                "ctl00_OnlineContent_tdEngNo",
    "Chassis No":               "ctl00_OnlineContent_tdChassisno",
    "Prev Registration No":     "ctl00_OnlineContent_tdPrevRegn",
    "Harvester Chassis No":     "ctl00_OnlineContent_tdharvesterchassisno",
    "Fuel Type":                "ctl00_OnlineContent_tdFuelType",
    "Vehicle Color":            "ctl00_OnlineContent_tdColor",
    "Maker's Name":             "ctl00_OnlineContent_tdMkrName",
    "Maker's Class":            "ctl00_OnlineContent_tdMkrClass",
    "Date Of Registration":     "ctl00_OnlineContent_tdDOR",
    "Financier":                "ctl00_OnlineContent_tdFin",
    "Registration Authority":   "ctl00_OnlineContent_tdAuthority",
    "Status":                   "ctl00_OnlineContent_tdStatus",
}

# Ordered list of headers for the output file
OUTPUT_HEADERS = ["CHASSIS_NO_INPUT"] + list(FIELD_MAP.keys()) + ["STATUS"]


# ============================================================
# EXCEL HELPERS
# ============================================================

def read_chassis_list(path: str, col_name: str):
    """Read chassis numbers from column `col_name` of the input sheet."""
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active

    headers = [str(c.value).strip() if c.value is not None else ""
               for c in next(ws.iter_rows(min_row=1, max_row=1))]

    # Case-insensitive match on the header
    target = col_name.strip().lower()
    col_idx = None
    for i, h in enumerate(headers):
        if h.lower() == target:
            col_idx = i
            break

    if col_idx is None:
        raise RuntimeError(
            f"Column '{col_name}' not found in {path}.\n"
            f"Found columns: {headers}\n"
            f"Tip: edit CHASSIS_COL at the top of the script."
        )

    out = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if col_idx < len(row) and row[col_idx] is not None:
            v = str(row[col_idx]).strip()
            if v:
                out.append(v)
    wb.close()
    return out


def read_done_set(path: str):
    """Chassis numbers already present in output.xlsx."""
    if not Path(path).exists():
        return set()
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    if "CHASSIS_NO_INPUT" not in headers:
        wb.close()
        return set()

    col_idx = headers.index("CHASSIS_NO_INPUT")
    done = set()
    for row in ws.iter_rows(min_row=2, values_only=True):
        if col_idx < len(row) and row[col_idx] is not None:
            done.add(str(row[col_idx]).strip())
    wb.close()
    return done


def append_row(row_dict: dict):
    """Append one row to output.xlsx, creating the file if needed."""
    if Path(OUTPUT_FILE).exists():
        wb = load_workbook(OUTPUT_FILE)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "Results"
        ws.append(OUTPUT_HEADERS)

    ws.append([row_dict.get(h, "") for h in OUTPUT_HEADERS])
    wb.save(OUTPUT_FILE)
    wb.close()


# ============================================================
# SCRAPING
# ============================================================

def parse_vehicle_details(page):
    """Extract all fields from the result table via their IDs."""
    if page.locator(SEL_RESULT).count() == 0:
        return None

    out = {}
    for label, elem_id in FIELD_MAP.items():
        loc = page.locator(f"#{elem_id}")
        out[label] = loc.inner_text().strip() if loc.count() > 0 else ""
    return out


def fetch_one(page, chassis: str, attempt: int = 1):
    result = {"CHASSIS_NO_INPUT": chassis}

    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_selector(SEL_CAPTCHA_IMG, state="attached", timeout=15000)

    # ---- 1. Select "Chassis No" — this triggers an ASP.NET postback ----
    page.select_option(SEL_DROPDOWN, value=DROPDOWN_VALUE_CHASSIS)

    # ---- 2. Wait for the postback to finish ----
    # The captcha image gets reloaded with a new src during the postback.
    # Waiting for it to load means the page is ready for input.
    page.wait_for_function(
        """(sel) => {
            const img = document.querySelector(sel);
            return img && img.complete && img.naturalWidth > 0;
        }""",
        arg=SEL_CAPTCHA_IMG,
        timeout=15000,
    )
    page.wait_for_timeout(500)  # small buffer for ASP.NET to finish

    # ---- 3. Fill the chassis number ----
    page.fill(SEL_INPUT, chassis)

    # Confirm the value actually stuck
    actual = page.input_value(SEL_INPUT)
    if actual != chassis:
        print(f"   [!] input failed — expected {chassis!r}, got {actual!r}")
        result["STATUS"] = "INPUT_FAILED"
        return result

    # ---- 4. Read captcha from image URL ----
    src = page.get_attribute(SEL_CAPTCHA_IMG, "src")
    if not src or "query=" not in src:
        result["STATUS"] = "CAPTCHA_NOT_FOUND"
        return result
    captcha_text = src.split("query=")[1].strip()
    print(f"   [CAPTCHA] {captcha_text}")

    # ---- 5. Fill captcha ----
    page.fill(SEL_CAPTCHA_IN, captcha_text)
    page.wait_for_timeout(300)

    # ---- 6. Submit ----
    page.click(SEL_SUBMIT)

    # ---- 7. Wait for a response ----
    try:
        page.wait_for_function(
            """() => {
                const body = document.body.innerText.toLowerCase();
                return body.includes('no data found')
                    || document.querySelector('#ctl00_OnlineContent_tblData') !== null
                    || body.includes('invalid captcha')
                    || body.includes('invalid image');
            }""",
            timeout=45000,
        )
    except PWTimeout:
        # Save debug info before giving up
        page.screenshot(path=f"debug_timeout_{chassis}.png", full_page=True)
        with open(f"debug_timeout_{chassis}.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        result["STATUS"] = "TIMEOUT"
        return result

    html = page.content()

    if "invalid captcha" in html.lower():
        result["STATUS"] = "CAPTCHA_FAIL"
        return result

    if "No Data Found" in html:
        result["STATUS"] = "NOT_FOUND"
        return result

    parsed = parse_vehicle_details(page)
    if parsed is None:
        result["STATUS"] = "UNKNOWN"
        return result

    result.update(parsed)
    result["STATUS"] = "OK"
    return result
    """
    Single attempt: navigate, fill form, read captcha from URL,
    submit, and parse the result.
    """
    result = {"CHASSIS_NO_INPUT": chassis}

    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_selector(SEL_CAPTCHA_IMG, state="attached", timeout=15000)

    # ---- 1. Select "Chassis No" in the dropdown ----
    page.select_option(SEL_DROPDOWN, value=DROPDOWN_VALUE_CHASSIS)

    # ---- 2. Fill the chassis number ----
    page.fill(SEL_INPUT, chassis)

    # ---- 3. Read captcha from the image URL (query= param) ----
    src = page.get_attribute(SEL_CAPTCHA_IMG, "src")
    if not src or "query=" not in src:
        result["STATUS"] = "CAPTCHA_NOT_FOUND"
        return result
    captcha_text = src.split("query=")[1].strip()
    print(f"   [CAPTCHA] {captcha_text}")

    # ---- 4. Fill captcha and submit ----
    page.fill(SEL_CAPTCHA_IN, captcha_text)
    page.click(SEL_SUBMIT)

    # ---- 5. Wait for one of: result table, "No Data Found", invalid captcha ----
    try:
        page.wait_for_function(
            """() => {
                const body = document.body.innerText;
                return body.includes('No Data Found')
                    || document.querySelector('#ctl00_OnlineContent_tblData') !== null
                    || body.toLowerCase().includes('invalid captcha');
            }""",
            timeout=20000,
        )
    except PWTimeout:
        result["STATUS"] = "TIMEOUT"
        return result

    html = page.content()

    # ---- 6. Interpret the response ----
    if "invalid captcha" in html.lower():
        result["STATUS"] = "CAPTCHA_FAIL"
        return result

    if "No Data Found" in html:
        result["STATUS"] = "NOT_FOUND"
        return result

    parsed = parse_vehicle_details(page)
    if parsed is None:
        result["STATUS"] = "UNKNOWN"
        return result

    result.update(parsed)
    result["STATUS"] = "OK"
    return result


def fetch_one_with_retries(page, chassis: str):
    """Try up to MAX_RETRIES times if captcha fails."""
    for attempt in range(1, MAX_RETRIES + 1):
        row = fetch_one(page, chassis, attempt=attempt)
        status = row.get("STATUS")

        if status == "CAPTCHA_FAIL" and attempt < MAX_RETRIES:
            print(f"   [!] captcha rejected — retry {attempt}/{MAX_RETRIES}")
            time.sleep(1.0)
            continue

        return row
    return row


# ============================================================
# MAIN
# ============================================================

def main():
    if not Path(INPUT_FILE).exists():
        print(f"!! {INPUT_FILE} not found.")
        print(f"   Create it with a column named '{CHASSIS_COL}'.")
        return

    chassis_list = read_chassis_list(INPUT_FILE, CHASSIS_COL)
    done_set     = read_done_set(OUTPUT_FILE)
    todo         = [c for c in chassis_list if c not in done_set]

    print(f"Total rows:    {len(chassis_list)}")
    print(f"Already done:  {len(done_set)}")
    print(f"To fetch:      {len(todo)}")
    print("-" * 50)

    if not todo:
        print("Nothing to do.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = browser.new_page()

        for i, chassis in enumerate(todo, start=1):
            print(f"[{i}/{len(todo)}] {chassis}")
            try:
                row = fetch_one_with_retries(page, chassis)
                print(f"   → {row.get('STATUS')}")
                append_row(row)
            except Exception as e:
                print(f"   [ERROR] {e}")
                traceback.print_exc()
                append_row({
                    "CHASSIS_NO_INPUT": chassis,
                    "STATUS": f"ERROR: {e}",
                })

            if i < len(todo):
                delay = random.uniform(MIN_DELAY_SEC, MAX_DELAY_SEC)
                time.sleep(delay)

        browser.close()

    print("-" * 50)
    print(f"Done. Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()