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
st.set_page_config(page_title="ระบบแจ้งปัญหาภายในอาคาร", page_icon="🏢", layout="wide")

# =============================================================
# Global CSS — matches the HTML reference design
# =============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

:root {
  --bg:           #f5f6f9;
  --surface:      #ffffff;
  --navy:         #1e2d45;
  --navy-mid:     #263d5a;
  --primary:      #3b5fc0;
  --primary-lt:   #eef2fb;
  --primary-hov:  #2f4fa3;
  --success:      #1a7a4a;
  --success-bg:   #edfaf3;
  --warning:      #b45309;
  --warning-bg:   #fffbeb;
  --danger:       #b91c1c;
  --danger-bg:    #fff1f1;
  --inprog:       #1d4ed8;
  --inprog-bg:    #eff6ff;
  --border:       #e4e7ed;
  --text:         #1a2033;
  --text-muted:   #6b7280;
  --text-light:   #9ca3af;
  --shadow-sm:    0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow:       0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
  --r:            12px;
  --r-sm:         8px;
}

html, body, [class*="css"] {
  font-family: 'Sarabun', sans-serif !important;
  background: var(--bg) !important;
  color: var(--text) !important;
  font-size: 15px;
}

/* ── Strip Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
  padding: 0 !important;
  max-width: 100% !important;
}
section[data-testid="stSidebar"] { display: none !important; }

/* ── App header ── */
.app-header {
  background: var(--navy);
  padding: 0 36px;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.2);
  position: sticky;
  top: 0;
  z-index: 100;
}
.app-header-title { font-size: 18px; font-weight: 700; color: #fff; }
.app-header-sub   { font-size: 12px; color: #8aa5c8; margin-top: 1px; }

/* ── Tab bar  ── */
.tab-bar {
  background: var(--surface);
  border-bottom: 1.5px solid var(--border);
  padding: 0 36px;
  display: flex;
  gap: 0;
  box-shadow: var(--shadow-sm);
}

/* Streamlit radio → styled as tab bar */
div[data-testid="stHorizontalBlock"] > div { padding: 0 !important; }

div[data-baseweb="radio"] {
  display: flex !important;
  flex-direction: row !important;
  gap: 0 !important;
  background: var(--surface) !important;
  padding: 0 !important;
}
div[data-baseweb="radio"] label {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  padding: 17px 22px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  color: var(--text-muted) !important;
  cursor: pointer !important;
  border-bottom: 2.5px solid transparent !important;
  margin: 0 !important;
  transition: all 0.18s !important;
  white-space: nowrap !important;
  background: transparent !important;
}
div[data-baseweb="radio"] label:hover { color: var(--primary) !important; }
div[data-baseweb="radio"] [aria-checked="true"] ~ label,
div[data-baseweb="radio"] label:has(input:checked) {
  color: var(--primary) !important;
  border-bottom-color: var(--primary) !important;
  font-weight: 600 !important;
}
div[data-baseweb="radio"] [data-checked="true"] + div {
  color: var(--primary) !important;
}
div[data-baseweb="radio"] input[type="radio"] { display: none !important; }
/* hide the default circle marker */
div[data-baseweb="radio"] [data-baseweb="radio"] { display: none !important; }

/* ── Page wrapper ── */
.page-wrap {
  max-width: 900px;
  margin: 0 auto;
  padding: 36px 24px 64px;
}

/* ── Section header ── */
.sec-header { margin-bottom: 28px; }
.sec-header h2 {
  font-size: 22px; font-weight: 700;
  color: var(--text); letter-spacing: -0.02em;
}
.sec-header p { font-size: 14px; color: var(--text-muted); margin-top: 4px; }

/* ── Card ── */
.ui-card {
  background: var(--surface);
  border-radius: var(--r);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
  padding: 28px;
  margin-bottom: 20px;
}
.card-title {
  font-size: 14.5px; font-weight: 600; color: var(--text);
  margin-bottom: 20px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 8px;
}

/* ── Status badge ── */
.badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 11px; border-radius: 999px;
  font-size: 12px; font-weight: 600; white-space: nowrap;
}
.badge-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.b-done    { background: var(--success-bg); color: var(--success); }
.b-done    .badge-dot { background: var(--success); }
.b-wait    { background: var(--warning-bg); color: var(--warning); }
.b-wait    .badge-dot { background: #f59e0b; }
.b-proc    { background: var(--inprog-bg);  color: var(--inprog); }
.b-proc    .badge-dot { background: var(--inprog); }

/* ── Stat cards ── */
.stats-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 28px; }
.stat-card {
  background: var(--surface);
  border-radius: var(--r);
  border: 1px solid var(--border);
  padding: 20px 22px;
  box-shadow: var(--shadow-sm);
  position: relative; overflow: hidden;
  transition: transform 0.15s, box-shadow 0.15s;
}
.stat-card:hover { transform: translateY(-2px); box-shadow: var(--shadow); }
.stat-card::before {
  content: ''; position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
}
.sc-all::before  { background: var(--primary); }
.sc-wait::before { background: #f59e0b; }
.sc-proc::before { background: var(--inprog); }
.sc-done::before { background: var(--success); }
.stat-label { font-size: 11.5px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.stat-value { font-size: 38px; font-weight: 700; line-height: 1.1; margin-top: 8px; letter-spacing: -0.02em; }
.sc-all  .stat-value { color: var(--primary); }
.sc-wait .stat-value { color: #d97706; }
.sc-proc .stat-value { color: var(--inprog); }
.sc-done .stat-value { color: var(--success); }

/* ── Filter bar ── */
.filter-bar {
  display: grid; grid-template-columns: 1fr 190px 165px;
  gap: 12px; margin-bottom: 16px;
  background: var(--surface); padding: 16px;
  border-radius: var(--r); border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}
.filter-bar label {
  font-size: 11px; font-weight: 700; color: var(--text-light);
  text-transform: uppercase; letter-spacing: 0.06em;
  display: block; margin-bottom: 6px;
}

/* ── Table ── */
.tbl-wrap {
  background: var(--surface); border-radius: var(--r);
  border: 1px solid var(--border); box-shadow: var(--shadow-sm);
  overflow: hidden; margin-bottom: 16px;
}
.tbl-wrap table { width: 100%; border-collapse: collapse; }
.tbl-wrap thead tr { background: #f7f8fb; }
.tbl-wrap th {
  padding: 12px 14px; text-align: left;
  font-size: 11px; font-weight: 700; color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.06em;
  border-bottom: 1.5px solid var(--border); white-space: nowrap;
}
.tbl-wrap td {
  padding: 13px 14px; font-size: 13.5px;
  color: var(--text); border-bottom: 1px solid var(--border);
  vertical-align: middle;
}
.tbl-wrap tr:last-child td { border-bottom: none; }
.tbl-wrap tbody tr:hover td { background: #f8f9ff; }
.id-cell { font-family: 'Courier New', monospace; font-size: 12.5px; color: var(--text-muted); font-weight: 600; }

/* ── Pagination ── */
.pag-bar {
  display: flex; align-items: center;
  justify-content: space-between;
  padding: 12px 16px; background: var(--surface);
  border-radius: var(--r); border: 1px solid var(--border);
  margin-bottom: 24px;
}
.pag-info { font-size: 13px; color: var(--text-muted); }

/* ── Admin section box ── */
.adm-box {
  background: var(--surface); border-radius: var(--r);
  border: 1px solid var(--border); box-shadow: var(--shadow-sm);
  padding: 24px; margin-bottom: 20px;
}
.adm-box-title {
  font-size: 14px; font-weight: 700; color: var(--text);
  margin-bottom: 18px; display: flex; align-items: center; gap: 8px;
  padding-bottom: 14px; border-bottom: 1px solid var(--border);
}

/* ── Detail card (track / admin view) ── */
.det-card {
  background: var(--surface); border-radius: var(--r);
  border: 1px solid var(--border); box-shadow: var(--shadow-sm);
  overflow: hidden; margin-top: 4px;
}
.det-card-hdr {
  background: #f7f8fb; padding: 14px 22px;
  display: flex; align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
}
.det-card-hdr .id-tag {
  font-family: 'Courier New', monospace;
  font-size: 13px; font-weight: 700; color: var(--primary);
  background: var(--primary-lt); padding: 4px 10px; border-radius: 6px;
}
.det-grid { display: grid; grid-template-columns: auto 1fr; }
.det-k {
  padding: 13px 22px; font-size: 13px; font-weight: 600;
  color: var(--text-muted); border-bottom: 1px solid var(--border);
  background: #fafbfc; white-space: nowrap;
}
.det-v {
  padding: 13px 22px; font-size: 14px; color: var(--text);
  border-bottom: 1px solid var(--border);
}
.det-last .det-k,
.det-last .det-v { border-bottom: none; }

/* ── Streamlit input overrides to match design ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
  border: 1.5px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  font-family: 'Sarabun', sans-serif !important;
  font-size: 14.5px !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px rgba(59,95,192,0.12) !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stFileUploader"] label {
  font-size: 12px !important; font-weight: 700 !important;
  color: var(--text-muted) !important; text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
}

/* ── Buttons ── */
div[data-testid="stButton"] button[kind="primary"] {
  background: var(--primary) !important;
  border: none !important; border-radius: var(--r-sm) !important;
  font-family: 'Sarabun', sans-serif !important;
  font-weight: 600 !important; font-size: 14px !important;
  transition: all 0.15s !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
  background: var(--primary-hov) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(59,95,192,0.35) !important;
}
div[data-testid="stButton"] button[kind="secondary"],
div[data-testid="stButton"] button[kind="tertiary"] {
  background: var(--bg) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  color: var(--text) !important;
  font-family: 'Sarabun', sans-serif !important;
  font-weight: 600 !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 28px 0 !important; }

@media (max-width: 640px) {
  .stats-grid { grid-template-columns: repeat(2,1fr); }
  .filter-bar { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)

# ── App-level header ────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <svg width="26" height="26" viewBox="0 0 24 24" fill="none"
       stroke="#8aa5c8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <rect x="3" y="3" width="18" height="18" rx="2"/>
    <path d="M3 9h18M9 21V9"/>
  </svg>
  <div>
    <div class="app-header-title">ระบบแจ้งปัญหาภายในอาคาร</div>
    <div class="app-header-sub">Facility Issue Reporting System</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tab navigation ──────────────────────────────────────────
menu = st.radio(
    "nav",
    ["✏️  แจ้งปัญหา", "🔍  ติดตามสถานะ", "🛡️  Admin"],
    horizontal=True,
    label_visibility="collapsed",
)
menu = menu.strip()

# ── Initialize session state ────────────────────────────────
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

# ── Helper ──────────────────────────────────────────────────
def status_badge(status):
    cfg = {
        "รอดำเนินการ":     ("b-wait", "รอดำเนินการ"),
        "กำลังดำเนินการ":  ("b-proc", "กำลังดำเนินการ"),
        "เสร็จสิ้น":       ("b-done", "เสร็จสิ้น"),
    }
    cls, label = cfg.get(status, ("b-wait", status))
    return (f'<span class="badge {cls}">'
            f'<span class="badge-dot"></span>{label}</span>')

# wrap content in centred page container
def _open():  st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
def _close(): st.markdown('</div>', unsafe_allow_html=True)

# =============================================================
# PAGE 1 : แจ้งปัญหา
# =============================================================
if menu == "✏️  แจ้งปัญหา":
    _open()
    st.markdown("""
    <div class="sec-header">
      <h2>แจ้งปัญหา</h2>
      <p>กรอกข้อมูลเพื่อแจ้งปัญหาภายในอาคาร ทีมงานจะดำเนินการโดยเร็ว</p>
    </div>""", unsafe_allow_html=True)

    # Card 1 — ข้อมูลผู้แจ้ง
    st.markdown('<div class="ui-card"><div class="card-title">👤 ข้อมูลผู้แจ้ง</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        name  = st.text_input("ชื่อผู้แจ้ง *", placeholder="กรอกชื่อ-นามสกุล")
    with col2:
        phone = st.text_input("เบอร์โทร *", placeholder="0XX-XXX-XXXX")
    st.markdown('</div>', unsafe_allow_html=True)

    # Card 2 — รายละเอียดปัญหา
    st.markdown('<div class="ui-card"><div class="card-title">ℹ️ รายละเอียดปัญหา</div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        category = st.selectbox("หมวดปัญหา", [
            "ลิฟต์","ไฟฟ้า","ระบบแอร์","น้ำประปา","ห้องน้ำ",
            "ประตู/หน้าต่าง","ไฟส่องสว่าง","กล้องวงจรปิด",
            "อินเทอร์เน็ต","ที่จอดรถ","ความสะอาด","อื่นๆ"
        ])
    with col4:
        location = st.text_input("สถานที่ *", placeholder="เช่น อาคาร A ชั้น 3")
    detail = st.text_area("รายละเอียดปัญหา", height=110, placeholder="อธิบายปัญหาที่พบ...")
    st.markdown('</div>', unsafe_allow_html=True)

    # Card 3 — รูปภาพ
    st.markdown('<div class="ui-card"><div class="card-title">🖼️ อัปโหลดรูปภาพ <span style="font-size:12px;font-weight:400;color:var(--text-light);margin-left:4px;">(ไม่บังคับ)</span></div>', unsafe_allow_html=True)
    image = st.file_uploader("เลือกไฟล์", type=["jpg","jpeg","png","gif"],
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

            components.html(f"""
            <style>
              @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&display=swap');
              * {{ box-sizing: border-box; margin: 0; padding: 0; }}
              body {{ font-family: 'Sarabun', sans-serif; background: transparent; }}
              .wrap {{
                background: #edfaf3; border: 1px solid rgba(26,122,74,0.25);
                border-radius: 10px; padding: 18px 22px;
                display: flex; align-items: center; gap: 14px;
              }}
              .icon {{ font-size: 20px; }}
              .msg {{ font-size: 14px; color: #1a7a4a; font-weight: 600; flex: 1; }}
              .id-code {{
                font-family: 'Courier New', monospace; font-size: 16px;
                font-weight: 700; color: #0d4f2e;
                background: #fff; border: 1px solid rgba(26,122,74,0.3);
                border-radius: 6px; padding: 4px 14px; cursor: pointer;
                transition: all 0.15s;
              }}
              .id-code:hover {{ background: #d1fae5; }}
              .copy-hint {{ font-size: 11px; color: #6b9e80; margin-top: 4px; text-align: center; }}
            </style>
            <div class="wrap">
              <div class="icon">✅</div>
              <div class="msg">ส่งรายงานสำเร็จ! รหัสของคุณคือ</div>
              <div>
                <div class="id-code" id="rid" onclick="
                  navigator.clipboard.writeText('{report_id}');
                  this.textContent='✓ คัดลอกแล้ว!';
                  this.style.background='#d1fae5';
                  var t=this;
                  setTimeout(function(){{t.textContent='{report_id}';t.style.background='#fff';}},2000);
                ">{report_id}</div>
                <div class="copy-hint">คลิกเพื่อคัดลอก</div>
              </div>
            </div>
            """, height=90)

    _close()

# =============================================================
# PAGE 2 : ติดตามสถานะ
# =============================================================
elif menu == "🔍  ติดตามสถานะ":
    _open()
    st.markdown("""
    <div class="sec-header">
      <h2>ติดตามสถานะ</h2>
      <p>กรอกรหัสการแจ้งเพื่อตรวจสอบสถานะการดำเนินการ</p>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="ui-card"><div class="card-title">🔍 รหัสการแจ้ง</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        track_id = st.text_input("รหัส", placeholder="RP-XXXXXX",
                                  label_visibility="collapsed")
    with col2:
        check = st.button("ตรวจสอบ", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if check:
        found = False
        for r in st.session_state.reports:
            if r["ID"] == track_id.strip():
                found = True
                badge_html = status_badge(r["Status"])
                st.markdown(f"""
                <div class="det-card">
                  <div class="det-card-hdr">
                    <span style="font-size:14px;font-weight:600;color:var(--text);">รายละเอียดการแจ้ง</span>
                    <span class="id-tag">{r["ID"]}</span>
                  </div>
                  <div class="det-grid">
                    <div class="det-k">👤 ชื่อผู้แจ้ง</div>
                    <div class="det-v">{r["Name"]}</div>
                    <div class="det-k">📂 หมวดปัญหา</div>
                    <div class="det-v">{r["Category"]}</div>
                    <div class="det-k">📍 สถานที่</div>
                    <div class="det-v">{r["Location"]}</div>
                    <div class="det-k">🗒️ รายละเอียด</div>
                    <div class="det-v">{r["Detail"] or "—"}</div>
                    <div class="det-k">📅 วัน/เวลา</div>
                    <div class="det-v">{r["Date"]} เวลา {r["Time"]} น.</div>
                    <div class="det-k det-last">📌 สถานะ</div>
                    <div class="det-v det-last">{badge_html}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
                if r.get("ImageUrl"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.image(r["ImageUrl"], caption=r.get("ImageName",""), width=340)
                break
        if not found:
            st.error("ไม่พบข้อมูล กรุณาตรวจสอบรหัสอีกครั้ง")

    _close()

# =============================================================
# PAGE 3 : Admin
# =============================================================
elif menu == "🛡️  Admin":
    _open()
    st.markdown("""
    <div class="sec-header">
      <h2>Admin</h2>
      <p>เข้าสู่ระบบเพื่อจัดการรายงานปัญหาทั้งหมด</p>
    </div>""", unsafe_allow_html=True)

    # ── Login ────────────────────────────────────────────────
    col_c, col_r = st.columns([1, 2])
    with col_c:
        st.markdown('<div class="ui-card"><div class="card-title">🔒 เข้าสู่ระบบ Admin</div>', unsafe_allow_html=True)
        password = st.text_input("รหัสผ่าน", type="password",
                                  placeholder="กรอกรหัสผ่าน",
                                  label_visibility="collapsed")
        st.button("เข้าสู่ระบบ", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if password != st.secrets["admin"]["password"]:
        st.warning("🔒 กรุณาใส่รหัสผ่านเพื่อเข้าสู่ระบบ")
        _close()
        st.stop()

    st.success("✅ เข้าสู่ระบบสำเร็จ")

    col_head, col_btn = st.columns([5, 1])
    with col_btn:
        if st.button("🔄 รีโหลด", use_container_width=True):
            reload_reports()
            st.rerun()

    df = pd.DataFrame(st.session_state.reports)
    if len(df) == 0:
        st.info("ยังไม่มีข้อมูลในระบบ")
        _close()
        st.stop()

    # ── Stat cards ───────────────────────────────────────────
    total   = len(df)
    wait    = len(df[df["Status"] == "รอดำเนินการ"])
    process = len(df[df["Status"] == "กำลังดำเนินการ"])
    done    = len(df[df["Status"] == "เสร็จสิ้น"])

    st.markdown(f"""
    <div class="stats-grid">
      <div class="stat-card sc-all">
        <div class="stat-label">แจ้งทั้งหมด</div>
        <div class="stat-value">{total}</div>
      </div>
      <div class="stat-card sc-wait">
        <div class="stat-label">รอดำเนินการ</div>
        <div class="stat-value">{wait}</div>
      </div>
      <div class="stat-card sc-proc">
        <div class="stat-label">กำลังดำเนินการ</div>
        <div class="stat-value">{process}</div>
      </div>
      <div class="stat-card sc-done">
        <div class="stat-label">เสร็จสิ้น</div>
        <div class="stat-value">{done}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Filter ───────────────────────────────────────────────
    st.markdown("""
    <div class="filter-bar">
      <div><label>ค้นหา ID</label></div>
      <div><label>Filter เดือน</label></div>
      <div><label>สถานะ</label></div>
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        search = st.text_input("ID", placeholder="RP-XXXXXX",
                                label_visibility="collapsed")
    with col2:
        month = st.selectbox("เดือน", ["ทั้งหมด"] + df["Month"].unique().tolist(),
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

    # ── Table + Pagination ───────────────────────────────────
    rows_per_page = 10
    total_rows    = len(filtered)

    if total_rows == 0:
        st.info("ไม่พบข้อมูลที่ตรงกับเงื่อนไข")
    else:
        total_pages = max(1, (total_rows - 1) // rows_per_page + 1)
        if st.session_state.page > total_pages:
            st.session_state.page = 1

        start     = (st.session_state.page - 1) * rows_per_page
        page_data = filtered.iloc[start: start + rows_per_page].copy()

        rows_html = ""
        for _, row in page_data.iterrows():
            img_cell = (f'<a href="{row["ImageUrl"]}" target="_blank" '
                        f'style="color:var(--primary);font-size:12.5px;font-weight:500;">'
                        f'{row["ImageName"]}</a>'
                        if row.get("ImageUrl") else
                        '<span style="color:var(--text-light);font-size:13px;">—</span>')
            rows_html += (
                "<tr>"
                f'<td><span class="id-cell">{row["ID"]}</span></td>'
                f'<td>{row["Name"]}</td>'
                f'<td style="color:var(--text-muted);font-size:13px;">{row["Phone"]}</td>'
                f'<td>{row["Category"]}</td>'
                f'<td style="font-size:13px;">{row["Location"]}</td>'
                f'<td style="font-size:13px;color:var(--text-muted);">{row["Date"]}</td>'
                f'<td style="font-size:13px;color:var(--text-muted);">{row["Time"]}</td>'
                f'<td>{status_badge(row["Status"])}</td>'
                f'<td>{img_cell}</td>'
                "</tr>"
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

        # Pagination controls
        col_prev, col_info, col_next = st.columns([1, 3, 1])
        with col_prev:
            if st.button("◀ ก่อนหน้า", disabled=st.session_state.page <= 1,
                         use_container_width=True):
                st.session_state.page -= 1
                st.rerun()
        with col_info:
            st.markdown(
                f"<div style='text-align:center;padding:10px 0;"
                f"font-size:13px;color:var(--text-muted);'>"
                f"หน้า <b style='color:var(--text)'>{st.session_state.page}</b> / "
                f"<b style='color:var(--text)'>{total_pages}</b>"
                f" &nbsp;·&nbsp; {total_rows} รายการ</div>",
                unsafe_allow_html=True)
        with col_next:
            if st.button("ถัดไป ▶", disabled=st.session_state.page >= total_pages,
                         use_container_width=True):
                st.session_state.page += 1
                st.rerun()

    st.divider()

    # ── Update Status ─────────────────────────────────────────
    st.markdown("""
    <div class="adm-box-title" style="font-size:14px;font-weight:700;color:var(--text);
         display:flex;align-items:center;gap:8px;padding-bottom:14px;
         border-bottom:1px solid var(--border);margin-bottom:18px;">
      ⚡ เปลี่ยนสถานะ
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        selected_id = st.selectbox("เลือก ID", df["ID"],
                                    label_visibility="collapsed")
    with col2:
        statuses   = ["รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"]
        cur_status = next((r["Status"] for r in st.session_state.reports
                           if r["ID"] == selected_id), statuses[0])
        new_status = st.selectbox("สถานะใหม่", statuses,
                                   index=statuses.index(cur_status),
                                   label_visibility="collapsed")
    with col3:
        if st.button("อัปเดต", type="primary", use_container_width=True):
            with st.spinner("กำลังอัปเดต..."):
                update_report(selected_id, {"Status": new_status})
                reload_reports()
            st.success(f"✅ อัปเดต **{selected_id}** → {new_status}")
            st.rerun()

    st.divider()

    # ── View / Edit / Delete ──────────────────────────────────
    st.markdown("""
    <div class="adm-box-title" style="font-size:14px;font-weight:700;color:var(--text);
         display:flex;align-items:center;gap:8px;padding-bottom:14px;
         border-bottom:1px solid var(--border);margin-bottom:18px;">
      📄 ดูรายละเอียด / แก้ไข / ลบรายงาน
    </div>""", unsafe_allow_html=True)

    view_id = st.selectbox("เลือก ID รายการ", df["ID"], key="view_select",
                            label_visibility="collapsed")

    col_v, col_e, col_d = st.columns(3)
    with col_v:
        show_detail = st.button("👁 แสดงรายละเอียด", use_container_width=True)
    with col_e:
        if st.button("✏️ แก้ไขรายการ", use_container_width=True):
            st.session_state.edit_id = view_id
            st.session_state.confirm_delete_id = None
    with col_d:
        if st.button("🗑️ ลบรายการ", use_container_width=True, type="primary"):
            st.session_state.confirm_delete_id = view_id
            st.session_state.edit_id = None

    # Confirm delete
    if st.session_state.confirm_delete_id == view_id:
        st.warning(f"⚠️ ยืนยันการลบ **{view_id}** ? ไม่สามารถกู้คืนได้")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ ยืนยันลบ", use_container_width=True, type="primary"):
                with st.spinner("กำลังลบ..."):
                    delete_report(view_id)
                    reload_reports()
                st.session_state.confirm_delete_id = None
                st.success(f"ลบ {view_id} เรียบร้อย")
                st.rerun()
        with c2:
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

    # View detail
    elif show_detail:
        for r in st.session_state.reports:
            if r["ID"] == view_id:
                badge_html = status_badge(r["Status"])
                st.markdown(f"""
                <div class="det-card" style="margin-top:16px;">
                  <div class="det-card-hdr">
                    <span style="font-size:14px;font-weight:600;color:var(--text);">รายละเอียดรายการ</span>
                    <span class="id-tag">{r["ID"]}</span>
                  </div>
                  <div class="det-grid">
                    <div class="det-k">👤 ชื่อผู้แจ้ง</div>
                    <div class="det-v">{r["Name"]}</div>
                    <div class="det-k">📞 เบอร์โทร</div>
                    <div class="det-v">{r["Phone"]}</div>
                    <div class="det-k">📂 หมวดปัญหา</div>
                    <div class="det-v">{r["Category"]}</div>
                    <div class="det-k">📍 สถานที่</div>
                    <div class="det-v">{r["Location"]}</div>
                    <div class="det-k">🗒️ รายละเอียด</div>
                    <div class="det-v">{r["Detail"] or "—"}</div>
                    <div class="det-k">📅 วัน/เวลา</div>
                    <div class="det-v">{r["Date"]} เวลา {r["Time"]} น.</div>
                    <div class="det-k det-last">📌 สถานะ</div>
                    <div class="det-v det-last">{badge_html}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
                if r.get("ImageUrl"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.image(r["ImageUrl"], caption=r.get("ImageName",""), width=380)
                else:
                    st.info("ไม่มีรูปภาพ")

    _close()
