import datetime
import hashlib
import html
import secrets
import time
import extra_streamlit_components as stx
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
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp {
    background-color: #090d16 !important;
    color: #ffffff !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"] {
    background-color: #090d16 !important;
    color: #ffffff !important;
}
h1, h2, h3, h4, h5, h6, p, span, label, li, div, .stMarkdown {
    color: #ffffff !important;
}
input, textarea, select, [data-baseweb="input"] input, [data-baseweb="textarea"] textarea, [data-baseweb="select"] > div {
    background-color: #161f33 !important;
    color: #ffffff !important;
    border: 1px solid #334155 !important;
    -webkit-text-fill-color: #ffffff !important;
}
input::placeholder, textarea::placeholder {
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
}
[data-testid="stExpander"], [data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #111827 !important;
    border-color: #263248 !important;
    color: #ffffff !important;
}
div.stButton > button {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 4px 8px !important;
}
div.stButton > button {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 4px 10px !important;
    white-space: nowrap !important;
}

button[kind="primaryFormSubmit"], [data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #059669 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: none !important;
}
.hero-banner { background: linear-gradient(135deg, #059669 0%, #2563eb 100%); border-radius: 16px; padding: 20px; margin-bottom: 14px; color: #ffffff !important; box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5); }
.notice-board { background: linear-gradient(145deg, #161f33, #0d1322); border: 1px solid #f59e0b; border-left: 6px solid #f59e0b; border-radius: 12px; padding: 14px 18px; margin-bottom: 16px; }
.notice-title { color: #fbbf24 !important; font-size: 13px; font-weight: 800; letter-spacing: 0.6px; margin-bottom: 6px; text-transform: uppercase; }
.notice-body { color: #f8fafc !important; font-size: 15px; line-height: 1.6; white-space: pre-line; }
.trip-card { background: linear-gradient(145deg, #161f33, #0d1322); border: 1px solid #3b82f6; border-radius: 14px; padding: 20px; margin-bottom: 12px; }
.vote-badge { display: inline-block; background-color: #064e3b; color: #34d399 !important; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 700; margin-bottom: 8px; }
.member-card { background-color: #161f33; border: 1px solid #334155; border-radius: 12px; padding: 14px 18px; margin-bottom: 10px; }
.notif-row { background-color: #131b2e; border: 1px solid #263248; border-left: 4px solid #38bdf8; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; }
.notif-row-vip { background-color: #1c1917; border: 1px solid #f59e0b; border-left: 4px solid #f59e0b; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; }
.grid-title { background: linear-gradient(90deg, #1e3a8a, #0f172a); border: 1px solid #3b82f6; border-radius: 10px 10px 0 0; padding: 10px 14px; font-weight: 800; color: #93c5fd !important; font-size: 15px; margin-top: 16px; }
.grid-head { background-color: #1e293b; border-left: 1px solid #334155; border-right: 1px solid #334155; border-bottom: 1px solid #334155; padding: 6px 10px; font-size: 12px; font-weight: 700; color: #94a3b8 !important; text-transform: uppercase; }
.grid-cell { padding: 6px 4px; font-size: 13.5px; color: #ffffff !important; border-bottom: 1px solid #1e293b; }
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)
def now_vn() -> datetime.datetime:
    return datetime.datetime.utcnow() + datetime.timedelta(hours=7)

def make_hash(text: str) -> str:
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()

def send_external_push(data_dict: dict, clean_msg: str):
    cfg = data_dict.get("config", {})
    discord_url = cfg.get("discord_webhook", "").strip()
    tg_token = cfg.get("tg_token", "").strip()
    tg_chat = cfg.get("tg_chat_id", "").strip()
    if discord_url:
        try:
            requests.post(discord_url, json={"content": f"⛺ **THÔNG BÁO ĐỘI:** {clean_msg}"}, timeout=4)
        except Exception:
            pass
    if tg_token and tg_chat:
        try:
            tg_api = f"https://telegram.org{tg_token}/sendMessage"
            requests.post(tg_api, json={"chat_id": tg_chat, "text": f"⛺ THÔNG BÁO ĐỘI:\n{clean_msg}"}, timeout=4)
        except Exception:
            pass

def add_log(data_dict: dict, msg: str, is_important: bool = False):
    logs = data_dict.get("notifications", [])
    ts = now_vn().strftime("%H:%M %d/%m/%Y")
    item_id = f"{now_vn().timestamp()}_{len(logs)}"
    logs.insert(0, {"id": item_id, "time": ts, "msg": msg, "important": is_important})
    data_dict["notifications"] = logs[:40]
    plain_msg = msg.replace("**", "").replace("*", "")
    send_external_push(data_dict, plain_msg)

def trigger_browser_push(notif_item):
    if isinstance(notif_item, list):
        notif_item = notif_item[0] if notif_item else None
    if not isinstance(notif_item, dict):
        return
    nid = notif_item.get("id", "")
    if st.session_state.get("last_pushed_id") == nid:
        return
    st.session_state.last_pushed_id = nid
    safe_text = notif_item.get("msg", "").replace('"', '\\"').replace("\n", " ").replace("**", "")
    js_code = f"""
    <script>
    if ("Notification" in window) {{
        if (Notification.permission === "granted") {{
            new Notification("⛺ Thông báo từ Đội", {{ body: "{safe_text}" }});
        }}
    }}
    </script>
    """
    components.html(js_code, height=0)

@st.cache_data(ttl=10, show_spinner=False)
def load_cloud() -> dict:
    default = {"users": {}, "sessions": {}, "trips": {}, "notifications": [], "config": {}}
    try:
        latest_url = "/".join([API_URL, "latest"])
        r = requests.get(latest_url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            res_json = r.json()
            record = res_json.get("record", res_json)
            if isinstance(record, dict):
                default["users"] = record.get("users", {})
                default["sessions"] = record.get("sessions", {})
                default["notifications"] = record.get("notifications", [])
                default["config"] = record.get("config", {})
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
cookie_manager = stx.CookieManager(key="team_auth_cookie_v4")

if "user" not in st.session_state:
    st.session_state.user = None
if "selected_trip" not in st.session_state:
    st.session_state.selected_trip = None
if "active_token" not in st.session_state:
    st.session_state.active_token = ""

db = load_cloud()

if st.session_state.user is None:
    url_tk = st.query_params.get("token", "")
    ck_tk = cookie_manager.get("team_trip_session_v4")
    found_tk = ck_tk or url_tk

    if found_tk and found_tk in db.get("sessions", {}):
        auto_user = db["sessions"][found_tk]
        if auto_user in db.get("users", {}):
            st.session_state.user = auto_user
            st.session_state.active_token = found_tk
            if st.query_params.get("token", "") != found_tk:
                st.query_params["token"] = found_tk
            if not ck_tk:
                exp_d = datetime.datetime.now() + datetime.timedelta(days=365)
                cookie_manager.set("team_trip_session_v4", found_tk, expires_at=exp_d)
            st.rerun()
if st.session_state.user is None:
    AUTH_HTML = '<div class="hero-banner" style="text-align: center;"><h2 style="margin:0;">⛺ CỔNG THÀNH VIÊN ĐỘI</h2><p style="margin:8px 0 0 0; opacity: 0.9;">Đăng ký tài khoản mới (lần đầu) hoặc đăng nhập để tham gia các chuyến đi của đội</p></div>'
    st.markdown(AUTH_HTML, unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 Đăng Nhập", "📝 Đăng Ký Lần Đầu"])

    with tab1:
        with st.form("login_box"):
            name = st.text_input("Tên của bạn", placeholder="Nhập tên đã đăng ký...").strip()
            pwd = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu...")
            st.caption("🔒 Hệ thống tự động ghi nhớ đăng nhập vĩnh viễn trên thiết bị này sau khi vào.")
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
                        new_tk = secrets.token_hex(16)
                        fresh_db.setdefault("sessions", {})[new_tk] = name
                        save_cloud(fresh_db)
                        exp_date = datetime.datetime.now() + datetime.timedelta(days=365)
                        cookie_manager.set("team_trip_session_v4", new_tk, expires_at=exp_date)
                        st.query_params["token"] = new_tk
                        st.session_state.active_token = new_tk
                        st.session_state.user = name
                        time.sleep(0.8)
                        st.rerun()

    with tab2:
        with st.form("reg_box"):
            r_name = st.text_input("Tên hiển thị của bạn", placeholder="Ví dụ: Huy Đỗ...").strip()
            r_pwd = st.text_input("Tạo mật khẩu", type="password")
            r_pwd2 = st.text_input("Nhập lại mật khẩu", type="password")
            st.caption("🔒 Tài khoản sẽ được lưu trực tuyến và tự động ghi nhớ trên thiết bị này.")
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
                        new_tk = secrets.token_hex(16)
                        fresh_db.setdefault("sessions", {})[new_tk] = r_name
                        exp_date = datetime.datetime.now() + datetime.timedelta(days=365)
                        cookie_manager.set("team_trip_session_v4", new_tk, expires_at=exp_date)
                        add_log(fresh_db, f"🎉 Thành viên mới **{r_name}** vừa đăng ký gia nhập đội!", True)
                        if save_cloud(fresh_db):
                            st.query_params["token"] = new_tk
                            st.session_state.active_token = new_tk
                            st.session_state.user = r_name
                            time.sleep(0.8)
                            st.success("Đăng ký thành công!")
                            st.rerun()

    st.stop()
me = st.session_state.user
is_admin = (me.strip().lower() == "athuy125")

cur_session_tk = st.session_state.get("active_token") or st.query_params.get("token", "") or cookie_manager.get("team_trip_session_v4")
if cur_session_tk:
    if st.query_params.get("token", "") != cur_session_tk:
        st.query_params["token"] = cur_session_tk
    if not st.session_state.get("cookie_refreshed"):
        exp_d = datetime.datetime.now() + datetime.timedelta(days=365)
        cookie_manager.set("team_trip_session_v4", cur_session_tk, expires_at=exp_d)
        st.session_state.cookie_refreshed = True

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
    st.success(f"🟢 Xin chào **{me}**! *(Đã lưu đăng nhập)*")
with col_b:
    if st.button("🔄 Làm mới", use_container_width=True):
        load_cloud.clear()
        st.rerun()
with col_c:
    if st.button("Thoát", use_container_width=True):
        if cur_session_tk:
            load_cloud.clear()
            clean_db = load_cloud()
            if cur_session_tk in clean_db.get("sessions", {}):
                del clean_db["sessions"][cur_session_tk]
                save_cloud(clean_db)
            try:
                cookie_manager.delete("team_trip_session_v4")
            except Exception:
                pass
            time.sleep(0.5)
        st.query_params.clear()
        st.session_state.active_token = ""
        st.session_state.cookie_refreshed = False
        st.session_state.user = None
        st.session_state.selected_trip = None
        st.rerun()

with st.expander("🔔 Bảng Thông Báo & Hoạt Động Mới Nhất Của Đội", expanded=True):
    top_n1, top_n2 = st.columns([3.2, 2.2])
    with top_n1:
        st.caption("📌 Cập nhật mọi hoạt động mới nhất của anh em trong đội")
    with top_n2:
        components.html(
            """
            <div style="text-align:right;">
                <button onclick="Notification.requestPermission().then(p => alert(p === 'granted' ? 'Đã bật thông báo trên máy thành công!' : 'Trình duyệt đang chặn thông báo, hãy bật trong cài đặt trang web.'))"
                style="background:#2563eb; color:white; border:none; padding:6px 12px; border-radius:8px; font-weight:600; cursor:pointer; font-size:12.5px;">
                📲 Bật thông báo máy
                </button>
            </div>
            """,
            height=36,
        )

    if is_admin:
        with st.form("admin_broadcast_form", clear_on_submit=True):
            b_col1, b_col2 = st.columns([4.2, 1.4])
            with b_col1:
                b_msg = st.text_input("Soạn thông báo chung", placeholder="Nhập thông báo gửi tới cả đội...", label_visibility="collapsed")
            with b_col2:
                send_b = st.form_submit_button("📢 Gửi tin", use_container_width=True)
            if send_b:
                if b_msg.strip():
                    load_cloud.clear()
                    current_db = load_cloud()
                    add_log(current_db, f"📢 **THÔNG BÁO CHUNG:** {b_msg.strip()}", True)
                    if save_cloud(current_db):
                        st.success("Đã gửi thông báo đến toàn bộ thành viên!")
                        st.rerun()
                else:
                    st.warning("Vui lòng nhập nội dung thông báo!")

        with st.expander("⚙️ Cài đặt gửi thông báo về điện thoại (Discord / Telegram)", expanded=False):
            with st.form("webhook_cfg_form"):
                cur_cfg = db.get("config", {})
                in_discord = st.text_input("Link Discord Webhook nhóm đội", value=cur_cfg.get("discord_webhook", ""), placeholder="https://discord.com...")
                in_tg_tk = st.text_input("Telegram Bot Token (Tùy chọn)", value=cur_cfg.get("tg_token", ""), placeholder="123456:ABC-DEF...")
                in_tg_id = st.text_input("Telegram Chat ID nhóm đội (Tùy chọn)", value=cur_cfg.get("tg_chat_id", ""), placeholder="-100123456789")
                if st.form_submit_button("💾 Lưu cấu hình thông báo ngoài web", use_container_width=True):
                    load_cloud.clear()
                    current_db = load_cloud()
                    current_db["config"] = {
                        "discord_webhook": in_discord.strip(),
                        "tg_token": in_tg_tk.strip(),
                        "tg_chat_id": in_tg_id.strip(),
                    }
                    if save_cloud(current_db):
                        st.success("Đã lưu cấu hình thông báo tự động!")
                        st.rerun()

    if not all_notifs:
        st.info("Chưa có hoạt động nào được ghi nhận.")
    else:
        for idx_n, n_item in enumerate(all_notifs[:6]):
            is_vip = n_item.get("important", False)
            row_cls = "notif-row-vip" if is_vip else "notif-row"
            time_badge_color = "#fbbf24" if is_vip else "#38bdf8"
            raw_msg = html.escape(n_item.get("msg", "")).replace("**", "")
            card_notif = f'<div class="{row_cls}"><span style="color:{time_badge_color}; font-size:12px; font-weight:700;">🕒 {html.escape(n_item.get("time", ""))}</span><div style="color:#ffffff; font-size:14px; margin-top:3px;">{raw_msg}</div></div>'

            if is_admin:
                col_n1, col_n2 = st.columns([5.2, 0.8])
                with col_n1:
                    st.markdown(card_notif, unsafe_allow_html=True)
                with col_n2:
                    if st.button("🗑️", key=f"del_notif_{idx_n}", use_container_width=True):
                        load_cloud.clear()
                        current_db = load_cloud()
                        cur_list = current_db.get("notifications", [])
                        if idx_n < len(cur_list):
                            cur_list.pop(idx_n)
                            current_db["notifications"] = cur_list
                            if save_cloud(current_db):
                                st.rerun()
            else:
                st.markdown(card_notif, unsafe_allow_html=True)

        if is_admin:
            if st.button("🧹 Xóa tất cả thông báo", key="clear_all_notifs", use_container_width=True):
                load_cloud.clear()
                current_db = load_cloud()
                current_db["notifications"] = []
                if save_cloud(current_db):
                    st.rerun()
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

# Tối ưu gọn gàng khung tiêu đề + mô tả chuyến đi ngay đầu trang
raw_desc = trip_data.get("desc", "").strip() or "Chưa có thông tin chi tiết cho chuyến đi này."
safe_desc = html.escape(raw_desc)
HEADER_DESC_HTML = f"""
<div class="notice-board">
    <div style="font-size:20px; font-weight:800; color:#38bdf8; margin-bottom:8px;">⛺ {html.escape(cur_trip.upper())}</div>
    <div class="notice-title">📢 THÔNG TIN & MÔ TẢ LỊCH TRÌNH</div>
    <div class="notice-body">{safe_desc}</div>
</div>
"""
st.markdown(HEADER_DESC_HTML, unsafe_allow_html=True)

if is_admin:
    with st.expander("✏️ Chỉnh sửa thông tin / mô tả chuyến đi", expanded=False):
        with st.form("edit_trip_desc_form"):
            updated_desc = st.text_area("Nội dung thông báo / lịch trình", value=trip_data.get("desc", ""), height=110)
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
        st.markdown(
        """
        <style>
        /* Khóa cứng cấu trúc bảng 5 cột nằm ngang chuẩn trên cả điện thoại và máy tính */
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            gap: 6px !important;
            align-items: stretch !important;
        }
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            flex: 0 0 auto !important;
        }
        /* Cột 1: Ô tích hoàn thành nhỏ gọn 38px */
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) > div:nth-child(1) {
            width: 38px !important;
            min-width: 38px !important;
            max-width: 38px !important;
        }
        /* Cột 2: Tên vật dụng */
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) > div:nth-child(2) {
            width: 145px !important;
            min-width: 145px !important;
        }
        /* Cột 3: SL / Ghi chú */
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) > div:nth-child(3) {
            width: 195px !important;
            min-width: 195px !important;
        }
        /* Cột 4: Người góp */
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) > div:nth-child(4) {
            width: 135px !important;
            min-width: 135px !important;
        }
        /* Cột 5: Nút Góp & Xóa */
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) > div:nth-child(5) {
            width: 130px !important;
            min-width: 130px !important;
        }
        /* Giữ 2 nút Góp và Xóa bên trong Cột 5 luôn nằm cạnh nhau */
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) > div:nth-child(5) div[data-testid="stHorizontalBlock"] {
            overflow-x: visible !important;
            gap: 4px !important;
        }
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) > div:nth-child(5) div[data-testid="stHorizontalBlock"] > div:nth-child(1) {
            width: 82px !important;
            min-width: 82px !important;
        }
        div[data-testid="stTabs"] div[data-testid="stHorizontalBlock"]:has(> div:nth-child(5)) > div:nth-child(5) div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
            width: 42px !important;
            min-width: 42px !important;
        }
        /* Định dạng ô chữ & nút bấm gọn gàng */
        div[data-testid="stTextArea"] textarea {
            padding: 6px 8px !important;
            font-size: 13px !important;
            line-height: 1.4 !important;
            min-height: 40px !important;
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            border-radius: 6px !important;
        }
        div[data-testid="stTabs"] div.stButton > button {
            padding: 4px 6px !important;
            font-size: 12.5px !important;
            min-height: 40px !important;
            white-space: nowrap !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    can_manage_req = is_admin or (me.strip().lower() == "trần phước long")
    reqs = trip_data.get("requirements", [])
    if not isinstance(reqs, list):
        reqs = []

    extra_cols = trip_data.get("extra_cols", [])
    if not isinstance(extra_cols, list):
        extra_cols = []

    done_count = sum(1 for r in reqs if r.get("done", False))
    st.markdown(
        f'<div style="background:#131c31; border:1px solid #334155; border-radius:10px; padding:9px 14px; margin-bottom:12px; font-size:13.5px;">📊 <b>Tiến độ chuẩn bị:</b> <span style="color:#34d399; font-weight:800;">{done_count}/{len(reqs)}</span> mục đã xong &nbsp;|&nbsp; <i>Trên điện thoại có thể vuốt ngang bảng để xem & bấm sửa trực tiếp.</i></div>',
        unsafe_allow_html=True,
    )

    col_tool1, col_tool2 = st.columns([2.1, 2.9])
    with col_tool1:
        if can_manage_req:
            if st.button("📥 Nạp danh sách mẫu chuẩn", key="load_sample_reqs", use_container_width=True):
                load_cloud.clear()
                current_db = load_cloud()
                sample_items = [
                    {"category": "📦 Nhu Yếu Phẩm & Vật Dụng", "task": "Đèn Pin", "qty_note": "Góp càng nhiều càng tốt (đi sáng sớm).", "assigned": "", "done": False},
                    {"category": "📦 Nhu Yếu Phẩm & Vật Dụng", "task": "Dụng cụ y tế cần thiết", "qty_note": "Ai có mang thêm, thiếu nhóm chi quỹ mua.", "assigned": "", "done": False},
                    {"category": "📦 Nhu Yếu Phẩm & Vật Dụng", "task": "Đồ Dùng Thiết Yếu Cá Nhân", "qty_note": "Tự túc gọn nhẹ, tránh mang đồ cồng kềnh.", "assigned": "Tự túc cá nhân", "done": False},
                    {"category": "📦 Nhu Yếu Phẩm & Vật Dụng", "task": "Thiết Bị Điện (Sạc dự phòng, dây sạc)", "qty_note": "Ai có mang thêm dự phòng.", "assigned": "", "done": False},
                    {"category": "🍖 Thức Ăn & Nước Uống", "task": "Nước uống", "qty_note": "Dự kiến 2 thùng 20L + nước ngọt các loại.", "assigned": "", "done": False},
                    {"category": "🍖 Thức Ăn & Nước Uống", "task": "Thức Ăn Chính & Đồ Nướng", "qty_note": "Lên thực đơn và chia nhóm đi chợ.", "assigned": "", "done": False},
                    {"category": "🍳 Dụng Cụ Nấu Ăn & Khác", "task": "Dao Kéo", "qty_note": "Báo Gia Huy kiểm kê số lượng.", "assigned": "Gia Huy", "done": False},
                    {"category": "🍳 Dụng Cụ Nấu Ăn & Khác", "task": "Dụng cụ nấu ăn", "qty_note": "Cần góp thêm ngoài bộ của Hoàng Phát.", "assigned": "Hoàng Phát", "done": False},
                    {"category": "🍳 Dụng Cụ Nấu Ăn & Khác", "task": "Than nướng", "qty_note": "Dự kiến 2-3 Kg. Ai có ib Gia Huy.", "assigned": "Gia Huy", "done": False},
                ]
                current_db["trips"][cur_trip]["requirements"].extend(sample_items)
                add_log(current_db, f"📋 **{me}** đã nạp danh sách đồ dùng chuẩn cho *{cur_trip}*.")
                if save_cloud(current_db):
                    st.rerun()

    with col_tool2:
        with st.form("add_col_inline_form", clear_on_submit=True):
            c_in1, c_in2 = st.columns([2.7, 1.3])
            with c_in1:
                new_col_txt = st.text_input("Thêm cột", placeholder="Tên cột mới (VD: Chi phí, Nơi mua)...", label_visibility="collapsed")
            with c_in2:
                btn_add_col = st.form_submit_button("➕ Thêm cột", use_container_width=True)
            if btn_add_col and new_col_txt.strip():
                col_clean = new_col_txt.strip()
                load_cloud.clear()
                current_db = load_cloud()
                cur_ec = current_db["trips"][cur_trip].get("extra_cols", [])
                if col_clean not in cur_ec:
                    cur_ec.append(col_clean)
                    current_db["trips"][cur_trip]["extra_cols"] = cur_ec
                    for item in current_db["trips"][cur_trip].get("requirements", []):
                        item.setdefault(col_clean, "")
                    add_log(current_db, f"📊 **{me}** đã thêm cột **{col_clean}** vào bảng (*{cur_trip}*).")
                    if save_cloud(current_db):
                        st.rerun()
    categories_order = ["📦 Nhu Yếu Phẩm & Vật Dụng", "🍖 Thức Ăn & Nước Uống", "🍳 Dụng Cụ Nấu Ăn & Khác"]
    cat_themes = {
        "📦 Nhu Yếu Phẩm & Vật Dụng": ("linear-gradient(90deg, #1d4ed8, #0f172a)", "#60a5fa", "#dbeafe"),
        "🍖 Thức Ăn & Nước Uống": ("linear-gradient(90deg, #b45309, #1c1917)", "#f59e0b", "#fef3c7"),
        "🍳 Dụng Cụ Nấu Ăn & Khác": ("linear-gradient(90deg, #047857, #064e3b)", "#10b981", "#d1fae5"),
    }

    existing_cats = []
    for r in reqs:
        c_name = r.get("category", "📦 Nhu Yếu Phẩm & Vật Dụng")
        if c_name not in existing_cats:
            existing_cats.append(c_name)
    all_cats = categories_order + [c for c in existing_cats if c not in categories_order]

    def calc_box_height(texts_list):
        max_lines = 1
        for txt, chars_per_line in texts_list:
            if txt:
                lines = sum(max(1, (len(part) + chars_per_line - 1) // chars_per_line) for part in txt.split("\n"))
                if lines > max_lines:
                    max_lines = lines
        return max(42, max_lines * 22 + 18)

    for cat_idx, cat_title in enumerate(all_cats):
        cat_indices = [idx for idx, r in enumerate(reqs) if r.get("category", "📦 Nhu Yếu Phẩm & Vật Dụng") == cat_title]
        bg_grad, border_col, txt_col = cat_themes.get(
            cat_title, ("linear-gradient(90deg, #1e3a8a, #0f172a)", "#3b82f6", "#93c5fd")
        )

        st.markdown(
            f'<div style="background:{bg_grad}; border:1px solid {border_col}; border-radius:10px 10px 0 0; padding:10px 14px; font-weight:800; color:{txt_col} !important; font-size:15px; margin-top:20px;">{html.escape(cat_title)} ({len(cat_indices)} mục)</div>',
            unsafe_allow_html=True,
        )

        th1, th2, th3, th4, th5 = st.columns([0.4, 1.65, 2.05, 1.45, 1.35])
        with th1:
            st.markdown(f'<div style="background:#1e293b; border-bottom:2px solid {border_col}; padding:6px 2px; font-size:11px; font-weight:800; color:#cbd5e1 !important; text-align:center;">TT</div>', unsafe_allow_html=True)
        with th2:
            st.markdown(f'<div style="background:#1e293b; border-bottom:2px solid {border_col}; padding:6px 8px; font-size:11px; font-weight:800; color:#cbd5e1 !important;">VẬT DỤNG</div>', unsafe_allow_html=True)
        with th3:
            st.markdown(f'<div style="background:#1e293b; border-bottom:2px solid {border_col}; padding:6px 8px; font-size:11px; font-weight:800; color:#cbd5e1 !important;">SL / GHI CHÚ</div>', unsafe_allow_html=True)
        with th4:
            st.markdown(f'<div style="background:#1e293b; border-bottom:2px solid {border_col}; padding:6px 8px; font-size:11px; font-weight:800; color:#cbd5e1 !important;">NGƯỜI GÓP</div>', unsafe_allow_html=True)
        with th5:
            st.markdown(f'<div style="background:#1e293b; border-bottom:2px solid {border_col}; padding:6px 4px; font-size:11px; font-weight:800; color:#cbd5e1 !important; text-align:center;">THAO TÁC</div>', unsafe_allow_html=True)

        if not cat_indices:
            st.caption("Chưa có mục nào trong bảng này. Bấm nút bên dưới để thêm dòng mới.")
        else:
            for i in cat_indices:
                req = reqs[i]
                is_done = bool(req.get("done", False))
                task_val = str(req.get("task", ""))
                note_val = str(req.get("qty_note", ""))
                raw_who = str(req.get("assigned", "")).strip()
                clean_who = "" if raw_who in ["Chưa phân công", "Chưa có người góp", "Mọi người cùng góp"] else raw_who
                contributors = [x.strip() for x in clean_who.split(",") if x.strip()]
                already_joined = (me in contributors)

                row_h = calc_box_height([(task_val, 17), (note_val, 23), (clean_who, 15)])

                c_chk, c_task, c_note, c_who, c_btn = st.columns([0.4, 1.65, 2.05, 1.45, 1.35])

                with c_chk:
                    new_done = st.checkbox("", value=is_done, key=f"tbl_done_{cur_trip}_{i}", label_visibility="collapsed")
                    if new_done != is_done:
                        load_cloud.clear()
                        current_db = load_cloud()
                        t_reqs = current_db["trips"][cur_trip]["requirements"]
                        if i < len(t_reqs):
                            t_reqs[i]["done"] = new_done
                            status_txt = "đã xong" if new_done else "chưa xong"
                            add_log(current_db, f"✅ **{me}** đánh dấu **{t_reqs[i]['task']}** ({status_txt}) trong *{cur_trip}*.")
                            if save_cloud(current_db):
                                st.rerun()

                with c_task:
                    st.text_area("Vật dụng", value=task_val, height=row_h, placeholder="Tên vật dụng...", key=f"tbl_task_{cur_trip}_{i}", label_visibility="collapsed")

                with c_note:
                    st.text_area("Ghi chú", value=note_val, height=row_h, placeholder="SL / Ghi chú...", key=f"tbl_note_{cur_trip}_{i}", label_visibility="collapsed")

                with c_who:
                    st.text_area("Người góp", value=clean_who, height=row_h, placeholder="Chưa ai góp...", key=f"tbl_who_{cur_trip}_{i}", label_visibility="collapsed")
                with c_btn:
                    b_g1, b_g2 = st.columns([2.2, 1])
                    with b_g1:
                        if already_joined:
                            if st.button("↩️ Hủy", key=f"tbl_leave_{cur_trip}_{i}", use_container_width=True):
                                load_cloud.clear()
                                current_db = load_cloud()
                                t_reqs = current_db["trips"][cur_trip]["requirements"]
                                if i < len(t_reqs):
                                    contributors.remove(me)
                                    t_reqs[i]["assigned"] = ", ".join(contributors)
                                    add_log(current_db, f"↩️ **{me}** đã rút tên khỏi mục **{t_reqs[i]['task']}** (*{cur_trip}*).")
                                    if save_cloud(current_db):
                                        st.rerun()
                        else:
                            if st.button("🙋‍♂️ Góp", key=f"tbl_join_{cur_trip}_{i}", use_container_width=True):
                                load_cloud.clear()
                                current_db = load_cloud()
                                t_reqs = current_db["trips"][cur_trip]["requirements"]
                                if i < len(t_reqs):
                                    contributors.append(me)
                                    t_reqs[i]["assigned"] = ", ".join(contributors)
                                    add_log(current_db, f"🙋‍♂️ **{me}** đã đăng ký góp **{t_reqs[i]['task']}** (*{cur_trip}*).")
                                    if save_cloud(current_db):
                                        st.rerun()
                    with b_g2:
                        if st.button("🗑️", key=f"tbl_del_{cur_trip}_{i}", use_container_width=True):
                            load_cloud.clear()
                            current_db = load_cloud()
                            t_reqs = current_db["trips"][cur_trip]["requirements"]
                            if i < len(t_reqs):
                                del_name = t_reqs[i].get("task", "mục trống")
                                t_reqs.pop(i)
                                add_log(current_db, f"🗑️ **{me}** đã xóa mục **{del_name}** (*{cur_trip}*).")
                                if save_cloud(current_db):
                                    st.rerun()

                if extra_cols:
                    ec_cols = st.columns(len(extra_cols))
                    for ec_i, ec_name in enumerate(extra_cols):
                        with ec_cols[ec_i]:
                            ec_val = str(req.get(ec_name, ""))
                            ec_h = calc_box_height([(ec_val, 35)])
                            st.text_area(ec_name, value=ec_val, height=ec_h, placeholder=f"{ec_name}...", key=f"tbl_ec_{cur_trip}_{i}_{ec_name}")

                st.markdown('<div style="border-bottom:1px solid #1e293b; margin:2px 0 6px 0;"></div>', unsafe_allow_html=True)

        foot_c1, foot_c2 = st.columns(2)
        with foot_c1:
            if st.button("➕ Thêm hàng vào bảng này", key=f"add_row_cat_{cat_idx}", use_container_width=True):
                load_cloud.clear()
                current_db = load_cloud()
                blank_item = {"category": cat_title, "task": "Mục mới (bấm để sửa)", "qty_note": "", "assigned": "", "done": False}
                for ec in extra_cols:
                    blank_item[ec] = ""
                current_db["trips"][cur_trip]["requirements"].append(blank_item)
                if save_cloud(current_db):
                    st.rerun()
        with foot_c2:
            if cat_indices:
                if st.button("💾 Lưu chữ đã sửa ở bảng này", key=f"save_cat_{cat_idx}", use_container_width=True):
                    load_cloud.clear()
                    current_db = load_cloud()
                    t_reqs = current_db["trips"][cur_trip]["requirements"]
                    for i in cat_indices:
                        if i < len(t_reqs):
                            new_t = st.session_state.get(f"tbl_task_{cur_trip}_{i}", t_reqs[i].get("task", "")).strip()
                            new_n = st.session_state.get(f"tbl_note_{cur_trip}_{i}", t_reqs[i].get("qty_note", "")).strip()
                            new_w = st.session_state.get(f"tbl_who_{cur_trip}_{i}", t_reqs[i].get("assigned", "")).strip()
                            if new_t:
                                t_reqs[i]["task"] = new_t
                            t_reqs[i]["qty_note"] = new_n
                            t_reqs[i]["assigned"] = new_w
                            for ec in extra_cols:
                                t_reqs[i][ec] = st.session_state.get(f"tbl_ec_{cur_trip}_{i}_{ec}", t_reqs[i].get(ec, "")).strip()
                    add_log(current_db, f"✏️ **{me}** đã cập nhật nội dung bảng **{cat_title}** (*{cur_trip}*).")
                    if save_cloud(current_db):
                        st.success("Đã lưu thay đổi!")
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
            assigned_tasks = [req["task"] for req in reqs if member_name in req.get("assigned", "")]
            task_status = f"🎒 Nhận lo ({len(assigned_tasks)}): {', '.join(assigned_tasks)}" if assigned_tasks else "📋 Chưa nhận đồ dùng"

            card_html = f'<div class="member-card"><div style="font-size: 16px; font-weight: 700; color: #38bdf8;">{idx}. 👤 {member_name}</div><div style="font-size: 13px; color: #cbd5e1; margin-top: 4px;">{vote_status} &nbsp;|&nbsp; {task_status}</div></div>'
            st.markdown(card_html, unsafe_allow_html=True)
