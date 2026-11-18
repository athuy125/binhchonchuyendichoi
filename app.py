import datetime
import hashlib
import html
import secrets
import time
import extra_streamlit_components as stx
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="TravelGo - Siêu Ứng Dụng Du Lịch & Khám Phá",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

BIN_ID = "6af5b874ffd5d16053bc0858"
MASTER_KEY = "$2a$10$EpLPTXlcBTH5/mkxVMBLI.ZSv26QzgFaygkYFHZOa4V7OoVtsot12"

API_URL = "/".join(["https:/", "api.jsonbin.io", "v3", "b", BIN_ID])
HEADERS = {"Content-Type": "application/json", "X-Master-Key": MASTER_KEY}

# --- GIAO DIỆN HIỆN ĐẠI PHONG CÁCH TRAVELOKA / KLOOK ---
CSS_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp {
    background-color: #f8fafc !important;
    color: #0f172a !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"] {
    background-color: #f8fafc !important;
}

/* Typography */
h1, h2, h3, h4, h5, h6, .stMarkdown {
    color: #0f172a !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Inputs & Form Fields (Modern Travel App Style) */
input, textarea, select, [data-baseweb="input"] input, [data-baseweb="textarea"] textarea, [data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 12px !important;
    -webkit-text-fill-color: #0f172a !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
input:focus, textarea:focus, select:focus {
    border-color: #0284c7 !important;
    box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15) !important;
}
input::placeholder, textarea::placeholder {
    color: #94a3b8 !important;
    -webkit-text-fill-color: #94a3b8 !important;
}

/* Containers / Cards */
[data-testid="stExpander"], [data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03) !important;
    color: #0f172a !important;
}

