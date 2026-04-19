# ============================================================
# TAB 3: Admin
# ============================================================
with tab_admin:
    _l, col, _r = st.columns([1, 6, 1])
    with col:
        st.markdown("""
        <div class="sec-hdr">
          <h2>Admin</h2>
          <p>เข้าสู่ระบบเพื่อจัดการรายงานปัญหาทั้งหมด</p>
        </div>""", unsafe_allow_html=True)

        # Login box
        _ll, mid, _rr = st.columns([1, 2, 1])
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
        f1, f2, f3 = st.columns([3, 2, 2])
        with f1: search = st.text_input("🔎 ค้นหา ID", placeholder="RP-XXXXXX", label_visibility="collapsed")
        with f2: month  = st.selectbox("📅 เดือน", ["ทั้งหมด"] + df["Month"].unique().tolist(), label_visibility="collapsed")
        with f3: sf     = st.selectbox("📌 สถานะ", ["ทั้งหมด","รอดำเนินการ","กำลังดำเนินการ","เสร็จสิ้น"], label_visibility="collapsed")

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

            p1, p2, p3 = st.columns([1, 3, 1])
            with p1:
                if st.button("◀ ก่อนหน้า", disabled=st.session_state.page <= 1,
                             use_container_width=True):
                    st.session_state.page -= 1
                    st.rerun()
            with p2:
                st.markdown(
                    f"<div style='text-align:center;padding:10px 0;font-size:13px;color:#6b7280;'>"
                    f"หน้า <b style='color:#111827'>{st.session_state.page}</b> / "
                    f"<b style='color:#111827'>{total_pages}</b> · {total_rows} รายการ</div>",
                    unsafe_allow_html=True)
            with p3:
                if st.button("ถัดไป ▶", disabled=st.session_state.page >= total_pages,
                             use_container_width=True):
                    st.session_state.page += 1
                    st.rerun()

        st.divider()

        # ── Update Status ──
        st.markdown('<div class="card"><div class="adm-title">⚡ เปลี่ยนสถานะ</div>', unsafe_allow_html=True)
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
            st.markdown("<div style='padding-top:24px'>", unsafe_allow_html=True)
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
        st.markdown('<div class="card"><div class="adm-title">📄 ดูรายละเอียด / แก้ไข / ลบรายงาน</div>', unsafe_allow_html=True)
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
