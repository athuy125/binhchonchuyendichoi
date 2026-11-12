import hashlib
import requests
import streamlit as st

st.set_page_config(page_title="ĐI CHƠIIIII", page_icon="⛺", layout="centered")

BIN_ID = "6af5b874ffd5d16053bc0858"
MASTER_KEY = "$2a$10$EpLPTXlcBTH5/mkxVMBLI.ZSv26QzgFaygkYFHZOa4V7OoVtsot12"

API_URL = "/".join(["https:/", "api.jsonbin.io", "v3", "b", BIN_ID])
HEADERS = {"Content-Type": "application/json", "X-Master-Key": MASTER_KEY}

CSS_STYLE = """
<style>
.stApp { background-color: #0b1120; color: #f8fafc; }
.hero-banner { background: linear-gradient(135deg, #059669 0%, #2563eb 100%); border-radius: 16px; padding: 24px; margin-bottom: 22px; color: #ffffff; box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4); }
.vote-badge { display: inline-block; background-color: #064e3b; color: #34d399; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 700; margin-bottom: 8px; }
.member-card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 14px 18px; margin-bottom: 10px; }
div.stButton > button { border-radius: 10px; font-weight: 600; }
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

def make_hash(text: str) -> str:
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()

@st.cache_data(ttl=15, show_spinner=False)
def load_cloud() -> dict:
    default = {"users": {}, "locations": [], "requirements": []}
    try:
        latest_url = "/".join([API_URL, "latest"])
        r = requests.get(latest_url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            res_json = r.json()
            record = res_json.get("record", res_json)
            if isinstance(record, dict):
                default["users"] = record.get("users", {})
                default["locations"] = record.get("locations", [])
                default["requirements"] = record.get("requirements", [])
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

db = load_cloud()

if st.session_state.user is None:
    AUTH_HTML = '<div class="hero-banner" style="text-align: center;"><h2 style="margin:0;">⛺ CỔNG THÀNH VIÊN ĐỘI</h2><p style="margin:8px 0 0 0; opacity: 0.9;">Đăng ký tài khoản mới (lần đầu) hoặc đăng nhập để tham gia kế hoạch 24/11</p></div>'
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
                        if save_cloud(fresh_db):
                            st.session_state.user = r_name
                            st.success("Đăng ký thành công!")
                            st.rerun()

    st.stop()
me = st.session_state.user

col_a, col_b, col_c = st.columns([3.5, 1.3, 1.2])
with col_a:
    st.success(f"🟢 Xin chào **{me}**! Đã bật tiết kiệm API.")
with col_b:
    if st.button("🔄 Làm mới", use_container_width=True):
        load_cloud.clear()
        st.rerun()
with col_c:
    if st.button("Thoát", use_container_width=True):
        st.session_state.user = None
        st.rerun()

MAIN_HTML = '<div class="hero-banner"><h2 style="margin:0;">⛺ DÃ NGOẠI & SÁT HẠCH TOÀN ĐỘI (24/11)</h2><p style="margin:8px 0 0 0; font-size:15px;">Ngày <b>24/11</b> anh em nghỉ nguyên ngày để đi cắm trại kết hợp Vòng 2 sát hạch nhân sự mới.</p></div>'
st.markdown(MAIN_HTML, unsafe_allow_html=True)

t_loc, t_req, t_mem = st.tabs(["🗳️ Bình Chọn Địa Điểm", "🎒 Đồ Cần Chuẩn Bị", "👥 Thành Viên"])

with t_loc:
    with st.expander("➕ Đề xuất địa điểm mới"):
        with st.form("add_loc_form", clear_on_submit=True):
            l_name = st.text_input("Tên địa điểm", placeholder="Ví dụ: Hồ Trị An...")
            l_desc = st.text_input("Mô tả / Khoảng cách", placeholder="Đường đẹp, cách trung tâm 40km...")
            if st.form_submit_button("Thêm Địa Điểm", use_container_width=True):
                if l_name.strip():
                    load_cloud.clear()
                    current_db = load_cloud()
                    new_loc = {"name": l_name.strip(), "desc": l_desc.strip() or "Chưa có mô tả", "voters": [me]}
                    current_db["locations"].append(new_loc)
                    if save_cloud(current_db):
                        st.rerun()
                else:
                    st.warning("Vui lòng nhập tên địa điểm!")

    if len(db["locations"]) == 0:
        st.info("Chưa có địa điểm nào được đề xuất.")

    for i, loc in enumerate(db["locations"]):
        voters = loc.get("voters", [])
        voted = me in voters

        with st.container(border=True):
            st.subheader(f"📍 {loc['name']}")
            st.write(loc.get("desc", ""))
            st.markdown(f'<span class="vote-badge">🔥 {len(voters)} phiếu bầu</span>', unsafe_allow_html=True)
            st.caption(f"👤 Đã vote: {', '.join(voters) if voters else 'Chưa có ai'}")

            c1, c2 = st.columns([4, 1.2])
            with c1:
                btn_text = "✅ Đã Vote (Bấm để hủy)" if voted else "👍 Bầu Chọn"
                if st.button(btn_text, key=f"vote_{i}", use_container_width=True):
                    load_cloud.clear()
                    current_db = load_cloud()
                    if i < len(current_db["locations"]):
                        cur_voters = current_db["locations"][i].get("voters", [])
                        if me in cur_voters:
                            cur_voters.remove(me)
                        else:
                            cur_voters.append(me)
                        current_db["locations"][i]["voters"] = cur_voters
                        if save_cloud(current_db):
                            st.rerun()
            with c2:
                if st.button("🗑️", key=f"del_loc_{i}", use_container_width=True):
                    load_cloud.clear()
                    current_db = load_cloud()
                    if i < len(current_db["locations"]):
                        current_db["locations"].pop(i)
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
                new_req = {"task": t_name.strip(), "assigned": t_who.strip() or "Chưa phân công", "done": False}
                current_db["requirements"].append(new_req)
                if save_cloud(current_db):
                    st.rerun()
            else:
                st.warning("Vui lòng nhập tên đồ dùng!")

    st.divider()
    if len(db["requirements"]) == 0:
        st.info("Chưa có đồ dùng nào trong danh sách.")

    for i, req in enumerate(db["requirements"]):
        r1, r2 = st.columns([4.5, 1])
        with r1:
            label_text = f"**{req['task']}** — *(Phụ trách: {req['assigned']})*"
            chk = st.checkbox(label_text, value=req.get("done", False), key=f"chk_{i}")
            if chk != req.get("done", False):
                load_cloud.clear()
                current_db = load_cloud()
                if i < len(current_db["requirements"]):
                    current_db["requirements"][i]["done"] = chk
                    if save_cloud(current_db):
                        st.rerun()
        with r2:
            if st.button("🗑️", key=f"del_req_{i}", use_container_width=True):
                load_cloud.clear()
                current_db = load_cloud()
                if i < len(current_db["requirements"]):
                    current_db["requirements"].pop(i)
                    if save_cloud(current_db):
                        st.rerun()

with t_mem:
    all_members = list(db["users"].keys())
    st.subheader(f"👥 Danh sách thành viên đã tham gia ({len(all_members)} người)")

    if len(all_members) == 0:
        st.info("Chưa có thành viên nào đăng ký.")
    else:
        for idx, member_name in enumerate(all_members, start=1):
            voted_places = [loc["name"] for loc in db["locations"] if member_name in loc.get("voters", [])]
            vote_status = f"✅ Đã vote: {', '.join(voted_places)}" if voted_places else "⏳ Chưa bình chọn địa điểm"
            assigned_tasks = [req["task"] for req in db["requirements"] if req.get("assigned") == member_name]
            task_status = f"🎒 Nhận lo ({len(assigned_tasks)}): {', '.join(assigned_tasks)}" if assigned_tasks else "📋 Chưa nhận đồ dùng"
            card_html = f'<div class="member-card"><div style="font-size: 16px; font-weight: 700; color: #38bdf8;">{idx}. 👤 {member_name}</div><div style="font-size: 13px; color: #cbd5e1; margin-top: 4px;">{vote_status} &nbsp;|&nbsp; {task_status}</div></div>'
            st.markdown(card_html, unsafe_allow_html=True)
