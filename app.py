import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
from datetime import datetime
import io

import gspread
from google.oauth2.service_account import Credentials
import cloudinary
import cloudinary.uploader

# =============================================================
# Google Sheets & Drive Setup
# =============================================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

cloudinary.config(
    cloud_name = "dmtcuvfxu",
    api_key    = "166733879592223",
    api_secret = "1YKnxcY8QxgXOR0OvJ_hKCZhtBo",
    secure     = True
)
COLS = ["ID","Name","Phone","Category","Location",
        "Detail","Status","Date","Time","Month","ImageUrl","ImageName"]

@st.cache_resource
def get_gspread_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    return gspread.Client(auth=creds)

def get_sheet():
    return get_gspread_client().open(st.secrets["sheet"]["name"]).sheet1

def load_reports():
    try:
        return get_sheet().get_all_records()
    except Exception:
        return []

def add_report(report: dict):
    get_sheet().append_row(
        [report.get(c, "") for c in COLS],
        value_input_option="USER_ENTERED"
    )

def update_report(report_id: str, updates: dict):
    sheet   = get_sheet()
    records = sheet.get_all_records()
    for i, rec in enumerate(records):
        if rec["ID"] == report_id:
            row_num = i + 2          # row 1 = header
            for col, val in updates.items():
                sheet.update_cell(row_num, COLS.index(col) + 1, val)
            return

def delete_report(report_id: str):
    sheet   = get_sheet()
    records = sheet.get_all_records()
    for i, rec in enumerate(records):
        if rec["ID"] == report_id:
            sheet.delete_rows(i + 2)
            return

def upload_image(image_bytes: bytes, filename: str) -> str:
    result = cloudinary.uploader.upload(
        image_bytes,
        public_id=filename,
        folder="facility_reports"
    )
    return result["secure_url"]

# =============================================================
# App Config
# =============================================================
st.set_page_config(page_title="Facility Report", page_icon="🏢", layout="wide")