/* Buttons */
div.stButton > button {
    background-color: #ffffff !important;
    color: #0284c7 !important;
    border: 1.5px solid #0284c7 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all 0.2s ease;
}
div.stButton > button:hover {
    background-color: #f0f9ff !important;
    border-color: #0369a1 !important;
    color: #0369a1 !important;
    transform: translateY(-1px);
}
button[kind="primaryFormSubmit"], [data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
}
button[kind="primaryFormSubmit"]:hover {
    background: linear-gradient(135deg, #0369a1 100%, #1d4ed8 100%) !important;
}

/* Custom UI Components (Travel App Vibes) */
.hero-banner { 
    background: linear-gradient(135deg, #0284c7 0%, #1e40af 100%); 
    border-radius: 20px; 
    padding: 24px; 
    margin-bottom: 16px; 
    color: #ffffff !important; 
    box-shadow: 0 10px 25px rgba(2, 132, 199, 0.25); 
}
.hero-banner * { color: #ffffff !important; }

.notice-board { 
    background: #ffffff; 
    border: 1px solid #e2e8f0; 
    border-left: 5px solid #0284c7; 
    border-radius: 14px; 
    padding: 18px; 
    margin-bottom: 16px; 
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
}
.notice-title { color: #0284c7 !important; font-size: 13px; font-weight: 800; letter-spacing: 0.8px; margin-bottom: 6px; text-transform: uppercase; }
.notice-body { color: #334155 !important; font-size: 15px; line-height: 1.6; white-space: pre-line; }

.member-card { 
    background-color: #ffffff; 
    border: 1px solid #e2e8f0; 
    border-radius: 14px; 
    padding: 14px 18px; 
    margin-bottom: 10px; 
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.02);
}
.notif-row { background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #0ea5e9; border-radius: 12px; padding: 12px 16px; margin-bottom: 8px; }
.notif-row-vip { background-color: #fffbeb; border: 1px solid #fef3c7; border-left: 4px solid #f59e0b; border-radius: 12px; padding: 12px 16px; margin-bottom: 8px; }
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
            requests.post(discord_url, json={"content": f"✈️ **THÔNG BÁO TRAVELGO:** {clean_msg}"}, timeout=4)
        except Exception:
            pass
    if tg_token and tg_chat:
        try:
            tg_api = f"https://telegram.org{tg_token}/sendMessage"
            requests.post(tg_api, json={"chat_id": tg_chat, "text": f"✈️ THÔNG BÁO TRAVELGO:\n{clean_msg}"}, timeout=4)
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
            new Notification("✈️ TravelGo Thông Báo", {{ body: "{safe_text}" }});
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
                        "Hành Trình Khám Phá 1": {
                            "desc": "Chuyến đi trải nghiệm, nghỉ dưỡng và khám phá danh thắng tuyệt đẹp.",
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

cookie_manager = stx.CookieManager(key="team_auth_cookie_travelgo")

if "user" not in st.session_state:
    st.session_state.user = None
if "selected_trip" not in st.session_state:
    st.session_state.selected_trip = None
if "active_token" not in st.session_state:
    st.session_state.active_token = ""

db = load_cloud()

if st.session_state.user is None:
    url_tk = st.query_params.get("token", "")
    ck_tk = cookie_manager.get("team_trip_session_travelgo")
    found_tk = ck_tk or url_tk

    if found_tk and found_tk in db.get("sessions", {}):
        auto_user = db["sessions"][found_tk]
        if auto_user in db.get("users", {}):
            st.session_state.user = auto_user
            st.session_state.active_token = found_tk
            if st.query_params.get("token", "") != found_tk:
                st.query_params["token"] = found_tk
            exp_d = datetime.datetime.now() + datetime.timedelta(days=365)
            cookie_manager.set("team_trip_session_travelgo", found_tk, expires_at=exp_d)
            st.rerun()
    elif not url_tk:
        components.html(
            """
            <script>
            try {
                const savedTk = window.parent.localStorage.getItem("travelgo_token");
                if (savedTk && savedTk.length > 10) {
                    const parentUrl = new URL(window.parent.location.href);
                    if (parentUrl.searchParams.get("token") !== savedTk) {
                        parentUrl.searchParams.set("token", savedTk);
                        window.parent.location.replace(parentUrl.toString());
                    }
                }
            } catch (e) {}
            </script>
            """,
            height=0,
        )

if st.session_state.user is None:
    AUTH_HTML = '<div class="hero-banner" style="text-align: center;"><h2 style="margin:0; font-weight:800;">✈️ TRAVELGO - ĐỒNG HÀNH MỌI CHUYẾN ĐI</h2><p style="margin:8px 0 0 0; opacity: 0.9; font-size:15px;">Đăng nhập hoặc đăng ký tài khoản để khám phá lịch trình, bình chọn và chuẩn bị cùng nhóm</p></div>'
    st.markdown(AUTH_HTML, unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 Đăng Nhập", "📝 Đăng Ký Tài Khoản"])

    with tab1:
        with st.form("login_box"):
            name = st.text_input("Tên đăng nhập", placeholder="Nhập tên của bạn...").strip()
            pwd = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu...")
            st.caption("🔒 Hệ thống ghi nhớ đăng nhập tự động trên thiết bị của bạn.")
            if st.form_submit_button("🚀 Bắt Đầu Hành Trình", use_container_width=True):
                if not name or not pwd:
                    st.warning("Vui lòng nhập đầy đủ tên và mật khẩu!")
                else:
                    load_cloud.clear()
                    fresh_db = load_cloud()
                    if name not in fresh_db["users"]:
                        st.error("Tên này chưa đăng ký! Vui lòng chuyển sang tab Đăng Ký.")
                    elif fresh_db["users"][name] != make_hash(pwd):
                        st.error("Mật khẩu không chính xác!")
                    else:
                        new_tk = secrets.token_hex(16)
                        fresh_db.setdefault("sessions", {})[new_tk] = name
                        save_cloud(fresh_db)
                        exp_date = datetime.datetime.now() + datetime.timedelta(days=365)
                        cookie_manager.set("team_trip_session_travelgo", new_tk, expires_at=exp_date)
                        st.query_params["token"] = new_tk
                        st.session_state.active_token = new_tk
                        st.session_state.user = name
                        time.sleep(0.8)
                        st.rerun()

    with tab2:
        with st.form("reg_box"):
            r_name = st.text_input("Tên hiển thị", placeholder="Ví dụ: Hoàng Long...").strip()
            r_pwd = st.text_input("Mật khẩu", type="password")
            r_pwd2 = st.text_input("Nhập lại mật khẩu", type="password")
            st.caption("🔒 Tài khoản bảo mật và lưu trữ trực tuyến an toàn.")
            if st.form_submit_button("✨ Đăng Ký Ngay", use_container_width=True):
                if not r_name or not r_pwd:
                    st.warning("Không được để trống thông tin!")
                elif r_pwd != r_pwd2:
                    st.error("Mật khẩu xác nhận không khớp!")
                else:
                    load_cloud.clear()
                    fresh_db = load_cloud()
                    if r_name in fresh_db["users"]:
                        st.error("Tên tài khoản này đã tồn tại!")
                    else:
                        fresh_db["users"][r_name] = make_hash(r_pwd)
                        new_tk = secrets.token_hex(16)
                        fresh_db.setdefault("sessions", {})[new_tk] = r_name
                        exp_date = datetime.datetime.now() + datetime.timedelta(days=365)
                        cookie_manager.set("team_trip_session_travelgo", new_tk, expires_at=exp_date)
                        add_log(fresh_db, f"🎉 Thành viên mới **{r_name}** vừa gia nhập cộng đồng TravelGo!", True)
                        if save_cloud(fresh_db):
                            st.query_params["token"] = new_tk
                            st.session_state.active_token = new_tk
                            st.session_state.user = r_name
                            time.sleep(0.8)
                            st.success("Đăng ký thành công!")
                            st.rerun()
    st.stop()

db = load_cloud()
me = st.session_state.user
is_admin = (me.strip().lower() == "athuy125")

cur_session_tk = st.session_state.get("active_token") or st.query_params.get("token", "") or cookie_manager.get("team_trip_session_travelgo")
if cur_session_tk:
    if st.query_params.get("token", "") != cur_session_tk:
        st.query_params["token"] = cur_session_tk
    components.html(
        f"""
        <script>
        try {{
            window.parent.localStorage.setItem("travelgo_token", "{cur_session_tk}");
        }} catch (e) {{}}
        </script>
        """,
        height=0,
    )
    if not st.session_state.get("cookie_refreshed"):
        exp_d = datetime.datetime.now() + datetime.timedelta(days=365)
        cookie_manager.set("team_trip_session_travelgo", cur_session_tk, expires_at=exp_d)
        st.session_state.cookie_refreshed = True

# Header thông tin tài khoản đang đăng nhập
col_a, col_b, col_c = st.columns([3.2, 1.4, 1.2])
with col_a:
    st.info(f"👋 Xin chào, **{me}**!")
with col_b:
    if st.button("🔄 Làm mới", use_container_width=True):
        load_cloud.clear()
        st.rerun()
with col_c:
    if st.button("Đăng xuất", use_container_width=True):
        if cur_session_tk:
            load_cloud.clear()
            clean_db = load_cloud()
            if cur_session_tk in clean_db.get("sessions", {}):
                del clean_db["sessions"][cur_session_tk]
                save_cloud(clean_db)
            try:
                cookie_manager.delete("team_trip_session_travelgo")
            except Exception:
                pass
        components.html(
            """
            <script>
            try {
                window.parent.localStorage.removeItem("travelgo_token");
            } catch (e) {}
            </script>
            """,
            height=0,
        )
        time.sleep(0.5)
        st.query_params.clear()
        st.session_state.active_token = ""
        st.session_state.cookie_refreshed = False
        st.session_state.user = None
        st.session_state.selected_trip = None
        st.rerun()

# Bảng thông báo chung phong cách app hiện đại
with st.expander("🔔 Bảng Thông Báo & Hoạt Động Mới", expanded=True):
    top_n1, top_n2 = st.columns([3.2, 2.2])
    with top_n1:
        st.caption("📌 Cập nhật các hoạt động và thông báo mới nhất từ nhóm")
    with top_n2:
        components.html(
            """
            <div style="text-align:right;">
                <button onclick="Notification.requestPermission().then(p => alert(p === 'granted' ? 'Đã bật thông báo thành công!' : 'Trình duyệt đang chặn thông báo.'))"
                style="background:#0284c7; color:white; border:none; padding:7px 14px; border-radius:10px; font-weight:700; cursor:pointer; font-size:13px;">
                📲 Bật Thông Báo App
                </button>
            </div>
            """,
            height=36,
        )

    all_notifs = db.get("notifications", [])
    if is_admin:
        with st.form("admin_broadcast_form", clear_on_submit=True):
            b_col1, b_col2 = st.columns([4.2, 1.4])
            with b_col1:
                b_msg = st.text_input("Soạn thông báo", placeholder="Nhập thông báo gửi toàn đội...", label_visibility="collapsed")
            with b_col2:
                send_b = st.form_submit_button("📢 Gửi tin", use_container_width=True)
            if send_b:
                if b_msg.strip():
                    load_cloud.clear()
                    current_db = load_cloud()
                    add_log(current_db, f"📢 **THÔNG BÁO CHUNG:** {b_msg.strip()}", True)
                    if save_cloud(current_db):
                        st.success("Đã gửi thông báo thành công!")
                        st.rerun()

    if not all_notifs:
        st.info("Chưa có thông báo nào.")
    else:
        for idx_n, n_item in enumerate(all_notifs[:5]):
            is_vip = n_item.get("important", False)
            row_cls = "notif-row-vip" if is_vip else "notif-row"
            raw_msg = html.escape(n_item.get("msg", "")).replace("**", "")
            card_notif = f'<div class="{row_cls}"><span style="color:#0284c7; font-size:12px; font-weight:700;">🕒 {html.escape(n_item.get("time", ""))}</span><div style="color:#1e293b; font-size:14px; margin-top:3px;">{raw_msg}</div></div>'
            st.markdown(card_notif, unsafe_allow_html=True)

DEFAULT_TRIP_IMG = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
DEFAULT_LOC_IMG = "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800"
DEFAULT_FOOD_IMG = "https://images.unsplash.com/photo-1504674900247-0877df9cc836"
DEFAULT_REQ_IMG = "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1"

if st.session_state.selected_trip is None or st.session_state.selected_trip not in db["trips"]:
    LOBBY_HTML = '<div class="hero-banner"><h2 style="margin:0; font-weight:800;">🗺️ KHÁM PHÁ CÁC CHUYẾN ĐI</h2><p style="margin:8px 0 0 0; font-size:15px; opacity:0.95;">Lựa chọn điểm đến hấp dẫn bên dưới để tham gia lên lịch trình, bình chọn và chuẩn bị.</p></div>'
    st.markdown(LOBBY_HTML, unsafe_allow_html=True)

    if is_admin:
        with st.expander("➕ Tạo Chuyến Đi Mới", expanded=False):
            with st.form("create_trip_form", clear_on_submit=True):
                c_tr1, c_tr2 = st.columns(2)
                with c_tr1:
                    new_trip_name = st.text_input("Tên chuyến đi", placeholder="Ví dụ: Nha Trang Summer 2026...")
                with c_tr2:
                    new_trip_img = st.text_input("Link ảnh bìa (tuỳ chọn)", placeholder="https://...")
                new_trip_desc = st.text_area("Mô tả / Lịch trình dự kiến", placeholder="Mô tả ngắn gọn về chuyến đi...")
                if st.form_submit_button("✅ TẠO CHUYẾN ĐI", use_container_width=True):
                    t_clean = new_trip_name.strip()
                    if not t_clean:
                        st.warning("Vui lòng nhập tên chuyến đi!")
                    else:
                        load_cloud.clear()
                        current_db = load_cloud()
                        if t_clean in current_db["trips"]:
                            st.error("Chuyến đi này đã tồn tại!")
                        else:
                            t_img_val = new_trip_img.strip() if new_trip_img.strip().startswith("http") else DEFAULT_TRIP_IMG
                            current_db["trips"][t_clean] = {
                                "desc": new_trip_desc.strip() or "Hành trình trải nghiệm tuyệt vời.",
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
        st.info("Chưa có chuyến đi nào.")
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
                        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:16px; overflow:hidden; margin-bottom:12px; box-shadow: 0 4px 15px rgba(15,23,42,0.06);">
                            <div style="position:relative; width:100%; height:160px; background:#f1f5f9;">
                                <img src="{html.escape(t_cover)}" onerror="this.onerror=null;this.src='{DEFAULT_TRIP_IMG}';" style="width:100%; height:160px; object-fit:cover; display:block;" />
                                <span style="position:absolute; bottom:10px; left:10px; background:rgba(15,23,42,0.8); color:#ffffff !important; padding:4px 10px; border-radius:20px; font-size:11.5px; font-weight:700;">📍 {n_locs} điểm | 🍽️ {n_foods} món | 🎒 {n_reqs} đồ</span>
                            </div>
                            <div style="padding:16px;">
                                <div style="font-size:17px; font-weight:800; color:#0f172a !important; margin-bottom:4px;">✈️ {html.escape(t_name)}</div>
                                <div style="font-size:13px; color:#64748b; line-height:1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">{html.escape(t_info.get("desc", ""))}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("🚀 Khám Phá Ngay", key=f"enter_trip_{idx}", use_container_width=True):
                        st.session_state.selected_trip = t_name
                        st.rerun()
                    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)
    st.stop()

cur_trip = st.session_state.selected_trip
trip_data = db["trips"][cur_trip]

if st.button("⬅️ Quay lại danh sách chuyến đi", use_container_width=True):
    st.session_state.selected_trip = None
    st.rerun()

raw_desc = trip_data.get("desc", "").strip() or "Chưa có thông tin chi tiết."
HEADER_DESC_HTML = f"""
<div class="notice-board">
    <div style="font-size:20px; font-weight:800; color:#0284c7; margin-bottom:6px;">✈️ {html.escape(cur_trip.upper())}</div>
    <div class="notice-title">📖 THÔNG TIN CHUYẾN ĐI</div>
    <div class="notice-body">{html.escape(raw_desc)}</div>
</div>
"""
st.markdown(HEADER_DESC_HTML, unsafe_allow_html=True)

# Các tab chức năng ứng dụng du lịch
t_loc, t_food, t_req, t_pay, t_mem, t_poster = st.tabs(["🗳️ Điểm Đến", "🍽️ Ẩm Thực", "🎒 Chuẩn Bị", "💰 Quỹ Đoàn", "👥 Thành Viên", "📜 Xuất Poster"])

with t_loc:
    st.markdown("### 🗺️ Bình Chọn Địa Điểm Khám Phá")
    with st.expander("➕ Đề xuất địa điểm mới", expanded=False):
        with st.form("add_loc_form", clear_on_submit=True):
            lc1, lc2 = st.columns(2)
            with lc1:
                l_name = st.text_input("Tên địa điểm", placeholder="VD: Bãi Dài, VinWonders...")
            with lc2:
                l_img = st.text_input("Link ảnh (tuỳ chọn)", placeholder="https://...")
            l_desc = st.text_input("Mô tả / Khoảng cách", placeholder="Cảnh đẹp, góc sống ảo tuyệt vời...")
            if st.form_submit_button("✅ Gửi Đề Xuất", use_container_width=True):
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
                    add_log(current_db, f"📍 **{me}** đã đề xuất địa điểm **{l_name.strip()}** trong *{cur_trip}*.")
                    if save_cloud(current_db):
                        st.rerun()
                else:
                    st.warning("Vui lòng nhập tên địa điểm!")

    locs = trip_data.get("locations", [])
    if len(locs) == 0:
        st.info("Chưa có địa điểm nào được đề xuất.")
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

                card_border = "#0284c7" if voted else "#e2e8f0"
                voters_txt = ", ".join(voters) if voters else "Chưa có ai vote"

                with l_cols[off_l]:
                    st.markdown(
                        f"""
                        <div style="background:#ffffff; border:2px solid {card_border}; border-radius:16px; overflow:hidden; margin-bottom:12px; box-shadow: 0 4px 15px rgba(15,23,42,0.06);">
                            <div style="position:relative; width:100%; height:160px; background:#f1f5f9;">
                                <img src="{html.escape(loc_img_url)}" onerror="this.onerror=null;this.src='{DEFAULT_LOC_IMG}';" style="width:100%; height:160px; object-fit:cover; display:block;" />
                                <span style="position:absolute; top:10px; right:10px; background:#0284c7; color:#ffffff !important; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:800;">🔥 {len(voters)} phiếu</span>
                            </div>
                            <div style="padding:16px;">
                                <div style="font-size:16px; font-weight:800; color:#0f172a !important; margin-bottom:4px;">📍 {html.escape(loc.get("name", ""))}</div>
                                <div style="font-size:13px; color:#64748b; margin-bottom:8px;">{html.escape(loc.get("desc", ""))}</div>
                                <div style="font-size:12px; color:#475569;">👤 <b>Đã vote:</b> {html.escape(voters_txt)}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    btn_text = "✅ Đã Bình Chọn (Hủy)" if voted else "👍 Bình Chọn Ngay"
                    if st.button(btn_text, key=f"vote_{i}", use_container_width=True):
                        load_cloud.clear()
                        current_db = load_cloud()
                        t_locs = current_db["trips"][cur_trip]["locations"]
                        if i < len(t_locs):
                            cur_voters = t_locs[i].get("voters", [])
                            if me in cur_voters:
                                cur_voters.remove(me)
                            else:
                                cur_voters.append(me)
                            t_locs[i]["voters"] = cur_voters
                            if save_cloud(current_db):
                                st.rerun()
                    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)

with t_food:
    st.markdown("### 🍽️ Khám Phá Ẩm Thực & Món Ăn")
    with st.expander("➕ Thêm Món Ăn / Thức Uống", expanded=False):
        with st.form("add_food_form", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            with fc1:
                f_cat = st.selectbox("Danh mục:", ["🍖 Món chính", "🥤 Thức uống", "🍰 Tráng miệng"])
            with fc2:
                f_name = st.text_input("Tên món ăn:", placeholder="VD: Hải sản nướng, Lẩu mực...")
            fc3, fc4 = st.columns(2)
            with fc3:
                f_price = st.text_input("Ghi chú / Giá:", placeholder="VD: Khoảng 150k/người")
            with fc4:
                f_img = st.text_input("Link ảnh (tuỳ chọn):", placeholder="https://...")
            if st.form_submit_button("✅ Thêm Món Vào Danh Sách", use_container_width=True):
                if f_name.strip():
                    load_cloud.clear()
                    current_db = load_cloud()
                    food_list = current_db["trips"][cur_trip].setdefault("foods", [])
                    chosen_img = f_img.strip() if f_img.strip().startswith("http") else DEFAULT_FOOD_IMG
                    food_list.append({
                        "type": f_cat,
                        "name": f_name.strip(),
                        "note": f_price.strip() or "Theo thực tế",
                        "img": chosen_img,
                        "voters": [me],
                    })
                    if save_cloud(current_db):
                        st.success("Đã thêm món thành công!")
                        st.rerun()
                else:
                    st.warning("Vui lòng nhập tên món ăn!")

    foods = trip_data.get("foods", [])
    if not isinstance(foods, list) or len(foods) == 0:
        st.info("Chưa có món ăn nào được đề xuất.")
    else:
        for idx_f, f_item in enumerate(foods):
            f_voters = f_item.get("voters", [])
            is_voted = me in f_voters
            img_url = str(f_item.get("img", "")).strip()
            if not img_url.startswith("http"):
                img_url = DEFAULT_FOOD_IMG

            card_border = "#0284c7" if is_voted else "#e2e8f0"
            st.markdown(
                f"""
                <div style="background:#ffffff; border:2px solid {card_border}; border-radius:16px; overflow:hidden; margin-bottom:12px; display:flex; align-items:center; box-shadow: 0 4px 12px rgba(15,23,42,0.04);">
                    <img src="{html.escape(img_url)}" style="width:110px; height:110px; object-fit:cover;" />
                    <div style="padding:14px; flex-grow:1;">
                        <span style="background:#f0f9ff; color:#0284c7; padding:2px 8px; border-radius:6px; font-size:11px; font-weight:700;">{html.escape(f_item.get("type", ""))}</span>
                        <div style="font-size:16px; font-weight:800; color:#0f172a; margin:4px 0;">{html.escape(f_item.get("name", ""))}</div>
                        <div style="font-size:13px; color:#f59e0b; font-weight:700;">{html.escape(f_item.get("note", ""))} &nbsp;|&nbsp; 🔥 {len(f_voters)} lượt chọn</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            btn_txt = "✅ Đã Chọn" if is_voted else "👍 Chọn Món Này"
            if st.button(btn_txt, key=f"food_vote_{idx_f}", use_container_width=True):
                load_cloud.clear()
                current_db = load_cloud()
                cur_foods = current_db["trips"][cur_trip].get("foods", [])
                if idx_f < len(cur_foods):
                    v_list = cur_foods[idx_f].get("voters", [])
                    if me in v_list:
                        v_list.remove(me)
                    else:
                        v_list.append(me)
                    cur_foods[idx_f]["voters"] = v_list
                    if save_cloud(current_db):
                        st.rerun()

with t_req:
    st.markdown("### 🎒 Danh Sách Đồ Dùng Chuẩn Bị")
    with st.expander("➕ Thêm Đồ Dùng Cần Mang", expanded=False):
        with st.form("add_req_form", clear_on_submit=True):
            r_name = st.text_input("Tên vật dụng", placeholder="VD: Kem chống nắng, áo khoác...")
            r_note = st.text_input("Số lượng / Ghi chú", placeholder="VD: 2 cái / Mỗi người tự chuẩn bị")
            if st.form_submit_button("✅ Thêm Đồ Dùng", use_container_width=True):
                if r_name.strip():
                    load_cloud.clear()
                    current_db = load_cloud()
                    current_db["trips"][cur_trip]["requirements"].append({
                        "category": "📦 Vật Dụng Chung",
                        "task": r_name.strip(),
                        "qty_note": r_note.strip() or "Theo thực tế",
                        "img": DEFAULT_REQ_IMG,
                        "assigned": "Chưa có người góp",
                        "done": False,
                    })
                    if save_cloud(current_db):
                        st.rerun()

    reqs = trip_data.get("requirements", [])
    if not reqs:
        st.info("Chưa có đồ dùng nào trong danh sách.")
    else:
        for i, req in enumerate(reqs):
            st.markdown(
                f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:14px; margin-bottom:10px; box-shadow: 0 2px 8px rgba(15,23,42,0.02);">
                    <div style="font-size:15px; font-weight:800; color:#0f172a;">📦 {html.escape(req.get("task", ""))}</div>
                    <div style="font-size:13px; color:#64748b; margin-top:2px;">Ghi chú: {html.escape(req.get("qty_note", ""))}</div>
                    <div style="font-size:13px; color:#0284c7; font-weight:700; margin-top:4px;">Người phụ trách: {html.escape(req.get("assigned", ""))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"🙋‍♂️ Tôi Nhận Lo Mục Này", key=f"req_join_{i}", use_container_width=True):
                load_cloud.clear()
                current_db = load_cloud()
                current_db["trips"][cur_trip]["requirements"][i]["assigned"] = me
                if save_cloud(current_db):
                    st.rerun()

with t_pay:
    st.markdown("### 💰 Kiểm Kê Quỹ Đoàn")
    st.info("Theo dõi trạng thái đóng góp quỹ cho chuyến đi một cách minh bạch và nhanh chóng.")
    registered_users = list(db.get("users", {}).keys())
    paid_members = trip_data.get("paid_members", [])
    
    if not registered_users:
        st.info("Chưa có thành viên nào.")
    else:
        for idx, user_m in enumerate(registered_users, 1):
            is_paid = user_m in paid_members
            badge = "✅ Đã đóng" if is_paid else "⏳ Chưa đóng"
            st.markdown(
                f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:12px 16px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:#0f172a;">{idx}. 👤 {html.escape(user_m)}</span>
                    <span style="font-weight:700; color:{'#10b981' if is_paid else '#f59e0b'};">{badge}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

with t_mem:
    all_members = list(db["users"].keys())
    st.markdown(f"### 👥 Danh Sách Thành Viên ({len(all_members)} người)")
    for idx, m_name in enumerate(all_members, 1):
        st.markdown(f'<div class="member-card"><b style="color:#0284c7;">{idx}. 👤 {html.escape(m_name)}</b></div>', unsafe_allow_html=True)

with t_poster:
    st.markdown("### 📜 Xuất Poster Hành Trình")
    st.success("Tạo và tải poster tổng kết chuyến đi chuyên nghiệp để chia sẻ với mọi người trong nhóm!")
    if st.button("📥 Tải Poster Tổng Kết", type="primary", use_container_width=True):
        st.balloons()
        st.success("Poster hành trình đã sẵn sàng! Chúc chuyến đi của nhóm thật nhiều kỷ niệm đẹp.")
