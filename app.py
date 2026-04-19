import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials
import cloudinary
import cloudinary.uploader

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
cloudinary.config(
    cloud_name="dmtcuvfxu",
    api_key="166733879592223",
    api_secret="1YKnxcY8QxgXOR0OvJ_hKCZhtBo",
    secure=True,
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
    get_sheet().append_row([report.get(c, "") for c in COLS],
                            value_input_option="USER_ENTERED")

def update_report(report_id: str, updates: dict):
    sheet = get_sheet()
    for i, rec in enumerate(sheet.get_all_records()):
        if rec["ID"] == report_id:
            for col, val in updates.items():
                sheet.update_cell(i + 2, COLS.index(col) + 1, val)
            return

def delete_report(report_id: str):
    sheet = get_sheet()
    for i, rec in enumerate(sheet.get_all_records()):
        if rec["ID"] == report_id:
            sheet.delete_rows(i + 2)
            return

def upload_image(image_bytes: bytes, filename: str) -> str:
    result = cloudinary.uploader.upload(
        image_bytes, public_id=filename, folder="facility_reports"
    )
    return result["secure_url"]

# ─────────────────────────────────────────────
st.set_page_config(page_title="แจ้งปัญหาอาคาร", page_icon="🏢", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Sarabun', sans-serif !important; }

#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.stApp { background: #f4f6f9 !important; }

/* ── Top bar ── */
.topbar {
  background: #0f2044;
  height: 58px; padding: 0 40px;
  display: flex; align-items: center; gap: 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  position: sticky; top: 0; z-index: 999;
}
.topbar-icon {
  width: 34px; height: 34px; background: rgba(255,255,255,0.1);
  border-radius: 8px; display: flex; align-items: center;
  justify-content: center; flex-shrink: 0;
}
.topbar-title { font-size: 16px; font-weight: 700; color: #fff; }
.topbar-sub   { font-size: 11.5px; color: #7fa8d4; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: #fff !important;
  border-bottom: 1px solid #e8eaed !important;
  padding: 0 40px !important;
  gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: #5f6368 !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  font-family: 'Sarabun', sans-serif !important;
  padding: 15px 20px !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #1a56db !important; }
.stTabs [aria-selected="true"] {
  color: #1a56db !important;
  border-bottom-color: #1a56db !important;
  font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] {
  background: #f4f6f9 !important;
  padding-top: 32px !important;
}

/* ── Inputs ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
  border: 1.5px solid #dadce0 !important;
  border-radius: 8px !important;
  font-family: 'Sarabun', sans-serif !important;
  font-size: 15px !important;
  color: #202124 !important;
  background: #fff !important;
  transition: border-color .15s, box-shadow .15s !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
  border-color: #1a56db !important;
  box-shadow: 0 0 0 3px rgba(26,86,219,.1) !important;
  outline: none !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stFileUploader"] label,
div[data-testid="stCheckbox"] label {
  font-family: 'Sarabun', sans-serif !important;
  font-size: 13.5px !important;
  font-weight: 600 !important;
  color: #3c4043 !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  border: 1.5px solid #dadce0 !important;
  border-radius: 8px !important;
  font-size: 15px !important;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
  border-color: #1a56db !important;
  box-shadow: 0 0 0 3px rgba(26,86,219,.1) !important;
}
div[data-testid="stCheckbox"] label {
  font-size: 14px !important;
  font-weight: 400 !important;
  color: #3c4043 !important;
}
/* ── File uploader ── */
div[data-testid="stFileUploader"] > div {
  border: 2px dashed #dadce0 !important;
  border-radius: 10px !important;
  background: #fafafa !important;
}
div[data-testid="stFileUploader"] > div:hover {
  border-color: #1a56db !important;
  background: #f0f4ff !important;
}

/* ── Track search: align input + button ── */
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {
  height: 44px !important;
  margin-top: 0 !important;
}

/* ── Buttons ── */
div[data-testid="stButton"] button {
  font-family: 'Sarabun', sans-serif !important;
  font-size: 14px !important; font-weight: 600 !important;
  border-radius: 8px !important;
  transition: all .15s !important;
}
div[data-testid="stButton"] button[kind="primary"] {
  background: #1a56db !important;
  border: none !important; color: #fff !important;
  padding: 10px 24px !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
  background: #1446b8 !important;
  box-shadow: 0 4px 14px rgba(26,86,219,.35) !important;
  transform: translateY(-1px) !important;
}
div[data-testid="stButton"] button[kind="secondary"] {
  background: #fff !important;
  border: 1.5px solid #dadce0 !important;
  color: #3c4043 !important;
}
div[data-testid="stButton"] button[kind="secondary"]:hover {
  background: #f8f9fa !important;
  border-color: #bdc1c6 !important;
}

/* ── Section card ── */
.scard {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e8eaed;
  padding: 24px 28px;
  margin-bottom: 18px;
  box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
.scard-title {
  font-size: 14px; font-weight: 700; color: #202124;
  padding-bottom: 16px; margin-bottom: 20px;
  border-bottom: 1px solid #f1f3f4;
  display: flex; align-items: center; gap: 8px;
}

/* ── Stat grid ── */
.stat-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:22px; }
.stat-box {
  background:#fff; border-radius:12px;
  border:1px solid #e8eaed; padding:20px 22px;
  box-shadow:0 1px 3px rgba(0,0,0,.05);
  position:relative; overflow:hidden;
  transition: box-shadow .15s;
}
.stat-box:hover { box-shadow:0 4px 12px rgba(0,0,0,.1); }
.stat-box::after {
  content:''; position:absolute; top:0; left:0; right:0; height:3px;
}
.s-blue::after  { background:#1a56db; }
.s-amber::after { background:#f59e0b; }
.s-indigo::after{ background:#6366f1; }
.s-green::after { background:#10b981; }
.stat-lbl { font-size:11.5px; font-weight:700; color:#9aa0a6;
            text-transform:uppercase; letter-spacing:.05em; }
.stat-val { font-size:38px; font-weight:700; line-height:1.1; margin-top:6px; }
.s-blue  .stat-val { color:#1a56db; }
.s-amber .stat-val { color:#d97706; }
.s-indigo.stat-val { color:#6366f1; }
.s-green .stat-val { color:#059669; }

/* ── Badge ── */
.badge {
  display:inline-flex; align-items:center; gap:5px;
  padding:4px 10px; border-radius:999px;
  font-size:12px; font-weight:600;
}
.dot { width:6px; height:6px; border-radius:50%; }
.b-wait  { background:#fffbeb; color:#b45309; }
.b-wait  .dot { background:#f59e0b; }
.b-proc  { background:#eef2ff; color:#4338ca; }
.b-proc  .dot { background:#6366f1; }
.b-done  { background:#ecfdf5; color:#065f46; }
.b-done  .dot { background:#10b981; }

/* ── Table ── */
.tbl { background:#fff; border-radius:12px; border:1px solid #e8eaed;
       overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.05); margin-bottom:14px; }
.tbl table { width:100%; border-collapse:collapse; }
.tbl thead tr { background:#f8f9fa; }
.tbl th {
  padding:11px 14px; text-align:left;
  font-size:11px; font-weight:700; color:#9aa0a6;
  text-transform:uppercase; letter-spacing:.06em;
  border-bottom:1.5px solid #e8eaed; white-space:nowrap;
}
.tbl td {
  padding:12px 14px; font-size:13.5px; color:#3c4043;
  border-bottom:1px solid #f1f3f4; vertical-align:middle;
}
.tbl tr:last-child td { border-bottom:none; }
.tbl tbody tr:hover td { background:#f8f9ff; }
.id-tag { font-family:'Courier New',monospace; font-size:12px;
          color:#5f6368; font-weight:600; }

/* ── Detail card ── */
.dcard { background:#fff; border-radius:12px; border:1px solid #e8eaed;
         overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.05); margin-top:12px; }
.dcard-hdr {
  background:#f8f9fa; padding:14px 22px;
  display:flex; align-items:center; justify-content:space-between;
  border-bottom:1px solid #e8eaed;
  font-size:14px; font-weight:600; color:#202124;
}
.id-chip {
  font-family:'Courier New',monospace; font-size:13px; font-weight:700;
  color:#1a56db; background:#e8f0fe; padding:4px 10px; border-radius:6px;
}
.dgrid { display:grid; grid-template-columns:150px 1fr; }
.dk {
  padding:12px 22px; font-size:13px; font-weight:600; color:#5f6368;
  border-bottom:1px solid #f1f3f4; background:#fafafa;
}
.dv {
  padding:12px 22px; font-size:14px; color:#202124;
  border-bottom:1px solid #f1f3f4;
}
.dlast .dk, .dlast .dv { border-bottom:none; }

div[data-testid="stAlert"] { border-radius:8px !important; }
hr { border-color:#e8eaed !important; margin:24px 0 !important; }

/* ── Bottom padding so page is scrollable past last element ── */
.stTabs [data-baseweb="tab-panel"] > div > div:last-child {
  padding-bottom: 80px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Top bar ──────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="topbar-icon">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
         stroke="#7fa8d4" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <rect x="3" y="3" width="18" height="18" rx="2"/>
      <path d="M3 9h18M9 21V9"/>
    </svg>
  </div>
  <div>
    <div class="topbar-title">ระบบแจ้งปัญหาภายในอาคาร</div>
    <div class="topbar-sub">Facility Issue Reporting System</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────
if "reports" not in st.session_state:
    with st.spinner("กำลังโหลดข้อมูล..."):
        st.session_state.reports = load_reports()
for k, v in [("page", 1), ("edit_id", None), ("confirm_delete_id", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

def reload_reports():
    get_gspread_client.clear()
    st.session_state.reports = load_reports()

def badge(status):
    m = {"รอดำเนินการ":("b-wait","รอดำเนินการ"),
         "กำลังดำเนินการ":("b-proc","กำลังดำเนินการ"),
         "เสร็จสิ้น":("b-done","เสร็จสิ้น")}
    cls, lbl = m.get(status, ("b-wait", status))
    return f'<span class="badge {cls}"><span class="dot"></span>{lbl}</span>'

def detail_card(r):
    return f"""
    <div class="dcard">
      <div class="dcard-hdr">
        <span>รายละเอียดการแจ้ง</span>
        <span class="id-chip">{r["ID"]}</span>
      </div>
      <div class="dgrid">
        <div class="dk">👤 ชื่อผู้แจ้ง</div><div class="dv">{r["Name"]}</div>
        <div class="dk">📂 หมวดปัญหา</div><div class="dv">{r["Category"]}</div>
        <div class="dk">📍 สถานที่</div><div class="dv">{r["Location"]}</div>
        <div class="dk">🗒 รายละเอียด</div><div class="dv">{r.get("Detail") or "—"}</div>
        <div class="dk">📅 วัน/เวลา</div><div class="dv">{r["Date"]} เวลา {r["Time"]} น.</div>
        <div class="dk dlast">📌 สถานะ</div>
        <div class="dv dlast">{badge(r["Status"])}</div>
      </div>
    </div>"""

CATS = ["ลิฟต์","ไฟฟ้า","ระบบแอร์","น้ำประปา","ห้องน้ำ","ประตู/หน้าต่าง",
        "ไฟส่องสว่าง","กล้องวงจรปิด","อินเทอร์เน็ต","ที่จอดรถ","ความสะอาด","อื่นๆ"]
STATUSES = ["รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"]

# ── Tabs ─────────────────────────────────────────────────────
t1, t2, t3 = st.tabs(["✏️  แจ้งปัญหา", "🔍  ติดตามสถานะ", "🛡️  Admin"])

# ═══════════════════════════════════════════════════════════
# TAB 1 — แจ้งปัญหา
# ═══════════════════════════════════════════════════════════
with t1:
    _, col, _ = st.columns([1, 5, 1])
    with col:
        st.markdown("### แจ้งปัญหา")
        st.caption("กรอกข้อมูลเพื่อแจ้งปัญหาภายในอาคาร ทีมงานจะดำเนินการโดยเร็ว")
        st.markdown("<br>", unsafe_allow_html=True)

        # Card 1
        st.markdown('<div class="scard"><div class="scard-title">👤 ข้อมูลผู้แจ้ง</div>',
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: name  = st.text_input("ชื่อ-นามสกุล *", placeholder="กรอกชื่อ-นามสกุล")
        with c2: phone = st.text_input("เบอร์โทรศัพท์ *", placeholder="08X-XXX-XXXX")
        st.markdown("</div>", unsafe_allow_html=True)

        # Card 2
        st.markdown('<div class="scard"><div class="scard-title">📋 รายละเอียดปัญหา</div>',
                    unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3: category = st.selectbox("หมวดหมู่ปัญหา", CATS)
        with c4: location = st.text_input("สถานที่ *", placeholder="เช่น อาคาร A ชั้น 3")
        detail = st.text_area("รายละเอียด", height=100,
                               placeholder="อธิบายปัญหาที่พบ เช่น อาการ วิธีสังเกต ...")
        st.markdown("</div>", unsafe_allow_html=True)

        # Card 3
        st.markdown('<div class="scard"><div class="scard-title">🖼️ แนบรูปภาพ <span style="font-size:12px;font-weight:400;color:#9aa0a6;">(ไม่บังคับ)</span></div>',
                    unsafe_allow_html=True)
        image = st.file_uploader("อัปโหลดรูป", type=["jpg","jpeg","png","gif"],
                                  label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

        confirmed = st.checkbox("ฉันยืนยันว่าข้อมูลข้างต้นถูกต้องและเป็นความจริง")
        st.markdown("<br>", unsafe_allow_html=True)

        sb1, sb2, sb3 = st.columns([2, 3, 2])
        with sb2:
            submit = st.button("📤  ส่งรายงาน", type="primary", use_container_width=True)

        if submit:
            errs = []
            if not name.strip():     errs.append("ชื่อ-นามสกุล")
            if not phone.strip():    errs.append("เบอร์โทร")
            if not location.strip(): errs.append("สถานที่")
            if not confirmed:        errs.append("การยืนยัน")
            if errs:
                st.error(f"กรุณากรอก: **{', '.join(errs)}**")
            else:
                rid = "RP-" + str(random.randint(100000, 999999))
                img_url, img_name = "", ""
                if image:
                    with st.spinner("กำลังอัปโหลดรูป..."):
                        img_url  = upload_image(image.read(), image.name)
                        img_name = image.name
                rec = {"ID":rid,"Name":name.strip(),"Phone":phone.strip(),
                       "Category":category,"Location":location.strip(),
                       "Detail":detail,"Status":"รอดำเนินการ",
                       "Date":datetime.now().strftime("%d/%m/%Y"),
                       "Time":datetime.now().strftime("%H:%M"),
                       "Month":datetime.now().strftime("%B %Y"),
                       "ImageUrl":img_url,"ImageName":img_name}
                with st.spinner("กำลังบันทึก..."):
                    add_report(rec)
                    reload_reports()

                components.html(f"""
                <style>
                  @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@500;700&display=swap');
                  *{{margin:0;padding:0;box-sizing:border-box;}}
                  body{{font-family:'Sarabun',sans-serif;background:transparent;padding:2px 0;}}
                  .box{{
                    background:#ecfdf5;border:1px solid #6ee7b7;border-radius:12px;
                    padding:18px 22px;display:flex;align-items:center;gap:16px;
                  }}
                  .ico{{font-size:24px;}}
                  .txt{{flex:1;}}
                  .txt .top{{font-size:14px;color:#065f46;font-weight:600;}}
                  .txt .sub{{font-size:12px;color:#6b9e80;margin-top:2px;}}
                  .chip{{
                    font-family:'Courier New',monospace;font-size:16px;font-weight:700;
                    color:#065f46;background:#d1fae5;border:1px solid #a7f3d0;
                    border-radius:8px;padding:8px 18px;cursor:pointer;
                    transition:all .15s;text-align:center;white-space:nowrap;
                  }}
                  .chip:hover{{background:#a7f3d0;}}
                  .sub2{{font-size:11px;color:#6b9e80;text-align:center;margin-top:4px;}}
                </style>
                <div class="box">
                  <div class="ico">✅</div>
                  <div class="txt">
                    <div class="top">ส่งรายงานสำเร็จ!</div>
                    <div class="sub">เก็บรหัสนี้ไว้ติดตามสถานะ</div>
                  </div>
                  <div>
                    <div class="chip" onclick="
                      navigator.clipboard.writeText('{rid}');
                      this.textContent='✓ คัดลอกแล้ว';
                      var t=this;setTimeout(()=>t.textContent='{rid}',2000);">{rid}</div>
                    <div class="sub2">คลิกเพื่อคัดลอก</div>
                  </div>
                </div>
                """, height=85)

# ═══════════════════════════════════════════════════════════
# TAB 2 — ติดตามสถานะ
# ═══════════════════════════════════════════════════════════
with t2:
    _, col, _ = st.columns([1, 5, 1])
    with col:
        st.markdown("### ติดตามสถานะ")
        st.caption("กรอกรหัสที่ได้รับเพื่อตรวจสอบสถานะการดำเนินการ")
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="scard"><div class="scard-title">🔍 ค้นหาด้วยรหัส</div>',
                    unsafe_allow_html=True)
        cx, cy = st.columns([5, 1], vertical_alignment="bottom")
        with cx:
            tid = st.text_input("รหัส", placeholder="RP-XXXXXX",
                                 label_visibility="collapsed")
        with cy:
            go = st.button("ค้นหา", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if go:
            found = next((r for r in st.session_state.reports
                          if r["ID"] == tid.strip()), None)
            if found:
                st.markdown(detail_card(found), unsafe_allow_html=True)
                if found.get("ImageUrl"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.image(found["ImageUrl"], caption=found.get("ImageName",""), width=340)
            else:
                st.error("❌ ไม่พบรหัสนี้ในระบบ กรุณาตรวจสอบอีกครั้ง")

# ═══════════════════════════════════════════════════════════
# TAB 3 — Admin
# ═══════════════════════════════════════════════════════════
with t3:
    _, col, _ = st.columns([1, 7, 1])
    with col:
        st.markdown("### Admin")
        st.caption("เข้าสู่ระบบเพื่อจัดการรายงานปัญหาทั้งหมด")
        st.markdown("<br>", unsafe_allow_html=True)

        # Login
        _a, mid, _b = st.columns([1, 2, 1])
        with mid:
            st.markdown("""
            <div class="scard" style="margin-bottom:0;">
              <div class="scard-title">🔒 เข้าสู่ระบบ Admin</div>
            </div>""", unsafe_allow_html=True)
            pwd = st.text_input("รหัสผ่าน", type="password",
                                 placeholder="กรอกรหัสผ่าน",
                                 label_visibility="collapsed")
            st.button("เข้าสู่ระบบ", type="primary",
                      use_container_width=True, key="do_login")

        if pwd != st.secrets["admin"]["password"]:
            if pwd:
                st.error("รหัสผ่านไม่ถูกต้อง")
            else:
                st.info("🔒 กรุณาใส่รหัสผ่านเพื่อเข้าใช้งาน")
            st.stop()

        # Header
        hc1, hc2 = st.columns([6, 1])
        with hc1: st.success("✅ เข้าสู่ระบบสำเร็จ")
        with hc2:
            if st.button("🔄 รีโหลด", use_container_width=True):
                reload_reports(); st.rerun()

        df = pd.DataFrame(st.session_state.reports)
        if df.empty:
            st.info("ยังไม่มีข้อมูล")
            st.stop()

        # Stats
        total   = len(df)
        wait    = (df["Status"] == "รอดำเนินการ").sum()
        process = (df["Status"] == "กำลังดำเนินการ").sum()
        done    = (df["Status"] == "เสร็จสิ้น").sum()

        st.markdown(f"""
        <div class="stat-grid">
          <div class="stat-box s-blue">
            <div class="stat-lbl">ทั้งหมด</div>
            <div class="stat-val">{total}</div>
          </div>
          <div class="stat-box s-amber">
            <div class="stat-lbl">รอดำเนินการ</div>
            <div class="stat-val">{wait}</div>
          </div>
          <div class="stat-box s-indigo">
            <div class="stat-lbl">กำลังดำเนินการ</div>
            <div class="stat-val">{process}</div>
          </div>
          <div class="stat-box s-green">
            <div class="stat-lbl">เสร็จสิ้น</div>
            <div class="stat-val">{done}</div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Filter
        st.markdown('<div class="scard" style="padding:16px 20px;margin-bottom:16px;">',
                    unsafe_allow_html=True)
        f1, f2, f3 = st.columns([3, 2, 2])
        with f1: srch = st.text_input("ค้นหา ID", placeholder="RP-XXXXXX", label_visibility="collapsed")
        with f2: mon  = st.selectbox("เดือน", ["ทั้งหมด"] + df["Month"].unique().tolist(), label_visibility="collapsed")
        with f3: sf   = st.selectbox("สถานะ", ["ทั้งหมด"]+STATUSES, label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

        fdf = df.copy()
        if srch: fdf = fdf[fdf["ID"].str.contains(srch, case=False)]
        if mon  != "ทั้งหมด": fdf = fdf[fdf["Month"] == mon]
        if sf   != "ทั้งหมด": fdf = fdf[fdf["Status"] == sf]

        # Table
        PER = 10
        n   = len(fdf)
        if n == 0:
            st.info("ไม่พบข้อมูลที่ตรงกับเงื่อนไข")
        else:
            pages = max(1, (n - 1) // PER + 1)
            if st.session_state.page > pages: st.session_state.page = 1
            chunk = fdf.iloc[(st.session_state.page-1)*PER : st.session_state.page*PER]

            rows = ""
            for _, r in chunk.iterrows():
                img = (f'<a href="{r["ImageUrl"]}" target="_blank" style="color:#1a56db;font-size:12.5px;">{r["ImageName"]}</a>'
                       if r.get("ImageUrl") else '<span style="color:#dadce0;">—</span>')
                rows += (f'<tr><td><span class="id-tag">{r["ID"]}</span></td>'
                         f'<td>{r["Name"]}</td>'
                         f'<td style="color:#5f6368;font-size:13px;">{r["Phone"]}</td>'
                         f'<td>{r["Category"]}</td>'
                         f'<td style="font-size:13px;">{r["Location"]}</td>'
                         f'<td style="font-size:12.5px;color:#5f6368;">{r["Date"]}</td>'
                         f'<td style="font-size:12.5px;color:#5f6368;">{r["Time"]}</td>'
                         f'<td>{badge(r["Status"])}</td>'
                         f'<td>{img}</td></tr>')

            st.markdown(f"""
            <div class="tbl"><table>
              <thead><tr>
                <th>ID</th><th>ชื่อ</th><th>เบอร์</th><th>หมวด</th>
                <th>สถานที่</th><th>วันที่</th><th>เวลา</th><th>สถานะ</th><th>รูป</th>
              </tr></thead>
              <tbody>{rows}</tbody>
            </table></div>""", unsafe_allow_html=True)

            p1, p2, p3 = st.columns([1, 3, 1])
            with p1:
                if st.button("◀ ก่อนหน้า", disabled=st.session_state.page<=1,
                             use_container_width=True):
                    st.session_state.page -= 1; st.rerun()
            with p2:
                st.markdown(
                    f"<div style='text-align:center;padding:10px 0;font-size:13px;color:#5f6368;'>"
                    f"หน้า <b style='color:#202124'>{st.session_state.page}</b> / "
                    f"<b style='color:#202124'>{pages}</b> · {n} รายการ</div>",
                    unsafe_allow_html=True)
            with p3:
                if st.button("ถัดไป ▶", disabled=st.session_state.page>=pages,
                             use_container_width=True):
                    st.session_state.page += 1; st.rerun()

        st.divider()

        # Update status
        st.markdown('<div class="scard"><div class="scard-title">⚡ เปลี่ยนสถานะ</div>',
                    unsafe_allow_html=True)
        u1, u2, u3 = st.columns([2, 2, 1], vertical_alignment="bottom")
        with u1:
            sel_id = st.selectbox("ID", df["ID"], label_visibility="collapsed")
        with u2:
            cur = next((r["Status"] for r in st.session_state.reports
                        if r["ID"] == sel_id), STATUSES[0])
            new_s = st.selectbox("สถานะ", STATUSES, index=STATUSES.index(cur),
                                  label_visibility="collapsed")
        with u3:
            if st.button("บันทึก", type="primary", use_container_width=True):
                with st.spinner("กำลังอัปเดต..."):
                    update_report(sel_id, {"Status": new_s}); reload_reports()
                st.success(f"✅ อัปเดต **{sel_id}** → {new_s}"); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        # View / Edit / Delete
        st.markdown('<div class="scard"><div class="scard-title">📄 จัดการรายงาน</div>',
                    unsafe_allow_html=True)
        vid = st.selectbox("เลือกรายการ", df["ID"], key="vsid",
                            label_visibility="collapsed")
        bv, be, bd = st.columns(3)
        with bv: show = st.button("👁 ดูรายละเอียด", use_container_width=True)
        with be:
            if st.button("✏️ แก้ไข", use_container_width=True):
                st.session_state.edit_id = vid
                st.session_state.confirm_delete_id = None
        with bd:
            if st.button("🗑️ ลบ", use_container_width=True, type="primary"):
                st.session_state.confirm_delete_id = vid
                st.session_state.edit_id = None

        # Confirm delete
        if st.session_state.confirm_delete_id == vid:
            st.warning(f"⚠️ ยืนยันลบ **{vid}** ? ไม่สามารถกู้คืนได้")
            d1, d2 = st.columns(2)
            with d1:
                if st.button("✅ ยืนยัน", use_container_width=True, type="primary"):
                    with st.spinner("กำลังลบ..."):
                        delete_report(vid); reload_reports()
                    st.session_state.confirm_delete_id = None
                    st.success("ลบเรียบร้อย"); st.rerun()
            with d2:
                if st.button("ยกเลิก", use_container_width=True):
                    st.session_state.confirm_delete_id = None; st.rerun()

        # Edit form
        elif st.session_state.edit_id == vid:
            rec = next((r for r in st.session_state.reports if r["ID"] == vid), None)
            if rec:
                st.markdown("---")
                st.markdown(f"**✏️ แก้ไข: {vid}**")
                e1, e2 = st.columns(2)
                with e1:
                    en = st.text_input("ชื่อ-นามสกุล", value=rec["Name"],     key="en")
                    ep = st.text_input("เบอร์โทร",     value=rec["Phone"],    key="ep")
                    el = st.text_input("สถานที่",       value=rec["Location"], key="el")
                with e2:
                    ec = st.selectbox("หมวดหมู่", CATS,
                                      index=CATS.index(rec["Category"]) if rec["Category"] in CATS else 0,
                                      key="ec")
                    es = st.selectbox("สถานะ", STATUSES,
                                      index=STATUSES.index(rec["Status"]), key="es")
                ed = st.text_area("รายละเอียด", value=rec["Detail"], key="ed")
                s1, s2 = st.columns(2)
                with s1:
                    if st.button("💾 บันทึก", use_container_width=True, type="primary"):
                        with st.spinner("บันทึก..."):
                            update_report(vid, {"Name":en.strip(),"Phone":ep.strip(),
                                                "Location":el.strip(),"Category":ec,
                                                "Status":es,"Detail":ed})
                            reload_reports()
                        st.session_state.edit_id = None
                        st.success(f"✅ บันทึก {vid} สำเร็จ"); st.rerun()
                with s2:
                    if st.button("ยกเลิก", use_container_width=True, key="ce"):
                        st.session_state.edit_id = None; st.rerun()

        # View detail
        elif show:
            rec = next((r for r in st.session_state.reports if r["ID"] == vid), None)
            if rec:
                st.markdown(detail_card(rec), unsafe_allow_html=True)
                if rec.get("ImageUrl"):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.image(rec["ImageUrl"], caption=rec.get("ImageName",""), width=380)
                else:
                    st.caption("ไม่มีรูปภาพ")

        st.markdown("</div>", unsafe_allow_html=True)
