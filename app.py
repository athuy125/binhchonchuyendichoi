import datetime
import hashlib
import html
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Kế Hoạch Đội - Quản Lý Chuyến Đi", page_icon="⛺", layout="centered")

BIN_ID = "6af5b874ffd5d16053bc0858"
MASTER_KEY = "$2a$10$EpLPTXlcBTH5/mkxVMBLI.ZSv26QzgFaygkYFHZOa4V7OoVtsot12"

API_URL = "/".join(["https:/", "api.jsonbin.io", "v3", "b", BIN_ID])
HEADERS = {"Content-Type": "application/json", "X-Master-Key": MASTER_KEY}

CSS_STYLE = """
<style>
.stApp { background-color: #0b1120; color: #f8fafc; }
.hero-banner { background: linear-gradient(135deg, #059669 0%, #2563eb 100%); border-radius: 16px; padding: 22px; margin-bottom: 16px; color: #ffffff; box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4); }
.notice-board { background: linear-gradient(145deg, #1e293b, #0f172a); border: 1px solid #f59e0b; border-left: 6px solid #f59e0b; border-radius: 14px; padding: 18px 20px; margin-bottom: 18px; box-shadow: 0 6px 18px rgba(245, 158, 11, 0.18); }
.notice-title { color: #fbbf24; font-size: 14px; font-weight: 800; letter-spacing: 0.5px; margin-bottom: 8px; text-transform: uppercase; }
.notice-body { color: #f8fafc; font-size: 16px; line-height: 1.6; white-space: pre-line; }
.trip-card { background: linear-gradient(145deg, #1e293b, #0f172a); border: 1px solid #3b82f6; border-radius: 14px; padding: 20px; margin-bottom: 12px; }
.vote-badge { display: inline-block; background-color: #064e3b; color: #34d399; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 700; margin-bottom: 8px; }
.member-card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 14px 18px; margin-bottom: 10px; }
div.stButton > button { border-radius: 10px; font-weight: 600; }
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

def now_vn() -> datetime.datetime:
    return datetime.datetime.utcnow() + datetime.timedelta(hours=7)

def make_hash(text: str) -> str:
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()

def add_log(data_dict: dict, msg: str, is_important: bool = False):
    logs = data_dict.get("notifications", [])
    ts = now_vn().strftime("%H:%M %d/%m/%Y")
    item_id = f"{now_vn().timestamp()}_{len(logs)}"
    logs.insert(0, {"id": item_id, "time": ts, "msg": msg, "important": is_important})
    data_dict["notifications"] = logs[:40]

def trigger_browser_push(notif_item: dict):
    if not notif_item:
        return
    nid = notif_item.get("id", "")
    if st.session_state.get("last_pushed_id") == nid:
        return
    st.session_state.last_pushed_id = nid
    safe_text = notif_item.get("msg", "").replace('"', '\\"').replace("\n", " ")
    js_code = f"""
    <script>
    if ("Notification" in window) {{
        if (Notification.permission === "granted") {{
            new Notification("⛺ Thông báo từ Đội", {{ body: "{safe_text}" }});
        }} else if (Notification.permission !== "denied") {{
            Notification.requestPermission().then(function(p) {{
                if (p === "granted") {{
                    new Notification("⛺ Thông báo từ Đội", {{ body: "{safe_text}" }});
                }}
            }});
        }}
    }}
    </script>
    """
    components.html(js_code, height=0)

@st.cache_data(ttl=10, show_spinner=False)
def load_cloud() -> dict:
    default = {"users": {}, "trips": {}, "notifications": []}
    try:
        latest_url = "/".join([API_URL, "latest"])
        r = requests.get(latest_url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            res_json = r.json()
            record = res_json.get("record", res_json)
            if isinstance(record, dict):
                default["users"] = record.get("users", {})
                default["notifications"] = record.get("notifications", [])
                trips = record.get("trips", {})
                if not trips:
                    old_locs = record.get("locations", [])
                    old_reqs = record.get("requirements", [])
                    trips = {
                        "Chuyến đi chơi 1 (24/11)": {
                            "desc": "Ngày 24/11 anh em nghỉ nguyên ngày để đi cắm trại kết hợp Vòng 2 sát hạch nhân sự mới.",
                            "locations": old_locs,
                            "requirements": old_reqs,
                            "vote_deadline": "",
                            "deadline_notified": False,
                        }
                    }
                default["trips"] = trips
    except Exception as e:
        st.warning(f"Đang kết nối lại máy chủ: {e}")
    return default

def save_cloud(data: dict) -> bool:
    try:
        r = requests.put(API_URL, json=data, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            load_cloud.clear()
            return True
        st.error(f"Lỗi lưu dữ liệu (Mã {r.status_code}): {r.text}")
        return False
    except Exception as e:
        st.error(f"Lỗi mạng: {e}")
        return False

if "user" not in st.session_state:
    st.session_state.user = None
if "selected_trip" not in st.session_state:
    st.session_state.selected_trip = None

db = load_cloud()
if st.session_state.user is None:
    AUTH_HTML = '<div class="hero-banner" style="text-align: center;"><h2 style="margin:0;">⛺ CỔNG THÀNH VIÊN ĐỘI</h2><p style="margin:8px 0 0 0; opacity: 0.9;">Đăng ký tài khoản mới (lần đầu) hoặc đăng nhập để tham gia các chuyến đi của đội</p></div>'
    st.markdown(AUTH_HTML, unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 Đăng Nhập", "📝 Đăng Ký Lần Đầu"])

    with tab1:
        with st.form("login_box"):
            name = st.text_input("Tên của bạn", placeholder="Nhập tên đã đăng ký...").strip()
            pwd = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu...")
            if st.form_submit_button("🚀 Vào Hệ Thống", use_container_width=True):
                if not name or not pwd:
                    st.warning("Vui lòng nhập đủ tên và mật khẩu!")
                else:
                    load_cloud.clear()
                    fresh_db = load_cloud()
                    if name not in fresh_db["users"]:
                        st.error("Tên này chưa đăng ký! Hãy chuyển sang tab Đăng Ký Lần Đầu.")
                    elif fresh_db["users"][name] != make_hash(pwd):
                        st.error("Mật khẩu không đúng!")
                    else:
                        st.session_state.user = name
                        st.rerun()

    with tab2:
        with st.form("reg_box"):
            r_name = st.text_input("Tên hiển thị của bạn", placeholder="Ví dụ: Huy Đỗ...").strip()
            r_pwd = st.text_input("Tạo mật khẩu", type="password")
            r_pwd2 = st.text_input("Nhập lại mật khẩu", type="password")
            if st.form_submit_button("✅ Đăng Ký & Lưu Online", use_container_width=True):
                if not r_name or not r_pwd:
                    st.warning("Không được để trống tên hoặc mật khẩu!")
                elif r_pwd != r_pwd2:
                    st.error("Mật khẩu xác nhận không khớp!")
                else:
                    load_cloud.clear()
                    fresh_db = load_cloud()
                    if r_name in fresh_db["users"]:
                        st.error("Tên này đã có người đăng ký rồi!")
                    else:
                        fresh_db["users"][r_name] = make_hash(r_pwd)
                        add_log(fresh_db, f"🎉 Thành viên mới **{r_name}** vừa đăng ký gia nhập đội!", True)
                        if save_cloud(fresh_db):
                            st.session_state.user = r_name
                            st.success("Đăng ký thành công!")
                            st.rerun()

    st.stop()

me = st.session_state.user
is_admin = (me.strip().lower() == "athuy125")

need_deadline_save = False
for t_key, t_val in db["trips"].items():
    dl_str = t_val.get("vote_deadline", "")
    if dl_str and not t_val.get("deadline_notified", False):
        try:
            dl_dt = datetime.datetime.strptime(dl_str, "%Y-%m-%d %H:%M")
            if now_vn() >= dl_dt:
                locs_check = t_val.get("locations", [])
                if locs_check:
                    top_loc = max(locs_check, key=lambda x: len(x.get("voters", [])))
                    win_msg = f"⏰ Đã hết hạn bình chọn cho **{t_key}**! Địa điểm dẫn đầu: **{top_loc['name']}** ({len(top_loc.get('voters', []))} phiếu)."
                else:
                    win_msg = f"⏰ Đã hết thời gian bình chọn địa điểm cho **{t_key}**!"
                add_log(db, win_msg, True)
                db["trips"][t_key]["deadline_notified"] = True
                need_deadline_save = True
        except Exception:
            pass

if need_deadline_save:
    save_cloud(db)
    db = load_cloud()

all_notifs = db.get("notifications", [])
if all_notifs:
    trigger_browser_push(all_notifs[0])


col_a, col_b, col_c = st.columns([3.5, 1.3, 1.2])
with col_a:
    st.success(f"🟢 Xin chào **{me}**!")
with col_b:
    if st.button("🔄 Làm mới", use_container_width=True):
        load_cloud.clear()
        st.rerun()
with col_c:
    if st.button("Thoát", use_container_width=True):
        st.session_state.user = None
        st.session_state.selected_trip = None
        st.rerun()

with st.expander("🔔 Bảng Thông Báo & Hoạt Động Mới Nhất Của Đội", expanded=True):
    components.html(
        """
        <button onclick="Notification.requestPermission().then(p => alert(p === 'granted' ? 'Đã bật thông báo về máy thành công!' : 'Trình duyệt đang chặn thông báo, hãy bật trong cài đặt trang web.'))"
        style="background:#2563eb; color:white; border:none; padding:6px 14px; border-radius:8px; font-weight:600; cursor:pointer; font-size:13px;">
        📲 Bật thông báo đẩy về máy này
        </button>
        """,
        height=38,
    )

    if is_admin:
        with st.form("admin_broadcast_form", clear_on_submit=True):
            b_msg = st.text_input("Soạn thông báo gửi tới tất cả thành viên", placeholder="Nhập nội dung thông báo chung...")
            if st.form_submit_button("📢 Gửi Thông Báo Cho Cả Đội", use_container_width=True):
                if b_msg.strip():
                    load_cloud.clear()
                    current_db = load_cloud()
                    add_log(current_db, f"📢 **THÔNG BÁO CHUNG:** {b_msg.strip()}", True)
                    if save_cloud(current_db):
                        st.success("Đã gửi thông báo đến toàn bộ thành viên!")
                        st.rerun()
                else:
                    st.warning("Vui lòng nhập nội dung thông báo!")

    if not all_notifs:
        st.caption("Chưa có hoạt động nào được ghi nhận.")
    else:
        for n_item in all_notifs[:6]:
            st.markdown(f"- `[{n_item.get('time', '')}]` {n_item.get('msg', '')}")
if st.session_state.selected_trip is None or st.session_state.selected_trip not in db["trips"]:
    LOBBY_HTML = '<div class="hero-banner"><h2 style="margin:0;">🗺️ DANH SÁCH CHUYẾN ĐI CỦA ĐỘI</h2><p style="margin:8px 0 0 0; font-size:15px;">Chọn một chuyến đi bên dưới để xem chi tiết, bình chọn địa điểm và phân công đồ dùng.</p></div>'
    st.markdown(LOBBY_HTML, unsafe_allow_html=True)

    if is_admin:
        with st.expander("➕ Tạo Chuyến Đi Mới", expanded=False):
            with st.form("create_trip_form", clear_on_submit=True):
                new_trip_name = st.text_input("Tên chuyến đi mới", placeholder="Ví dụ: Chuyến đi chơi 2 - Vũng Tàu...")
                new_trip_desc = st.text_area("Mô tả / Thời gian dự kiến (Chỉ hiện khi bấm vào chuyến đi)", placeholder="Ví dụ: Đi 2 ngày 1 đêm cuối tháng...")
                if st.form_submit_button("➕ Tạo Chuyến Đi", use_container_width=True):
                    t_clean = new_trip_name.strip()
                    if not t_clean:
                        st.warning("Vui lòng nhập tên chuyến đi!")
                    else:
                        load_cloud.clear()
                        current_db = load_cloud()
                        if t_clean in current_db["trips"]:
                            st.error("Tên chuyến đi này đã tồn tại!")
                        else:
                            current_db["trips"][t_clean] = {
                                "desc": new_trip_desc.strip() or "Kế hoạch dã ngoại mới của toàn đội.",
                                "locations": [],
                                "requirements": [],
                                "vote_deadline": "",
                                "deadline_notified": False,
                            }
                            add_log(current_db, f"🗺️ Chuyến đi mới **{t_clean}** vừa được tạo!", True)
                            if save_cloud(current_db):
                                st.success(f"Đã tạo '{t_clean}'!")
                                st.rerun()

    trip_names = list(db["trips"].keys())
    if len(trip_names) == 0:
        st.info("Chưa có chuyến đi nào được tạo.")
    else:
        for idx, t_name in enumerate(trip_names):
            t_info = db["trips"][t_name]
            n_locs = len(t_info.get("locations", []))
            n_reqs = len(t_info.get("requirements", []))
            card_t = f'<div class="trip-card"><h3 style="margin:0 0 8px 0; color:#38bdf8;">⛺ {html.escape(t_name)}</h3><span class="vote-badge">📍 {n_locs} địa điểm &nbsp;|&nbsp; 🎒 {n_reqs} món đồ</span></div>'
            st.markdown(card_t, unsafe_allow_html=True)

            if is_admin and len(trip_names) > 1:
                b_enter, b_del = st.columns([4, 1.2])
                with b_enter:
                    if st.button(f"🚀 Vào {t_name}", key=f"enter_trip_{idx}", use_container_width=True):
                        st.session_state.selected_trip = t_name
                        st.rerun()
                with b_del:
                    if st.button("🗑️ Xóa", key=f"del_trip_{idx}", use_container_width=True):
                        load_cloud.clear()
                        current_db = load_cloud()
                        if t_name in current_db["trips"]:
                            del current_db["trips"][t_name]
                            add_log(current_db, f"🗑️ Chuyến đi **{t_name}** đã bị xóa khỏi danh sách.")
                            if save_cloud(current_db):
                                st.rerun()
            else:
                if st.button(f"🚀 Vào {t_name}", key=f"enter_trip_{idx}", use_container_width=True):
                    st.session_state.selected_trip = t_name
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

    st.stop()

cur_trip = st.session_state.selected_trip
trip_data = db["trips"][cur_trip]

if st.button("⬅️ Quay lại danh sách chuyến đi", use_container_width=True):
    st.session_state.selected_trip = None
    st.rerun()

MAIN_HTML = f'<div class="hero-banner" style="padding: 18px 22px;"><h2 style="margin:0;">⛺ {html.escape(cur_trip.upper())}</h2></div>'
st.markdown(MAIN_HTML, unsafe_allow_html=True)

raw_desc = trip_data.get("desc", "").strip() or "Chưa có thông tin chi tiết cho chuyến đi này."
safe_desc = html.escape(raw_desc)
NOTICE_HTML = f'<div class="notice-board"><div class="notice-title">📢 THÔNG TIN & MÔ TẢ CHUYẾN ĐI</div><div class="notice-body">{safe_desc}</div></div>'
st.markdown(NOTICE_HTML, unsafe_allow_html=True)

if is_admin:
    with st.expander("✏️ Chỉnh sửa thông tin / mô tả chuyến đi", expanded=False):
        with st.form("edit_trip_desc_form"):
            updated_desc = st.text_area("Nội dung thông báo / lịch trình", value=trip_data.get("desc", ""), height=120)
            if st.form_submit_button("💾 Lưu mô tả", use_container_width=True):
                load_cloud.clear()
                current_db = load_cloud()
                if cur_trip in current_db["trips"]:
                    current_db["trips"][cur_trip]["desc"] = updated_desc.strip()
                    add_log(current_db, f"📝 Thông tin mô tả của **{cur_trip}** vừa được cập nhật.")
                    if save_cloud(current_db):
                        st.success("Đã cập nhật thông tin chuyến đi!")
                        st.rerun()
t_loc, t_req, t_mem = st.tabs(["🗳️ Bình Chọn Địa Điểm", "🎒 Đồ Cần Chuẩn Bị", "👥 Thành Viên"])

with t_loc:
    dl_str = trip_data.get("vote_deadline", "")
    is_voting_closed = False
    if dl_str:
        try:
            dl_dt = datetime.datetime.strptime(dl_str, "%Y-%m-%d %H:%M")
            if now_vn() >= dl_dt:
                is_voting_closed = True
                st.error(f"🔒 **Bình chọn đã kết thúc** vào lúc **{dl_dt.strftime('%H:%M ngày %d/%m/%Y')}**.")
            else:
                st.warning(f"⏳ **Thời hạn bình chọn kết thúc lúc:** {dl_dt.strftime('%H:%M ngày %d/%m/%Y')}")
        except Exception:
            pass

    if is_admin:
        with st.expander("⏰ Cài đặt ngày giờ kết thúc bình chọn", expanded=False):
            with st.form("set_deadline_form"):
                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    sel_date = st.date_input("Chọn ngày kết thúc", value=now_vn().date())
                with d_col2:
                    sel_time = st.time_input("Chọn giờ kết thúc", value=datetime.time(20, 0))
                b_set1, b_set2 = st.columns(2)
                with b_set1:
                    save_dl = st.form_submit_button("✅ Lưu thời hạn", use_container_width=True)
                with b_set2:
                    clear_dl = st.form_submit_button("🔓 Mở lại không giới hạn", use_container_width=True)

                if save_dl:
                    load_cloud.clear()
                    current_db = load_cloud()
                    combined_str = f"{sel_date.strftime('%Y-%m-%d')} {sel_time.strftime('%H:%M')}"
                    current_db["trips"][cur_trip]["vote_deadline"] = combined_str
                    current_db["trips"][cur_trip]["deadline_notified"] = False
                    add_log(current_db, f"⏰ Thời hạn bình chọn **{cur_trip}** được đặt đến **{sel_time.strftime('%H:%M')} ngày {sel_date.strftime('%d/%m/%Y')}**.", True)
                    if save_cloud(current_db):
                        st.rerun()
                if clear_dl:
                    load_cloud.clear()
                    current_db = load_cloud()
                    current_db["trips"][cur_trip]["vote_deadline"] = ""
                    current_db["trips"][cur_trip]["deadline_notified"] = False
                    add_log(current_db, f"🔓 Bình chọn cho **{cur_trip}** đã được mở lại không giới hạn thời gian.")
                    if save_cloud(current_db):
                        st.rerun()

    if not is_voting_closed:
        with st.expander("➕ Đề xuất địa điểm mới"):
            with st.form("add_loc_form", clear_on_submit=True):
                l_name = st.text_input("Tên địa điểm", placeholder="Ví dụ: Hồ Trị An...")
                l_desc = st.text_input("Mô tả / Khoảng cách", placeholder="Đường đẹp, cách trung tâm 40km...")
                if st.form_submit_button("Thêm Địa Điểm", use_container_width=True):
                    if l_name.strip():
                        load_cloud.clear()
                        current_db = load_cloud()
                        new_loc = {"name": l_name.strip(), "desc": l_desc.strip() or "Chưa có mô tả", "voters": [me]}
                        current_db["trips"][cur_trip]["locations"].append(new_loc)
                        add_log(current_db, f"📍 **{me}** đã đề xuất địa điểm mới **{l_name.strip()}** trong *{cur_trip}*.")
                        if save_cloud(current_db):
                            st.rerun()
                    else:
                        st.warning("Vui lòng nhập tên địa điểm!")

    locs = trip_data.get("locations", [])
    if len(locs) == 0:
        st.info("Chưa có địa điểm nào được đề xuất cho chuyến đi này.")

    for i, loc in enumerate(locs):
        voters = loc.get("voters", [])
        voted = me in voters

        with st.container(border=True):
            st.subheader(f"📍 {loc['name']}")
            st.write(loc.get("desc", ""))
            st.markdown(f'<span class="vote-badge">🔥 {len(voters)} phiếu bầu</span>', unsafe_allow_html=True)
            st.caption(f"👤 Đã vote: {', '.join(voters) if voters else 'Chưa có ai'}")

            c1, c2 = st.columns([4, 1.2])
            with c1:
                if is_voting_closed:
                    st.button("🔒 Đã hết hạn bình chọn", key=f"closed_{i}", disabled=True, use_container_width=True)
                else:
                    btn_text = "✅ Đã Vote (Bấm để hủy)" if voted else "👍 Bầu Chọn"
                    if st.button(btn_text, key=f"vote_{i}", use_container_width=True):
                        load_cloud.clear()
                        current_db = load_cloud()
                        t_locs = current_db["trips"][cur_trip]["locations"]
                        if i < len(t_locs):
                            cur_voters = t_locs[i].get("voters", [])
                            if me in cur_voters:
                                cur_voters.remove(me)
                                add_log(current_db, f"↩️ **{me}** đã hủy bình chọn cho **{t_locs[i]['name']}** (*{cur_trip}*).")
                            else:
                                cur_voters.append(me)
                                add_log(current_db, f"👍 **{me}** đã bình chọn cho **{t_locs[i]['name']}** (*{cur_trip}*).")
                            t_locs[i]["voters"] = cur_voters
                            if save_cloud(current_db):
                                st.rerun()
            with c2:
                if st.button("🗑️", key=f"del_loc_{i}", use_container_width=True):
                    load_cloud.clear()
                    current_db = load_cloud()
                    t_locs = current_db["trips"][cur_trip]["locations"]
                    if i < len(t_locs):
                        removed_name = t_locs[i]["name"]
                        t_locs.pop(i)
                        add_log(current_db, f"🗑️ **{me}** đã xóa địa điểm **{removed_name}** (*{cur_trip}*).")
                        if save_cloud(current_db):
                            st.rerun()
with t_req:
    with st.form("add_req_form", clear_on_submit=True):
        t_name = st.text_input("Đồ dùng / Công việc cần lo", placeholder="Ví dụ: 5 thùng nước suối...")
        t_who = st.text_input("Người nhận việc", value=me)
        if st.form_submit_button("➕ Thêm Vào Danh Sách", use_container_width=True):
            if t_name.strip():
                load_cloud.clear()
                current_db = load_cloud()
                assigned_person = t_who.strip() or "Chưa phân công"
                new_req = {"task": t_name.strip(), "assigned": assigned_person, "done": False}
                current_db["trips"][cur_trip]["requirements"].append(new_req)
                add_log(current_db, f"🎒 **{me}** đã thêm đồ cần chuẩn bị: **{t_name.strip()}** (Phụ trách: *{assigned_person}*) trong *{cur_trip}*.")
                if save_cloud(current_db):
                    st.rerun()
            else:
                st.warning("Vui lòng nhập tên đồ dùng!")

    st.divider()
    reqs = trip_data.get("requirements", [])
    if len(reqs) == 0:
        st.info("Chưa có đồ dùng nào trong danh sách của chuyến đi này.")

    for i, req in enumerate(reqs):
        r1, r2 = st.columns([4.5, 1])
        with r1:
            label_text = f"**{req['task']}** — *(Phụ trách: {req['assigned']})*"
            chk = st.checkbox(label_text, value=req.get("done", False), key=f"chk_{i}")
            if chk != req.get("done", False):
                load_cloud.clear()
                current_db = load_cloud()
                t_reqs = current_db["trips"][cur_trip]["requirements"]
                if i < len(t_reqs):
                    t_reqs[i]["done"] = chk
                    status_txt = "đã chuẩn bị xong" if chk else "đang chuẩn bị"
                    add_log(current_db, f"✅ **{me}** đánh dấu món **{t_reqs[i]['task']}** ({status_txt}) trong *{cur_trip}*.")
                    if save_cloud(current_db):
                        st.rerun()
        with r2:
            if st.button("🗑️", key=f"del_req_{i}", use_container_width=True):
                load_cloud.clear()
                current_db = load_cloud()
                t_reqs = current_db["trips"][cur_trip]["requirements"]
                if i < len(t_reqs):
                    del_task = t_reqs[i]["task"]
                    t_reqs.pop(i)
                    add_log(current_db, f"🗑️ **{me}** đã xóa món **{del_task}** khỏi danh sách (*{cur_trip}*).")
                    if save_cloud(current_db):
                        st.rerun()

with t_mem:
    all_members = list(db["users"].keys())
    st.subheader(f"👥 Danh sách thành viên đội ({len(all_members)} người)")

    if is_admin:
        with st.container(border=True):
            st.markdown("⚙️ **Quản lý danh sách thành viên:**")
            deletable_members = [m for m in all_members if m != me]
            if deletable_members:
                c_sel, c_btn = st.columns([3.5, 1.5])
                with c_sel:
                    target_user = st.selectbox("Chọn tên", deletable_members, label_visibility="collapsed")
                with c_btn:
                    if st.button("🗑️ Xóa", key="admin_del_btn", use_container_width=True):
                        load_cloud.clear()
                        current_db = load_cloud()
                        if target_user in current_db["users"]:
                            del current_db["users"][target_user]
                        for tr in current_db["trips"].values():
                            for loc in tr.get("locations", []):
                                if target_user in loc.get("voters", []):
                                    loc["voters"].remove(target_user)
                        add_log(current_db, f"👋 Thành viên **{target_user}** đã rời khỏi danh sách đội.")
                        if save_cloud(current_db):
                            st.success(f"Đã xóa {target_user}!")
                            st.rerun()
            else:
                st.caption("Không có thành viên nào khác để xóa.")

    if len(all_members) == 0:
        st.info("Chưa có thành viên nào đăng ký.")
    else:
        for idx, member_name in enumerate(all_members, start=1):
            voted_places = [loc["name"] for loc in locs if member_name in loc.get("voters", [])]
            vote_status = f"✅ Đã vote: {', '.join(voted_places)}" if voted_places else "⏳ Chưa bình chọn địa điểm"
            assigned_tasks = [req["task"] for req in reqs if req.get("assigned") == member_name]
            task_status = f"🎒 Nhận lo ({len(assigned_tasks)}): {', '.join(assigned_tasks)}" if assigned_tasks else "📋 Chưa nhận đồ dùng"

            card_html = f'<div class="member-card"><div style="font-size: 16px; font-weight: 700; color: #38bdf8;">{idx}. 👤 {member_name}</div><div style="font-size: 13px; color: #cbd5e1; margin-top: 4px;">{vote_status} &nbsp;|&nbsp; {task_status}</div></div>'
            st.markdown(card_html, unsafe_allow_html=True)
