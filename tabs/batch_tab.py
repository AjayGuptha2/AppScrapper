"""
Tab 1: Batch Excel Processing
------------------------------
Spreadsheet ingestion, auto-detection, multi-tab parallel scraping,
locking controls during execution, and instant live top-level feedback.
"""

import time
import random
import traceback
import threading
from io import BytesIO
from queue import Queue, Empty

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from playwright.sync_api import sync_playwright

from scraper import FIELD_MAP
from scraper_engine import scrape_single_chassis, split_work


FIELD_DISPLAY_NAMES = {
    "Registration Authority": "🏛️ RTO Location",
    "Registration No": "🔢 Registration No",
    "Owner Name": "👤 Owner Name",
    "Vehicle Class": "🚗 Vehicle Class",
    "Maker's Name": "🏭 Maker's Name",
    "Maker's Class": "🏷️ Model Class",
    "Mfg. Year": "📅 Mfg. Year",
    "Date Of Registration": "🗓️ Reg Date",
    "Engine No": "⚙️ Engine No",
    "Chassis No": "🔍 Chassis No",
    "Fuel Type": "⛽ Fuel Type",
    "Vehicle Color": "🎨 Vehicle Color",
    "Financier": "🏦 Financier",
    "Status": "✅ Status",
}

DEFAULT_FIELDS = [
    "Registration Authority",
    "Financier",
    "Mfg. Year",
    "Owner Name",
]


