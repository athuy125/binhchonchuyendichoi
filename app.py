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
}
div.stButton > button:hover {
    background-color: #2563eb !important;
    color: #ffffff !important;
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
.member-card { background-color: #161f33; border: 1px solid #334155; border-radius: 12px; padding: 14px 18px; margin-bottom: 10px; }
.notif-row { background-color: #131b2e; border: 1px solid #263248; border-left: 4px solid #38bdf8; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; }
.notif-row-vip { background-color: #1c1917; border: 1px solid #f59e0b; border-left: 4px solid #f59e0b; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; }
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
        notif_item = notif_item if notif_item else None
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
                            "foods": [],
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

cookie_manager = stx.CookieManager(key="team_auth_cookie_grid")

if "user" not in st.session_state:
    st.session_state.user = None
if "selected_trip" not in st.session_state:
    st.session_state.selected_trip = None
if "active_token" not in st.session_state:
    st.session_state.active_token = ""

db = load_cloud()

if st.session_state.user is None:
    url_tk = st.query_params.get("token", "")
    ck_tk = cookie_manager.get("team_trip_session_grid")
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
                cookie_manager.set("team_trip_session_grid", found_tk, expires_at=exp_d)
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
                        cookie_manager.set("team_trip_session_grid", new_tk, expires_at=exp_date)
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
                        cookie_manager.set("team_trip_session_grid", new_tk, expires_at=exp_date)
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

cur_session_tk = st.session_state.get("active_token") or st.query_params.get("token", "") or cookie_manager.get("team_trip_session_grid")
if cur_session_tk:
    if st.query_params.get("token", "") != cur_session_tk:
        st.query_params["token"] = cur_session_tk
    if not st.session_state.get("cookie_refreshed"):
        exp_d = datetime.datetime.now() + datetime.timedelta(days=365)
        cookie_manager.set("team_trip_session_grid", cur_session_tk, expires_at=exp_d)
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
    trigger_browser_push(all_notifs)

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
                cookie_manager.delete("team_trip_session_grid")
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
DEFAULT_TRIP_IMG = "https://unsplash.com"
DEFAULT_LOC_IMG = "https://unsplash.com"
DEFAULT_REQ_IMGS = {
    "📦 Nhu Yếu Phẩm & Vật Dụng": "https://unsplash.com",
    "🍖 Thức Ăn & Nước Uống": "https://unsplash.com",
    "🍳 Dụng Cụ Nấu Ăn & Khác": "https://unsplash.com",
}

if st.session_state.selected_trip is None or st.session_state.selected_trip not in db["trips"]:
    LOBBY_HTML = '<div class="hero-banner"><h2 style="margin:0;">🗺️ DANH SÁCH CHUYẾN ĐI CỦA ĐỘI</h2><p style="margin:8px 0 0 0; font-size:15px;">Chọn một chuyến đi bên dưới để xem thực đơn, bình chọn địa điểm và đăng ký góp đồ dùng.</p></div>'
    st.markdown(LOBBY_HTML, unsafe_allow_html=True)

    if is_admin:
        with st.expander("➕ Tạo Chuyến Đi Mới", expanded=False):
            with st.form("create_trip_form", clear_on_submit=True):
                c_tr1, c_tr2 = st.columns(2)
                with c_tr1:
                    new_trip_name = st.text_input("Tên chuyến đi mới", placeholder="Ví dụ: Chuyến đi chơi 2 - Vũng Tàu...")
                with c_tr2:
                    new_trip_img = st.text_input("Link ảnh bìa (Bỏ trống tự lấy ảnh đẹp)", placeholder="https://...")
                new_trip_desc = st.text_area("Mô tả / Lịch trình dự kiến", placeholder="Ví dụ: Đi 2 ngày 1 đêm cuối tháng...")
                if st.form_submit_button("✅ TẠO CHUYẾN ĐI", use_container_width=True):
                    t_clean = new_trip_name.strip()
                    if not t_clean:
                        st.warning("Vui lòng nhập tên chuyến đi!")
                    else:
                        load_cloud.clear()
                        current_db = load_cloud()
                        if t_clean in current_db["trips"]:
                            st.error("Tên chuyến đi này đã tồn tại!")
                        else:
                            t_img_val = new_trip_img.strip() if new_trip_img.strip().startswith("http") else DEFAULT_TRIP_IMG
                            current_db["trips"][t_clean] = {
                                "desc": new_trip_desc.strip() or "Kế hoạch dã ngoại mới của toàn đội.",
                                "img": t_img_val,
                                "locations": [],
                                "foods": [],
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
        for start_t in range(0, len(trip_names), 2):
            t_cols = st.columns(2)
            for off_t in range(2):
                if start_t + off_t >= len(trip_names):
                    break
                idx = start_t + off_t
                t_name = trip_names[idx]
                t_info = db["trips"][t_name]
                n_locs = len(t_info.get("locations", []))
                n_foods = len(t_info.get("foods", []))
                n_reqs = len(t_info.get("requirements", []))
                t_cover = str(t_info.get("img", "")).strip()
                if not t_cover.startswith("http"):
                    t_cover = DEFAULT_TRIP_IMG

                with t_cols[off_t]:
                    st.markdown(
                        f"""
                        <div style="background:#131b2e; border:2px solid #3b82f6; border-radius:14px; overflow:hidden; margin-bottom:8px;">
                            <div style="position:relative; width:100%; height:155px; background:#090d16;">
                                <img src="{html.escape(t_cover)}" style="width:100%; height:155px; object-fit:cover; display:block;" />
                                <span style="position:absolute; bottom:8px; left:8px; background:rgba(6,78,59,0.92); color:#6ee7b7 !important; padding:3px 10px; border-radius:10px; font-size:12px; font-weight:700; border:1px solid #10b981;">📍 {n_locs} điểm | 🍽️ {n_foods} món | 🎒 {n_reqs} đồ</span>
                            </div>
                            <div style="padding:12px; text-align:center;">
                                <div style="font-size:17px; font-weight:800; color:#38bdf8 !important; text-transform:uppercase;">⛺ {html.escape(t_name)}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if is_admin and len(trip_names) > 1:
                        b_enter, b_del = st.columns([3.8, 1])
                        with b_enter:
                            if st.button("🚀 VÀO CHUYẾN ĐI", key=f"enter_trip_{idx}", use_container_width=True):
                                st.session_state.selected_trip = t_name
                                st.rerun()
                        with b_del:
                            if st.button("🗑️", key=f"del_trip_{idx}", use_container_width=True):
                                load_cloud.clear()
                                current_db = load_cloud()
                                if t_name in current_db["trips"]:
                                    del current_db["trips"][t_name]
                                    add_log(current_db, f"🗑️ Chuyến đi **{t_name}** đã bị xóa khỏi danh sách.")
                                    if save_cloud(current_db):
                                        st.rerun()
                    else:
                        if st.button("🚀 VÀO CHUYẾN ĐI", key=f"enter_trip_{idx}", use_container_width=True):
                            st.session_state.selected_trip = t_name
                            st.rerun()
                    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)

    st.stop()

cur_trip = st.session_state.selected_trip
trip_data = db["trips"][cur_trip]

if st.button("⬅️ Quay lại danh sách chuyến đi", use_container_width=True):
    st.session_state.selected_trip = None
    st.rerun()

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
    with st.expander("✏️ Chỉnh sửa thông tin / ảnh bìa chuyến đi", expanded=False):
        with st.form("edit_trip_desc_form"):
            updated_desc = st.text_area("Nội dung thông báo / lịch trình", value=trip_data.get("desc", ""), height=100)
            updated_t_img = st.text_input("Link ảnh bìa chuyến đi", value=trip_data.get("img", DEFAULT_TRIP_IMG))
            if st.form_submit_button("💾 Lưu thay đổi", use_container_width=True):
                load_cloud.clear()
                current_db = load_cloud()
                if cur_trip in current_db["trips"]:
                    current_db["trips"][cur_trip]["desc"] = updated_desc.strip()
                    if updated_t_img.strip().startswith("http"):
                        current_db["trips"][cur_trip]["img"] = updated_t_img.strip()
                    add_log(current_db, f"📝 Thông tin của **{cur_trip}** vừa được cập nhật.")
                    if save_cloud(current_db):
                        st.success("Đã cập nhật thông tin chuyến đi!")
                        st.rerun()
t_loc, t_food, t_req, t_mem = st.tabs(["🗳️ Bình Chọn Địa Điểm", "🍽️ Bình Chọn Thức Ăn", "🎒 Đồ Cần Chuẩn Bị", "👥 Thành Viên"])

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
        with st.expander("➕ Đề xuất địa điểm mới (Có hình ảnh)", expanded=False):
            with st.form("add_loc_form", clear_on_submit=True):
                lc1, lc2 = st.columns(2)
                with lc1:
                    l_name = st.text_input("Tên địa điểm", placeholder="Ví dụ: Hồ Trị An...")
                with lc2:
                    l_img = st.text_input("Link ảnh địa điểm (Bỏ trống tự lấy ảnh đẹp)", placeholder="https://...")
                l_desc = st.text_input("Mô tả / Khoảng cách", placeholder="Đường đẹp, cách trung tâm 40km...")
                if st.form_submit_button("✅ THÊM ĐỊA ĐIỂM", use_container_width=True):
                    if l_name.strip():
                        load_cloud.clear()
                        current_db = load_cloud()
                        chosen_l_img = l_img.strip() if l_img.strip().startswith("http") else DEFAULT_LOC_IMG
                        new_loc = {
                            "name": l_name.strip(),
                            "desc": l_desc.strip() or "Chưa có mô tả",
                            "img": chosen_l_img,
                            "voters": [me],
                        }
                        current_db["trips"][cur_trip]["locations"].append(new_loc)
                        add_log(current_db, f"📍 **{me}** đã đề xuất địa điểm mới **{l_name.strip()}** trong *{cur_trip}*.")
                        if save_cloud(current_db):
                            st.rerun()
                    else:
                        st.warning("Vui lòng nhập tên địa điểm!")
        locs = trip_data.get("locations", [])
    if len(locs) == 0:
        st.info("Chưa có địa điểm nào được đề xuất cho chuyến đi này.")
    else:
        for start_l in range(0, len(locs), 2):
            l_cols = st.columns(2)
            for off_l in range(2):
                if start_l + off_l >= len(locs):
                    break
                i = start_l + off_l
                loc = locs[i]
                voters = loc.get("voters", [])
                voted = me in voters
                loc_img_url = str(loc.get("img", "")).strip()
                if not loc_img_url.startswith("http"):
                    loc_img_url = DEFAULT_LOC_IMG

                card_border = "#10b981" if voted else "#334155"
                voters_txt = ", ".join(voters) if voters else "Chưa có ai vote"

                with l_cols[off_l]:
                    st.markdown(
                        f"""
                        <div style="background:#131b2e; border:2px solid {card_border}; border-radius:14px; overflow:hidden; margin-bottom:8px;">
                            <div style="position:relative; width:100%; height:165px; background:#090d16;">
                                <img src="{html.escape(loc_img_url)}" onerror="this.onerror=null;this.src='{DEFAULT_LOC_IMG}';" style="width:100%; height:165px; object-fit:cover; display:block;" />
                                <span style="position:absolute; top:8px; right:8px; background:#064e3b; color:#6ee7b7 !important; padding:4px 11px; border-radius:12px; font-size:12.5px; font-weight:800; border:1px solid #10b981;">🔥 {len(voters)} phiếu</span>
                            </div>
                            <div style="padding:12px; text-align:center;">
                                <div style="font-size:17px; font-weight:800; color:#ffffff !important; text-transform:uppercase; margin-bottom:4px;">📍 {html.escape(loc.get("name", ""))}</div>
                                <div style="font-size:13.5px; color:#fde68a !important; margin-bottom:6px;">{html.escape(loc.get("desc", ""))}</div>
                                <div style="font-size:12.5px; color:#cbd5e1 !important; min-height:34px;">👤 <b>Đã vote:</b> {html.escape(voters_txt)}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    c1, c2 = st.columns([3.8, 1])
                    with c1:
                        if is_voting_closed:
                            st.button("🔒 Đã hết hạn", key=f"closed_{i}", disabled=True, use_container_width=True)
                        else:
                            btn_text = "✅ ĐÃ VOTE (Bỏ)" if voted else "👍 BẦU CHỌN"
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

                    with st.expander("🖼️ Đổi ảnh / Sửa địa điểm này", expanded=False):
                        with st.form(f"edit_loc_form_{cur_trip}_{i}"):
                            el_name = st.text_input("Tên địa điểm", value=loc.get("name", ""))
                            el_desc = st.text_input("Mô tả", value=loc.get("desc", ""))
                            el_img = st.text_input("Dán link hình ảnh mới", value=loc.get("img", ""), placeholder="https://...")
                            if st.form_submit_button("💾 Lưu cập nhật", use_container_width=True):
                                load_cloud.clear()
                                current_db = load_cloud()
                                t_locs = current_db["trips"][cur_trip]["locations"]
                                if i < len(t_locs):
                                    if el_name.strip():
                                        t_locs[i]["name"] = el_name.strip()
                                    t_locs[i]["desc"] = el_desc.strip()
                                    t_locs[i]["img"] = el_img.strip() if el_img.strip().startswith("http") else DEFAULT_LOC_IMG
                                    if save_cloud(current_db):
                                        st.rerun()

                    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)

with t_food:
    DEFAULT_FOOD_IMGS = {
        "🍖 Món chính": "https://unsplash.com",
        "🥤 Thức uống": "https://unsplash.com",
        "🍰 Tráng miệng": "https://unsplash.com",
    }

    st.markdown(
        """
        <div style="background:linear-gradient(90deg, #92400e, #1e293b); border:2px solid #f59e0b; border-radius:14px; padding:14px 18px; margin-bottom:14px;">
            <div style="font-size:19px; font-weight:800; color:#fbbf24 !important; letter-spacing:0.5px;">🍽️ THỰC ĐƠN BÌNH CHỌN CỦA ĐỘI</div>
            <div style="font-size:14.5px; color:#ffffff !important; margin-top:4px;">Xem hình món ăn bên dưới và bấm nút <b>👍 CHỌN MÓN</b> để bình chọn (có thể chọn nhiều món).</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("➕ Thêm Món Ăn / Thức Uống Mới (Có Hình Ảnh)", expanded=False):
        with st.form("add_food_grid_form", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            with fc1:
                f_cat = st.selectbox("Danh mục thực đơn:", ["🍖 Món chính", "🥤 Thức uống", "🍰 Tráng miệng"])
            with fc2:
                f_name = st.text_input("Tên món ăn / thức uống:", placeholder="VD: Gà nướng, Lẩu Thái, Nước ép...")
            fc3, fc4 = st.columns(2)
            with fc3:
                f_price = st.text_input("Giá dự kiến / Ghi chú:", placeholder="VD: 150.000đ/con hoặc Tự ướp...")
            with fc4:
                f_img = st.text_input("Link hình ảnh (Bỏ trống tự lấy ảnh mẫu):", placeholder="https://...")
            if st.form_submit_button("✅ ĐƯA MÓN LÊN THỰC ĐƠN", use_container_width=True):
                if f_name.strip():
                    load_cloud.clear()
                    current_db = load_cloud()
                    food_list = current_db["trips"][cur_trip].setdefault("foods", [])
                    chosen_img = f_img.strip() if f_img.strip().startswith("http") else DEFAULT_FOOD_IMGS.get(f_cat, DEFAULT_FOOD_IMGS["🍖 Món chính"])
                    food_list.append({
                        "type": f_cat,
                        "name": f_name.strip(),
                        "note": f_price.strip() or "Theo thực tế",
                        "img": chosen_img,
                        "voters": [me],
                    })
                    add_log(current_db, f"🍽️ **{me}** đã thêm món **{f_name.strip()}** ({f_cat}) vào thực đơn *{cur_trip}*.")
                    if save_cloud(current_db):
                        st.success(f"Đã thêm {f_name.strip()} vào thực đơn!")
                        st.rerun()
                else:
                    st.warning("Vui lòng nhập tên món ăn hoặc thức uống!")

    cat_filter = st.radio(
        "Danh mục:",
        ["📋 Tất cả thực đơn", "🍖 Món chính", "🥤 Thức uống", "🍰 Tráng miệng"],
        horizontal=True,
        label_visibility="collapsed",
    )
    foods = trip_data.get("foods", [])
    if not isinstance(foods, list) or len(foods) == 0:
        st.info("Thực đơn chưa có món nào. Hãy bấm nút '➕ Thêm Món Ăn / Thức Uống Mới' ở trên để thêm món đầu tiên!")
    else:
        filtered_indices = []
        for idx_f, item in enumerate(foods):
            item_type = item.get("type", "🍖 Món chính")
            if item_type == "🍖 Món Ăn":
                item_type = "🍖 Món chính"
            elif item_type == "🥤 Nước Uống":
                item_type = "🥤 Thức uống"
            if cat_filter == "📋 Tất cả thực đơn" or item_type == cat_filter:
                filtered_indices.append(idx_f)

        if not filtered_indices:
            st.info(f"Chưa có món nào trong mục {cat_filter}.")
        else:
            for start_i in range(0, len(filtered_indices), 2):
                grid_cols = st.columns(2)
                for offset in range(2):
                    if start_i + offset >= len(filtered_indices):
                        break
                    idx_f = filtered_indices[start_i + offset]
                    f_item = foods[idx_f]
                    f_voters = f_item.get("voters", [])
                    is_voted = (me in f_voters)
                    f_type = f_item.get("type", "🍖 Món chính")
                    img_url = str(f_item.get("img", "")).strip()
                    if not img_url.startswith("http"):
                        img_url = DEFAULT_FOOD_IMGS.get(f_type, DEFAULT_FOOD_IMGS["🍖 Món chính"])

                    card_border = "#10b981" if is_voted else "#334155"
                    voters_str = ", ".join(f_voters) if f_voters else "Chưa ai chọn"

                    with grid_cols[offset]:
                        st.markdown(
                            f"""
                            <div style="background:#131b2e; border:2px solid {card_border}; border-radius:14px; overflow:hidden; margin-bottom:8px;">
                                <div style="position:relative; width:100%; height:165px; background:#090d16;">
                                    <img src="{html.escape(img_url)}" style="width:100%; height:165px; object-fit:cover; display:block;" />
                                    <span style="position:absolute; top:8px; left:8px; background:rgba(15,23,42,0.88); color:#fbbf24 !important; padding:3px 9px; border-radius:8px; font-size:11.5px; font-weight:700; border:1px solid #f59e0b;">{html.escape(f_type)}</span>
                                    <span style="position:absolute; top:8px; right:8px; background:#064e3b; color:#6ee7b7 !important; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:800; border:1px solid #10b981;">🔥 {len(f_voters)} chọn</span>
                                </div>
                                <div style="padding:12px; text-align:center;">
                                    <div style="font-size:16.5px; font-weight:800; color:#ffffff !important; text-transform:uppercase; margin-bottom:4px;">{html.escape(f_item.get("name", ""))}</div>
                                    <div style="font-size:14px; font-weight:700; color:#fb923c !important; margin-bottom:6px;">{html.escape(f_item.get("note", "") or "Theo thực tế")}</div>
                                    <div style="font-size:12.5px; color:#cbd5e1 !important; min-height:34px;">👤 <b>Đã chọn:</b> {html.escape(voters_str)}</div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        b1, b2 = st.columns([3.8, 1])
                        with b1:
                            btn_txt = "✅ ĐÃ CHỌN (Bỏ)" if is_voted else "👍 CHỌN MÓN"
                            if st.button(btn_txt, key=f"grid_vote_food_{cur_trip}_{idx_f}", use_container_width=True):
                                load_cloud.clear()
                                current_db = load_cloud()
                                cur_foods = current_db["trips"][cur_trip].get("foods", [])
                                if idx_f < len(cur_foods):
                                    v_list = cur_foods[idx_f].get("voters", [])
                                    if me in v_list:
                                        v_list.remove(me)
                                        add_log(current_db, f"↩️ **{me}** đã bỏ chọn món **{cur_foods[idx_f]['name']}** (*{cur_trip}*).")
                                    else:
                                        v_list.append(me)
                                        add_log(current_db, f"🍽️ **{me}** đã chọn món **{cur_foods[idx_f]['name']}** (*{cur_trip}*).")
                                    cur_foods[idx_f]["voters"] = v_list
                                    if save_cloud(current_db):
                                        st.rerun()
                        with b2:
                            if st.button("🗑️", key=f"grid_del_food_{cur_trip}_{idx_f}", use_container_width=True):
                                load_cloud.clear()
                                current_db = load_cloud()
                                cur_foods = current_db["trips"][cur_trip].get("foods", [])
                                if idx_f < len(cur_foods):
                                    del_fn = cur_foods[idx_f].get("name", "")
                                    cur_foods.pop(idx_f)
                                    add_log(current_db, f"🗑️ **{me}** đã xóa món **{del_fn}** (*{cur_trip}*).")
                                    if save_cloud(current_db):
                                        st.rerun()

                        st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
with t_req:
    can_manage_req = is_admin or (me.strip().lower() == "trần phước long")
    reqs = trip_data.get("requirements", [])
    if not isinstance(reqs, list):
        reqs = []

    if can_manage_req:
        with st.expander("⚡ Nạp nhanh danh sách mẫu chuẩn", expanded=False):
            st.caption("Tự động thêm các mục nhu yếu phẩm, thức ăn, dụng cụ vào chuyến đi này.")
            if st.button("📥 Nạp danh sách mẫu vào chuyến đi", key="load_sample_reqs", use_container_width=True):
                load_cloud.clear()
                current_db = load_cloud()
                sample_items = [
                    {"category": "📦 Nhu Yếu Phẩm & Vật Dụng", "task": "Đèn Pin", "qty_note": "Góp càng nhiều càng tốt (đi sáng sớm).", "assigned": "Chưa có người góp", "done": False},
                    {"category": "📦 Nhu Yếu Phẩm & Vật Dụng", "task": "Dụng cụ y tế cần thiết", "qty_note": "Ai có mang thêm, thiếu nhóm chi quỹ mua.", "assigned": "Chưa có người góp", "done": False},
                    {"category": "📦 Nhu Yếu Phẩm & Vật Dụng", "task": "Đồ Dùng Thiết Yếu Cá Nhân", "qty_note": "Tự túc gọn nhẹ, tránh mang đồ cồng kềnh.", "assigned": "Tự túc cá nhân", "done": False},
                    {"category": "📦 Nhu Yếu Phẩm & Vật Dụng", "task": "Thiết Bị Điện (Sạc dự phòng, dây sạc)", "qty_note": "Ai có mang thêm dự phòng.", "assigned": "Chưa có người góp", "done": False},
                    {"category": "🍖 Thức Ăn & Nước Uống", "task": "Nước uống", "qty_note": "Dự kiến 2 thùng 20L + nước ngọt các loại.", "assigned": "Chưa có người góp", "done": False},
                    {"category": "🍖 Thức Ăn & Nước Uống", "task": "Thức Ăn Chính & Đồ Nướng", "qty_note": "Lên thực đơn và chia nhóm đi chợ.", "assigned": "Chưa có người góp", "done": False},
                    {"category": "🍳 Dụng Cụ Nấu Ăn & Khác", "task": "Dao Kéo", "qty_note": "Báo Gia Huy kiểm kê số lượng.", "assigned": "Gia Huy", "done": False},
                    {"category": "🍳 Dụng Cụ Nấu Ăn & Khác", "task": "Dụng cụ nấu ăn", "qty_note": "Cần góp thêm ngoài bộ của Hoàng Phát.", "assigned": "Hoàng Phát", "done": False},
                    {"category": "🍳 Dụng Cụ Nấu Ăn & Khác", "task": "Than nướng", "qty_note": "Dự kiến 2-3 Kg. Ai có ib Gia Huy.", "assigned": "Gia Huy", "done": False},
                ]
                current_db["trips"][cur_trip]["requirements"].extend(sample_items)
                add_log(current_db, f"📋 **{me}** đã nạp danh sách đồ dùng chuẩn cho *{cur_trip}*.")
                if save_cloud(current_db):
                    st.rerun()

    with st.expander("➕ Thêm Vật Dụng / Đồ Dùng Mới (Có Hình Ảnh)", expanded=False):
        with st.form("add_req_form", clear_on_submit=True):
            c_add1, c_add2 = st.columns(2)
            with c_add1:
                cat_choice = st.selectbox("Danh mục đồ dùng:", ["📦 Nhu Yếu Phẩm & Vật Dụng", "🍖 Thức Ăn & Nước Uống", "🍳 Dụng Cụ Nấu Ăn & Khác"])
            with c_add2:
                t_name = st.text_input("Tên vật dụng:", placeholder="VD: Đèn pin, Than, Thùng đá...")
            c_add3, c_add4 = st.columns(2)
            with c_add3:
                t_qty = st.text_input("SL / Ghi chú chi tiết:", placeholder="VD: Dự kiến 2-3 Kg, ai có góp thêm...")
            with c_add4:
                t_img = st.text_input("Link hình ảnh (Bỏ trống tự lấy ảnh mẫu):", placeholder="https://...")
            if st.form_submit_button("✅ THÊM VÀO DANH SÁCH ĐỒ DÙNG", use_container_width=True):
                if t_name.strip():
                    load_cloud.clear()
                    current_db = load_cloud()
                    chosen_r_img = t_img.strip() if t_img.strip().startswith("http") else DEFAULT_REQ_IMGS.get(cat_choice, DEFAULT_REQ_IMGS["📦 Nhu Yếu Phẩm & Vật Dụng"])
                    new_req = {
                        "category": cat_choice,
                        "task": t_name.strip(),
                        "qty_note": t_qty.strip() or "Theo thực tế",
                        "img": chosen_r_img,
                        "assigned": "Chưa có người góp",
                        "done": False,
                    }
                    current_db["trips"][cur_trip]["requirements"].append(new_req)
                    add_log(current_db, f"🎒 **{me}** đã thêm **{t_name.strip()}** vào danh sách đồ dùng (*{cur_trip}*).")
                    if save_cloud(current_db):
                        st.rerun()
                else:
                    st.warning("Vui lòng nhập tên vật dụng!")
        SAFE_REQ_IMGS = {
        "📦 Nhu Yếu Phẩm & Vật Dụng": "https://pexels.com",
        "🍖 Thức Ăn & Nước Uống": "https://pexels.com",
        "🍳 Dụng Cụ Nấu Ăn & Khác": "https://pexels.com",
    }

    req_filter = st.radio(
        "Lọc đồ dùng:",
        ["📋 Tất cả đồ dùng", "📦 Nhu Yếu Phẩm & Vật Dụng", "🍖 Thức Ăn & Nước Uống", "🍳 Dụng Cụ Nấu Ăn & Khác"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if len(reqs) == 0:
        st.info("Chưa có đồ dùng nào trong danh sách của chuyến đi này.")
    else:
        done_count = sum(1 for r in reqs if r.get("done", False))
        st.caption(f"📊 **Tổng tiến độ chuẩn bị:** Đã hoàn thành **{done_count}/{len(reqs)}** mục")

        filtered_req_idx = [
            idx for idx, r in enumerate(reqs)
            if req_filter == "📋 Tất cả đồ dùng" or r.get("category", "📦 Nhu Yếu Phẩm & Vật Dụng") == req_filter
        ]

        if not filtered_req_idx:
            st.info(f"Chưa có mục nào trong nhóm {req_filter}.")
        else:
            for start_r in range(0, len(filtered_req_idx), 2):
                r_cols = st.columns(2)
                for off_r in range(2):
                    if start_r + off_r >= len(filtered_req_idx):
                        break
                    i = filtered_req_idx[start_r + off_r]
                    req = reqs[i]
                    is_done = bool(req.get("done", False))
                    r_cat = req.get("category", "📦 Nhu Yếu Phẩm & Vật Dụng")
                    fallback_img = SAFE_REQ_IMGS.get(r_cat, SAFE_REQ_IMGS["📦 Nhu Yếu Phẩm & Vật Dụng"])
                    r_img = str(req.get("img", "")).strip()
                    if not r_img.startswith("http") or "unsplash.com" in r_img:
                        r_img = fallback_img

                    cur_assigned = req.get("assigned", "").strip()
                    contributors = [x.strip() for x in cur_assigned.split(",") if x.strip() and x.strip() not in ["Chưa phân công", "Chưa có người góp", "Mọi người cùng góp"]]
                    already_joined = (me in contributors)

                    status_html = '<span style="position:absolute; top:8px; right:8px; background:#064e3b; color:#6ee7b7 !important; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:800; border:1px solid #10b981;">✅ Đã xong</span>' if is_done else '<span style="position:absolute; top:8px; right:8px; background:rgba(120,53,15,0.92); color:#fde68a !important; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:800; border:1px solid #f59e0b;">⏳ Đang lo</span>'
                    card_border = "#10b981" if (is_done or already_joined) else "#334155"
                    who_display = ", ".join(contributors) if contributors else "Chưa có người góp"
                    who_color = "#34d399" if contributors else "#94a3b8"

                    with r_cols[off_r]:
                        st.markdown(
                            f"""
                            <div style="background:#131b2e; border:2px solid {card_border}; border-radius:14px; overflow:hidden; margin-bottom:8px;">
                                <div style="position:relative; width:100%; height:150px; background:#090d16;">
                                    <img src="{html.escape(r_img)}" onerror="this.onerror=null;this.src='{fallback_img}';" style="width:100%; height:150px; object-fit:cover; display:block;" />
                                    <span style="position:absolute; top:8px; left:8px; background:rgba(15,23,42,0.88); color:#93c5fd !important; padding:3px 8px; border-radius:8px; font-size:11px; font-weight:700;">{html.escape(r_cat)}</span>
                                    {status_html}
                                </div>
                                <div style="padding:12px; text-align:center;">
                                    <div style="font-size:16px; font-weight:800; color:#ffffff !important; text-transform:uppercase; margin-bottom:4px;">{html.escape(req.get("task", ""))}</div>
                                    <div style="font-size:13px; color:#fde68a !important; margin-bottom:6px;">{html.escape(req.get("qty_note", "") or "Theo thực tế")}</div>
                                    <div style="font-size:13px; font-weight:700; color:{who_color} !important; min-height:34px;">🙋‍♂️ Góp: {html.escape(who_display)}</div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if can_manage_req:
                            rb1, rb2, rb3 = st.columns([2.8, 1, 1])
                        else:
                            rb1 = st.container()
                            rb2 = None
                            rb3 = None

                        with rb1:
                            if already_joined:
                                if st.button("↩️ HỦY GÓP", key=f"grid_leave_req_{cur_trip}_{i}", use_container_width=True):
                                    load_cloud.clear()
                                    current_db = load_cloud()
                                    t_reqs = current_db["trips"][cur_trip]["requirements"]
                                    if i < len(t_reqs):
                                        contributors.remove(me)
                                        t_reqs[i]["assigned"] = ", ".join(contributors) if contributors else "Chưa có người góp"
                                        add_log(current_db, f"↩️ **{me}** đã rút tên khỏi mục **{t_reqs[i]['task']}** (*{cur_trip}*).")
                                        if save_cloud(current_db):
                                            st.rerun()
                            else:
                                if st.button("🙋‍♂️ TÔI GÓP", key=f"grid_join_req_{cur_trip}_{i}", use_container_width=True):
                                    load_cloud.clear()
                                    current_db = load_cloud()
                                    t_reqs = current_db["trips"][cur_trip]["requirements"]
                                    if i < len(t_reqs):
                                        contributors.append(me)
                                        t_reqs[i]["assigned"] = ", ".join(contributors)
                                        add_log(current_db, f"🙋‍♂️ **{me}** đã đăng ký góp **{t_reqs[i]['task']}** (*{cur_trip}*).")
                                        if save_cloud(current_db):
                                            st.rerun()

                        if can_manage_req and rb2 is not None and rb3 is not None:
                            with rb2:
                                toggle_icon = "🔄" if is_done else "✅"
                                if st.button(toggle_icon, key=f"grid_done_req_{cur_trip}_{i}", use_container_width=True):
                                    load_cloud.clear()
                                    current_db = load_cloud()
                                    t_reqs = current_db["trips"][cur_trip]["requirements"]
                                    if i < len(t_reqs):
                                        t_reqs[i]["done"] = not is_done
                                        st_txt = "đã xong" if not is_done else "đang lo"
                                        add_log(current_db, f"✅ **{me}** đánh dấu **{t_reqs[i]['task']}** ({st_txt}) trong *{cur_trip}*.")
                                        if save_cloud(current_db):
                                            st.rerun()
                            with rb3:
                                if st.button("🗑️", key=f"grid_del_req_{cur_trip}_{i}", use_container_width=True):
                                    load_cloud.clear()
                                    current_db = load_cloud()
                                    t_reqs = current_db["trips"][cur_trip]["requirements"]
                                    if i < len(t_reqs):
                                        del_t = t_reqs[i]["task"]
                                        t_reqs.pop(i)
                                        add_log(current_db, f"🗑️ **{me}** đã xóa mục **{del_t}** (*{cur_trip}*).")
                                        if save_cloud(current_db):
                                            st.rerun()

                        # Khung gắn hình ảnh & chỉnh sửa cho tất cả các mục cũ lẫn mới
                                                with st.expander("🖼️ Gắn ảnh / Sửa mục"):
                            with st.form(f"edit_req_{cur_trip}_{i}"):
                                er_task = st.text_input("Tên đồ dùng", value=req.get("task", ""))
                                er_note = st.text_input("SL / Ghi chú", value=req.get("qty_note", ""))
                                er_img = st.text_input("Link ảnh (https://...)", value=req.get("img", ""))
                                if st.form_submit_button("💾 Lưu cập nhật", use_container_width=True):
                                    load_cloud.clear()
                                    current_db = load_cloud()
                                    t_reqs = current_db["trips"][cur_trip]["requirements"]
                                    if i < len(t_reqs):
                                        if er_task.strip():
                                            t_reqs[i]["task"] = er_task.strip()
                                        t_reqs[i]["qty_note"] = er_note.strip()
                                        if er_img.strip().startswith("http"):
                                            t_reqs[i]["img"] = er_img.strip()
                                        add_log(current_db, f"🖼️ **{me}** đã cập nhật **{t_reqs[i]['task']}**.")
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
            vote_status = f"✅ Địa điểm: {', '.join(voted_places)}" if voted_places else "⏳ Chưa chọn địa điểm"
            voted_foods = [f["name"] for f in foods if member_name in f.get("voters", [])]
            food_status = f"🍽️ Món ăn ({len(voted_foods)}): {', '.join(voted_foods)}" if voted_foods else "🍴 Chưa chọn món"
            assigned_tasks = [req["task"] for req in reqs if member_name in req.get("assigned", "")]
            task_status = f"🎒 Góp đồ ({len(assigned_tasks)}): {', '.join(assigned_tasks)}" if assigned_tasks else "📋 Chưa nhận đồ"

            card_html = f'<div class="member-card"><div style="font-size: 16px; font-weight: 700; color: #38bdf8;">{idx}. 👤 {member_name}</div><div style="font-size: 13px; color: #cbd5e1; margin-top: 4px;">{vote_status} &nbsp;|&nbsp; {food_status} &nbsp;|&nbsp; {task_status}</div></div>'
            st.markdown(card_html, unsafe_allow_html=True)
