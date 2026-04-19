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
    "https://www.googleapis.com/auth/drive",
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
            row_num = i + 2
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
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Sarabun', sans-serif !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 3rem !important; }

/* ── Page header ── */
.page-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
    border-radius: 18px;
    padding: 28px 32px;
    margin-bottom: 28px;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 4px 20px rgba(30,58,95,0.25);
}
.page-header .icon { font-size: 2.8rem; line-height: 1; }
.page-header h1 { margin: 0; font-size: 1.75rem; font-weight: 800; letter-spacing: 0.3px; }
.page-header p  { margin: 4px 0 0; font-size: 0.95rem; opacity: 0.8; }

/* ── Metric cards ── */
.dashboard { display: flex; gap: 16px; margin: 0 0 28px; flex-wrap: wrap; }
.card {
    flex: 1; min-width: 140px;
    border-radius: 16px;
    padding: 20px 22px 18px;
    color: #fff;
    box-shadow: 0 4px 14px rgba(0,0,0,0.12);
    position: relative;
    overflow: hidden;
}
.card::after {
    content: '';
    position: absolute;
    top: -20px; right: -20px;
    width: 90px; height: 90px;
    border-radius: 50%;
    background: rgba(255,255,255,0.10);
}
.card .label { font-size: 13px; font-weight: 600; opacity: 0.88; letter-spacing: 0.4px; }
.card .num   { font-size: 2.8rem; font-weight: 900; line-height: 1.1; margin-top: 6px; }
.card .sub   { font-size: 12px; opacity: 0.7; margin-top: 2px; }
.c-total   { background: linear-gradient(135deg, #2d6a9f, #1e3a5f); }
.c-wait    { background: linear-gradient(135deg, #f59e0b, #d97706); }
.c-process { background: linear-gradient(135deg, #7c3aed, #5b21b6); }
.c-done    { background: linear-gradient(135deg, #059669, #047857); }

/* ── Status badges ── */
.badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 13px; border-radius: 99px;
    font-size: 12.5px; font-weight: 700; white-space: nowrap;
}
.badge-wait    { background: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }
.badge-process { background: #EDE9FE; color: #5B21B6; border: 1px solid #C4B5FD; }
.badge-done    { background: #D1FAE5; color: #065F46; border: 1px solid #6EE7B7; }

/* ── Info card ── */
.info-card {
    background: #fff;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 0;
    margin-top: 16px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.info-card .ic-header {
    background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
    color: #fff;
    padding: 14px 24px;
    font-weight: 700;
    font-size: 15px;
}
.info-card .row {
    display: flex;
    padding: 12px 24px;
    border-bottom: 1px solid #F3F4F6;
    font-size: 14.5px;
    align-items: flex-start;
}
.info-card .row:last-child { border-bottom: none; }
.info-card .label { min-width: 140px; color: #6B7280; font-weight: 600; padding-top: 1px; }
.info-card .value { color: #111827; flex: 1; }

/* ── Data table ── */
.styled-table {
    width: 100%; border-collapse: collapse;
    font-size: 13.5px; margin-top: 8px;
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
}
.styled-table th {
    background: #1e3a5f;
    color: #fff;
    padding: 12px 14px;
    text-align: left;
    font-weight: 700;
    letter-spacing: 0.3px;
}
.styled-table td {
    padding: 10px 14px;
    border-bottom: 1px solid #F3F4F6;
    vertical-align: middle;
    color: #374151;
}
.styled-table tr:last-child td { border-bottom: none; }
.styled-table tr:hover td { background: #F0F7FF; }
.styled-table tbody tr:nth-child(even) td { background: #FAFAFA; }
.styled-table tbody tr:nth-child(even):hover td { background: #F0F7FF; }

/* ── Section title ── */
.section-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #1e3a5f;
    margin: 24px 0 14px;
    padding-left: 10px;
    border-left: 4px solid #2d6a9f;
}

/* ── Form styling ── */
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stFileUploader"] label {
    font-weight: 600 !important;
    color: #374151 !important;
    font-size: 14px !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3a5f 0%, #163050 100%) !important;
}
section[data-testid="stSidebar"] * { color: #e2eaf4 !important; }
section[data-testid="stSidebar"] .stRadio > label { color: #94b8d8 !important; font-size: 13px !important; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 10px 14px !important;
    margin-bottom: 6px;
    font-weight: 600 !important;
    font-size: 15px !important;
    transition: background 0.2s;
    cursor: pointer;
    color: #d1e4f5 !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.12) !important;
}

/* ── Pagination bar ── */
.page-info {
    text-align: center;
    padding: 9px 0;
    color: #4B5563;
    font-size: 14.5px;
    font-weight: 600;
}
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
    get_gspread_client.clear()
    st.session_state.reports = load_reports()

# -----------------------
# Helper
# -----------------------
def status_badge(status):
    icons = {"รอดำเนินการ": "🟡", "กำลังดำเนินการ": "🟣", "เสร็จสิ้น": "🟢"}
    cls   = {"รอดำเนินการ": "badge-wait", "กำลังดำเนินการ": "badge-process", "เสร็จสิ้น": "badge-done"}
    icon  = icons.get(status, "⚪")
    c     = cls.get(status, "badge-wait")
    return f'<span class="badge {c}">{icon} {status}</span>'

# =============================================================
# Sidebar Navigation
# =============================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 28px;">
        <div style="font-size:3rem;">🏢</div>
        <div style="font-weight:800;font-size:1.15rem;color:#fff;margin-top:8px;line-height:1.3;">
            ระบบแจ้งปัญหา<br>ภายในอาคาร
        </div>
        <div style="color:#94b8d8;font-size:12px;margin-top:6px;">Facility Report System</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    menu = st.radio(
        "เมนูหลัก",
        ["📢  แจ้งปัญหา", "🔎  ติดตามสถานะ", "🔐  Admin"],
        label_visibility="collapsed"
    )
    st.markdown("""
    <div style="position:absolute;bottom:20px;left:0;right:0;text-align:center;
         color:#4a7099;font-size:12px;padding:0 16px;">
        v1.0 · Office Maintenance
    </div>
    """, unsafe_allow_html=True)

# normalise menu key (strip extra spaces)
menu = menu.strip()

# =============================================================
# PAGE 1 : REPORT
# =============================================================
if menu == "📢  แจ้งปัญหา":
    st.markdown("""
    <div class="page-header">
        <div class="icon">📢</div>
        <div>
            <h1>แจ้งปัญหา</h1>
            <p>กรอกข้อมูลให้ครบถ้วนเพื่อแจ้งปัญหาภายในอาคาร</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            name  = st.text_input("👤 ชื่อผู้แจ้ง *")
        with col2:
            phone = st.text_input("📞 เบอร์โทรศัพท์ *")

        col3, col4 = st.columns(2)
        with col3:
            category = st.selectbox("📂 หมวดปัญหา *", [
                "ลิฟต์","ไฟฟ้า","ระบบแอร์","น้ำประปา","ห้องน้ำ",
                "ประตู/หน้าต่าง","ไฟส่องสว่าง","กล้องวงจรปิด",
                "อินเทอร์เน็ต","ที่จอดรถ","ความสะอาด","อื่นๆ"
            ])
        with col4:
            location = st.text_input("📍 สถานที่ *")

        detail = st.text_area("🗒️ รายละเอียดปัญหา", height=120,
                               placeholder="อธิบายปัญหาที่พบโดยละเอียด...")
        image  = st.file_uploader("📸 อัปโหลดรูปภาพ (ไม่บังคับ)", type=["jpg","jpeg","png","gif"])
        confirm = st.checkbox("✅ ฉันยืนยันข้อมูลที่กรอกถูกต้องและขอแจ้งปัญหานี้")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📤  ส่งรายงาน", type="primary", use_container_width=False):
        errors = []
        if not name.strip():     errors.append("ชื่อผู้แจ้ง")
        if not phone.strip():    errors.append("เบอร์โทร")
        if not location.strip(): errors.append("สถานที่")
        if not confirm:          errors.append("การยืนยัน")

        if errors:
            st.error(f"กรุณากรอกข้อมูลให้ครบ: **{', '.join(errors)}**")
        else:
            report_id  = "RP-" + str(random.randint(100000, 999999))
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

            st.success("แจ้งปัญหาสำเร็จแล้ว! กรุณาเก็บรหัสด้านล่างไว้ติดตามสถานะ")
            components.html(f"""
            <div style="background:linear-gradient(135deg,#E8F5E9,#F0FDF4);
                border:1.5px solid #86EFAC; border-radius:18px; padding:30px 28px 24px;
                text-align:center; font-family:'Sarabun','Segoe UI',sans-serif;
                box-shadow:0 4px 20px rgba(5,150,105,0.12);">
                <div style="font-size:12px;color:#065F46;font-weight:700;letter-spacing:1.5px;
                     text-transform:uppercase;margin-bottom:12px;">
                    📋 รหัสการแจ้งปัญหาของคุณ
                </div>
                <div style="font-size:2.5rem;font-weight:900;color:#064E3B;letter-spacing:5px;
                    font-family:monospace;background:#fff;border-radius:12px;
                    display:inline-block;padding:12px 36px;border:1.5px solid #6EE7B7;margin:8px 0 20px;">
                    {report_id}
                </div><br>
                <button id="copyBtn" onclick="
                    navigator.clipboard.writeText('{report_id}').then(function(){{
                        var b=document.getElementById('copyBtn');
                        b.innerHTML='✅ &nbsp;คัดลอกแล้ว!';
                        b.style.background='#047857';
                        b.style.transform='scale(0.97)';
                        setTimeout(function(){{
                            b.innerHTML='📋 &nbsp;คัดลอกรหัส';
                            b.style.background='#059669';
                            b.style.transform='scale(1)';
                        }},2000);
                    }})"
                style="background:#059669;color:white;border:none;border-radius:10px;
                    padding:12px 32px;font-size:15px;font-weight:700;cursor:pointer;
                    transition:all 0.2s ease;box-shadow:0 3px 10px rgba(5,150,105,0.35);
                    font-family:'Sarabun',sans-serif;">
                    📋 &nbsp;คัดลอกรหัส
                </button>
                <div style="color:#6B7280;font-size:13px;margin-top:16px;">
                    กรุณาเก็บรหัสนี้ไว้เพื่อติดตามสถานะในภายหลัง
                </div>
            </div>
            """, height=275)

# =============================================================
# PAGE 2 : TRACK
# =============================================================
elif menu == "🔎  ติดตามสถานะ":
    st.markdown("""
    <div class="page-header">
        <div class="icon">🔎</div>
        <div>
            <h1>ติดตามสถานะ</h1>
            <p>กรอกรหัสที่ได้รับเพื่อตรวจสอบสถานะการดำเนินการ</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        track_id = st.text_input("รหัสการแจ้งปัญหา", placeholder="RP-XXXXXX",
                                  label_visibility="collapsed")
    with col2:
        check = st.button("🔍  ตรวจสอบ", type="primary", use_container_width=True)

    if check:
        found = False
        for r in st.session_state.reports:
            if r["ID"] == track_id.strip():
                found = True
                badge_html = status_badge(r["Status"])
                st.markdown(f"""<div class="info-card">
<div class="ic-header">📋 ข้อมูลการแจ้งปัญหา</div>
<div class="row"><span class="label">🔖 รหัสแจ้ง</span><span class="value"><b>{r["ID"]}</b></span></div>
<div class="row"><span class="label">👤 ชื่อผู้แจ้ง</span><span class="value">{r["Name"]}</span></div>
<div class="row"><span class="label">📂 หมวดปัญหา</span><span class="value">{r["Category"]}</span></div>
<div class="row"><span class="label">📍 สถานที่</span><span class="value">{r["Location"]}</span></div>
<div class="row"><span class="label">🗒️ รายละเอียด</span><span class="value">{r["Detail"] or "-"}</span></div>
<div class="row"><span class="label">📅 วันที่/เวลา</span><span class="value">{r["Date"]} เวลา {r["Time"]} น.</span></div>
<div class="row"><span class="label">📌 สถานะ</span><span class="value">{badge_html}</span></div>
</div>""", unsafe_allow_html=True)
                if r.get("ImageUrl"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.image(r["ImageUrl"], caption=r.get("ImageName",""), width=360)
                break
        if not found:
            st.error("❌ ไม่พบข้อมูล กรุณาตรวจสอบรหัสอีกครั้ง")

# =============================================================
# PAGE 3 : ADMIN
# =============================================================
elif menu == "🔐  Admin":
    st.markdown("""
    <div class="page-header">
        <div class="icon">🔐</div>
        <div>
            <h1>Admin Dashboard</h1>
            <p>จัดการและติดตามรายงานทั้งหมดในระบบ</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    password = st.text_input("รหัสผ่าน Admin", type="password",
                              placeholder="กรอกรหัสผ่าน...")
    if password != st.secrets["admin"]["password"]:
        st.warning("🔒 กรุณาใส่รหัสผ่านเพื่อเข้าสู่ระบบ Admin")
        st.stop()

    st.success("✅ เข้าสู่ระบบ Admin เรียบร้อย")

    if st.button("🔄  รีโหลดข้อมูล"):
        reload_reports()
        st.rerun()

    df = pd.DataFrame(st.session_state.reports)
    if len(df) == 0:
        st.info("ยังไม่มีข้อมูลในระบบ")
        st.stop()

    # ── Dashboard Cards ─────────────────────────────────────
    total   = len(df)
    wait    = len(df[df["Status"] == "รอดำเนินการ"])
    process = len(df[df["Status"] == "กำลังดำเนินการ"])
    done    = len(df[df["Status"] == "เสร็จสิ้น"])

    st.markdown(f"""<div class="dashboard">
<div class="card c-total">
    <div class="label">📊 แจ้งปัญหาทั้งหมด</div>
    <div class="num">{total}</div>
    <div class="sub">รายการในระบบ</div>
</div>
<div class="card c-wait">
    <div class="label">⏳ รอดำเนินการ</div>
    <div class="num">{wait}</div>
    <div class="sub">รายการ</div>
</div>
<div class="card c-process">
    <div class="label">⚙️ กำลังดำเนินการ</div>
    <div class="num">{process}</div>
    <div class="sub">รายการ</div>
</div>
<div class="card c-done">
    <div class="label">✅ เสร็จสิ้น</div>
    <div class="num">{done}</div>
    <div class="sub">รายการ</div>
</div>
</div>""", unsafe_allow_html=True)

    # ── Filter ──────────────────────────────────────────────
    st.markdown('<div class="section-title">🔍 ค้นหา &amp; กรองข้อมูล</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        search = st.text_input("ค้นหา ID", placeholder="RP-XXXXXX", label_visibility="collapsed")
    with col2:
        month = st.selectbox("Filter เดือน", ["ทั้งหมด"] + df["Month"].unique().tolist(),
                              label_visibility="collapsed")
    with col3:
        status_filter = st.selectbox("สถานะ",
                                     ["ทั้งหมด","รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"],
                                     label_visibility="collapsed")

    filtered = df.copy()
    if search:
        filtered = filtered[filtered["ID"].str.contains(search, case=False)]
    if month != "ทั้งหมด":
        filtered = filtered[filtered["Month"] == month]
    if status_filter != "ทั้งหมด":
        filtered = filtered[filtered["Status"] == status_filter]

    # ── Pagination ───────────────────────────────────────────
    rows_per_page = 10
    total_rows    = len(filtered)

    st.markdown('<div class="section-title">📋 รายการแจ้งปัญหา</div>', unsafe_allow_html=True)

    if total_rows == 0:
        st.info("ไม่พบข้อมูลที่ตรงกับเงื่อนไข")
    else:
        total_pages = max(1, (total_rows - 1) // rows_per_page + 1)
        if st.session_state.page > total_pages:
            st.session_state.page = 1

        col_prev, col_info, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("◀  ก่อนหน้า", disabled=st.session_state.page <= 1, use_container_width=True):
                st.session_state.page -= 1
                st.rerun()
        with col_info:
            st.markdown(
                f"<div class='page-info'>หน้า <b>{st.session_state.page}</b> / <b>{total_pages}</b>"
                f" &nbsp;·&nbsp; <span style='color:#9CA3AF;font-size:13px;'>{total_rows} รายการ</span></div>",
                unsafe_allow_html=True)
        with col_next:
            if st.button("ถัดไป  ▶", disabled=st.session_state.page >= total_pages, use_container_width=True):
                st.session_state.page += 1
                st.rerun()

        start     = (st.session_state.page - 1) * rows_per_page
        page_data = filtered.iloc[start: start + rows_per_page].copy()
        page_data["สถานะ"]  = page_data["Status"].apply(status_badge)
        page_data["รูปภาพ"] = page_data["ImageName"].apply(
            lambda x: f"<span style='color:#059669;font-weight:600'>✓ {x}</span>"
                      if x else "<span style='color:#D1D5DB'>—</span>"
        )

        html_rows = ""
        for _, row in page_data.iterrows():
            html_rows += (
                "<tr>"
                f"<td><b style='color:#1e3a5f'>{row['ID']}</b></td>"
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
            '<table class="styled-table"><thead><tr>'
            "<th>ID</th><th>ชื่อ</th><th>เบอร์</th><th>หมวด</th>"
            "<th>สถานที่</th><th>วันที่</th><th>เวลา</th><th>สถานะ</th><th>รูปภาพ</th>"
            f"</tr></thead><tbody>{html_rows}</tbody></table>",
            unsafe_allow_html=True
        )

    st.divider()

    # ── Update Status ────────────────────────────────────────
    st.markdown('<div class="section-title">🔄 เปลี่ยนสถานะรายการ</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        selected_id = st.selectbox("เลือก ID", df["ID"], label_visibility="collapsed")
    with col2:
        statuses   = ["รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"]
        cur_status = next((r["Status"] for r in st.session_state.reports if r["ID"] == selected_id), statuses[0])
        new_status = st.selectbox("สถานะใหม่", statuses, index=statuses.index(cur_status),
                                   label_visibility="collapsed")
    with col3:
        st.markdown("<div style='margin-top:4px'>", unsafe_allow_html=True)
        if st.button("💾  บันทึก", type="primary", use_container_width=True):
            with st.spinner("กำลังอัปเดต..."):
                update_report(selected_id, {"Status": new_status})
                reload_reports()
            st.success(f"✅ อัปเดต **{selected_id}** → {new_status}")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # ── View / Edit / Delete ─────────────────────────────────
    st.markdown('<div class="section-title">📋 ดูรายละเอียด / แก้ไข / ลบรายงาน</div>', unsafe_allow_html=True)
    view_id = st.selectbox("เลือก ID รายการ", df["ID"], key="view_select",
                            label_visibility="collapsed")

    col_view, col_edit, col_del = st.columns(3)
    with col_view:
        show_detail = st.button("🔍  แสดงรายละเอียด", use_container_width=True)
    with col_edit:
        if st.button("✏️  แก้ไขรายการ", use_container_width=True):
            st.session_state.edit_id = view_id
            st.session_state.confirm_delete_id = None
    with col_del:
        if st.button("🗑️  ลบรายการ", use_container_width=True, type="primary"):
            st.session_state.confirm_delete_id = view_id
            st.session_state.edit_id = None

    # ── Confirm Delete ───────────────────────────────────────
    if st.session_state.confirm_delete_id == view_id:
        st.warning(f"⚠️ ยืนยันการลบ **{view_id}** ? การลบจะไม่สามารถกู้คืนได้")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅  ยืนยันลบ", use_container_width=True, type="primary"):
                with st.spinner("กำลังลบ..."):
                    delete_report(view_id)
                    reload_reports()
                st.session_state.confirm_delete_id = None
                st.success(f"ลบ {view_id} เรียบร้อยแล้ว")
                st.rerun()
        with c2:
            if st.button("❌  ยกเลิก", use_container_width=True):
                st.session_state.confirm_delete_id = None
                st.rerun()

    # ── Edit Form ────────────────────────────────────────────
    elif st.session_state.edit_id == view_id:
        rec = next((r for r in st.session_state.reports if r["ID"] == view_id), None)
        if rec:
            st.markdown(f"---\n**✏️ แก้ไขรายการ: {view_id}**")
            e_col1, e_col2 = st.columns(2)
            with e_col1:
                e_name  = st.text_input("ชื่อผู้แจ้ง",  value=rec["Name"],     key="e_name")
                e_phone = st.text_input("เบอร์โทร",     value=rec["Phone"],    key="e_phone")
                e_loc   = st.text_input("สถานที่",       value=rec["Location"], key="e_loc")
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
                if st.button("💾  บันทึกการแก้ไข", use_container_width=True, type="primary"):
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
                if st.button("❌  ยกเลิก", use_container_width=True, key="cancel_edit"):
                    st.session_state.edit_id = None
                    st.rerun()

    # ── View Detail ──────────────────────────────────────────
    elif show_detail:
        for r in st.session_state.reports:
            if r["ID"] == view_id:
                badge_html = status_badge(r["Status"])
                st.markdown(f"""<div class="info-card">
<div class="ic-header">📋 รายละเอียดรายการ {r["ID"]}</div>
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
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.image(r["ImageUrl"], caption=r.get("ImageName",""), width=420)
                else:
                    st.info("ไม่มีรูปภาพ")