def render_batch_tab(engine_cfg: dict):
    """
    Renders the Batch Excel Scraper tab.
    Takes engine configuration from sidebar (workers, delays, retries, headless, preset).
    """
    # ── State preservation ──
    if "is_scraping" not in st.session_state:
        st.session_state.is_scraping = False
    if "results" not in st.session_state:
        st.session_state.results = None
    if "batch_config" not in st.session_state:
        st.session_state.batch_config = None

    is_scraping = st.session_state.is_scraping

    num_workers = engine_cfg.get("num_workers", 5)
    min_delay = engine_cfg.get("min_delay", 0.8)
    max_delay = engine_cfg.get("max_delay", 1.5)
    max_retries = engine_cfg.get("max_retries", 2)
    headless = engine_cfg.get("headless", True)
    speed_preset = engine_cfg.get("speed_preset", "Fast")

    # ────────────────────────────────────────────────────────────
    # 1. TOP SECTION: RESULTS ACTION BAR (Ready for download)
    # ────────────────────────────────────────────────────────────
    if not is_scraping and st.session_state.results is not None:
        payload = st.session_state.results
        df_out = payload["df_merged"]
        orig_has_headers = payload.get("has_headers", True)
        elapsed_sec = payload.get("elapsed", 0)
        tot_recs = payload.get("total", len(df_out))

        if payload.get("just_completed"):
            st.toast(f"🎉 Scraping complete! {tot_recs:,} records ready for download.", icon="⚡")
            components.html(
                """
                <script>
                (function() {
                    try {
                        const AudioCtx = window.parent.AudioContext || window.AudioContext || window.webkitAudioContext;
                        if (!AudioCtx) return;
                        const ctx = new AudioCtx();
                        const now = ctx.currentTime;
                        
                        // Harmonious double chime
                        const osc1 = ctx.createOscillator();
                        const gain1 = ctx.createGain();
                        osc1.type = 'sine';
                        osc1.frequency.setValueAtTime(587.33, now); // D5
                        gain1.gain.setValueAtTime(0.2, now);
                        gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
                        osc1.connect(gain1);
                        gain1.connect(ctx.destination);
                        osc1.start(now);
                        osc1.stop(now + 0.35);

                        const osc2 = ctx.createOscillator();
                        const gain2 = ctx.createGain();
                        osc2.type = 'sine';
                        osc2.frequency.setValueAtTime(880.00, now + 0.12); // A5
                        gain2.gain.setValueAtTime(0.25, now + 0.12);
                        gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.6);
                        osc2.connect(gain2);
                        gain2.connect(ctx.destination);
                        osc2.start(now + 0.12);
                        osc2.stop(now + 0.6);
                    } catch(e) {}
                })();
                </script>
                """,
                height=0,
                width=0,
            )
            payload["just_completed"] = False

        st.markdown(
            f"""
            <div style="background: rgba(16, 185, 129, 0.12); border: 1.5px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 12px 18px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <span style="font-weight: 800; color: #34d399; font-size: 15px;">🎉 Scraping Completed Successfully!</span>
                        <div style="font-size: 12px; color: #cbd5e1; margin-top: 2px;">
                            {tot_recs:,} records merged with original data in {elapsed_sec:.1f}s. Ready to download!
                        </div>
                    </div>
                    <div class="live-badge" style="background: rgba(16,185,129,0.2); border-color:#10b981;">
                        ✓ READY FOR DOWNLOAD
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        buf_out = BytesIO()
        with pd.ExcelWriter(buf_out, engine="openpyxl") as writer:
            df_out.to_excel(writer, index=False, header=orig_has_headers, sheet_name="Vehicle_Data")
        buf_out.seek(0)

        c_btn1, c_btn2, c_btn3 = st.columns([2.0, 1.2, 1.5])
        with c_btn1:
            st.download_button(
                label=f"📥 Download Merged Excel ({len(df_out):,} Rows)",
                data=buf_out.getvalue(),
                file_name=f"merged_vehicle_data_{int(time.time())}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
            )
        with c_btn2:
            csv_data = df_out.to_csv(index=False, header=orig_has_headers).encode("utf-8")
            st.download_button(
                label="📄 Export CSV",
                data=csv_data,
                file_name=f"merged_vehicle_data_{int(time.time())}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with c_btn3:
            if st.button("🔄 Clear / New Upload", use_container_width=True):
                st.session_state.results = None
                st.rerun()

        with st.expander("📊 View Merged Output Table (Original + Extracted Data)", expanded=True):
            st.dataframe(df_out, use_container_width=True, height=280)

        st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid rgba(255,255,255,0.08);' />", unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────
    # 2. TOP SECTION: LIVE SCRAPING MONITOR (Visible while scraping!)
    # ────────────────────────────────────────────────────────────
    if is_scraping:
        cfg = st.session_state.batch_config or {}
        tot_cfg = cfg.get("num_to_process", 0)
        eff_workers = cfg.get("num_workers", 5)

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(168, 85, 247, 0.25)); border: 1.5px solid #6366f1; border-radius: 12px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 0 25px rgba(99,102,241,0.25);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <div style="font-weight: 800; font-size: 16px; color: #ffffff; display: flex; align-items: center; gap: 8px;">
                            <span>⚡</span> SCRAPING IN PROGRESS — {eff_workers} PARALLEL TABS ACTIVE
                        </div>
                        <div style="font-size: 12px; color: #cbd5e1; margin-top: 2px;">
                            Processing {tot_cfg:,} records in parallel. Column settings below are locked until completion.
                        </div>
                    </div>
                    <div class="live-badge" style="background: rgba(16, 185, 129, 0.2); border-color: #10b981;">
                        <span class="live-dot"></span> {eff_workers} TABS RUNNING
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        progress_bar = st.progress(0.0, text=f"Launching {eff_workers} parallel browser tabs...")
        status_box = st.empty()

        # Real-time counter metrics at eye level
        m1, m2, m3, m4 = st.columns(4)
        stat_proc = m1.empty()
        stat_ok = m2.empty()
        stat_fail = m3.empty()
        stat_time = m4.empty()

        stat_proc.markdown(
            f'<div class="stat-card"><div class="stat-label">Progress</div><div class="stat-value" style="color:#38bdf8;">0 / {tot_cfg:,}</div></div>',
            unsafe_allow_html=True,
        )
        stat_ok.markdown(
            '<div class="stat-card"><div class="stat-label">Successful</div><div class="stat-value" style="color:#34d399;">0</div></div>',
            unsafe_allow_html=True,
        )
        stat_fail.markdown(
            '<div class="stat-card"><div class="stat-label">Not Found / Fail</div><div class="stat-value" style="color:#f87171;">0</div></div>',
            unsafe_allow_html=True,
        )
        stat_time.markdown(
            '<div class="stat-card"><div class="stat-label">Speed & ETA</div><div class="stat-value" style="color:#c084fc;">Calculating...</div></div>',
            unsafe_allow_html=True,
        )

        with st.expander("⚡ Live Execution Console", expanded=True):
            log_terminal = st.empty()
            log_history = []

        def append_log(line):
            log_history.append(line)
            log_terminal.code("\n".join(log_history[-15:]), language="text")

    # ────────────────────────────────────────────────────────────
    # 3. MAIN CONFIGURATION & UPLOAD SECTION
    # ────────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1.0, 1.8], gap="medium")

    df_in = None
    target_col = None
    search_type = "C"
    num_to_process = 0
    start_row = 0
    end_row = 0
    selected_fields = list(DEFAULT_FIELDS)
    start_batch = False

    with col_left:
        st.markdown(
            "#### 📁 1. Spreadsheet" + (" <span style='font-size:12px; color:#f59e0b;'>[🔒 Locked]</span>" if is_scraping else ""),
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader(
            "Drop your Excel file below",
            type=["xlsx", "xls"],
            label_visibility="collapsed",
            disabled=is_scraping,
        )

    # If currently scraping, use cached DataFrame
    if is_scraping and "cached_df" in st.session_state:
        df_in = st.session_state.cached_df
        total_in_file = len(df_in)
        cfg = st.session_state.batch_config or {}
        has_headers = cfg.get("has_headers", True)
        target_col = cfg.get("target_col", df_in.columns[0])
        search_type = "C"
        selected_fields = cfg.get("selected_fields", DEFAULT_FIELDS)
        start_row = cfg.get("start_row", 0)
        end_row = cfg.get("end_row", total_in_file)
        num_to_process = cfg.get("num_to_process", total_in_file)

        with col_left:
            st.checkbox("File has column headers (titles)", value=has_headers, disabled=True)
            st.button("⏳ Scraping in Progress...", disabled=True, use_container_width=True)
            st.caption(f"🔒 {num_workers} tabs running on {num_to_process:,} rows.")

        with col_right:
            st.markdown("#### ⚙️ 2. Extraction & Column Settings <span style='font-size:12px; color:#f59e0b;'>[🔒 Locked]</span>", unsafe_allow_html=True)
            field_display_names = [FIELD_DISPLAY_NAMES.get(f, f).split(" ", 1)[-1] for f in selected_fields]
            st.info(f"Chassis Column: **{target_col}** • Fields: **{', '.join(field_display_names)}**")

    elif uploaded is not None:
        try:
            # 1. Inspect first few rows without headers to see structure
            df_peek = pd.read_excel(uploaded, header=None, nrows=8, dtype=str)

            # Auto-detect whether row 0 looks like a header or raw data
            row0 = df_peek.iloc[0].dropna().astype(str).str.strip().tolist()
            has_headers_guess = True
            for val in row0:
                is_vin = (len(val) == 17 and val.isalnum())
                if is_vin:
                    has_headers_guess = False
                    break

            with col_left:
                has_headers = st.checkbox("File has column headers (titles)", value=has_headers_guess, disabled=is_scraping)

            # 2. Load dataframe based on header setting
            uploaded.seek(0)
            if has_headers:
                df_in = pd.read_excel(uploaded, dtype=str)
            else:
                df_in = pd.read_excel(uploaded, header=None, dtype=str)

            total_in_file = len(df_in)

            # 3. Analyze each column to find Chassis No
            detected_chassis_col = None
            col_options = []
            col_display_map = {}

            for c in df_in.columns:
                series = df_in[c].dropna().astype(str).str.strip()
                if series.empty:
                    continue

                sample_val = series.iloc[0]
                is_chassis = (series.apply(lambda x: len(x) == 17 and x.isalnum()).mean() > 0.4)

                if has_headers:
                    label = f"{c} (e.g. {sample_val[:14]})"
                    if "chassis" in str(c).lower() or is_chassis:
                        detected_chassis_col = c
                        label += " 🎯 [Chassis]"
                else:
                    col_num = c + 1 if isinstance(c, int) else c
                    if is_chassis and detected_chassis_col is None:
                        detected_chassis_col = c
                        label = f"Col {col_num}: Chassis ({sample_val[:17]}) 🎯"
                    else:
                        label = f"Col {col_num} ({sample_val[:14]})"

                col_options.append(c)
                col_display_map[c] = label

            default_selection = detected_chassis_col or col_options[0]
            default_idx = col_options.index(default_selection)

            with col_right:
                st.markdown("#### ⚙️ 2. Extraction & Column Settings")
                grid1, grid2 = st.columns(2, gap="small")

                with grid1:
                    target_col = st.selectbox(
                        "Column with Chassis No:",
                        options=col_options,
                        index=default_idx,
                        format_func=lambda x: col_display_map.get(x, str(x)),
                        disabled=is_scraping,
                    )

                    batch_mode = st.selectbox(
                        "Execution Scope:",
                        [f"All {total_in_file:,} Rows", "Test Run: First 10 Rows", "Test Run: First 50 Rows", "Custom Range"],
                        index=0,
                        disabled=is_scraping,
                    )
                    if "First 10" in batch_mode:
                        start_row, end_row = 0, min(10, total_in_file)
                    elif "First 50" in batch_mode:
                        start_row, end_row = 0, min(50, total_in_file)
                    elif "Custom Range" in batch_mode:
                        cr1, cr2 = st.columns(2)
                        with cr1:
                            start_row = st.number_input("Start Row", min_value=1, max_value=total_in_file, value=1, disabled=is_scraping) - 1
                        with cr2:
                            end_row = st.number_input("End Row", min_value=1, max_value=total_in_file, value=min(100, total_in_file), disabled=is_scraping)
                    else:
                        start_row, end_row = 0, total_in_file

                    num_to_process = max(0, end_row - start_row)

                with grid2:
                    selectable_fields = [k for k in FIELD_MAP.keys() if k in FIELD_DISPLAY_NAMES]
                    selected_fields = st.multiselect(
                        "Fields to Extract:",
                        options=selectable_fields,
                        default=DEFAULT_FIELDS,
                        format_func=lambda x: FIELD_DISPLAY_NAMES.get(x, x),
                        disabled=is_scraping,
                    )
                    if not selected_fields:
                        selected_fields = list(DEFAULT_FIELDS)

                # Compact Summary Ribbon
                field_names_clean = ", ".join([FIELD_DISPLAY_NAMES.get(f, f).split(" ", 1)[-1] for f in selected_fields])
                st.markdown(
                    f"""
                    <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 7px 12px; font-size: 12px; color: #cbd5e1; margin-top: 4px;">
                        ✓ <b>Ready:</b> Appending <b>{field_names_clean}</b> to <b>{num_to_process:,} rows</b> ({'Rows ' + str(start_row+1) + '-' + str(end_row) if num_to_process < total_in_file else 'All rows'})
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Calculate Smart Pre-Check Metrics for target_col (support standard 17-char and extended 12-21 char VINs)
            target_series = df_in[target_col].dropna().astype(str).str.strip()
            total_rows = len(df_in)
            blank_count = total_rows - len(target_series)
            valid_vin_mask = target_series.apply(lambda x: len(x) >= 12 and len(x) <= 21 and x.isalnum())
            valid_vin_count = int(valid_vin_mask.sum())
            invalid_vin_count = len(target_series) - valid_vin_count
            duplicate_count = int(target_series.duplicated().sum())

            # Left column action button
            with col_left:
                st.markdown(
                    f"<div style='font-size:12px; color:#38bdf8; margin: 4px 0 6px 0;'>✓ <b>{uploaded.name}</b> • {total_in_file:,} rows</div>",
                    unsafe_allow_html=True,
                )

                # Smart Excel Pre-Check Badges with High-Visibility Red Error Styles
                precheck_badges = []
                if valid_vin_count == 0:
                    precheck_badges.append(
                        f"<span style='background:rgba(239,68,68,0.22); border:1.5px solid #ef4444; border-radius:6px; padding:3px 9px; font-size:11px; font-weight:700; color:#f87171;'>🚨 0 / {total_rows:,} Valid VINs</span>"
                    )
                else:
                    precheck_badges.append(
                        f"<span style='background:rgba(14,165,233,0.14); border:1px solid rgba(56,189,248,0.3); border-radius:6px; padding:3px 8px; font-size:11px; font-weight:600; color:#38bdf8;'>✓ {valid_vin_count:,} Valid VINs</span>"
                    )
                    if invalid_vin_count > 0:
                        precheck_badges.append(
                            f"<span style='background:rgba(239,68,68,0.18); border:1px solid rgba(239,68,68,0.45); border-radius:6px; padding:3px 8px; font-size:11px; font-weight:600; color:#f87171;'>❌ {invalid_vin_count:,} Invalid</span>"
                        )

                if duplicate_count > 0:
                    precheck_badges.append(
                        f"<span style='background:rgba(245,158,11,0.14); border:1px solid rgba(245,158,11,0.35); border-radius:6px; padding:3px 8px; font-size:11px; font-weight:600; color:#fbbf24;'>⚠ {duplicate_count:,} Duplicates</span>"
                    )
                if blank_count > 0:
                    precheck_badges.append(
                        f"<span style='background:rgba(148,163,184,0.14); border:1px solid rgba(148,163,184,0.3); border-radius:6px; padding:3px 8px; font-size:11px; font-weight:600; color:#94a3b8;'>⚪ {blank_count:,} Blanks</span>"
                    )

                st.markdown(
                    f"<div style='display:flex; flex-wrap:wrap; gap:6px; margin-bottom:8px;'>{' '.join(precheck_badges)}</div>",
                    unsafe_allow_html=True,
                )

                # Collect detailed issues for invalid/blank rows
                issues_list = []
                for idx, val in enumerate(df_in[target_col]):
                    row_num = idx + (2 if has_headers else 1)
                    s_val = str(val).strip() if pd.notna(val) else ""
                    if not s_val or s_val.lower() == "nan":
                        issues_list.append({
                            "Excel Row": f"Row {row_num}",
                            "Found Value": "(empty)",
                            "Reason": "Blank / Empty cell",
                        })
                    elif len(s_val) < 12:
                        issues_list.append({
                            "Excel Row": f"Row {row_num}",
                            "Found Value": s_val,
                            "Reason": f"Too short: {len(s_val)} chars (expected 17)",
                        })
                    elif len(s_val) > 21:
                        issues_list.append({
                            "Excel Row": f"Row {row_num}",
                            "Found Value": s_val,
                            "Reason": f"Too long: {len(s_val)} chars (max 21)",
                        })
                    elif not s_val.isalnum():
                        issues_list.append({
                            "Excel Row": f"Row {row_num}",
                            "Found Value": s_val,
                            "Reason": "Contains invalid symbols or spaces",
                        })

                if issues_list:
                    with st.expander(f"🔍 Inspect {len(issues_list)} Row Issue{'s' if len(issues_list) > 1 else ''}", expanded=False):
                        st.dataframe(pd.DataFrame(issues_list), use_container_width=True, height=min(220, 36 * len(issues_list) + 38))

                if valid_vin_count == 0:
                    st.markdown(
                        f"""
                        <div style="background: rgba(239, 68, 68, 0.14); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 8px; padding: 7px 10px; font-size: 11px; color: #fca5a5; margin-bottom: 10px; line-height: 1.4;">
                            ⚠️ <b>No valid Chassis Numbers found in this column.</b> Please choose your chassis number column in the dropdown.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                est_seconds = round((num_to_process / max(num_workers, 1)) * ((min_delay + max_delay) / 2 + 1.2), 0)
                if est_seconds < 60:
                    est_text = f"~{int(est_seconds)}s"
                elif est_seconds < 3600:
                    est_text = f"~{round(est_seconds / 60, 1)}m"
                else:
                    est_text = f"~{round(est_seconds / 3600, 1)}h"

                if is_scraping:
                    st.button("⏳ Scraping in Progress... (Locked)", disabled=True, use_container_width=True)
                else:
                    start_batch = st.button(
                        f"🚀 Start Scraping ({num_to_process:,} Rows)",
                        type="primary",
                        use_container_width=True,
                    )
                    st.caption(f"Estimated: {est_text} • {num_workers} tabs parallel")

        except Exception as e:
            st.error(f"Could not parse Excel: {e}")

    else:
        with col_right:
            st.markdown("#### ⚙️ 2. Configuration")
            st.info(
                "Upload your vehicle Excel file on the left. The scraper will automatically detect "
                "whether it has headers or raw values, auto-select the Chassis Number column, and extract "
                "RTO Location, Financier, Mfg. Year, Owner Name, and more!"
            )

    # Preview expandable
    if not is_scraping and df_in is not None and not df_in.empty:
        with st.expander("🔍 Preview Input Data (First 15 Rows)", expanded=False):
            st.dataframe(df_in.head(15), use_container_width=True)

    # ────────────────────────────────────────────────────────────
    # 4. TRIGGER BATCH EXECUTION (Instantly reloads with locked state)
    # ────────────────────────────────────────────────────────────
    if start_batch and df_in is not None and num_to_process > 0:
        st.session_state.is_scraping = True
        st.session_state.cached_df = df_in
        st.session_state.batch_config = {
            "start_row": start_row,
            "end_row": end_row,
            "target_col": target_col,
            "search_type": search_type,
            "selected_fields": selected_fields,
            "num_to_process": num_to_process,
            "has_headers": has_headers,
            "num_workers": num_workers,
            "min_delay": min_delay,
            "max_delay": max_delay,
            "max_retries": max_retries,
            "headless": headless,
        }
        st.session_state.results = None
        st.rerun()

    # ────────────────────────────────────────────────────────────
    # 5. ACTIVE SCRAPING ENGINE (Runs when is_scraping is True)
    # ────────────────────────────────────────────────────────────
    if is_scraping and df_in is not None:
        cfg = st.session_state.batch_config
        target_col = cfg["target_col"]
        search_type = cfg["search_type"]
        selected_fields = cfg["selected_fields"]
        s_row = cfg["start_row"]
        e_row = cfg["end_row"]
        eff_workers = cfg.get("num_workers", 5)
        m_delay = cfg.get("min_delay", min_delay)
        mx_delay = cfg.get("max_delay", max_delay)
        m_retries = cfg.get("max_retries", max_retries)
        h_less = cfg.get("headless", headless)

        df_target_slice = df_in.iloc[s_row:e_row].copy()
        total = len(df_target_slice)

        t_start = time.time()
        results_map = {}
        results_lock = threading.Lock()
        completed_count = [0]
        ok_count_t = [0]
        fail_count_t = [0]
        log_queue = Queue()

        rows_list = list(df_target_slice.iterrows())

        def worker(thread_id: int, work_items: list):
            """Each thread launches its own Playwright context + page."""
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(
                        headless=h_less,
                        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
                    )
                    page = browser.new_page()
                    page.on("dialog", lambda d: d.accept())

                    for orig_idx, row_series in work_items:
                        raw_val = row_series[target_col]
                        item_val = str(raw_val).strip() if pd.notna(raw_val) else ""

                        if not item_val or item_val.lower() == "nan":
                            row_res = {"STATUS": "INVALID_VALUE"}
                            for f in selected_fields:
                                row_res[f] = ""
                            log_queue.put((orig_idx, item_val, row_res, "INVALID_VALUE"))
                        else:
                            log_queue.put((orig_idx, item_val, None, "QUERYING"))
                            try:
                                row_res = scrape_single_chassis(
                                    page, item_val,
                                    search_type=search_type,
                                    max_retries=m_retries,
                                )
                            except Exception as exc:
                                row_res = {"STATUS": f"ERROR: {str(exc)[:60]}"}
                                for f in selected_fields:
                                    row_res[f] = ""
                            log_queue.put((orig_idx, item_val, row_res, row_res.get("STATUS", "UNKNOWN")))
                            time.sleep(random.uniform(m_delay, mx_delay))

                        with results_lock:
                            results_map[orig_idx] = row_res
                            completed_count[0] += 1
                            if row_res.get("STATUS") == "OK":
                                ok_count_t[0] += 1
                            else:
                                fail_count_t[0] += 1

                    browser.close()

            except Exception as e:
                log_queue.put((-1, "", None, f"THREAD-{thread_id} CRASHED: {str(e)[:80]}"))

        actual_workers = min(eff_workers, total)
        chunks = split_work(rows_list, actual_workers)

        try:
            append_log(f"🚀 Launching {actual_workers} parallel tabs for {total:,} rows...")

            threads = []
            for tid, chunk in enumerate(chunks):
                if not chunk:
                    continue
                t = threading.Thread(target=worker, args=(tid, chunk), daemon=True)
                t.start()
                threads.append(t)
                append_log(f"   Tab-{tid+1} started ({len(chunk)} rows)")

            # Live UI update loop
            while any(t.is_alive() for t in threads):
                while True:
                    try:
                        orig_idx, item_val, row_res, status = log_queue.get_nowait()
                        if status == "QUERYING":
                            append_log(f"  ↗ Querying {item_val}...")
                        elif status == "INVALID_VALUE":
                            append_log(f"  ⚠ Skipped empty row")
                        elif status == "OK":
                            rto = (row_res or {}).get("Registration Authority", "N/A")
                            append_log(f"  ✓ {item_val} → RTO: {rto}")
                        else:
                            append_log(f"  ✗ {item_val} → {status}")
                    except Empty:
                        break

                done = completed_count[0]
                elapsed_so_far = round(time.time() - t_start, 1)
                speed = done / elapsed_so_far if elapsed_so_far > 0 else 0
                remaining = total - done
                eta = round(remaining / speed) if speed > 0 else 0
                eta_text = f"{eta//3600}h {(eta%3600)//60}m" if eta >= 3600 else (f"{eta//60}m {eta%60}s" if eta >= 60 else f"{eta}s")

                status_box.markdown(
                    f"🔄 **{done:,}/{total:,} processed** • {actual_workers} tabs parallel | "
                    f"Speed: **{speed:.1f} rows/s** | ETA: **{eta_text}**"
                )
                stat_proc.markdown(
                    f'<div class="stat-card"><div class="stat-label">Progress</div><div class="stat-value" style="color:#38bdf8;">{done:,} / {total:,}</div></div>',
                    unsafe_allow_html=True,
                )
                stat_ok.markdown(
                    f'<div class="stat-card"><div class="stat-label">Successful</div><div class="stat-value" style="color:#34d399;">{ok_count_t[0]}</div></div>',
                    unsafe_allow_html=True,
                )
                stat_fail.markdown(
                    f'<div class="stat-card"><div class="stat-label">Not Found / Fail</div><div class="stat-value" style="color:#f87171;">{fail_count_t[0]}</div></div>',
                    unsafe_allow_html=True,
                )
                stat_time.markdown(
                    f'<div class="stat-card"><div class="stat-label">Speed & ETA</div><div class="stat-value" style="color:#c084fc;">{speed:.1f}/s • {eta_text}</div></div>',
                    unsafe_allow_html=True,
                )
                progress_bar.progress(min(done / total, 1.0), text=f"{done}/{total:,} ({int((done/total)*100)}%) — ETA: {eta_text}")
                time.sleep(1.0)

            for t in threads:
                t.join()

            while True:
                try:
                    orig_idx, item_val, row_res, status = log_queue.get_nowait()
                    if status == "OK":
                        rto = (row_res or {}).get("Registration Authority", "N/A")
                        append_log(f"  ✓ {item_val} → RTO: {rto}")
                    elif status not in ("QUERYING", "INVALID_VALUE"):
                        append_log(f"  ✗ {item_val} → {status}")
                except Empty:
                    break

            append_log(f"✅ All {actual_workers} tabs completed.")
            results = [results_map.get(orig_idx, {"STATUS": "MISSING"}) for orig_idx, _ in rows_list]

        except Exception as e:
            st.error(f"Process encountered an error: {e}")
            append_log(f"CRITICAL ERROR: {traceback.format_exc()}")
            results = [results_map.get(orig_idx, {"STATUS": "MISSING"}) for orig_idx, _ in rows_list]

        t_total = time.time() - t_start

        # Merge results with original dataframe
        df_merged = df_target_slice.copy()
        for field in selected_fields:
            col_name = "RTO Location" if field == "Registration Authority" else field
            df_merged[col_name] = [r.get(field, "") for r in results]

        # Save results in session_state, unlock scraping state, and rerun
        st.session_state.results = {
            "df_merged": df_merged,
            "elapsed": t_total,
            "total": total,
            "has_headers": cfg.get("has_headers", True),
            "selected_fields": selected_fields,
            "just_completed": True,
        }
        st.session_state.is_scraping = False
        st.rerun()