# -----------------------
# Global CSS
# -----------------------
st.markdown("""
<style>
.dashboard { display:flex; gap:16px; margin:16px 0 28px 0; }
.card {
    flex:1; border-radius:14px; padding:20px 24px;
    text-align:center; font-size:15px; font-weight:600;
    color:#fff; box-shadow:0 2px 8px rgba(0,0,0,0.10);
}
.card h1 { margin:8px 0 0 0; font-size:2.6rem; font-weight:800; }
.total   { background:linear-gradient(135deg,#4F8EF7,#3a6fd8); }
.wait    { background:linear-gradient(135deg,#f5a623,#e08c0a); }
.process { background:linear-gradient(135deg,#7B61FF,#5a3fd4); }
.done    { background:linear-gradient(135deg,#34C37A,#1fa05a); }

.badge { display:inline-block; padding:3px 12px; border-radius:20px; font-size:13px; font-weight:600; white-space:nowrap; }
.badge-wait    { background:#FFF3CD; color:#856404; }
.badge-process { background:#EDE7FF; color:#5a3fd4; }
.badge-done    { background:#D1F8E6; color:#1a7a46; }

.info-card { background:#f8f9fb; border:1px solid #e2e6ea; border-radius:14px; padding:24px 28px; margin-top:16px; }
.info-card .row { display:flex; padding:8px 0; border-bottom:1px solid #eee; font-size:15px; }
.info-card .row:last-child { border-bottom:none; }
.info-card .label { min-width:130px; color:#888; font-weight:600; }
.info-card .value { color:#222; }

.styled-table { width:100%; border-collapse:collapse; font-size:14px; margin-top:8px; }
.styled-table th { background:#4F8EF7; color:white; padding:10px 12px; text-align:left; font-weight:600; }
.styled-table td { padding:9px 12px; border-bottom:1px solid #eee; vertical-align:middle; }
.styled-table tr:hover td { background:#f5f8ff; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# Initialize session_state
# -----------------------
if "reports" not in st.session_state:
    with st.spinner("กำลังโหลดข้อมูล..."):
        st.session_state.reports = load_reports()
if "page" not in st.session_state:
    st.session_state.page = 1
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None
if "confirm_delete_id" not in st.session_state:
    st.session_state.confirm_delete_id = None

def reload_reports():
    st.session_state.reports = load_reports()

# -----------------------
# Helper
# -----------------------
def status_badge(status):
    cls = {"รอดำเนินการ":"badge-wait",
           "กำลังดำเนินการ":"badge-process",
           "เสร็จสิ้น":"badge-done"}.get(status, "badge-wait")
    return f'<span class="badge {cls}">{status}</span>'

# =============================================================
# Menu
# =============================================================
st.title("🏢 ระบบแจ้งปัญหาภายในอาคาร")
menu = st.radio("เมนู", ["📢 แจ้งปัญหา","🔎 ติดตามสถานะ","🔐 Admin"], horizontal=True, label_visibility="collapsed")

# =============================================================
# PAGE 1 : REPORT
# =============================================================
if menu == "📢 แจ้งปัญหา":
    st.header("📢 แจ้งปัญหา")

    col1, col2 = st.columns(2)
    with col1:
        name  = st.text_input("ชื่อผู้แจ้ง *")
    with col2:
        phone = st.text_input("เบอร์โทร *")

    category = st.selectbox("หมวดปัญหา", [
        "ลิฟต์","ไฟฟ้า","ระบบแอร์","น้ำประปา","ห้องน้ำ",
        "ประตู/หน้าต่าง","ไฟส่องสว่าง","กล้องวงจรปิด",
        "อินเทอร์เน็ต","ที่จอดรถ","ความสะอาด","อื่นๆ"
    ])
    location = st.text_input("สถานที่ *")
    detail   = st.text_area("รายละเอียดปัญหา")
    image    = st.file_uploader("📸 อัปโหลดรูปภาพ (ไม่บังคับ)", type=["jpg","jpeg","png","gif"])
    confirm  = st.checkbox("ยืนยันการแจ้งปัญหา")

    if st.button("ส่งรายงาน", type="primary"):
        errors = []
        if not name.strip():     errors.append("ชื่อผู้แจ้ง")
        if not phone.strip():    errors.append("เบอร์โทร")
        if not location.strip(): errors.append("สถานที่")
        if not confirm:          errors.append("การยืนยัน")

        if errors:
            st.error(f"กรุณากรอกข้อมูลให้ครบ: {', '.join(errors)}")
        else:
            report_id = "RP-" + str(random.randint(100000, 999999))

            # อัปโหลดรูปไป Google Drive
            image_url  = ""
            image_name = ""
            if image is not None:
                with st.spinner("กำลังอัปโหลดรูปภาพ..."):
                    image_url  = upload_image(image.read(), image.name)
                    image_name = image.name

            report = {
                "ID": report_id, "Name": name.strip(), "Phone": phone.strip(),
                "Category": category, "Location": location.strip(),
                "Detail": detail, "Status": "รอดำเนินการ",
                "Date": datetime.now().strftime("%d/%m/%Y"),
                "Time": datetime.now().strftime("%H:%M"),
                "Month": datetime.now().strftime("%B %Y"),
                "ImageUrl": image_url, "ImageName": image_name
            }

            with st.spinner("กำลังบันทึกข้อมูล..."):
                add_report(report)
                reload_reports()

            st.success("✅ แจ้งปัญหาสำเร็จแล้ว!")
            components.html(f"""
            <div style="background:linear-gradient(135deg,#E8F5E9,#F1F8E9);
                border:2px solid #66BB6A; border-radius:16px; padding:28px 24px 22px;
                text-align:center; font-family:'Segoe UI',sans-serif;
                box-shadow:0 4px 16px rgba(76,175,80,0.15);">
                <div style="font-size:13px;color:#558B2F;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;">
                    📋 รหัสการแจ้งปัญหาของคุณ
                </div>
                <div style="font-size:2.4rem;font-weight:900;color:#1B5E20;letter-spacing:4px;
                    font-family:monospace;background:#fff;border-radius:10px;
                    display:inline-block;padding:10px 32px;border:1.5px solid #A5D6A7;margin:10px 0 16px;">
                    {report_id}
                </div><br>
                <button id="copyBtn" onclick="
                    navigator.clipboard.writeText('{report_id}').then(function(){{
                        var b=document.getElementById('copyBtn');
                        b.innerHTML='✅ &nbsp;คัดลอกแล้ว!';
                        b.style.background='#2E7D32';
                        b.style.transform='scale(0.97)';
                        setTimeout(function(){{
                            b.innerHTML='📋 &nbsp;คัดลอกรหัส';
                            b.style.background='#43A047';
                            b.style.transform='scale(1)';
                        }},2000);
                    }})"
                style="background:#43A047;color:white;border:none;border-radius:10px;
                    padding:11px 28px;font-size:15px;font-weight:700;cursor:pointer;
                    transition:all 0.2s ease;box-shadow:0 2px 8px rgba(67,160,71,0.35);">
                    📋 &nbsp;คัดลอกรหัส
                </button>
                <div style="color:#6a6a6a;font-size:13px;margin-top:14px;">
                    กรุณาเก็บรหัสนี้ไว้เพื่อติดตามสถานะในภายหลัง
                </div>
            </div>
            """, height=270)

# =============================================================
# PAGE 2 : TRACK
# =============================================================
elif menu == "🔎 ติดตามสถานะ":
    st.header("🔎 ติดตามสถานะ")

    col1, col2 = st.columns([3, 1])
    with col1:
        track_id = st.text_input("", placeholder="RP-XXXXXX", label_visibility="collapsed")
    with col2:
        check = st.button("ตรวจสอบ", type="primary", use_container_width=True)

    if check:
        found = False
        for r in st.session_state.reports:
            if r["ID"] == track_id.strip():
                found = True
                badge_html = status_badge(r["Status"])
                st.markdown(f"""<div class="info-card">
<div class="row"><span class="label">🔖 รหัสแจ้ง</span><span class="value"><b>{r["ID"]}</b></span></div>
<div class="row"><span class="label">👤 ชื่อผู้แจ้ง</span><span class="value">{r["Name"]}</span></div>
<div class="row"><span class="label">📂 หมวดปัญหา</span><span class="value">{r["Category"]}</span></div>
<div class="row"><span class="label">📍 สถานที่</span><span class="value">{r["Location"]}</span></div>
<div class="row"><span class="label">🗒️ รายละเอียด</span><span class="value">{r["Detail"] or "-"}</span></div>
<div class="row"><span class="label">📅 วันที่/เวลา</span><span class="value">{r["Date"]} เวลา {r["Time"]} น.</span></div>
<div class="row"><span class="label">📌 สถานะ</span><span class="value">{badge_html}</span></div>
</div>""", unsafe_allow_html=True)
                if r.get("ImageUrl"):
                    st.image(r["ImageUrl"], caption=r.get("ImageName",""), width=340)
                break
        if not found:
            st.error("❌ ไม่พบข้อมูล กรุณาตรวจสอบรหัสอีกครั้ง")

# =============================================================
# PAGE 3 : ADMIN
# =============================================================
elif menu == "🔐 Admin":
    st.header("🔐 Admin Login")
    password = st.text_input("รหัสผ่าน", type="password")
    if password != st.secrets["admin"]["password"]:
        st.warning("กรุณาใส่รหัสผ่าน")
        st.stop()

    st.success("✅ เข้าสู่ระบบ Admin")

    if st.button("🔄 รีโหลดข้อมูล"):
        reload_reports()
        st.rerun()

    df = pd.DataFrame(st.session_state.reports)
    if len(df) == 0:
        st.info("ยังไม่มีข้อมูลในระบบ")
        st.stop()

    # ── Dashboard ──────────────────────────────────────────
    total   = len(df)
    wait    = len(df[df["Status"] == "รอดำเนินการ"])
    process = len(df[df["Status"] == "กำลังดำเนินการ"])
    done    = len(df[df["Status"] == "เสร็จสิ้น"])

    st.markdown(f"""<div class="dashboard">
<div class="card total">แจ้งทั้งหมด<br><h1>{total}</h1></div>
<div class="card wait">รอดำเนินการ<br><h1>{wait}</h1></div>
<div class="card process">กำลังดำเนินการ<br><h1>{process}</h1></div>
<div class="card done">เสร็จสิ้น<br><h1>{done}</h1></div>
</div>""", unsafe_allow_html=True)

    # ── Filter ─────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search = st.text_input("🔎 ค้นหา ID", placeholder="RP-XXXXXX")
    with col2:
        month = st.selectbox("📅 Filter เดือน", ["ทั้งหมด"] + df["Month"].unique().tolist())
    with col3:
        status_filter = st.selectbox("📌 สถานะ",
                                     ["ทั้งหมด","รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"])

    filtered = df.copy()
    if search:
        filtered = filtered[filtered["ID"].str.contains(search, case=False)]
    if month != "ทั้งหมด":
        filtered = filtered[filtered["Month"] == month]
    if status_filter != "ทั้งหมด":
        filtered = filtered[filtered["Status"] == status_filter]

    # ── Pagination ─────────────────────────────────────────
    rows_per_page = 10
    total_rows    = len(filtered)

    if total_rows == 0:
        st.info("ไม่พบข้อมูลที่ตรงกับเงื่อนไข")
    else:
        total_pages = max(1, (total_rows - 1) // rows_per_page + 1)
        if st.session_state.page > total_pages:
            st.session_state.page = 1

        col_prev, col_info, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("◀  Previous", disabled=st.session_state.page <= 1, use_container_width=True):
                st.session_state.page -= 1
                st.rerun()
        with col_info:
            st.markdown(
                f"<div style='text-align:center;padding:8px 0;color:#555;font-size:15px;'>"
                f"หน้า <b>{st.session_state.page}</b> / <b>{total_pages}</b> "
                f"<span style='color:#aaa;font-size:13px;'>({total_rows} รายการ)</span></div>",
                unsafe_allow_html=True)
        with col_next:
            if st.button("Next  ▶", disabled=st.session_state.page >= total_pages, use_container_width=True):
                st.session_state.page += 1
                st.rerun()

        start     = (st.session_state.page - 1) * rows_per_page
        page_data = filtered.iloc[start: start + rows_per_page].copy()

        page_data["สถานะ"]  = page_data["Status"].apply(status_badge)
        page_data["รูปภาพ"] = page_data["ImageName"].apply(
            lambda x: f"<span style='color:#2e7d32'>✓ {x}</span>" if x else "<span style='color:#aaa'>-</span>"
        )

        html_rows = ""
        for _, row in page_data.iterrows():
            html_rows += (
                "<tr>"
                f"<td><b>{row['ID']}</b></td>"
                f"<td>{row['Name']}</td>"
                f"<td>{row['Phone']}</td>"
                f"<td>{row['Category']}</td>"
                f"<td>{row['Location']}</td>"
                f"<td>{row['Date']}</td>"
                f"<td>{row['Time']}</td>"
                f"<td>{row['สถานะ']}</td>"
                f"<td>{row['รูปภาพ']}</td>"
                "</tr>"
            )
        st.markdown(
            '<table class="styled-table"><tr>'
            "<th>ID</th><th>ชื่อ</th><th>เบอร์</th><th>หมวด</th>"
            "<th>สถานที่</th><th>วันที่</th><th>เวลา</th><th>สถานะ</th><th>รูปภาพ</th>"
            f"</tr>{html_rows}</table>",
            unsafe_allow_html=True
        )

    st.divider()

    # ── Update Status ───────────────────────────────────────
    st.subheader("🔄 เปลี่ยนสถานะ")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        selected_id = st.selectbox("เลือก ID", df["ID"])
    with col2:
        statuses   = ["รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"]
        cur_status = next((r["Status"] for r in st.session_state.reports if r["ID"] == selected_id), statuses[0])
        new_status = st.selectbox("สถานะใหม่", statuses, index=statuses.index(cur_status))
    with col3:
        st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
        if st.button("💾 Update", type="primary", use_container_width=True):
            with st.spinner("กำลังอัปเดต..."):
                update_report(selected_id, {"Status": new_status})
                reload_reports()
            st.success(f"✅ อัปเดต {selected_id} → {new_status}")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ── View / Edit / Delete ────────────────────────────────
    st.subheader("📋 ดูรายละเอียด / แก้ไข / ลบรายงาน")
    view_id = st.selectbox("เลือก ID", df["ID"], key="view_select")

    col_view, col_edit, col_del = st.columns(3)
    with col_view:
        show_detail = st.button("🔍 แสดงรายละเอียด", use_container_width=True)
    with col_edit:
        if st.button("✏️ แก้ไขรายการ", use_container_width=True):
            st.session_state.edit_id = view_id
            st.session_state.confirm_delete_id = None
    with col_del:
        if st.button("🗑️ ลบรายการ", use_container_width=True, type="primary"):
            st.session_state.confirm_delete_id = view_id
            st.session_state.edit_id = None

    # ── Confirm Delete ──────────────────────────────────────
    if st.session_state.confirm_delete_id == view_id:
        st.warning(f"⚠️ ยืนยันการลบ **{view_id}** ? การลบจะไม่สามารถกู้คืนได้")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ ยืนยันลบ", use_container_width=True, type="primary"):
                with st.spinner("กำลังลบ..."):
                    delete_report(view_id)
                    reload_reports()
                st.session_state.confirm_delete_id = None
                st.success(f"ลบ {view_id} เรียบร้อยแล้ว")
                st.rerun()
        with c2:
            if st.button("❌ ยกเลิก", use_container_width=True):
                st.session_state.confirm_delete_id = None
                st.rerun()

    # ── Edit Form ───────────────────────────────────────────
    elif st.session_state.edit_id == view_id:
        rec = next((r for r in st.session_state.reports if r["ID"] == view_id), None)
        if rec:
            st.markdown("---")
            st.markdown(f"**✏️ แก้ไขรายการ: {view_id}**")
            e_col1, e_col2 = st.columns(2)
            with e_col1:
                e_name  = st.text_input("ชื่อผู้แจ้ง", value=rec["Name"],     key="e_name")
                e_phone = st.text_input("เบอร์โทร",    value=rec["Phone"],    key="e_phone")
                e_loc   = st.text_input("สถานที่",      value=rec["Location"], key="e_loc")
            with e_col2:
                cats = ["ลิฟต์","ไฟฟ้า","ระบบแอร์","น้ำประปา","ห้องน้ำ",
                        "ประตู/หน้าต่าง","ไฟส่องสว่าง","กล้องวงจรปิด",
                        "อินเทอร์เน็ต","ที่จอดรถ","ความสะอาด","อื่นๆ"]
                e_cat    = st.selectbox("หมวดปัญหา", cats,
                                        index=cats.index(rec["Category"]) if rec["Category"] in cats else 0,
                                        key="e_cat")
                e_status = st.selectbox("สถานะ", ["รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"],
                                         index=["รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"].index(rec["Status"]),
                                         key="e_status")
            e_detail = st.text_area("รายละเอียด", value=rec["Detail"], key="e_detail")

            s1, s2 = st.columns(2)
            with s1:
                if st.button("💾 บันทึกการแก้ไข", use_container_width=True, type="primary"):
                    with st.spinner("กำลังบันทึก..."):
                        update_report(view_id, {
                            "Name": e_name.strip(), "Phone": e_phone.strip(),
                            "Location": e_loc.strip(), "Category": e_cat,
                            "Status": e_status, "Detail": e_detail
                        })
                        reload_reports()
                    st.session_state.edit_id = None
                    st.success(f"✅ บันทึกการแก้ไข {view_id} เรียบร้อย")
                    st.rerun()
            with s2:
                if st.button("❌ ยกเลิก", use_container_width=True, key="cancel_edit"):
                    st.session_state.edit_id = None
                    st.rerun()

    # ── View Detail ─────────────────────────────────────────
    elif show_detail:
        for r in st.session_state.reports:
            if r["ID"] == view_id:
                badge_html = status_badge(r["Status"])
                st.markdown(f"""<div class="info-card">
<div class="row"><span class="label">🔖 รหัสแจ้ง</span><span class="value"><b>{r["ID"]}</b></span></div>
<div class="row"><span class="label">👤 ชื่อผู้แจ้ง</span><span class="value">{r["Name"]}</span></div>
<div class="row"><span class="label">📞 เบอร์โทร</span><span class="value">{r["Phone"]}</span></div>
<div class="row"><span class="label">📂 หมวดปัญหา</span><span class="value">{r["Category"]}</span></div>
<div class="row"><span class="label">📍 สถานที่</span><span class="value">{r["Location"]}</span></div>
<div class="row"><span class="label">🗒️ รายละเอียด</span><span class="value">{r["Detail"] or "-"}</span></div>
<div class="row"><span class="label">📅 วันที่/เวลา</span><span class="value">{r["Date"]} เวลา {r["Time"]} น.</span></div>
<div class="row"><span class="label">📌 สถานะ</span><span class="value">{badge_html}</span></div>
</div>""", unsafe_allow_html=True)
                if r.get("ImageUrl"):
                    st.image(r["ImageUrl"], caption=r.get("ImageName",""), width=420)
                else:
                    st.info("ไม่มีรูปภาพ")
