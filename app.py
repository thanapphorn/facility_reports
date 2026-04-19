import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
from datetime import datetime

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
st.set_page_config(
    page_title="ระบบแจ้งปัญหาภายในอาคาร",
    page_icon="🏢",
    layout="wide",
)

# =============================================================
# CSS
# =============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;500;600;700&display=swap');

html, body, [class*="css"], [class*="st-"] {
  font-family: 'Sarabun', sans-serif !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── Page background ── */
.stApp { background: #f0f2f5 !important; }

/* ── Remove default padding so header goes edge-to-edge ── */
.block-container {
  padding-top: 0 !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
  max-width: 100% !important;
}

/* ── App header ── */
.app-header {
  background: #1e2d45;
  padding: 0 40px;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 12px;
  position: sticky;
  top: 0;
  z-index: 999;
  box-shadow: 0 2px 12px rgba(0,0,0,0.25);
}
.app-header-title { font-size: 17px; font-weight: 700; color: #fff; }
.app-header-sub   { font-size: 12px; color: #7fa3c8; }

/* ── Tabs ── */
.stTabs { background: #fff; border-bottom: 1.5px solid #e4e7ed; }
.stTabs [data-baseweb="tab-list"] {
  background: #fff !important;
  padding: 0 32px !important;
  gap: 0 !important;
  border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  padding: 16px 22px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  color: #6b7280 !important;
  border-bottom: 2.5px solid transparent !important;
  border-radius: 0 !important;
  font-family: 'Sarabun', sans-serif !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #3b5fc0 !important; }
.stTabs [aria-selected="true"] {
  color: #3b5fc0 !important;
  border-bottom-color: #3b5fc0 !important;
  font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"]    { display: none !important; }

/* ── Tab content area ── */
.stTabs [data-baseweb="tab-panel"] {
  background: #f0f2f5 !important;
  padding: 0 !important;
}

/* ── Inner content wrapper ── */
.inner {
  max-width: 860px;
  margin: 0 auto;
  padding: 36px 24px 64px;
}

/* ── Section header ── */
.sec-hdr { margin-bottom: 28px; }
.sec-hdr h2 { font-size: 22px; font-weight: 700; color: #111827; letter-spacing: -0.02em; }
.sec-hdr p  { font-size: 14px; color: #6b7280; margin-top: 4px; }

/* ── Card ── */
.card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 24px 28px;
  margin-bottom: 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.card-title {
  font-size: 14px; font-weight: 600; color: #111827;
  padding-bottom: 14px; margin-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

/* ── Streamlit inputs inside cards ── */
div[data-testid="stTextInput"] > div > div > input,
div[data-testid="stTextArea"]  > div > div > textarea {
  border: 1.5px solid #d1d5db !important;
  border-radius: 8px !important;
  font-size: 14.5px !important;
  font-family: 'Sarabun', sans-serif !important;
  background: #fff !important;
  padding: 10px 14px !important;
  transition: border-color 0.15s, box-shadow 0.15s !important;
}
div[data-testid="stTextInput"] > div > div > input:focus,
div[data-testid="stTextArea"]  > div > div > textarea:focus {
  border-color: #3b5fc0 !important;
  box-shadow: 0 0 0 3px rgba(59,95,192,0.12) !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"]  label,
div[data-testid="stSelectbox"] label,
div[data-testid="stFileUploader"] label {
  font-size: 12px !important;
  font-weight: 700 !important;
  color: #6b7280 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
}

/* ── Select box ── */
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  border: 1.5px solid #d1d5db !important;
  border-radius: 8px !important;
  font-size: 14.5px !important;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
  border-color: #3b5fc0 !important;
  box-shadow: 0 0 0 3px rgba(59,95,192,0.12) !important;
}

/* ── Buttons ── */
div[data-testid="stButton"] > button {
  font-family: 'Sarabun', sans-serif !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  border-radius: 8px !important;
  padding: 10px 20px !important;
  transition: all 0.15s !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
  background: #3b5fc0 !important;
  border: none !important;
  color: #fff !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
  background: #2f4fa3 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(59,95,192,0.35) !important;
}
div[data-testid="stButton"] > button[kind="secondary"] {
  background: #fff !important;
  border: 1.5px solid #d1d5db !important;
  color: #374151 !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
  background: #f9fafb !important;
  border-color: #9ca3af !important;
}

/* ── Checkbox ── */
div[data-testid="stCheckbox"] label {
  font-size: 14px !important;
  color: #374151 !important;
  font-weight: 400 !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
}

/* ── Alerts / messages ── */
div[data-testid="stAlert"] {
  border-radius: 8px !important;
}

/* ── Status badges ── */
.badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 11px; border-radius: 999px;
  font-size: 12px; font-weight: 600;
}
.badge-dot { width: 6px; height: 6px; border-radius: 50%; }
.b-wait  { background: #fffbeb; color: #b45309; }
.b-wait  .badge-dot { background: #f59e0b; }
.b-proc  { background: #eff6ff; color: #1d4ed8; }
.b-proc  .badge-dot { background: #3b82f6; }
.b-done  { background: #f0fdf4; color: #15803d; }
.b-done  .badge-dot { background: #22c55e; }

/* ── Stat cards ── */
.stats-grid {
  display: grid; grid-template-columns: repeat(4,1fr);
  gap: 14px; margin-bottom: 24px;
}
.stat-card {
  background: #fff; border-radius: 12px;
  border: 1px solid #e4e7ed;
  padding: 18px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  position: relative; overflow: hidden;
}
.stat-card::before {
  content: ''; position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
}
.sc-all::before  { background: #3b5fc0; }
.sc-wait::before { background: #f59e0b; }
.sc-proc::before { background: #3b82f6; }
.sc-done::before { background: #22c55e; }
.stat-label { font-size: 11px; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; }
.stat-num   { font-size: 36px; font-weight: 700; line-height: 1.1; margin-top: 6px; }
.sc-all  .stat-num { color: #3b5fc0; }
.sc-wait .stat-num { color: #d97706; }
.sc-proc .stat-num { color: #1d4ed8; }
.sc-done .stat-num { color: #15803d; }

/* ── Data table ── */
.tbl-wrap {
  background: #fff; border-radius: 12px;
  border: 1px solid #e4e7ed;
  overflow: hidden; margin-bottom: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.tbl-wrap table { width: 100%; border-collapse: collapse; }
.tbl-wrap thead tr { background: #f8f9fb; }
.tbl-wrap th {
  padding: 11px 14px; text-align: left;
  font-size: 11px; font-weight: 700; color: #9ca3af;
  text-transform: uppercase; letter-spacing: 0.06em;
  border-bottom: 1.5px solid #e4e7ed;
  white-space: nowrap;
}
.tbl-wrap td {
  padding: 12px 14px; font-size: 13.5px;
  color: #374151; border-bottom: 1px solid #f3f4f6;
  vertical-align: middle;
}
.tbl-wrap tr:last-child td { border-bottom: none; }
.tbl-wrap tbody tr:hover td { background: #f8f9ff; }
.id-mono { font-family: 'Courier New', monospace; font-size: 12.5px; color: #6b7280; font-weight: 600; }

/* ── Pagination ── */
.pag { display:flex; align-items:center; justify-content:space-between; }
.pag-info { font-size: 13px; color: #9ca3af; }

/* ── Detail view ── */
.det-card {
  background: #fff; border-radius: 12px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  margin-top: 8px;
}
.det-hdr {
  background: #f8f9fb; padding: 14px 22px;
  display: flex; align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e4e7ed;
  font-size: 14px; font-weight: 600; color: #111827;
}
.id-chip {
  font-family: 'Courier New', monospace; font-size: 13px;
  font-weight: 700; color: #3b5fc0;
  background: #eef2fb; padding: 4px 10px; border-radius: 6px;
}
.det-grid { display: grid; grid-template-columns: 160px 1fr; }
.det-k {
  padding: 12px 22px; font-size: 13px; font-weight: 600;
  color: #6b7280; border-bottom: 1px solid #f3f4f6;
  background: #fafafa;
}
.det-v {
  padding: 12px 22px; font-size: 14px; color: #111827;
  border-bottom: 1px solid #f3f4f6;
}
.det-last .det-k, .det-last .det-v { border-bottom: none; }

/* ── Admin section title ── */
.adm-title {
  font-size: 14px; font-weight: 700; color: #111827;
  padding-bottom: 14px; margin-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex; align-items: center; gap: 8px;
}

/* ── File uploader ── */
div[data-testid="stFileUploader"] > div {
  border: 1.5px dashed #d1d5db !important;
  border-radius: 8px !important;
  background: #fafafa !important;
}
div[data-testid="stFileUploader"] > div:hover {
  border-color: #3b5fc0 !important;
  background: #eef2fb !important;
}

@media (max-width: 640px) {
  .stats-grid { grid-template-columns: repeat(2,1fr); }
  .inner { padding: 20px 16px 48px; }
}
</style>
""", unsafe_allow_html=True)

# =============================================================
# App header (sticky)
# =============================================================
st.markdown("""
<div class="app-header">
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
       stroke="#7fa3c8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <rect x="3" y="3" width="18" height="18" rx="2"/>
    <path d="M3 9h18M9 21V9"/>
  </svg>
  <div>
    <div class="app-header-title">ระบบแจ้งปัญหาภายในอาคาร</div>
    <div class="app-header-sub">Facility Issue Reporting System</div>
  </div>
</div>
""", unsafe_allow_html=True)

# =============================================================
# Session state
# =============================================================
if "reports" not in st.session_state:
    with st.spinner("กำลังโหลดข้อมูล..."):
        st.session_state.reports = load_reports()
if "page"              not in st.session_state: st.session_state.page = 1
if "edit_id"           not in st.session_state: st.session_state.edit_id = None
if "confirm_delete_id" not in st.session_state: st.session_state.confirm_delete_id = None

def reload_reports():
    get_gspread_client.clear()
    st.session_state.reports = load_reports()

def status_badge(status):
    cfg = {
        "รอดำเนินการ":    ("b-wait", "รอดำเนินการ"),
        "กำลังดำเนินการ": ("b-proc", "กำลังดำเนินการ"),
        "เสร็จสิ้น":      ("b-done", "เสร็จสิ้น"),
    }
    cls, label = cfg.get(status, ("b-wait", status))
    return f'<span class="badge {cls}"><span class="badge-dot"></span>{label}</span>'

def det_card(r):
    return f"""
    <div class="det-card">
      <div class="det-hdr">
        <span>รายละเอียดการแจ้ง</span>
        <span class="id-chip">{r["ID"]}</span>
      </div>
      <div class="det-grid">
        <div class="det-k">👤 ชื่อผู้แจ้ง</div>
        <div class="det-v">{r["Name"]}</div>
        <div class="det-k">📂 หมวดปัญหา</div>
        <div class="det-v">{r["Category"]}</div>
        <div class="det-k">📍 สถานที่</div>
        <div class="det-v">{r["Location"]}</div>
        <div class="det-k">🗒️ รายละเอียด</div>
        <div class="det-v">{r.get("Detail") or "—"}</div>
        <div class="det-k">📅 วัน/เวลา</div>
        <div class="det-v">{r["Date"]} เวลา {r["Time"]} น.</div>
        <div class="det-k det-last">📌 สถานะ</div>
        <div class="det-v det-last">{status_badge(r["Status"])}</div>
      </div>
    </div>"""

# =============================================================
# Tabs
# =============================================================
tab_report, tab_track, tab_admin = st.tabs(["✏️  แจ้งปัญหา", "🔍  ติดตามสถานะ", "🛡️  Admin"])

# ============================================================
# TAB 1: แจ้งปัญหา
# ============================================================
with tab_report:
    st.markdown('<div class="inner">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-hdr">
      <h2>แจ้งปัญหา</h2>
      <p>กรอกข้อมูลเพื่อแจ้งปัญหาภายในอาคาร ทีมงานจะดำเนินการโดยเร็ว</p>
    </div>""", unsafe_allow_html=True)

    # ── Card: ข้อมูลผู้แจ้ง ──
    st.markdown('<div class="card"><div class="card-title">👤 ข้อมูลผู้แจ้ง</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: name  = st.text_input("ชื่อผู้แจ้ง *", placeholder="กรอกชื่อ-นามสกุล")
    with c2: phone = st.text_input("เบอร์โทร *",    placeholder="0XX-XXX-XXXX")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Card: รายละเอียดปัญหา ──
    st.markdown('<div class="card"><div class="card-title">ℹ️ รายละเอียดปัญหา</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        category = st.selectbox("หมวดปัญหา", [
            "ลิฟต์","ไฟฟ้า","ระบบแอร์","น้ำประปา","ห้องน้ำ",
            "ประตู/หน้าต่าง","ไฟส่องสว่าง","กล้องวงจรปิด",
            "อินเทอร์เน็ต","ที่จอดรถ","ความสะอาด","อื่นๆ",
        ])
    with c4:
        location = st.text_input("สถานที่ *", placeholder="เช่น อาคาร A ชั้น 3")
    detail = st.text_area("รายละเอียดปัญหา", height=110,
                           placeholder="อธิบายปัญหาที่พบโดยละเอียด...")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Card: รูปภาพ ──
    st.markdown("""
    <div class="card">
      <div class="card-title">
        🖼️ อัปโหลดรูปภาพ
        <span style="font-size:12px;font-weight:400;color:#9ca3af;margin-left:6px;">(ไม่บังคับ)</span>
      </div>""", unsafe_allow_html=True)
    image = st.file_uploader("เลือกไฟล์รูปภาพ",
                              type=["jpg","jpeg","png","gif"],
                              label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    confirm = st.checkbox("ฉันยืนยันว่าข้อมูลที่กรอกถูกต้องและเป็นความจริง")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("ส่งรายงาน", type="primary", use_container_width=True):
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
            if image:
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
                "ImageUrl": image_url, "ImageName": image_name,
            }
            with st.spinner("กำลังบันทึกข้อมูล..."):
                add_report(report)
                reload_reports()

            components.html(f"""
            <style>
              @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&display=swap');
              * {{ box-sizing:border-box; margin:0; padding:0; }}
              body {{ font-family:'Sarabun',sans-serif; background:transparent; padding:4px 0; }}
              .wrap {{
                background:#f0fdf4; border:1px solid #bbf7d0;
                border-radius:10px; padding:16px 20px;
                display:flex; align-items:center; gap:14px;
              }}
              .msg {{ font-size:14px; color:#15803d; font-weight:600; flex:1; }}
              .chip {{
                font-family:'Courier New',monospace; font-size:15px;
                font-weight:700; color:#166534;
                background:#dcfce7; border:1px solid #86efac;
                border-radius:6px; padding:5px 14px; cursor:pointer;
                transition:all 0.15s; white-space:nowrap;
              }}
              .chip:hover {{ background:#bbf7d0; }}
              .hint {{ font-size:11px; color:#6b9e80; margin-top:3px; text-align:center; }}
            </style>
            <div class="wrap">
              <span style="font-size:20px;">✅</span>
              <span class="msg">ส่งรายงานสำเร็จ! รหัสของคุณคือ</span>
              <div>
                <div class="chip" id="c"
                  onclick="navigator.clipboard.writeText('{report_id}');
                           this.textContent='✓ คัดลอกแล้ว!';
                           var t=this;
                           setTimeout(function(){{t.textContent='{report_id}';}},2000);">
                  {report_id}
                </div>
                <div class="hint">คลิกเพื่อคัดลอก</div>
              </div>
            </div>
            """, height=80)

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# TAB 2: ติดตามสถานะ
# ============================================================
with tab_track:
    st.markdown('<div class="inner">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-hdr">
      <h2>ติดตามสถานะ</h2>
      <p>กรอกรหัสการแจ้งเพื่อตรวจสอบสถานะการดำเนินการ</p>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">🔍 รหัสการแจ้ง</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([5, 1])
    with c1:
        track_id = st.text_input("รหัส", placeholder="RP-XXXXXX",
                                  label_visibility="collapsed")
    with c2:
        check = st.button("ตรวจสอบ", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if check:
        found = False
        for r in st.session_state.reports:
            if r["ID"] == track_id.strip():
                found = True
                st.markdown(det_card(r), unsafe_allow_html=True)
                if r.get("ImageUrl"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.image(r["ImageUrl"], caption=r.get("ImageName",""), width=340)
                break
        if not found:
            st.error("ไม่พบข้อมูล กรุณาตรวจสอบรหัสอีกครั้ง")

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# TAB 3: Admin
# ============================================================
with tab_admin:
    st.markdown('<div class="inner">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sec-hdr">
      <h2>Admin</h2>
      <p>เข้าสู่ระบบเพื่อจัดการรายงานปัญหาทั้งหมด</p>
    </div>""", unsafe_allow_html=True)

    # Login box
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown('<div class="card"><div class="card-title">🔒 เข้าสู่ระบบ Admin</div>', unsafe_allow_html=True)
        password = st.text_input("รหัสผ่าน", type="password",
                                  placeholder="กรอกรหัสผ่าน",
                                  label_visibility="collapsed")
        st.button("เข้าสู่ระบบ", type="primary", use_container_width=True, key="login_btn")
        st.markdown('</div>', unsafe_allow_html=True)

    if password != st.secrets["admin"]["password"]:
        if password:
            st.error("รหัสผ่านไม่ถูกต้อง")
        else:
            st.info("🔒 กรุณาใส่รหัสผ่านเพื่อเข้าสู่ระบบ")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # ── Dashboard header ──
    hcol1, hcol2 = st.columns([6, 1])
    with hcol1:
        st.success("✅ เข้าสู่ระบบสำเร็จ")
    with hcol2:
        if st.button("🔄 รีโหลด", use_container_width=True):
            reload_reports()
            st.rerun()

    df = pd.DataFrame(st.session_state.reports)
    if len(df) == 0:
        st.info("ยังไม่มีข้อมูลในระบบ")
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # ── Stat cards ──
    total   = len(df)
    wait    = len(df[df["Status"] == "รอดำเนินการ"])
    process = len(df[df["Status"] == "กำลังดำเนินการ"])
    done    = len(df[df["Status"] == "เสร็จสิ้น"])

    st.markdown(f"""
    <div class="stats-grid">
      <div class="stat-card sc-all">
        <div class="stat-label">แจ้งทั้งหมด</div>
        <div class="stat-num">{total}</div>
      </div>
      <div class="stat-card sc-wait">
        <div class="stat-label">รอดำเนินการ</div>
        <div class="stat-num">{wait}</div>
      </div>
      <div class="stat-card sc-proc">
        <div class="stat-label">กำลังดำเนินการ</div>
        <div class="stat-num">{process}</div>
      </div>
      <div class="stat-card sc-done">
        <div class="stat-label">เสร็จสิ้น</div>
        <div class="stat-num">{done}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Filter ──
    st.markdown('<div class="card" style="padding:16px 20px;margin-bottom:16px;">', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([3, 2, 2])
    with f1: search = st.text_input("ค้นหา ID",   placeholder="RP-XXXXXX", label_visibility="collapsed")
    with f2: month  = st.selectbox("เดือน", ["ทั้งหมด"] + df["Month"].unique().tolist(), label_visibility="collapsed")
    with f3: sf     = st.selectbox("สถานะ", ["ทั้งหมด","รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    filtered = df.copy()
    if search: filtered = filtered[filtered["ID"].str.contains(search, case=False)]
    if month != "ทั้งหมด": filtered = filtered[filtered["Month"] == month]
    if sf    != "ทั้งหมด": filtered = filtered[filtered["Status"] == sf]

    # ── Table ──
    rows_per_page = 10
    total_rows    = len(filtered)

    if total_rows == 0:
        st.info("ไม่พบข้อมูลที่ตรงกับเงื่อนไข")
    else:
        total_pages = max(1, (total_rows - 1) // rows_per_page + 1)
        if st.session_state.page > total_pages:
            st.session_state.page = 1

        start     = (st.session_state.page - 1) * rows_per_page
        page_data = filtered.iloc[start: start + rows_per_page]

        rows_html = ""
        for _, row in page_data.iterrows():
            img = (f'<a href="{row["ImageUrl"]}" target="_blank" '
                   f'style="color:#3b5fc0;font-size:12.5px;font-weight:500;">{row["ImageName"]}</a>'
                   if row.get("ImageUrl") else
                   '<span style="color:#d1d5db;">—</span>')
            rows_html += (
                f'<tr><td><span class="id-mono">{row["ID"]}</span></td>'
                f'<td>{row["Name"]}</td>'
                f'<td style="color:#6b7280;font-size:13px;">{row["Phone"]}</td>'
                f'<td>{row["Category"]}</td>'
                f'<td style="font-size:13px;">{row["Location"]}</td>'
                f'<td style="font-size:13px;color:#6b7280;">{row["Date"]}</td>'
                f'<td style="font-size:13px;color:#6b7280;">{row["Time"]}</td>'
                f'<td>{status_badge(row["Status"])}</td>'
                f'<td>{img}</td></tr>'
            )

        st.markdown(f"""
        <div class="tbl-wrap">
          <table>
            <thead><tr>
              <th>ID</th><th>ชื่อ</th><th>เบอร์</th><th>หมวด</th>
              <th>สถานที่</th><th>วันที่</th><th>เวลา</th><th>สถานะ</th><th>รูปภาพ</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>""", unsafe_allow_html=True)

        # Pagination
        p1, p2, p3 = st.columns([1, 3, 1])
        with p1:
            if st.button("◀ ก่อนหน้า",
                         disabled=st.session_state.page <= 1,
                         use_container_width=True):
                st.session_state.page -= 1
                st.rerun()
        with p2:
            st.markdown(
                f"<div style='text-align:center;padding:10px 0;font-size:13px;color:#6b7280;'>"
                f"หน้า <b style='color:#111827'>{st.session_state.page}</b> / "
                f"<b style='color:#111827'>{total_pages}</b>"
                f" · {total_rows} รายการ</div>",
                unsafe_allow_html=True)
        with p3:
            if st.button("ถัดไป ▶",
                         disabled=st.session_state.page >= total_pages,
                         use_container_width=True):
                st.session_state.page += 1
                st.rerun()

    st.divider()

    # ── Update Status ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="adm-title">⚡ เปลี่ยนสถานะ</div>', unsafe_allow_html=True)
    u1, u2, u3 = st.columns([2, 2, 1])
    with u1:
        selected_id = st.selectbox("ID", df["ID"], label_visibility="collapsed")
    with u2:
        statuses   = ["รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"]
        cur_status = next((r["Status"] for r in st.session_state.reports
                           if r["ID"] == selected_id), statuses[0])
        new_status = st.selectbox("สถานะ", statuses,
                                   index=statuses.index(cur_status),
                                   label_visibility="collapsed")
    with u3:
        st.markdown("<div style='margin-top:24px'>", unsafe_allow_html=True)
        if st.button("อัปเดต", type="primary", use_container_width=True):
            with st.spinner("กำลังอัปเดต..."):
                update_report(selected_id, {"Status": new_status})
                reload_reports()
            st.success(f"✅ อัปเดต **{selected_id}** → {new_status}")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # ── View / Edit / Delete ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="adm-title">📄 ดูรายละเอียด / แก้ไข / ลบรายงาน</div>', unsafe_allow_html=True)

    view_id = st.selectbox("เลือก ID", df["ID"], key="view_select",
                            label_visibility="collapsed")

    bv, be, bd = st.columns(3)
    with bv: show_detail = st.button("👁 แสดงรายละเอียด", use_container_width=True)
    with be:
        if st.button("✏️ แก้ไขรายการ", use_container_width=True):
            st.session_state.edit_id = view_id
            st.session_state.confirm_delete_id = None
    with bd:
        if st.button("🗑️ ลบรายการ", use_container_width=True, type="primary"):
            st.session_state.confirm_delete_id = view_id
            st.session_state.edit_id = None

    # Confirm delete
    if st.session_state.confirm_delete_id == view_id:
        st.warning(f"⚠️ ยืนยันการลบ **{view_id}** ? ไม่สามารถกู้คืนได้")
        dc1, dc2 = st.columns(2)
        with dc1:
            if st.button("✅ ยืนยันลบ", use_container_width=True, type="primary"):
                with st.spinner("กำลังลบ..."):
                    delete_report(view_id)
                    reload_reports()
                st.session_state.confirm_delete_id = None
                st.success(f"ลบ {view_id} เรียบร้อย")
                st.rerun()
        with dc2:
            if st.button("❌ ยกเลิก", use_container_width=True):
                st.session_state.confirm_delete_id = None
                st.rerun()

    # Edit form
    elif st.session_state.edit_id == view_id:
        rec = next((r for r in st.session_state.reports if r["ID"] == view_id), None)
        if rec:
            st.markdown(f"---\n**✏️ แก้ไขรายการ: {view_id}**")
            e1, e2 = st.columns(2)
            with e1:
                e_name  = st.text_input("ชื่อผู้แจ้ง",  value=rec["Name"],     key="e_name")
                e_phone = st.text_input("เบอร์โทร",     value=rec["Phone"],    key="e_phone")
                e_loc   = st.text_input("สถานที่",       value=rec["Location"], key="e_loc")
            with e2:
                cats = ["ลิฟต์","ไฟฟ้า","ระบบแอร์","น้ำประปา","ห้องน้ำ",
                        "ประตู/หน้าต่าง","ไฟส่องสว่าง","กล้องวงจรปิด",
                        "อินเทอร์เน็ต","ที่จอดรถ","ความสะอาด","อื่นๆ"]
                e_cat    = st.selectbox("หมวดปัญหา", cats,
                                        index=cats.index(rec["Category"]) if rec["Category"] in cats else 0,
                                        key="e_cat")
                e_status = st.selectbox("สถานะ", statuses,
                                         index=statuses.index(rec["Status"]),
                                         key="e_status")
            e_detail = st.text_area("รายละเอียด", value=rec["Detail"], key="e_detail")
            s1, s2 = st.columns(2)
            with s1:
                if st.button("💾 บันทึกการแก้ไข", use_container_width=True, type="primary"):
                    with st.spinner("กำลังบันทึก..."):
                        update_report(view_id, {
                            "Name": e_name.strip(), "Phone": e_phone.strip(),
                            "Location": e_loc.strip(), "Category": e_cat,
                            "Status": e_status, "Detail": e_detail,
                        })
                        reload_reports()
                    st.session_state.edit_id = None
                    st.success(f"✅ บันทึกการแก้ไข {view_id} เรียบร้อย")
                    st.rerun()
            with s2:
                if st.button("❌ ยกเลิก", use_container_width=True, key="cancel_edit"):
                    st.session_state.edit_id = None
                    st.rerun()

    # View detail
    elif show_detail:
        for r in st.session_state.reports:
            if r["ID"] == view_id:
                st.markdown(det_card(r), unsafe_allow_html=True)
                if r.get("ImageUrl"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.image(r["ImageUrl"], caption=r.get("ImageName",""), width=380)
                else:
                    st.info("ไม่มีรูปภาพ")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
